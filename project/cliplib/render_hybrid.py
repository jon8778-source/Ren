"""Render short Ren host shots, moving infographics and brief story cutaways.
Paths in shot lists are relative to that JSON. Source clip audio is never used.
"""
import argparse
import json
import math
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
W, H, FPS = 1280, 720, 24
INK, GREEN, GOLD = '#13233F', '#1E9E5A', '#F5B82E'


def font(size):
    return ImageFont.truetype(str(ROOT / 'project/remotion/public/fonts/fredoka-latin-600-normal.woff2'), size)


def duration(path):
    return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(path)]))


def validate(spec, base):
    shots = spec.get('shots', [])
    if not shots:
        raise ValueError('shots must not be empty')
    library = json.loads((ROOT / 'assets/ren_library/ren_library.json').read_text())
    clips = {c['file']: c for c in library['clips']}
    for i, s in enumerate(shots, 1):
        kind, seconds = s.get('kind'), s.get('duration', 0)
        if kind not in ('ren', 'graphic', 'story'):
            raise ValueError(f'shot {i}: kind must be ren, graphic or story')
        limit = {'ren': 5.5, 'graphic': 3.5, 'story': 2.5}[kind]
        if not isinstance(seconds, (float, int)) or not math.isfinite(seconds) or not 0 < seconds <= limit:
            raise ValueError(f'shot {i}: duration must be 0–{limit}s; split longer narration across more shots')
        if kind == 'ren':
            c = clips.get(s.get('clip', '') + '.mp4')
            if not c or c.get('status') != 'ok':
                raise ValueError(f'shot {i}: unapproved or unknown clip')
            path = ROOT / 'assets/ren_library' / c['file']
            start = s.get('in_s', c['in_s'])
            if start < c['in_s'] or start + seconds > min(c['out_s'], duration(path)) + 1 / FPS:
                raise ValueError(f'shot {i}: usable clip window too short; choose another approved clip')
            if s.get('mirror') and not c.get('mirrorable'):
                raise ValueError(f'shot {i}: clip cannot be mirrored')
            s['_clip'], s['_start'] = str(path), start
        if kind == 'story' and not s.get('image'):
            raise ValueError(f'shot {i}: story requires an image')
        for field in ('image', 'background_image'):
            if s.get(field) and not (base / s[field]).is_file():
                raise ValueError(f'shot {i}: missing {field}: {s[field]}')
        if len(s.get('title', '')) > 44 or len(s.get('subtitle', '')) > 65:
            raise ValueError(f'shot {i}: shorten title/subtitle for mobile readability')
    return shots


def office():
    # Deliberately simple scene; replace via background_image with the approved office art.
    im = Image.new('RGB', (W, H), '#EDF1F4')
    d = ImageDraw.Draw(im)
    d.rectangle((0, 578, W, H), fill='#D1B9A1')
    d.rectangle((50, 70, 490, 390), fill='#D7E8EF', outline=INK, width=5)
    d.line((270, 70, 270, 390), fill='white', width=10)
    d.rectangle((510, 425, 1250, 452), fill='#A77D59')
    d.rectangle((550, 452, 574, 578), fill=INK)
    d.rectangle((1185, 452, 1209, 578), fill=INK)
    d.rounded_rectangle((1000, 306, 1160, 420), radius=8, fill=INK)
    d.rectangle((1068, 420, 1095, 431), fill=INK)
    return im


def cover(path, zoom=1):
    with Image.open(path) as source:
        im = ImageOps.fit(source.convert('RGB'), (round(W * zoom), round(H * zoom)))
    x, y = (im.width - W) // 2, (im.height - H) // 2
    return im.crop((x, y, x + W, y + H))


def label(d, text, y, size, fill, x=650):
    # Wrap by measured pixel width, never by estimated character count.
    f = font(size)
    lines, line = [], ''
    for word in text.split():
        test = (line + ' ' + word).strip()
        if d.textlength(test, font=f) > W - x - 70:
            if not line or d.textlength(word, font=f) > W - x - 70:
                raise ValueError('Text exceeds safe width; shorten the wording')
            lines.append(line)
            line = word
        else:
            line = test
    if line:
        lines.append(line)
    if len(lines) > 2:
        raise ValueError('Text needs more than two lines; shorten the wording')
    for k, line in enumerate(lines):
        d.text((x, y + k * (size + 8)), line, font=f, fill=fill)
    return y + len(lines) * (size + 8)


