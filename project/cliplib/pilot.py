"""Resumable, free-ZeroGPU-only coffee pilot. See project/pilots/daily-coffee/README.md."""
import argparse
import contextlib
import fcntl
import hashlib
import importlib.metadata
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import soundfile as sf

from qwen_voice import COFFEE_TEST_TEXT, validate_generated_duration

ROOT = Path(__file__).resolve().parents[2]
DEFAULT = ROOT / 'project/pilots/daily-coffee'
BRANCH = 'codex/ren-coffee-pilot'
FREE_RESERVE = 120  # conservative GPU-second budget for the demo's 60s allocation
VOICE = {
    'space': 'Qwen/Qwen3-TTS', 'endpoint': '/generate_voice_clone',
    'model': 'Qwen/Qwen3-TTS-12Hz-1.7B-Base', 'model_size': '1.7B',
    'language': 'English', 'use_xvector_only': True,
    'reference': 'Audio/ren_reference.wav', 'transcript': 'Audio/ren_reference.txt',
    'other_generation_parameters': 'unchanged public Space defaults',
}


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + '.tmp')
    with temp.open('w') as f:
        json.dump(value, f, indent=2, allow_nan=False)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())
    os.replace(temp, path)


def safe_error(error):
    message = str(error)
    token = os.environ.get('HF_TOKEN')
    if token:
        message = message.replace(token, '[REDACTED]')
    return re.sub(r'hf_[A-Za-z0-9]+', '[REDACTED]', message)[:1500]


def script_segments(folder):
    script = (folder / 'script.md').read_text()
    parts = re.findall(r'^## (s\d+) — ([^\n]+)\n(.*?)(?=^## |\Z)', script, re.M | re.S)
    if not parts or len({p[0] for p in parts}) != len(parts):
        raise ValueError('Missing or duplicate script segment IDs')
    return [{'id': key, 'title': title, 'text': ' '.join(text.split())} for key, title, text in parts]


def word_count(text):
    return len(re.findall(r"[A-Za-z0-9]+(?:['’][A-Za-z]+)?", text))


def current_settings():
    return {**VOICE, 'reference_sha256': digest(ROOT / VOICE['reference']),
            'transcript_sha256': digest(ROOT / VOICE['transcript'])}


def fingerprint(text, settings):
    return hashlib.sha256(json.dumps({'text': text, 'settings': settings}, sort_keys=True).encode()).hexdigest()


def checkpoint(folder, manifest, publish=False):
    manifest['updated_at'] = now()
    save(folder / 'manifest.json', manifest)
    if not publish:
        return
    branch = subprocess.check_output(['git', 'branch', '--show-current'], cwd=ROOT, text=True).strip()
    if branch != BRANCH:
        raise RuntimeError(f'Checkpoint publication requires branch {BRANCH}; never push main')
    relative = str(folder.relative_to(ROOT))
    # Only pilot files; caches/processed tracks/renders/locks are ignored. Never git add the workspace.
    subprocess.run(['git', 'add', '--', relative], cwd=ROOT, check=True)
    staged = subprocess.check_output(['git', 'diff', '--cached', '--name-only', '--', relative], cwd=ROOT, text=True)
    other = subprocess.check_output(['git', 'diff', '--cached', '--name-only'], cwd=ROOT, text=True)
    if set(other.splitlines()) - set(staged.splitlines()):
        raise RuntimeError('Unrelated staged changes: refusing to include them in checkpoint commit')
    token = os.environ.get('HF_TOKEN', '').encode()
    for name in staged.splitlines():
        path = ROOT / name
        if path.is_file() and token and token in path.read_bytes():
            raise RuntimeError('Secret detected in checkpoint; publication blocked')
    if staged:
        subprocess.run(['git', 'commit', '-m', 'Checkpoint daily coffee pilot'], cwd=ROOT, check=True,
                       stdout=subprocess.DEVNULL)
    subprocess.run(['git', 'push', 'origin', f'HEAD:refs/heads/{BRANCH}'], cwd=ROOT, check=True,
                   stdout=subprocess.DEVNULL)


