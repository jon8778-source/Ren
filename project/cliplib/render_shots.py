"""Clip-library renderer (prototype): shot list JSON -> 1280x720 24fps MP4 with Ren's voice.

  .tools/venv/bin/python cliplib/render_shots.py cliplib/shots/<name>.json [--out cliplib/out/<name>]

Each shot plays one library clip (assets/ren_library, metadata in ren_library.json):
  - trimmed to the clip's in_s/out_s window, shifted by x_offset_px (negated when mirrored, since
    the flip moves Ren to the other side of centre) and then to the shot list's ren_x, on pure white;
  - near-white source background is keyed to #FFFFFF (colour distance from white under 0.07, soft to
    0.10; the backgrounds measure up to ~0.06 and Ren's pale shirt ~0.095);
  - shorter shot: cut at the neutral frame nearest the requested length (either side; if it falls
    before, ren_idle_calm fills the rest, so the shot can come out a little longer than asked);
  - longer shot: the clip's whole window, then ren_idle_calm;
  - a shot whose voice line would run into the next line is held on ren_idle_calm until it fits
    (next line starts at least config voice.gap_s after this one ends); the voice is never sped up;
  - 0.3s crossfade between shots, source audio discarded.
Text overlays go in a panel beside Ren; the script measures Ren's bounding box on every rendered
frame and refuses to render if any text would touch him. The voice uses the same Kokoro blend,
speed, edge trim and loudness target as pipeline/voice.py, one line per shot, placed at voice_at.
With --voice-dir, each shot's line comes from <dir>/line_01.wav, line_02.wav, ... instead (same edge
trim and loudness target) and starts at the shot's start.
Writes <out>/video.mp4, <out>/voice_only.wav and <out>/report.json (timings, cut points, fills, notes).

Shot list:
{
  "ren_x": 330,                       # where Ren's centre sits (text panel takes the other side)
  "disclaimer": "Example only, not financial advice",
  "shots": [{"clip": "ren_point_right", "mirror": false, "duration": 5.0, "skip_s": 0,
             "voice": "Four dollars a day.", "voice_at": 0.4,
             "overlays": [{"text": "$4 a day", "style": "number", "color": "ink", "at": 0.5}]}]
}
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFont

PROJECT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT / "pipeline"))
from common import load_config  # noqa: E402

LIB = PROJECT.parent / "assets" / "ren_library"
FONTS = PROJECT / "remotion" / "public" / "fonts"
W, H, FPS = 1280, 720, 24
XFADE = 0.3
SR = 24000
FILLER = "ren_idle_calm.mp4"
NEUTRAL_DIFF = 1.0      # mean grey-level difference (320x180) from the in/out frame that counts as neutral
REN_DARK = 200          # pixels darker than this (min channel) are Ren, not background
TEXT_GAP = 48           # minimum gap between Ren and any text
WHITEN = "format=rgba,colorkey=0xFFFFFF:0.07:0.03"
STYLES = {  # font file weight, size px
    "number": (700, 96), "title": (600, 60), "body": (500, 44), "label": (600, 34), "small": (500, 24),
}
OPEN_MOUTH = re.compile(r"open (mouth|grin|smile)|toothy|teeth|mouth talks|open mouth", re.I)


def run(cmd):
    subprocess.run(cmd, check=True)


def probe_frames(path):
    out = subprocess.check_output(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v",
                                   "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0", str(path)])
    return int(out)


def grey_frames(path, size=(320, 180)):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(path), "-vf",
                                   f"scale={size[0]}:{size[1]},format=gray", "-f", "rawvideo", "-"])
    return np.frombuffer(raw, np.uint8).reshape(-1, size[1], size[0]).astype(np.float32)


def load_library():
    lib = json.loads((LIB / "ren_library.json").read_text())
    return {c["file"]: c for c in lib["clips"]}


def clip_entry(lib, name):
    f = name if name.endswith(".mp4") else name + ".mp4"
    if f not in lib:
        raise SystemExit(f"{name}: not in ren_library.json")
    c = lib[f]
    if c.get("status") != "ok":
        raise SystemExit(f"{name}: status is {c.get('status')!r}")
    if not (LIB / f).exists():
        raise SystemExit(f"{name}: {f} missing from {LIB}")
    n = probe_frames(LIB / f)
    if round(c["out_s"] * FPS) > n:
        raise SystemExit(f"{name}: out_s {c['out_s']}s is past the end of the file ({n / FPS:.2f}s)")
    return c


def neutral_frames(c):
    """Frame indices inside the clip window that match its neutral in or out frame."""
    F = grey_frames(LIB / c["file"])
    a, b = round(c["in_s"] * FPS), min(round(c["out_s"] * FPS), len(F) - 1)
    d = [min(np.abs(F[i] - F[a]).mean(), np.abs(F[i] - F[b]).mean()) for i in range(a, b + 1)]
    return [a + k for k, v in enumerate(d) if v < NEUTRAL_DIFF]


def plan_shot(lib, shot):
    """Return the pieces [(entry, start_frame, n_frames, mirror)] making up one shot, and a note."""
    c = clip_entry(lib, shot["clip"])
    mirror = bool(shot.get("mirror"))
    if mirror and not c.get("mirrorable"):
        raise SystemExit(f"{shot['clip']}: mirror requested but the clip is not mirrorable")
    want = round(shot["duration"] * FPS)
    a, b = round(c["in_s"] * FPS), round(c["out_s"] * FPS)
    a += round(shot.get("skip_s", 0) * FPS)  # optional: start later inside the window (e.g. a walk-in)
    if a >= b:
        raise SystemExit(f"{shot['clip']}: skip_s leaves nothing of the clip window")
    if want >= b - a:
        cut = b
        note = f"clip window {(b - a) / FPS:.2f}s used whole"
    else:
        neutral = min([i for i in neutral_frames(c) if i > a] or [b], key=lambda i: (abs(i - (a + want)), i))
        cut = min(neutral + 1, b)  # the neutral frame is the last one shown
        note = f"cut at neutral frame {neutral / FPS:.2f}s (asked {(a + want) / FPS:.2f}s)"
    pieces = [(c, a, cut - a, mirror)]
    fill = want - (cut - a)
    if fill > 0:
        hold_idle(lib, pieces, fill)
        note += f"; {FILLER[:-4]} fills {fill / FPS:.2f}s"
    elif fill < -1:
        note += f"; shot runs {-fill / FPS:.2f}s longer than asked"
    return pieces, sum(p[2] for p in pieces), note


def hold_idle(lib, pieces, frames):
    """Append `frames` of ren_idle_calm (from its in_s, repeating its window if needed) to a shot."""
    idle = clip_entry(lib, FILLER)
    ia, ib = round(idle["in_s"] * FPS), round(idle["out_s"] * FPS)
    while frames > 0:
        n = min(frames, ib - ia)
        pieces.append((idle, ia, n, False))
        frames -= n


def load_lines(folder, count):
    """line_01.wav ... from folder as mono SR float arrays, edges trimmed like synth_lines."""
    out = []
    for k in range(count):
        path = Path(folder) / f"line_{k + 1:02d}.wav"
        if not path.exists():
            raise SystemExit(f"{path} missing")
        raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(SR),
                                       "-f", "f32le", "-"])
        a = np.frombuffer(raw, np.float32)
        idx = np.where(np.abs(a) > 0.01)[0]
        if not len(idx):
            raise SystemExit(f"{path} is silent")
        out.append(a[max(0, idx[0] - int(0.01 * SR)): idx[-1] + int(0.08 * SR)].copy())
    return out


def piece_filter(i, entry, start, n, mirror, ren_x):
    shift = (ren_x - W // 2) + (-entry["x_offset_px"] if mirror else entry["x_offset_px"])
    chain = f"[{i}:v]trim=start_frame={start}:end_frame={start + n},setpts=PTS-STARTPTS,{WHITEN}"
    if mirror:
        chain += ",hflip"
    return chain + f"[p{i}];color=white:s={W}x{H}:r={FPS}:d={n / FPS:.6f}[bg{i}];" \
                   f"[bg{i}][p{i}]overlay=x={shift}:y=0:shortest=1:format=rgb,setsar=1,format=yuv420p[s{i}]"


def ren_bbox(path):
    """Union of Ren's bounding box over every frame of a rendered (text-free) segment, full-res pixels."""
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(path), "-vf", "scale=640:360,format=gray",
                                   "-f", "rawvideo", "-"])
    F = np.frombuffer(raw, np.uint8).reshape(-1, 360, 640)
    m = (F < REN_DARK).any(0)
    cols, rows = np.where(m.any(0))[0], np.where(m.any(1))[0]
    return [int(cols.min()) * 2, int(rows.min()) * 2, int(cols.max()) * 2 + 1, int(rows.max()) * 2 + 1]