def picture(s, frame, base, ren_frame=None):
    progress = frame / max(1, round(s['duration'] * FPS) - 1)
    kind = s['kind']
    if kind == 'story':
        im = Image.new('RGB', (W, H), '#EDF1F4')
        with Image.open(base / s['image']) as source:
            art = ImageOps.contain(source.convert('RGBA'), (round(510 * (1 + .025 * progress)), 520))
        im.paste(art, (70 + (510 - art.width) // 2, 95 + (520 - art.height) // 2), art)
    elif s.get('background_image'):
        im = cover(base / s['background_image'])
    else:
        im = office() if kind == 'ren' else Image.new('RGB', (W, H), '#FFFFFF')
    if ren_frame is not None:
        # Use the same soft white key as the existing clip renderer. No mouth animation added.
        a = np.asarray(ren_frame).astype(np.float32)
        distance = np.sqrt(np.mean(((255 - a) / 255) ** 2, axis=2))
        alpha = np.clip((distance - .07) / .03, 0, 1)
        rgba = np.dstack([a, alpha * 255]).astype(np.uint8)
        actor = Image.fromarray(rgba).resize((832, 468))
        if s.get('mirror'):
            actor = ImageOps.mirror(actor)
        im.paste(actor, (-88, 165), actor)
    d = ImageDraw.Draw(im)
    if kind in ('ren', 'story'):
        d.rounded_rectangle((610, 100, 1230, 405), radius=24, fill='white')
    x = 650 if kind in ('ren', 'story') else 100
    y = label(d, s.get('title', ''), 125, 52, INK, x)
    if kind == 'graphic':
        # A real count-up with a filling bar, rather than a held infographic slide.
        value = s.get('value')
        if value is not None:
            if not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
                raise ValueError('graphic value must be a finite nonnegative number')
            ease = min(1, progress / .75)
            d.text((100, 270), f"{s.get('prefix', '$')}{round(value * ease):,}", font=font(120), fill=GREEN)
            d.rounded_rectangle((100, 460, 1180, 492), radius=16, fill='#E3E7EE')
            if ease > .01:
                d.rounded_rectangle((100, 460, 100 + round(1080 * ease), 492), radius=16, fill=GOLD)
        y = 530
    label(d, s.get('subtitle', ''), max(265, y + 24), 36, INK, x)
    d.rectangle((0, 654, W, H), fill='white')
    d.text((48, 670), 'Illustrative example | Educational only, not financial advice', font=font(23), fill=INK)
    return im


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('shots', type=Path)
    ap.add_argument('--out', type=Path, default=HERE / 'out/hybrid')
    ap.add_argument('--voice-dir', type=Path)
    ap.add_argument('--silent-preview', action='store_true', help='Explicitly render a visual-only preview')
    ap.add_argument('--validate-only', action='store_true')
    args = ap.parse_args()
    spec = json.loads(args.shots.read_text())
    shots = validate(spec, args.shots.resolve().parent)
    if args.validate_only:
        print(f'VALID: {len(shots)} shots, {sum(s["duration"] for s in shots):.2f}s')
        return
    if not args.voice_dir and not args.silent_preview:
        ap.error('Supply --voice-dir with cloned narration, or explicitly use --silent-preview')
    args.out.mkdir(parents=True, exist_ok=True)
    segments, report, cursor = [], [], 0
    for i, s in enumerate(shots, 1):
        n = round(s['duration'] * FPS)
        voice = args.voice_dir / f'line_{i:02d}.wav' if args.voice_dir else None
        if voice and (not voice.is_file() or duration(voice) > n / FPS - .1):
            raise ValueError(f'shot {i}: missing voice or narration too long; split line across more shots')
        target = args.out / f'shot_{i:02d}.mp4'
        decoder = None
        if s['kind'] == 'ren':
            decoder = subprocess.Popen(['ffmpeg', '-v', 'error', '-ss', str(s['_start']), '-i', s['_clip'],
                '-an', '-vf', f'fps={FPS},scale={W}:{H}', '-frames:v', str(n), '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
        cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-']
        cmd += ['-i', str(voice)] if voice else ['-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=mono']
        cmd += ['-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'fast', '-crf', '20', '-pix_fmt', 'yuv420p',
                '-af', 'apad', '-t', str(n / FPS), '-c:a', 'aac', '-ar', '48000', '-ac', '1', '-movflags', '+faststart', str(target)]
        encoder = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        try:
            for frame in range(n):
                actor = None
                if decoder:
                    raw = decoder.stdout.read(W * H * 3)
                    if len(raw) != W * H * 3:
                        raise ValueError(f'shot {i}: source ended unexpectedly')
                    actor = Image.frombytes('RGB', (W, H), raw)
                encoder.stdin.write(picture(s, frame, args.shots.resolve().parent, actor).tobytes())
        finally:
            encoder.stdin.close()
            encoder_status = encoder.wait()
            if decoder:
                decoder.stdout.close()
                decoder_status = decoder.wait()
                if decoder_status:
                    raise RuntimeError(f'shot {i}: decoder failed ({decoder_status})')
        if encoder_status:
            raise RuntimeError(f'shot {i}: encoder failed ({encoder_status})')
        segments.append(target)
        report.append({'shot': i, 'kind': s['kind'], 'start_s': cursor / FPS, 'end_s': (cursor + n) / FPS, 'voice': s.get('voice', '')})
        cursor += n
        print(f'Rendered {i}/{len(shots)}: {s["kind"]}', flush=True)
    listing = args.out / 'concat.txt'
    listing.write_text(''.join(f"file '{p.name}'\n" for p in segments))
    final = args.out / 'video.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(listing),
                    '-c:v', 'copy', '-af', 'loudnorm=I=-16:TP=-1.5:LRA=9', '-c:a', 'aac', '-movflags', '+faststart', str(final)], check=True)
    (args.out / 'report.json').write_text(json.dumps({'duration_s': cursor / FPS, 'silent_preview': not bool(args.voice_dir), 'shots': report}, indent=2) + '\n')
    print(final)


if __name__ == '__main__':
    main()