def inspect_audio(path, text):
    audio, rate = sf.read(path, always_2d=True)
    if not len(audio) or audio.shape[1] != 1 or rate != 24000 or not np.isfinite(audio).all():
        raise ValueError('Corrupt audio or changed channel/sample-rate configuration')
    a = audio[:, 0]
    duration = len(a) / rate
    words = word_count(text)
    upper = 10 if text == COFFEE_TEST_TEXT else min(60, words / 1.8 + 3)
    lower = max(.5, words / 4.5)
    if not lower <= duration <= upper:
        raise ValueError(f'Duration {duration:.3f}s outside {lower:.2f}–{upper:.2f}s for {words} words')
    validate_generated_duration(text, path)  # retain the original sentence-specific guard
    hop = rate // 50
    rms = np.array([np.sqrt(np.mean(a[i:i + hop] ** 2)) for i in range(0, len(a), hop)])
    active = np.flatnonzero(rms > .004)
    if not len(active) or len(active) / len(rms) < .35 or np.sqrt(np.mean(a * a)) < .001:
        raise ValueError('Silent or predominantly silent narration')
    if np.mean(np.abs(a) >= .999) > .005:
        raise ValueError('Excessive clipping in original WAV')
    internal = rms[active[0]:active[-1] + 1] <= .004
    longest = run = 0
    for silent in internal:
        run = run + 1 if silent else 0
        longest = max(longest, run)
    if longest / 50 > 2.5:
        raise ValueError('Unexpected internal silence longer than 2.5 seconds; no automatic cut')
    # Only excessive edges are removed; keep 120ms of room tone on each side.
    first, last = active[0] / 50, min(duration, (active[-1] + 1) / 50)
    start = max(0, first - .12) if first > .4 else 0
    end = min(duration, last + .12) if duration - last > .4 else duration
    # Acoustic consistency screen, not speaker identification or pronunciation approval.
    pitches = []
    for i in range(0, len(a) - 1536, 4800):
        frame = a[i:i + 1536]
        if np.sqrt(np.mean(frame ** 2)) < .01:
            continue
        frame = (frame - frame.mean()) * np.hanning(len(frame))
        spectrum = np.fft.rfft(frame, n=4096)
        corr = np.fft.irfft(spectrum * spectrum.conj(), n=4096)
        lag = int(np.argmax(corr[60:401])) + 60
        if corr[0] and corr[lag] / corr[0] > .45:
            pitches.append(rate / lag)
    return {'duration_s': duration, 'sample_rate': rate, 'channels': 1, 'word_count': words,
            'duration_bounds_s': [lower, upper], 'active_fraction': len(active) / len(rms),
            'max_internal_silence_s': longest / 50, 'trim_start_s': start, 'trim_end_s': end,
            'processed_duration_s': end - start, 'median_pitch_hz': float(np.median(pitches)) if pitches else None,
            'technical': 'pass', 'transcription': 'unavailable; listening review required',
            'listening': 'pending', 'voice_identity': 'same cloning settings; listening review required'}


def load(folder):
    manifest = json.loads((folder / 'manifest.json').read_text())
    settings = current_settings()
    parts = script_segments(folder)
    if {p['id'] for p in parts} != {s['id'] for s in manifest['segments']}:
        raise ValueError('Segment IDs changed: explicitly revise the manifest before any generation')
    for p in parts:
        s = next(s for s in manifest['segments'] if s['id'] == p['id'])
        fp = fingerprint(p['text'], settings)
        if fp != s['fingerprint']:
            s.update(status='stale', pending_text=p['text'], pending_settings=settings,
                     stale_reason='Text or voice settings/reference hash changed')
        if s['status'] == 'complete':
            path = folder / s['file']
            if not path.exists() or digest(path) != s['sha256']:
                s.update(status='missing' if not path.exists() else 'stale',
                         stale_reason='Original WAV missing or hash mismatch')
            else:
                inspect_audio(path, s['text'])
    manifest['script_sha256'] = digest(folder / 'script.md')
    return manifest


