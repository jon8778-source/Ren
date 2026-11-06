"""Opt-in Ren v3 Shorts preflight, approval gate and technical QA.

No imports into long-form production. Rendering remains in approved adapters.
Requires FFmpeg/FFprobe and numpy for media QA; preflight uses only stdlib.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

SAFE = (72, 180, 900, 1560)
DISCLAIMER = 'Educational content only, not financial advice.'


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def load(path):
    return json.loads(Path(path).read_text())


def resolve(manifest_path, value):
    return (Path(manifest_path).resolve().parent / value).resolve()


def fingerprint(manifest_path):
    """Include actual bytes as well as declared hashes: stale approval fails closed."""
    m = load(manifest_path)
    files = {a['path']: sha(resolve(manifest_path, a['path']))
             for a in m['assets']}
    return digest({'manifest': m, 'files': files,
                   'asset_report_sha256': sha(resolve(manifest_path, m['asset_report']))})


def scene_cache_key(scene, dependency_hashes, renderer_hash):
    """Adapters may cache scene chunks with this key, never by filename alone."""
    return digest({'scene': scene, 'dependencies': dependency_hashes,
                   'renderer': renderer_hash})


class SceneCache:
    """Verified encoded scene chunks; unaffected keys survive targeted replacement."""
    def __init__(self, directory):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def paths(self, key):
        if len(key) != 64 or any(c not in '0123456789abcdef' for c in key):
            raise ValueError('Cache key must be a SHA-256 digest')
        return self.directory/(key+'.mp4'), self.directory/(key+'.json')

    def get(self, key, frames):
        video, metadata = self.paths(key)
        if not video.is_file() or not metadata.is_file():
            return None
        try:
            record = load(metadata)
            if record['frames'] == frames and record['sha256'] == sha(video):
                return video
        except (ValueError, KeyError, OSError):
            pass
        return None

    def store(self, key, source, frames):
        import shutil
        # Validate an adapter's chunk before declaring it reusable.
        probe = json.loads(subprocess.check_output([
            'ffprobe', '-v', 'error', '-count_frames', '-show_streams',
            '-of', 'json', str(source)]))
        streams = probe['streams']
        v = next((s for s in streams if s['codec_type'] == 'video'), {})
        if (v.get('width'), v.get('height'), v.get('r_frame_rate'),
            v.get('codec_name'), v.get('pix_fmt'), int(v.get('nb_read_frames', 0))) != (
                1080, 1920, '24/1', 'h264', 'yuv420p', frames):
            raise ValueError('Cached chunk geometry/codec/frame count invalid')
        if any(s['codec_type'] == 'audio' for s in streams):
            raise ValueError('Scene chunks must discard animation-source audio')
        subprocess.run(['ffmpeg', '-v', 'error', '-xerror', '-i', str(source),
                        '-f', 'null', '-'], check=True, capture_output=True)
        video, metadata = self.paths(key)
        temporary = video.with_suffix('.pending')
        shutil.copyfile(source, temporary)
        temporary.replace(video)
        metadata.write_text(json.dumps({'frames': frames, 'sha256': sha(video)})+'\n')
        return video


def preflight(path, stage='prototype'):
    m = load(path)
    errors, warnings = [], []
    if m.get('schema_version') != 1:
        errors.append('Unsupported/missing schema_version')
    if (m.get('width'), m.get('height'), m.get('fps')) != (1080, 1920, 24):
        errors.append('Canvas must be native 1080x1920 at 24fps')
    if m.get('full_bleed') is not True or m.get('permanent_border') is not False:
        errors.append('Require full-bleed scenes and no permanent border')
    total = m.get('frames', 0)
    if not isinstance(total, int) or total < 360:
        errors.append('Full timeline must contain at least the 360-frame prototype')
    if not m.get('asset_report') or not resolve(path, m['asset_report']).is_file():
        errors.append('Missing asset requirements report')
    assets = m.get('assets', [])
    ids = [a.get('id') for a in assets]
    if not assets or None in ids or len(ids) != len(set(ids)):
        errors.append('Assets require unique nonempty IDs')
    for kind in ('script', 'audio', 'renderer', 'configuration', 'character', 'environment'):
        if not any(a.get('kind') == kind for a in assets):
            errors.append(f'Missing dependency class: {kind}')
    for a in assets:
        target = resolve(path, a.get('path', ''))
        if not target.is_file():
            errors.append(f"Missing asset: {a.get('id')}")
        elif a.get('sha256') != sha(target):
            errors.append(f"Changed/unhashed asset: {a.get('id')}")
        if a.get('status') != 'approved' or not a.get('approval_evidence'):
            errors.append(f"Unapproved dependency: {a.get('id')}")
    scenes = m.get('scenes', [])
    cursor, animations = 0, Counter()
    scene_ids = [s.get('id') for s in scenes]
    if not scenes or None in scene_ids or len(scene_ids) != len(set(scene_ids)):
        errors.append('Scenes require unique nonempty IDs')
    for s in scenes:
        start, end = s.get('start_frame', -1), s.get('end_frame', -1)
        if not isinstance(start, int) or not isinstance(end, int) or start != cursor or end <= start:
            errors.append(f"Scene timeline gap/overlap/invalid frames: {s.get('id')}")
        cursor = end
        if not s.get('composition') or not s.get('action') or not s.get('motion_purpose'):
            errors.append(f"Scene lacks composition/action/purpose: {s.get('id')}")
        if not s.get('assets') or not set(s.get('assets', [])).issubset(ids):
            errors.append(f"Unresolved scene assets: {s.get('id')}")
        duration = (end - start) / 24
        if not 2 <= duration <= 4 and not s.get('timing_justification'):
            errors.append(f"Explain visual beat outside 2-4s: {s.get('id')}")
        limits = {'presenter': 5.5, 'story_still': 2.5, 'graphic': 3.5}
        if duration > limits.get(s.get('kind'), 4) and not s.get('timing_justification'):
            errors.append(f"Explain shot-length exception: {s.get('id')}")
        for animation in s.get('animations', []):
            animations[animation] += 1
            if animations[animation] > 1 and not s.get('repeat_justification'):
                errors.append(f"Repeated animation needs narrative reason: {animation}")
    if cursor != total:
        errors.append('Scene frame coverage differs from declared full timeline')
    preview = [s for s in scenes if s.get('start_frame', 999999) < 360]
    if len({s.get('composition') for s in preview}) < 3:
        errors.append('Prototype needs at least three distinct compositions')
    if not any(s.get('environment_fullscreen') for s in preview):
        errors.append('Prototype must demonstrate full-screen environmental artwork')
    cues = m.get('audio_cues', [])
    if not cues:
        errors.append('Missing narration cue timings')
    last = 0
    for c in cues:
        if not 0 <= c['start'] < c['end'] <= total / 24 or c['start'] < last:
            errors.append('Narration cues overlap or exceed timeline')
        last = c['end']
    return {'errors': errors, 'warnings': warnings, 'stage': stage}


class LayoutRecorder:
    """Record actual Pillow text bounds at final coordinates, including motion extrema."""
    def __init__(self):
        self.scenes = {}

    def begin_scene(self, scene):
        self.scenes.setdefault(scene, [])

    def record(self, scene, draw, xy, text, font, start, end, role='text', **kwargs):
        box = draw.multiline_textbbox(xy, text, font=font, **kwargs)
        self.scenes.setdefault(scene, []).append(dict(
            text=text, bbox=list(box), font_px=font.size, role=role,
            start=start, end=end))
        return box

    def save(self, path):
        Path(path).write_text(json.dumps({'scenes': self.scenes}, indent=2) + '\n')


def check_layout(m, layout, duration):
    errors = []
    scene_map = {s['id']: s for s in m['scenes'] if s['start_frame'] / 24 < duration}
    evidence = layout.get('scenes', {})
    for sid, scene in scene_map.items():
        if sid not in evidence:
            errors.append(f'Missing measured layout evidence: {sid}')
        for item in evidence.get(sid, []):
            x0, y0, x1, y1 = item['bbox']
            if not (SAFE[0] <= x0 < x1 <= SAFE[2] and SAFE[1] <= y0 < y1 <= SAFE[3]):
                errors.append(f'Text outside safe area: {sid}: {item["text"]}')
            minimum = {'caption': 40, 'disclaimer': 30}.get(item.get('role'), 42)
            if item.get('font_px', 0) < minimum:
                errors.append(f'Text too small: {sid}')
            if not (scene['start_frame']/24 <= item['start'] < item['end'] <= min(duration, scene['end_frame']/24)):
                errors.append(f'Text interval outside scene: {sid}')
    # Exact disclaimer may span connected scenes; require continuous final 2 seconds.
    intervals = sorted((i['start'], i['end']) for items in evidence.values() for i in items
                       if i.get('role') == 'disclaimer' and ' '.join(i['text'].split()) == DISCLAIMER)
    cursor = duration - 2
    for start, end in intervals:
        if start <= cursor + 1/24 and end > cursor:
            cursor = end
    if cursor < duration - 1/24:
        errors.append('Exact end disclaimer must remain visible for at least 2 seconds')
    return errors


def pixel_checks(frames):
    """Conservative heuristics; stable walls/holds need human interpretation."""
    import numpy as np
    errors, warnings = [], []
    if np.any((frames.mean(axis=(1,2,3)) < 3) & (frames.std(axis=(1,2,3)) < 3)):
        errors.append('Black/blank frames detected')
    sides = [frames[:, :3], frames[:, -3:], frames[:, :, :3], frames[:, :, -3:]]
    flat, dark = [], []
    for band in sides:
        means = band.mean(axis=(1,2))
        uniform = band.std(axis=(1,2)).max(axis=1) < 4
        flat.append(bool(uniform.mean() > .9 and means.std(axis=0).max() < 4))
        dark.append(bool((uniform & (means.max(axis=1) < 12)).mean() > .9))
    if (dark[0] and dark[1]) or (dark[2] and dark[3]):
        errors.append('Persistent black bars suspected on opposite edges')
    if (flat[0] and flat[1]) or (flat[2] and flat[3]):
        warnings.append('Persistent uniform edge bands: review for borders/letterboxing; walls may trigger this heuristic')
    diffs = np.max(np.abs(frames[1:].astype('int16') - frames[:-1].astype('int16')), axis=(1,2,3))
    longest = run = 0
    for equal in diffs == 0:
        run = run + 1 if equal else 0
        longest = max(longest, run)
    if longest >= 12:
        warnings.append(f'Frozen/duplicate sampled-frame run: {(longest+1)/24:.2f}s; review intentional holds')
    return errors, warnings, {'longest_identical_frame_run': longest + 1,
                              'persistent_uniform_edges': flat}


def media_qa(video, duration):
    import numpy as np
    errors, warnings = [], []
    probe = json.loads(subprocess.check_output([
        'ffprobe', '-v', 'error', '-count_frames', '-show_streams', '-show_format',
        '-of', 'json', str(video)]))
    streams = probe['streams']
    v = next((s for s in streams if s['codec_type'] == 'video'), {})
    a = next((s for s in streams if s['codec_type'] == 'audio'), {})
    if (v.get('width'), v.get('height')) != (1080, 1920):
        errors.append('Resolution/aspect must be 1080x1920 / 9:16')
    if v.get('r_frame_rate') != '24/1' or v.get('codec_name') != 'h264' or v.get('pix_fmt') != 'yuv420p':
        errors.append('Require 24fps H.264/yuv420p')
    if a.get('codec_name') != 'aac':
        errors.append('Missing AAC audio')
    count = int(v.get('nb_read_frames', 0))
    if count != round(duration * 24) or abs(float(probe['format']['duration']) - duration) > .08:
        errors.append('Output duration/frame count differs from expected timeline')
    if a:
        av = abs(float(a.get('start_time', 0)) - float(v.get('start_time', 0)))
        endpoint = abs(float(a.get('duration', 0)) - float(v.get('duration', 0)))
        if av > .08 or endpoint > .1:
            errors.append('A/V stream start/end differ by more than tolerance')
    else:
        av = endpoint = None
    timeline = json.loads(subprocess.check_output([
        'ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_frames',
        '-show_entries', 'frame=best_effort_timestamp_time', '-of', 'json', str(video)]))
    pts = [float(f['best_effort_timestamp_time']) for f in timeline['frames']]
    if len(pts) != count or any(abs(b-a-1/24) > .002 for a,b in zip(pts,pts[1:])):
        errors.append('Missing/duplicated/nonuniform frame timestamps')
    subprocess.run(['ffmpeg', '-v', 'error', '-xerror', '-i', str(video), '-f', 'null', '-'], check=True, capture_output=True)
    raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-xerror', '-i', str(video),
                                   '-map', '0:v:0', '-vf', 'scale=108:192', '-pix_fmt', 'rgb24', '-f', 'rawvideo', '-'])
    frames = np.frombuffer(raw, dtype='uint8').reshape(-1,192,108,3)
    e,w,pixels = pixel_checks(frames)
    errors.extend(e); warnings.extend(w)
    return {'errors': errors, 'warnings': warnings, 'frames': count,
            'duration_seconds': float(probe['format']['duration']), 'full_fatal_decode': True,
            'av_start_difference': av, 'av_duration_difference': endpoint, **pixels}


def write_report(path, report):
    path = Path(path)
    path.write_text(json.dumps(report, indent=2) + '\n')
    lines = ['# Ren Shorts QA', '', f"Status: {report['status']}", '']
    for key in ('errors', 'warnings'):
        lines += [f'{key.title()}:'] + ['- ' + s for s in report[key]] + ['']
    lines += ['Human review required: character/style consistency, environmental fill,',
              'storytelling, reading time, animation motivation, audio listening and device playback.',
              'Technical checks do not certify spoken words or lip sync.']
    path.with_suffix('.md').write_text('\n'.join(lines) + '\n')


def qa(manifest, video, stage, report_path):
    m = load(manifest)
    result = preflight(manifest, stage)
    if result['errors']:
        result['status'] = 'fail'
        write_report(report_path, result)
        return result
    duration = 15 if stage == 'prototype' else m['frames']/24
    media = media_qa(video, duration)
    for key in ('errors', 'warnings'):
        result[key].extend(media.pop(key))
    layout = resolve(manifest, m['layout_evidence'])
    if not layout.is_file():
        result['errors'].append('Missing renderer-measured layout evidence')
    else:
        result['errors'].extend(check_layout(m, load(layout), duration))
    result.update(media, video_sha256=sha(video), fingerprint=fingerprint(manifest),
                  stage=stage, status='fail' if result['errors'] else 'technical-pass-review-required')
    write_report(report_path, result)
    return result


def approved(manifest, prototype, report, approval):
    r, a = load(report), load(approval)
    current = fingerprint(manifest)
    if r.get('errors') or r.get('stage') != 'prototype' or r.get('status') != 'technical-pass-review-required':
        raise ValueError('Prototype QA must pass before approval/full rendering')
    if not (r.get('fingerprint') == a.get('fingerprint') == current and
            r.get('video_sha256') == a.get('prototype_sha256') == sha(prototype) and
            a.get('report_sha256') == sha(report)):
        raise ValueError('Stale prototype/report/approval: production inputs or media changed')
    if not a.get('by') or not a.get('evidence') or not a.get('approved_at') or not a.get('review_notes'):
        raise ValueError('Explicit owner approval evidence missing')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for command in ('preflight', 'qa', 'record-approval', 'run'):
        p = sub.add_parser(command)
        p.add_argument('--manifest', type=Path, required=True)
        if command in ('qa', 'run'):
            p.add_argument('--stage', choices=['prototype','full'], required=True)
            p.add_argument('--output', type=Path, required=True)
        if command in ('record-approval',):
            p.add_argument('--prototype', type=Path, required=True)
            p.add_argument('--report', type=Path, required=True)
            p.add_argument('--by', required=True)
            p.add_argument('--evidence', required=True)
            p.add_argument('--review-notes', type=Path, required=True,
                           help='Actual human review notes, including resolution of every QA warning')
        if command == 'run':
            p.add_argument('renderer_command', nargs=argparse.REMAINDER)
    p = sub.add_parser('inspect')
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--duration', type=float, required=True)
    p.add_argument('--report', type=Path, required=True)
    args = parser.parse_args(argv)
    if args.command == 'inspect':
        r = media_qa(args.output, args.duration)
        r['status'] = 'fail' if r['errors'] else 'technical-pass-review-required'
        r['scope'] = 'media only; asset/layout/approval checks not performed'
        write_report(args.report, r)
        print(json.dumps(r, indent=2))
        return 1 if r['errors'] else 0
    m = load(args.manifest)
    pre = preflight(args.manifest, getattr(args, 'stage', 'prototype'))
    if pre['errors']:
        print(json.dumps(pre, indent=2))
        return 1
    if args.command == 'preflight':
        print('Preflight passed; explicit prototype approval still required before full render.')
        return 0
    approval = resolve(args.manifest, 'prototype-approval.json')
    if args.command == 'record-approval':
        r = load(args.report)
        record = {'by': args.by, 'evidence': args.evidence,
                  'approved_at': datetime.now(timezone.utc).isoformat(),
                  'review_notes': args.review_notes.read_text().strip(),
                  'fingerprint': fingerprint(args.manifest),
                  'prototype_sha256': sha(args.prototype), 'report_sha256': sha(args.report)}
        # Validate before writing; do not replace an existing record on failure.
        temporary = approval.with_suffix('.pending.json')
        temporary.write_text(json.dumps(record, indent=2) + '\n')
        try:
            approved(args.manifest, args.prototype, args.report, temporary)
            temporary.replace(approval)
        finally:
            temporary.unlink(missing_ok=True)
        print('Recorded provided owner approval evidence; no rendering performed.')
        return 0
    if args.command == 'run':
        if args.stage == 'full':
            approved(args.manifest, resolve(args.manifest, m['prototype']),
                     resolve(args.manifest, m['prototype_report']), approval)
        cmd = args.renderer_command
        if cmd[:1] == ['--']:
            cmd = cmd[1:]
        if not cmd:
            raise ValueError('Supply an approved renderer adapter command after --')
        env = dict(os.environ, REN_SHORTS_STAGE=args.stage,
                   REN_SHORTS_MAX_FRAMES=str(360 if args.stage == 'prototype' else m['frames']))
        subprocess.run(cmd, check=True, env=env)
    report = args.output.with_suffix('.qa.json')
    result = qa(args.manifest, args.output, args.stage, report)
    print(f"{result['status']}: {report}")
    return 1 if result['errors'] else 0


def cli():
    try:
        return main()
    except (ValueError, KeyError, TypeError, OSError, subprocess.CalledProcessError) as error:
        print(f'Shorts workflow blocked: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(cli())