def font(style):
    weight, size = STYLES[style]
    return ImageFont.truetype(str(FONTS / f"fredoka-latin-{weight}-normal.woff2"), size)


def wrap(text, f, width):
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if f.getlength(trial) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    return lines + [cur]


def text_png(path, text, style, color, theme, panel, y):
    """Draw wrapped, left-aligned text in the panel starting at y. Returns its box (x0, y0, x1, y1)."""
    f = font(style)
    asc, desc = f.getmetrics()
    lh = int((asc + desc) * 1.08)
    lines = wrap(text, f, panel[1] - panel[0])
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for k, line in enumerate(lines):
        d.text((panel[0], y + k * lh), line, font=f, fill=theme[color])
    img.save(path)
    box = img.getbbox()
    return box, len(lines) * lh


def overlaps(a, b, gap=0):
    return not (a[2] + gap <= b[0] or b[2] + gap <= a[0] or a[3] + gap <= b[1] or b[3] + gap <= a[1])


def synth_lines(texts, voice_cfg):
    from kokoro_onnx import Kokoro
    tools = PROJECT / ".tools"
    style = sum(np.fromfile(tools / "voices" / f"{n}.bin", dtype=np.float32).reshape(-1, 1, 256) * w
                for n, w in voice_cfg["blend"].items())
    npz = tools / ".cliplib_voice.npz"
    np.savez(npz, voice=style)
    tts = Kokoro(str(tools / "kokoro-q8.onnx"), str(npz))
    out = []
    for t in texts:
        if not t:
            out.append(None)
            continue
        a, _ = tts.create(t, voice="voice", speed=voice_cfg["speed"], lang="en-us")
        idx = np.where(np.abs(a) > 0.01)[0]  # same edge trim as pipeline/voice.py
        out.append(a[max(0, idx[0] - int(0.01 * SR)): idx[-1] + int(0.08 * SR)].astype(np.float32))
    npz.unlink()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("shots")
    ap.add_argument("--out")
    ap.add_argument("--voice-dir", help="Use line_01.wav, line_02.wav, ... from here instead of Kokoro")
    args = ap.parse_args()
    spec = json.loads(Path(args.shots).read_text())
    out = Path(args.out or PROJECT / "cliplib" / "out" / Path(args.shots).stem)
    build = out / "build"
    shutil.rmtree(build, ignore_errors=True)
    build.mkdir(parents=True)
    cfg = load_config()
    theme = cfg["theme"]
    lib = load_library()
    ren_x = spec.get("ren_x", W // 2)
    shots = spec["shots"]

    # 1. Voice lines first, so a shot can be held long enough for its line
    if args.voice_dir:
        audio = load_lines(args.voice_dir, len(shots))
        voice_at = [0.0] * len(shots)
    else:
        audio = synth_lines([s.get("voice", "") for s in shots], cfg["voice"])
        voice_at = [s.get("voice_at", 0.4) for s in shots]

    # 2. Plan every shot and render its picture (no text yet)
    plans = []
    for k, shot in enumerate(shots):
        pieces, n, note = plan_shot(lib, shot)
        if audio[k] is not None:
            # This line must end gap_s before the next shot's line starts (or 0.6s before the end, if last)
            end = voice_at[k] + len(audio[k]) / SR
            nxt = voice_at[k + 1] if k + 1 < len(shots) and audio[k + 1] is not None else None
            need = end + XFADE + cfg["voice"]["gap_s"] - nxt if nxt is not None else end + 0.6
            short = int(np.ceil(need * FPS)) - n
            if short > 0:
                hold_idle(lib, pieces, short)
                n += short
                note += f"; held {short / FPS:.2f}s on {FILLER[:-4]} for the voice line"
        seg = build / f"shot{k:02d}_ren.mp4"
        inputs, graph = [], []
        for i, (entry, start, cnt, mirror) in enumerate(pieces):
            inputs += ["-i", str(LIB / entry["file"])]
            graph.append(piece_filter(i, entry, start, cnt, mirror, ren_x))
        graph.append("".join(f"[s{i}]" for i in range(len(pieces))) + f"concat=n={len(pieces)}:v=1:a=0[v]")
        run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(graph), "-map", "[v]", "-an",
             "-r", str(FPS), "-c:v", "libx264", "-crf", "12", "-preset", "fast", str(seg)])
        plans.append({"shot": k, "clip": shot["clip"], "mirror": bool(shot.get("mirror")),
                      "asked_s": shot["duration"], "frames": n, "duration_s": round(n / FPS, 3), "plan": note,
                      "pieces": [{"file": p[0]["file"], "from_s": round(p[1] / FPS, 3), "len_s": round(p[2] / FPS, 3),
                                  "mirror": p[3]} for p in pieces],
                      "ren_bbox": ren_bbox(seg), "segment": seg})

    # 3. Text panel beside Ren: everything on the far side of his widest reach in any shot
    right_side = ren_x < W // 2
    reach = max(p["ren_bbox"][2] for p in plans) if right_side else min(p["ren_bbox"][0] for p in plans)
    margin = cfg["layout"]["margin"] // 2
    panel = (reach + TEXT_GAP, W - margin) if right_side else (margin, reach - TEXT_GAP)
    if panel[1] - panel[0] < 320:
        raise SystemExit(f"Only {panel[1] - panel[0]}px beside Ren for text; move ren_x further to the side")

    # Disclaimer: small line at the bottom of the panel, whole video
    disc_png = build / "disclaimer.png"
    disc_box = None
    if spec.get("disclaimer"):
        f = font("small")
        y = H - margin // 2 - sum(f.getmetrics())
        disc_box, _ = text_png(disc_png, spec["disclaimer"], "small", "muted", theme, panel, y)

    # 4. Place each line on the final timeline
    starts, t = [], 0.0
    for p in plans:
        starts.append(t)
        t += p["duration_s"] - XFADE
    total = t + XFADE
    for k, (p, s, a) in enumerate(zip(plans, shots, audio)):
        p["start_s"] = round(starts[k], 3)
        if a is None:
            continue
        vs, ve = starts[k] + voice_at[k], starts[k] + voice_at[k] + len(a) / SR
        p.update(voice=s["voice"], voice_start_s=round(vs, 3), voice_end_s=round(ve, 3))
        if args.voice_dir:
            p["voice_file"] = str(Path(args.voice_dir) / f"line_{k + 1:02d}.wav")
    for k in range(1, len(plans)):
        if "voice_start_s" in plans[k] and "voice_end_s" in plans[k - 1]:
            plans[k]["gap_before_s"] = round(plans[k]["voice_start_s"] - plans[k - 1]["voice_end_s"], 3)

    # 5. Overlays per shot, checked against Ren's box on every frame of that shot
    for k, (p, s) in enumerate(zip(plans, shots)):
        ovs = s.get("overlays", [])
        heights = []
        for o in ovs:
            f = font(o.get("style", "body"))
            heights.append(len(wrap(o["text"], f, panel[1] - panel[0])) * int(sum(f.getmetrics()) * 1.08))
        gap = 18
        y = (H - sum(heights) - gap * max(0, len(ovs) - 1)) // 2 - 30
        p["overlays"] = []
        for j, o in enumerate(ovs):
            png = build / f"shot{k:02d}_text{j}.png"
            box, h = text_png(png, o["text"], o.get("style", "body"), o.get("color", "ink"), theme, panel, y)
            y += h + gap
            if overlaps(box, p["ren_bbox"], TEXT_GAP // 2):
                raise SystemExit(f"shot {k}: overlay {o['text']!r} {box} would touch Ren {p['ren_bbox']}")
            if disc_box and overlaps(box, disc_box, 8):
                raise SystemExit(f"shot {k}: overlay {o['text']!r} collides with the disclaimer")
            p["overlays"].append({"text": o["text"], "box": list(box), "at": o.get("at", 0.4), "png": png})
        if disc_box and overlaps(disc_box, p["ren_bbox"], TEXT_GAP // 2):
            raise SystemExit(f"shot {k}: disclaimer would touch Ren")

        # Burn this shot's text in, each overlay fading in over 0.25s at its time
        seg = build / f"shot{k:02d}.mp4"
        inputs, graph, last = ["-i", str(p["segment"])], [], "0:v"
        for j, o in enumerate(p["overlays"]):
            inputs += ["-loop", "1", "-framerate", str(FPS), "-i", str(o["png"])]
            graph.append(f"[{j + 1}:v]format=rgba,fade=t=in:st={o['at']}:d=0.25:alpha=1[t{j}];"
                         f"[{last}][t{j}]overlay=0:0:shortest=1[o{j}]")
            last = f"o{j}"
        graph.append(f"[{last}]format=yuv420p[v]")
        run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(graph), "-map", "[v]",
             "-frames:v", str(p["frames"]), "-r", str(FPS), "-c:v", "libx264", "-crf", "12", "-preset", "fast", str(seg)])
        p["segment"] = seg

    # 6. Crossfade the shots, lay the disclaimer over everything, mux the voice
    voice = np.zeros(int((total + 0.5) * SR), dtype=np.float32)
    for p, a in zip(plans, audio):
        if a is not None:
            i = int(p["voice_start_s"] * SR)
            voice[i:i + len(a)] += a
    voice = voice[:int(total * SR)]
    sf.write(build / "voice.wav", voice, SR)
    vc = cfg["voice"]
    voice_only = out / "voice_only.wav"  # the exact track muxed below
    run(["ffmpeg", "-v", "error", "-y", "-i", str(build / "voice.wav"), "-af",
         f"highpass=f=70,loudnorm=I={vc['target_lufs']}:TP=-1.5:LRA=9,aresample=48000,"
         f"apad=whole_len={round(total * 48000)},atrim=end_sample={round(total * 48000)}",
         "-c:a", "pcm_s16le", str(voice_only)])
    inputs, graph, last, off = [], [], "0:v", 0.0
    for k, p in enumerate(plans):
        inputs += ["-i", str(p["segment"])]
        if k:
            off += plans[k - 1]["duration_s"] - XFADE
            graph.append(f"[{last}][{k}:v]xfade=transition=fade:duration={XFADE}:offset={off:.4f}[x{k}]")
            last = f"x{k}"
    n = len(plans)
    if disc_box:
        inputs += ["-loop", "1", "-framerate", str(FPS), "-i", str(disc_png)]
        graph.append(f"[{last}][{n}:v]overlay=0:0:shortest=1[d]")
        last, n = "d", n + 1
    inputs += ["-i", str(voice_only)]
    graph.append(f"[{last}]format=yuv420p[v];[{n}:a]anull[a]")
    final = out / "video.mp4"
    run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(graph), "-map", "[v]", "-map", "[a]",
         "-frames:v", str(round(total * FPS)), "-r", str(FPS), "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(final)])

    # 7. Report
    for p, s in zip(plans, shots):
        c = lib[s["clip"] if s["clip"].endswith(".mp4") else s["clip"] + ".mp4"]
        p["clip_notes"] = c.get("notes", "")
        p["open_mouth_note_during_voice"] = bool(OPEN_MOUTH.search(p["clip_notes"])) and "voice" in p
        p["segment"] = str(p["segment"])
        for o in p.get("overlays", []):
            o["png"] = str(o["png"])
    report = {"video": str(final), "voice_only": str(voice_only), "duration_s": round(total, 3), "ren_x": ren_x, "text_panel_x": list(panel),
              "voice_settings": vc, "shots": plans}
    (out / "report.json").write_text(json.dumps(report, indent=1) + "\n")
    for p in plans:
        flag = "  [open-mouth note]" if p["open_mouth_note_during_voice"] else ""
        print(f"{p['start_s']:6.2f}s  {p['clip']:<26} {'mirrored ' if p['mirror'] else ''}{p['duration_s']:.2f}s  "
              f"{p['plan']}{flag}")
        if "voice" in p:
            print(f"         voice {p['voice_start_s']:.2f}-{p['voice_end_s']:.2f}  {p['voice']}")
    print(f"text panel x {panel[0]}-{panel[1]}; total {total:.2f}s -> {final}")


if __name__ == "__main__":
    main()