def init(folder):
    if (folder / 'manifest.json').exists():
        print('Existing checkpoint retained; use status or resume')
        return
    settings = current_settings()
    evidence_path = Path('/workspace/ren-xvector-review/settings.json')
    evidence = json.loads(evidence_path.read_text())
    if not (evidence['use_xvector_only'] is True and evidence['model'] == VOICE['model'] and
            evidence['language'] == VOICE['language'] and
            evidence['reference_wav_sha256'] == settings['reference_sha256'] and
            evidence['reference_transcript_sha256'] == settings['transcript_sha256']):
        raise ValueError('Diagnostic provenance does not match requested voice configuration')
    manifest = {'schema': 1, 'title': 'Is Your Daily Coffee Really the Problem?', 'created_at': now(),
                'script_sha256': digest(folder / 'script.md'), 'settings': settings,
                'target_duration_s': [285, 315], 'segments': [], 'quota_events': [],
                'hardware_policy': 'public ZeroGPU only; no hardware upgrades, paid endpoints or fallback',
                'free_reserve_gpu_seconds': FREE_RESERVE, 'overall_status': 'prepared',
                'voice_test_review': 'duration passed; words/accent/identity not yet confirmed by owner'}
    for p in script_segments(folder):
        manifest['segments'].append({**p, 'settings': settings, 'fingerprint': fingerprint(p['text'], settings),
                                     'status': 'pending', 'attempts': []})
    first = manifest['segments'][0]
    if first['text'] != COFFEE_TEST_TEXT:
        raise ValueError('Opening sentence changed; cannot import test WAV')
    source = Path('/workspace/ren-xvector-review/voice/line_01.wav')
    expected = '911506e01391e3f03b3134616d9a383467d37684f96c46e993445d5e78b5dac6'
    if digest(source) != expected:
        raise ValueError('Diagnostic WAV changed')
    original = folder / 'audio' / f"s001-{first['fingerprint'][:12]}.wav"
    original.parent.mkdir(exist_ok=True)
    shutil.copyfile(source, original)
    first.update(status='complete', file=str(original.relative_to(folder)), sha256=digest(original),
                 validation=inspect_audio(original, first['text']), imported_from='xvector-only diagnostic')
    save(folder / 'voice-test-provenance.json', {'settings': evidence, 'original_sha256': expected,
                                               'review': 'duration passed; owner listening review pending'})
    checkpoint(folder, manifest)
    print('Script, segment IDs, settings, hashes and imported original WAV checkpointed')


def quota(api):
    q = api.get_zero_gpu_quota()
    return {'at': now(), 'remaining_gpu_seconds': q.remaining, 'base_gpu_seconds': q.base,
            'overquota_used': q.overquota_used, 'reset_at': q.resets_at.isoformat() if q.resets_at else None}


def quota_decrease(before, after):
    # The Hub recomputes reset timestamps with subsecond jitter; exact string equality is unreliable.
    a, b = before.get('reset_at'), after.get('reset_at')
    same_window = a == b or bool(a and b and abs((datetime.fromisoformat(a) - datetime.fromisoformat(b)).total_seconds()) < 60)
    difference = before['remaining_gpu_seconds'] - after['remaining_gpu_seconds']
    return difference if same_window and difference >= 0 else None


