"""Assemble validated paragraph WAVs and schedule multiple independent visual cuts."""
import json
import math
import subprocess
from pathlib import Path

import numpy as np
import soundfile as sf

import render_hybrid as hybrid
from pilot import ROOT, checkpoint, load, process_segment, save


def cuts(total_frames):
    kinds = [('ren', 108), ('graphic', 78), ('ren', 108), ('story', 54), ('ren', 108)]
    remaining, result, i = total_frames, [], 0
    while remaining:
        kind, maximum = kinds[i % len(kinds)]
        n = min(maximum, remaining)
        result.append([kind, n])
        remaining -= n
        i += 1
    if len(result) > 1 and result[-1][1] < 36:
        transfer = 36 - result[-1][1]
        for donor in reversed(result[:-1]):
            take = min(transfer, max(0, donor[1] - 36))
            donor[1] -= take
            result[-1][1] += take
            transfer -= take
            if not transfer:
                break
        if transfer:
            raise ValueError('Cannot schedule natural visual cuts for this segment')
    return result


def visual_plan(folder, segment_durations):
    m = load(folder)
    library = json.loads((ROOT / 'assets/ren_library/ren_library.json').read_text())
    available = [c for c in library['clips'] if c.get('status') == 'ok' and
                 c['out_s'] - c['in_s'] >= 4.5 and
                 hybrid.duration(ROOT / 'assets/ren_library' / c['file']) - c['in_s'] >= 4.5 and
                 not any(x in c['file'] for x in ('walk', 'exit', 'enter'))]
    if not available:
        raise ValueError('No suitable approved animated Ren clips')
    available.sort(key=lambda c: c['file'])
    shots, frames_so_far, seconds_so_far, actor = [], 0, 0., 0
    cues = {
        's003': (1460, '$4 × 365 days = $1,460'),
        's004': (1095, '($4 − $1) × 365 days = $1,095'),
        's009': (416, '2 × $4 × 52 weeks = $416'),
    }
    for s in m['segments']:
        seconds_so_far += segment_durations[s['id']]
        target = math.ceil(seconds_so_far * hybrid.FPS)
        frames = target - frames_so_far
        frames_so_far = target
        for kind, n in cuts(frames):
            shot = {'kind': kind, 'duration': n / hybrid.FPS, 'segment_id': s['id'],
                    'title': s['title'], 'subtitle': 'Spend with intention. Keep tomorrow in view.'}
            if s['id'] == 's001':
                shot['title'] = 'Keep the coffee?'
            if kind == 'ren':
                clip = available[actor % len(available)]
                actor += 1
                shot['clip'] = Path(clip['file']).stem
            elif kind == 'story':
                character = 'max-30' if actor % 2 else 'lena-30'
                # Absolute paths only in generated, ignored build output, not durable source settings.
                shot['image'] = str(ROOT / f'project/characters/{character}/neutral.png')
                shot['subtitle'] = 'Different priorities. Different choices.'
            elif s['id'] in cues:
                value, caption = cues[s['id']]
                shot.update(value=value, subtitle=caption)
            else:
                shot.update(steps=['Enjoy it?', 'Does it fit?', 'What is the alternative?'],
                            subtitle='Your priorities, your actual numbers.')
            shots.append(shot)
    return {'title': m['title'], 'shots': shots}


def master(folder, paths):
    build = folder / 'build'
    build.mkdir(exist_ok=True)
    # Streams concatenated without added inter-segment silence or overlap; original WAVs never modified.
    joined = build / 'narration-unmastered.wav'
    with sf.SoundFile(joined, 'w', samplerate=48000, channels=1, subtype='PCM_24') as dst:
        for path in paths:
            with sf.SoundFile(path) as src:
                if src.samplerate != 48000:
                    raise ValueError('Processed sample-rate mismatch')
                for block in src.blocks(blocksize=48000):
                    dst.write(block)
    first = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', str(joined), '-af',
                             'loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json', '-f', 'null', '-'],
                            capture_output=True, text=True, check=True)
    stats = json.JSONDecoder().raw_decode(first.stderr[first.stderr.rfind('{'):])[0]
    filt = (f"loudnorm=I=-16:TP=-1.5:LRA=9:measured_I={stats['input_i']}:"
            f"measured_TP={stats['input_tp']}:measured_LRA={stats['input_lra']}:"
            f"measured_thresh={stats['input_thresh']}:offset={stats['target_offset']}:linear=true")
    out = build / 'narration.wav'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(joined), '-af', filt,
                    '-ar', '48000', '-c:a', 'pcm_s24le', str(out)], check=True)
    return out


def assemble(folder):
    m = load(folder)
    if any(s['status'] != 'complete' for s in m['segments']):
        raise ValueError('Narration incomplete; refusing to render or label a partial video as finished')
    asr_mismatch = [s['id'] for s in m['segments'] if s['validation'].get('wer', 0) > .1 and
                    s['validation'].get('listening') != 'owner approved']
    if asr_mismatch:
        raise ValueError(f'Transcription mismatches need listening review: {asr_mismatch}')
    paths, durations = [], {}
    for s in m['segments']:
        path, metrics = process_segment(folder, s)
        paths.append(path)
        durations[s['id']] = sf.info(path).duration
    total = sum(durations.values())
    if not 285 <= total <= 315:
        m['overall_status'] = 'duration_review_required'
        checkpoint(folder, m)
        raise ValueError(f'Natural narration is {total:.3f}s, outside 285–315s. Revise meaningful script content '
                         'and explicitly reject affected segments; no speed changes or silence padding.')
    narration = master(folder, paths)
    spec = visual_plan(folder, durations)
    hybrid.validate(spec, folder / 'build')
    save(folder / 'build/shots.json', spec)
    subprocess.run([__import__('sys').executable, str(ROOT / 'project/cliplib/render_hybrid.py'),
                    str(folder / 'build/shots.json'), '--narration', str(narration), '--out', str(folder / 'renders')],
                   check=True)
    frames = folder / 'build/review-frames'
    frames.mkdir(exist_ok=True)
    cursor = 0
    for i, shot in enumerate(spec['shots']):
        # One frame in every shot; covers every segment and every cut type.
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(cursor + shot['duration'] / 2), '-i',
                        str(folder / 'renders/video.mp4'), '-frames:v', '1', str(frames / f'{i:03d}.jpg')], check=True)
        cursor += shot['duration']
    pending = [s['id'] for s in m['segments'] if s['validation'].get('listening') != 'owner approved']
    pitch_flags = [s['id'] for s in m['segments'] if s['validation'].get('pitch_review_flag')]
    save(folder / 'quality-report.json', {'status': 'complete pilot for review; not publishing approval',
        'narration_duration_s': hybrid.duration(narration), 'video_duration_s': hybrid.duration(folder / 'renders/video.mp4'),
        'target_duration_s': [285, 315], 'visual_shots': len(spec['shots']), 'music': False,
        'source_clip_audio': False, 'speed_changes': False, 'duration_padding': False,
        'edge_silence_only': True, 'master_target_lufs': -16, 'master_true_peak_target_dbtp': -1.5,
        'listening_review_pending': pending, 'acoustic_voice_consistency_flags': pitch_flags,
        'visual_review': 'shot midpoints exported; human inspection required',
        'placeholder_art': 'Bundled office and narrative character stills; not approved office/Alex artwork',
        'narration': 'build/narration.wav', 'video': 'renders/video.mp4'})
    m['overall_status'] = 'pilot_rendered_review_pending'
    checkpoint(folder, m)
    print('Rendered complete pilot for review:', folder / 'renders/video.mp4')