def resume(folder, publish):
    from gradio_client import Client, handle_file
    from huggingface_hub import HfApi
    manifest = load(folder)
    if not os.environ.get('HF_TOKEN'):
        raise ValueError('HF_TOKEN missing; no request submitted')
    # Blocks accidental replay after interruption, stale input, or a failed/rejected output.
    blocked = [s['id'] for s in manifest['segments'] if s['status'] in ('inflight', 'stale', 'failed', 'invalid')]
    if blocked:
        checkpoint(folder, manifest, publish)
        raise ValueError(f'Explicit review/recovery required for {blocked}; no generation submitted')
    api = HfApi(token=os.environ['HF_TOKEN'])
    api.whoami()
    runtime = api.get_space_runtime(VOICE['space'])
    if not str(runtime.hardware).startswith('zero-') or str(runtime.stage) != 'RUNNING':
        raise ValueError('Space is not running on ZeroGPU; stopped without generation')
    revision = api.space_info(VOICE['space']).sha
    if manifest.get('space_revision') and manifest['space_revision'] != revision:
        raise ValueError('Upstream Space revision changed; inspect model/defaults before approving further generation')
    manifest['space_revision'] = revision
    client = None
    for s in manifest['segments']:
        if s['status'] == 'complete':
            continue
        before = quota(api)  # no token/header values in checkpoints
        manifest['quota_events'].append({'segment': s['id'], 'phase': 'before', **before})
        if before['remaining_gpu_seconds'] < FREE_RESERVE:
            manifest.update(overall_status='quota_checkpoint', blocked_segment=s['id'], quota=before)
            checkpoint(folder, manifest, publish)
            print(f"QUOTA CHECKPOINT: {before['remaining_gpu_seconds']:.2f} free GPU-seconds; "
                  f"reserve {FREE_RESERVE}; reset {before['reset_at']}. No further requests.")
            return
        if client is None:
            import httpx
            client = Client(VOICE['space'], token=os.environ['HF_TOKEN'], verbose=False,
                            httpx_kwargs={'timeout': httpx.Timeout(120, connect=30)})
        attempt = {'started_at': now(), 'settings': s['settings'], 'before': before,
                   'phase': 'reference_upload', 'network_read_timeout_seconds': 120}
        s['attempts'].append(attempt)
        s['status'] = 'inflight'
        checkpoint(folder, manifest, publish)  # remote durable intent BEFORE call; never replay an unknown request
        print(f"Generating {s['id']}: {word_count(s['text'])} words; one request", flush=True)
        # Record queue admission separately from upload. On upload failure no inference was submitted;
        # an uncertain queue POST must never be replayed automatically.
        send_data = client.send_data

        def tracked_send(*args, **kwargs):
            attempt['phase'] = 'queue_submission'
            checkpoint(folder, manifest)
            event = send_data(*args, **kwargs)
            attempt.update(phase='queued', event_id=event, session_hash=client.session_hash)
            checkpoint(folder, manifest, publish)
            return event

        client.send_data = tracked_send
        t0 = time.monotonic()
        try:
            result, status = client.predict(
                ref_audio=handle_file(str(ROOT / VOICE['reference'])),
                ref_text=(ROOT / VOICE['transcript']).read_text().strip().strip('"“”').strip(),
                target_text=s['text'], language='English', use_xvector_only=True,
                model_size='1.7B', api_name='/generate_voice_clone')
            attempt['phase'] = 'returned'
            attempt['elapsed_seconds'] = time.monotonic() - t0
            attempt['space_status'] = safe_error(status)
            if not result or status.startswith('Error'):
                raise ValueError(f'No usable returned audio: {status}')
            source = Path(result)
            dest = folder / 'audio' / f"{s['id']}-{s['fingerprint'][:12]}-a{len(s['attempts'])}{source.suffix}"
            dest.parent.mkdir(exist_ok=True)
            # Save original bytes immediately, even when validation subsequently rejects them.
            with source.open('rb') as src, dest.open('wb') as dst:
                shutil.copyfileobj(src, dst)
                dst.flush()
                os.fsync(dst.fileno())
            s.update(file=str(dest.relative_to(folder)), sha256=digest(dest))
            checkpoint(folder, manifest)  # local durability before any analysis
            s['validation'] = inspect_audio(dest, s['text'])
            s['status'] = 'complete'
        except Exception as e:
            attempt['elapsed_seconds'] = time.monotonic() - t0
            attempt['error'] = safe_error(e)
            attempt['error_type'] = type(e).__name__
            s['status'] = 'invalid' if s.get('file') else 'failed'
            manifest['overall_status'] = 'generation_failure'
            if not s.get('file') and re.search(r'\bquota\b|rate.?limit', str(e), re.I):
                s['status'] = 'quota_blocked'
                manifest['overall_status'] = 'quota_checkpoint'
        finally:
            client.send_data = send_data
        try:
            after = quota(api)
            attempt['after'] = after
            attempt['observed_quota_decrease_gpu_seconds'] = quota_decrease(before, after)
            manifest['quota_events'].append({'segment': s['id'], 'phase': 'after', **after})
            if after['overquota_used'] > before['overquota_used']:
                manifest['overall_status'] = 'quota_policy_stop'
                checkpoint(folder, manifest, publish)
                raise ValueError('Unexpected over-quota usage reported; stopped')
        except ValueError:
            raise
        except Exception as e:
            attempt['quota_after_error'] = safe_error(e)
            manifest['overall_status'] = 'quota_unknown_stop'
            checkpoint(folder, manifest, publish)
            print('Quota observation unavailable; stopped, no further generation requests')
            return
        checkpoint(folder, manifest, publish)  # publish original + result together, including failures
        if s['status'] != 'complete':
            print(f"STOPPED at {s['id']}: {attempt.get('error')}; no retry", flush=True)
            return
        print(f"Saved {s['id']}: {s['validation']['duration_s']:.3f}s; listening review pending", flush=True)
    manifest['overall_status'] = 'narration_generated_review_pending'
    checkpoint(folder, manifest, publish)


def process_segment(folder, s):
    raw = folder / s['file']
    v = inspect_audio(raw, s['text'])
    out = folder / 'processed' / f"{s['id']}-{s['sha256'][:12]}.wav"
    out.parent.mkdir(exist_ok=True)
    if not out.exists():
        trim = f"atrim=start={v['trim_start_s']}:end={v['trim_end_s']},asetpts=PTS-STARTPTS"
        p = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', str(raw), '-af',
                            trim + ',loudnorm=I=-18:TP=-2:LRA=7:print_format=json', '-f', 'null', '-'],
                           capture_output=True, text=True, check=True)
        stats = json.JSONDecoder().raw_decode(p.stderr[p.stderr.rfind('{'):])[0]
        normalize = (f"loudnorm=I=-18:TP=-2:LRA=7:measured_I={stats['input_i']}:"
                     f"measured_TP={stats['input_tp']}:measured_LRA={stats['input_lra']}:"
                     f"measured_thresh={stats['input_thresh']}:offset={stats['target_offset']}:linear=true")
        temp = out.with_suffix('.tmp.wav')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(raw), '-af', trim + ',' + normalize,
                        '-ar', '48000', '-ac', '1', '-c:a', 'pcm_s24le', str(temp)], check=True)
        os.replace(temp, out)
    info = sf.info(out)
    if info.samplerate != 48000 or abs(info.duration - v['processed_duration_s']) > .05:
        raise ValueError('Processed audio cache changed timing or sample rate; rebuild the derived cache')
    return out, v


def status(folder):
    m = load(folder)
    checkpoint(folder, m)
    counts = {}
    for s in m['segments']:
        counts[s['status']] = counts.get(s['status'], 0) + 1
    measured = sum(s.get('validation', {}).get('duration_s', 0) for s in m['segments'] if s['status'] == 'complete')
    used = sum(a.get('observed_quota_decrease_gpu_seconds') or 0 for s in m['segments'] for a in s['attempts'])
    elapsed = sum(a.get('elapsed_seconds', 0) for s in m['segments'] for a in s['attempts'])
    report = {'overall': m['overall_status'], 'segments': counts, 'completed_original_audio_seconds': measured,
              'observed_quota_decrease_gpu_seconds': used, 'request_elapsed_seconds': elapsed,
              'remaining_segments': [s['id'] for s in m['segments'] if s['status'] != 'complete'],
              'last_quota': m.get('quota') or (m['quota_events'][-1] if m['quota_events'] else None),
              'resume_command': 'python project/cliplib/pilot.py resume --publish-checkpoints',
              'limitations': ['Owner listening review pending; no automatic claim of British accent/voice identity',
                              'ASR requires an already available local model; never silently downloads or uses a voice service',
                              'Bundled office and narrative art are template placeholders',
                              'Final 285–315s duration cannot be confirmed until all narration is generated']}
    save(folder / 'checkpoint-report.json', report)
    print(json.dumps(report, indent=2))


def word_error_rate(expected, actual):
    words = lambda s: re.findall(r"[a-z0-9]+(?:'[a-z]+)?", s.lower().replace('’', "'"))
    a, b = words(expected), words(actual)
    row = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        new = [i]
        for j, y in enumerate(b, 1):
            new.append(min(new[-1] + 1, row[j] + 1, row[j - 1] + (x != y)))
        row = new
    return row[-1] / max(1, len(a))


def verify(folder, asr_model=None):
    m = load(folder)
    model = None
    if asr_model:
        if not Path(asr_model).is_dir():
            raise ValueError('ASR model must already be local; no automatic remote service/download')
        from faster_whisper import WhisperModel
        model = WhisperModel(str(asr_model), device='cpu', compute_type='int8', local_files_only=True)
    reference_pitch = inspect_audio_for_pitch(ROOT / VOICE['reference'])
    for s in m['segments']:
        if s['status'] != 'complete':
            continue
        metrics = inspect_audio(folder / s['file'], s['text'])
        old = s.get('validation', {})
        metrics.update({k: old[k] for k in ('listening', 'transcription', 'transcript', 'wer') if k in old})
        pitch = metrics['median_pitch_hz']
        metrics['reference_pitch_hz'] = reference_pitch
        metrics['pitch_review_flag'] = bool(pitch and reference_pitch and abs(12 * math.log2(pitch / reference_pitch)) > 5)
        if model:
            parts, _ = model.transcribe(str(folder / s['file']), language='en', beam_size=5)
            transcript = ' '.join(part.text.strip() for part in parts)
            metrics.update(transcript=transcript, wer=word_error_rate(s['text'], transcript))
            metrics['transcription'] = 'pass' if metrics['wer'] <= .1 else 'mismatch; listening review required'
        s['validation'] = metrics
    checkpoint(folder, m)
    print('Technical/acoustic checks saved. Word accuracy and voice identity remain review items where unverified.')


def inspect_audio_for_pitch(path):
    # Reuse only the pitch measurement logic with a word count appropriate to reference duration.
    a, sr = sf.read(path)
    pitches = []
    for i in range(0, len(a) - 1536, 4800):
        f = a[i:i + 1536]
        if np.sqrt(np.mean(f * f)) < .01:
            continue
        f = (f - f.mean()) * np.hanning(len(f))
        z = np.fft.rfft(f, n=4096)
        c = np.fft.irfft(z * z.conj(), n=4096)
        lag = int(np.argmax(c[60:401])) + 60
        if c[0] and c[lag] / c[0] > .45:
            pitches.append(sr / lag)
    return float(np.median(pitches)) if pitches else None


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('command', choices=['init', 'status', 'resume', 'verify', 'assemble', 'reject', 'approve'])
    ap.add_argument('--pilot', type=Path, default=DEFAULT)
    ap.add_argument('--publish-checkpoints', action='store_true')
    ap.add_argument('--asr-model', type=Path)
    ap.add_argument('--segments', nargs='+')
    ap.add_argument('--reason')
    args = ap.parse_args()
    folder = args.pilot.resolve()
    folder.mkdir(parents=True, exist_ok=True)
    with (folder / '.workflow.lock').open('w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if args.command == 'init':
            init(folder)
        elif args.command == 'resume':
            resume(folder, args.publish_checkpoints)
        elif args.command == 'status':
            status(folder)
        elif args.command == 'verify':
            verify(folder, args.asr_model)
        elif args.command == 'assemble':
            from pilot_render import assemble
            assemble(folder)
        else:
            if not args.segments or not args.reason:
                ap.error('Review commands require --segments and --reason')
            m = load(folder)
            if set(args.segments) - {s['id'] for s in m['segments']}:
                ap.error('Unknown segment ID')
            for s in m['segments']:
                if s['id'] not in args.segments:
                    continue
                if args.command == 'reject':
                    s.setdefault('history', []).append(json.loads(json.dumps({k: v for k, v in s.items() if k != 'history'})))
                    text = s.pop('pending_text', s['text'])
                    settings = s.pop('pending_settings', current_settings())
                    s.update(status='rejected', rejection_reason=args.reason, text=text, settings=settings,
                             fingerprint=fingerprint(text, settings))
                    for key in ('file', 'sha256', 'validation'):
                        s.pop(key, None)
                else:
                    if s['status'] != 'complete':
                        ap.error('Only a technically complete segment can be approved after listening')
                    s['validation'].update(listening='owner approved', listening_note=args.reason)
            checkpoint(folder, m, args.publish_checkpoints)


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print('STOPPED:', safe_error(error), file=sys.stderr)
        raise SystemExit(1)
