"""Build the ~60-second vertical short (1080x1920, 24 fps) from the long video's own narration lines.

  project/.tools/venv/bin/python videos/postponing_life/build_short.py [--out videos/postponing_life/renders]

Uses the same per-line voice files as the long video (voice/lines), so the short sounds identical, and
the same stills, Ren clips and house style. Layout follows project/config.vertical.json: nothing below
y=1500 (YouTube's controls), the right 130px kept clear, the disclaimer at y=150. Story stills are shown
whole across the middle of the frame over a blurred fill; tall subjects (the phone, the selfie) fill
the frame; Ren presents from the office with text above him.
Writes renders/postponing_life_short.mp4, renders/postponing_life_short_voice.wav and a report.
"""
import argparse
import json
import shutil
import subprocess
from pathlib import Path

import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFilter

import build_pilot as bp
import build_video as bv
from build_pilot import GREEN, LINE, MUTED, NAVY, STILLS, VOICE, WHITE, ease, fade, font, lerp, text_card

W, H, FPS, XF = 1080, 1920, 24, 0.25
LEAD, GAP, BEAT, TAIL = 0.4, 0.42, 0.6, 1.2
SAFE_BOTTOM, RIGHT_CLEAR, DISC_Y = 1500, 130, 150
REN_SCALE, FEET_Y = 1.15, 1470
EDU, EXAMPLE = "Educational only, not financial advice", "Example only, not financial advice"
LINES = ["S1_01", "S1_02", "S1_04", "S1_05", "S1_06", "S3_10", "S3_11", "S6_01", "S6_02", "S6_03", "S6_04",
         "S6_05", "S7_05", "S8_02", "S11_02", "S11_04", "S12_06", "S12_07", "S12_08", "S12_09"]


def timeline():
    tm = json.loads((VOICE / "timings.json").read_text())
    words = json.loads((VOICE / "word_times.json").read_text())
    text = {f"{s}_{l['line']:02d}": l["text"] for s, v in tm.items() for l in v["lines"]}
    L, t, prev = {}, LEAD, None
    for ln in LINES:
        if prev:  # a normal pause inside a passage, a slightly longer beat where the short skips ahead
            same = prev.split("_")[0] == ln.split("_")[0] and int(ln.split("_")[1]) == int(prev.split("_")[1]) + 1
            t += GAP if same else BEAT
        d = sf.info(VOICE / "lines" / f"{ln}.wav").duration
        L[ln] = {"start": t, "end": t + d, "text": text[ln]}
        t += d
        prev = ln
    end = t + TAIL

    def word(line, w):
        for x in words[line]:
            if x["word"].lower().strip(",.?!“”\"").startswith(w):
                return L[line]["start"] + x["start"]
        raise KeyError(f"{w!r} not in {line}")

    return L, end, word


def cover(img, cx, cy, zoom, size):
    """Crop `img` around (cx, cy) to the aspect of `size` at `zoom` (1 = as large as fits) and resize."""
    tw, th = size
    iw, ih = img.size
    ch = min(ih, iw * th / tw) / zoom
    cw = ch * tw / th
    x0 = min(max(cx - cw / 2, 0), iw - cw)
    y0 = min(max(cy - ch / 2, 0), ih - ch)
    return img.resize(size, Image.LANCZOS, box=(x0, y0, x0 + cw, y0 + ch))


def fit_frame(img, cx, cy, zoom, top=300):
    """A 16:9 view of a still across the frame, over a soft blurred fill of the same picture."""
    view = cover(img, cx, cy, zoom, (W, round(W * 9 / 16)))
    bg = view.resize((W // 8, H // 8)).filter(ImageFilter.GaussianBlur(6)).resize((W, H), Image.BICUBIC)
    bg = Image.blend(bg, Image.new("RGB", (W, H), "#F6F1E8"), 0.45).convert("RGBA")
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rectangle((0, top + 10, W, top + view.height + 18), fill=(19, 35, 63, 50))
    bg.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(12)))
    bg.paste(view, (0, top))
    return bg


_OFFICE = None


def office():
    global _OFFICE
    if _OFFICE is None:
        img = Image.open(STILLS / "office.png").convert("RGB")
        _OFFICE = cover(img, 900, 470, 1.0, (W, H)).filter(ImageFilter.GaussianBlur(5)).convert("RGBA")
    return _OFFICE


def disclaimer(f, text, alpha):
    if alpha <= 0:
        return None
    return text_card(f, [(text, 30, 500, MUTED)], W // 2 - 300, DISC_Y - 40, pad=18, alpha=alpha)


def build(out):
    L, END, word = timeline()
    lib = bp.rs.load_library()
    fridge, pbox = bp.fridge_still()
    px, py = (pbox[0] + pbox[2]) / 2, (pbox[1] + pbox[3]) / 2
    fridge_rgba = fridge.convert("RGBA")
    selfie = bp.cutout_photo(STILLS / "C_weekend_selfie.png", bg=(250, 240, 225))
    both = fridge_rgba.copy()
    bp.pin_photo(both, selfie, (1085, 385), 330, 3)
    both = both.convert("RGB")
    laptop = bp.laptop_still(760)
    phone = bv.warp_onto(Image.open(STILLS / "F_phone_in_hand.png").convert("RGB"), bv.phone_message(), bv.PHONE, 1.0)
    selfie_still = Image.open(STILLS / "C_weekend_selfie.png").convert("RGB")
    S = lambda ln: L[ln]["start"]  # noqa: E731
    ren = {}

    def card(f, lines, y, at, x=None, until=None, t=0.0):
        al = fade(t, at - 0.1) * ((1 - fade(t, until, 0.3)) if until else 1)
        if al <= 0:
            return None
        layer = Image.new("RGBA", f.size, (0, 0, 0, 0))
        box = text_card(layer, lines, 0, y, alpha=1)  # measure, then centre in the safe width
        bw = box[2] - box[0]
        bx = x if x is not None else max(40, (W - RIGHT_CLEAR - bw) // 2 + 30)
        return text_card(f, lines, bx, y, alpha=al)

    def presenter(clip, cards, end_on=None):
        def fn(t, a, b, k):
            if k not in ren:
                ren[k] = bp.RenShot(lib, clip, b - a, end_on=end_on)
            r = ren[k]
            i = min(int((t - a) * FPS), len(r.frames) - 1)
            f = office().copy()
            fr = Image.fromarray(r.frames[i], "RGBA")
            fr = fr.resize((round(1280 * REN_SCALE), round(720 * REN_SCALE)), Image.LANCZOS)
            off = r.shifts[i] / 1.5 - (bp.REN_X_1280 - 640)       # the clip's x_offset for this frame
            x = round(W / 2 - (640 - off) * REN_SCALE)
            feet = r.bbox[3] / 1.5
            y = round(FEET_Y - feet * REN_SCALE)
            sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(sh).ellipse((W / 2 - 150, FEET_Y - 18, W / 2 + 150, FEET_Y + 18), fill=(60, 40, 20, 70))
            f.alpha_composite(sh.filter(ImageFilter.GaussianBlur(12)))
            f.alpha_composite(fr, (x, y))
            ren_top = y + r.bbox[1] / 1.5 * REN_SCALE
            boxes = [card(f, c["lines"], c["y"], c["at"], t=t) for c in cards]
            r.box = (x + r.bbox[0] / 1.5 * REN_SCALE, ren_top, x + r.bbox[2] / 1.5 * REN_SCALE, FEET_Y)
            return f, boxes
        fn.clip = clip
        return fn

    def fit(img, cam0, cam1, cards=(), cap=None):
        def fn(t, a, b, k):
            x = ease((t - a) / (b - a))
            src = img(t) if callable(img) else img
            f = fit_frame(src, lerp(cam0[0], cam1[0], x), lerp(cam0[1], cam1[1], x), lerp(cam0[2], cam1[2], x))
            boxes = [card(f, c["lines"], c["y"], c["at"], t=t) for c in cards]
            if cap:
                boxes.append(disclaimer(f, cap, 1.0))
            return f, boxes
        return fn

    def tall(img, cam0, cam1, cards=()):
        def fn(t, a, b, k):
            x = ease((t - a) / (b - a))
            f = cover(img, lerp(cam0[0], cam1[0], x), lerp(cam0[1], cam1[1], x), lerp(cam0[2], cam1[2], x),
                      (W, H)).convert("RGBA")
            return f, [card(f, c["lines"], c["y"], c["at"], t=t) for c in cards]
        return fn

    def alex(lines):
        return [("Alex:", 40, 600, MUTED)] + [(s, 58, 600, NAVY) for s in lines]

    def alex_s(lines):  # slightly smaller, for two stacked cards above Ren
        return [("Alex:", 34, 600, MUTED)] + [(s, 50, 600, NAVY) for s in lines]

    # --- graphics ---------------------------------------------------------------------------------
    def g_checks(t, a, b, k):
        f = Image.new("RGBA", (W, H), WHITE)
        bp.plain_text(f, "Before he spends", 90, 330, 76, 700, NAVY)
        bp.plain_text(f, "anything:", 90, 425, 76, 700, NAVY)
        d = ImageDraw.Draw(f)
        for i, (label, w) in enumerate([("Bills checked", "bills"), ("Goals checked", "goals"),
                                        ("No borrowing", "borrowing"), ("Emergency fund", "emergency")]):
            y = 640 + i * 170
            on = fade(t, word("S7_05", w), 0.25)
            d.ellipse((90, y - 50, 190, y + 50), outline=LINE, width=8, fill=WHITE)
            bv.tick_badge(f, 140, y, 50, on)
            bp.plain_text(f, label, 230, y - 38, 62, 600, NAVY if on > 0.5 else MUTED, 0.35 + 0.65 * on)
        bp.plain_text(f, "untouched", 230, 640 + 3 * 170 + 32, 62, 600, NAVY if fade(t, word("S7_05", "emergency")) > .5
                      else MUTED, 0.35 + 0.65 * fade(t, word("S7_05", "emergency"), 0.25))
        return f, [disclaimer(f, EXAMPLE, 1.0)]

    def g_book(t, a, b, k):
        f = Image.new("RGBA", (W, H), WHITE)
        bp.plain_text(f, "Alex clicks \u201cbook.\u201d", 120, 560, 70, 700, NAVY, fade(t, S("S8_02") - 0.1))
        d = ImageDraw.Draw(f)
        click = word("S8_02", "book")
        pressed, done = fade(t, click, 0.12), fade(t, click + 0.35, 0.3)
        s = 1 - 0.05 * pressed * (1 - done)
        cx, cy, bw, bh = (W - RIGHT_CLEAR) / 2 + 30, 820, 620 * s, 190 * s
        d.rounded_rectangle((cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2), 44, fill=GREEN if done > .5 else NAVY)
        label = "Booked" if done > 0.5 else "Book"
        tw = d.textlength(label, font=font(96, 700))
        d.text((cx - tw / 2, cy - 60), label, font=font(96, 700), fill=WHITE)
        kk = ease((t - (click - 1.0)) / 0.9)
        mx, my = lerp(W - 200, cx + 120, kk), lerp(1350, cy + 40, kk)
        d.polygon([(mx, my), (mx, my + 80), (mx + 20, my + 62), (mx + 38, my + 100), (mx + 52, my + 94),
                   (mx + 34, my + 56), (mx + 62, my + 54)], fill=WHITE, outline=NAVY)
        return f, []

    def f_photo_up(t, a, b, k):
        land = word("S11_02", "puts")
        p = ease((t - land) / 0.8)
        img = fridge_rgba.copy()
        if p > 0:
            ph = selfie.resize((330, round(330 * selfie.height / selfie.width)), Image.LANCZOS)
            ph = ph.rotate(3 * p, resample=Image.BICUBIC, expand=True)
            ph.putalpha(ph.getchannel("A").point(lambda v: int(v * min(1, p * 1.6))))
            cx, cy = 1085, lerp(220, 385, p)
            img.alpha_composite(ph, (int(cx - ph.width / 2), int(cy - ph.height / 2)))
        return fit_frame(img.convert("RGB"), 892, 390, 1.75), []

    def f_end(t, a, b, k):
        x = ease((t - a) / (b - a))
        f = fit_frame(both, lerp(892, 860, x), lerp(390, 430, x), lerp(1.75, 1.3, x))
        boxes = [card(f, [("What’s still sitting", 66, 700, NAVY), ("on your fridge?", 66, 700, NAVY),
                          ("Tell me in the comments.", 46, 500, MUTED)], 1000, S("S12_09"), t=t),
                 disclaimer(f, EDU, fade(t, S("S12_09")))]
        return f, boxes

    def f_open(t, a, b, k):
        x = ease((t - a) / (b - a))
        f = cover(fridge, lerp(px + 60, px, x), lerp(py + 60, py, x), lerp(1.2, 1.55, x), (W, H)).convert("RGBA")
        return f, [disclaimer(f, EDU, 1 - fade(t, b - 0.8, 0.4))]

    shots = [
        (("S1_01", "S1_02"), "tall still", "fridge with the mountain photo", f_open),
        (("S1_04",), "tall still", "the photo, close; 4 years", tall(fridge, (px, py + 90, 2.0), (px, py + 85, 2.1), [
            dict(lines=[("4 years", 130, 700, NAVY), ("and still waiting", 50, 500, MUTED)], y=1180,
                 at=S("S1_04"))])),
        (("S1_05", "S1_06"), "story still", "D_alex_laptop; Alex: tag", fit(laptop, (700, 420, 1.35), (720, 400, 1.5), [
            dict(lines=alex(["“Next year. I’ll be", "in a better position.”"]), y=1000, at=S("S1_06") - 0.1)])),
        (("S3_10", "S3_11"), "presenter", "ren_point_up", presenter("ren_point_up", [
            dict(lines=[("Every time he got closer,", 54, 600, NAVY), ("“ready” moved too.", 54, 600, NAVY)],
                 y=230, at=S("S3_10")),
            dict(lines=[("A moving summit.", 70, 700, NAVY)], y=440, at=S("S3_11"))])),
        (("S6_01", "S6_02", "S6_03"), "tall still", "F_phone_in_hand + message", tall(
            phone, (800, 420, 1.0), (790, 400, 1.12))),
        (("S6_04", "S6_05"), "presenter", "ren_idle_listen", presenter("ren_idle_listen", [
            dict(lines=alex_s(["“It’s not really the", "trip I planned.”"]), y=210, at=word("S6_04", "it")),
            dict(lines=alex_s(["“But what part am", "I waiting for?”"]), y=440, at=word("S6_05", "know") - 0.3)])),
        (("S7_05",), "infographic", "checks before spending", g_checks),
        (("S8_02",), "infographic", "the Book button", g_book),
        (("S11_02",), "story still", "fridge: the weekend photo goes up", f_photo_up),
        (("S11_04",), "tall still", "C_weekend_selfie", tall(selfie_still, (760, 430, 1.0), (760, 420, 1.1), [
            dict(lines=[("He looks happy.", 72, 700, NAVY)], y=1250, at=S("S11_04"))])),
        (("S12_06",), "presenter", "ren_nod_yes", presenter("ren_nod_yes", [
            dict(lines=[("Give “someday”", 76, 700, NAVY), ("a next step.", 76, 700, NAVY)], y=300,
                 at=S("S12_06"))], end_on=8.0)),
        (("S12_07", "S12_08"), "story still", "fridge: both photos", fit(both, (892, 390, 1.9), (892, 390, 1.6), [
            dict(lines=[("Then: a place he wanted to go.", 50, 600, MUTED)], y=1000, at=S("S12_07")),
            dict(lines=[("Now: somewhere he’s been.", 58, 700, NAVY)], y=1150, at=S("S12_08"))])),
        (("S12_09",), "story still", "fridge: both photos (final)", f_end),
    ]
    assert [l for s in shots for l in s[0]] == LINES, "every line belongs to exactly one shot"

    cuts = [0.0] + [(L[shots[k][0][-1]]["end"] + L[shots[k + 1][0][0]]["start"]) / 2 for k in range(len(shots) - 1)] + [END]
    spans = [(max(0.0, cuts[k] - XF / 2), min(END, cuts[k + 1] + XF / 2)) for k in range(len(shots))]
    build_dir = out / "build_short"
    shutil.rmtree(build_dir, ignore_errors=True)
    build_dir.mkdir(parents=True)
    segs, log = [], []
    for k, (lines, kind, asset, fn) in enumerate(shots):
        a, b = spans[k]
        seg = build_dir / f"shot{k:02d}.mp4"
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                                "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "15", "-preset", "medium",
                                "-pix_fmt", "yuv420p", str(seg)], stdin=subprocess.PIPE)
        boxes = []
        for i in range(round((b - a) * FPS)):
            f, bx = fn(a + i / FPS, a, b, k)
            boxes += [x for x in bx if x]
            enc.stdin.write(f.convert("RGB").tobytes())
        enc.stdin.close()
        enc.wait()
        segs.append(seg)
        entry = {"shot": k + 1, "start": round(a, 2), "end": round(b, 2), "type": kind, "asset": asset,
                 "lines": list(lines),
                 "text_outside_safe_area": any(x[3] > SAFE_BOTTOM or x[2] > W - RIGHT_CLEAR + 40 for x in boxes)}
        if k in ren:
            r = ren[k]
            entry.update(clip=r.clip, clip_plan=r.note, clip_notes=lib[r.clip + ".mp4"].get("notes", ""),
                         text_over_ren=any(x[3] > r.box[1] + 10 and x[1] < r.box[3] and x[2] > r.box[0] and x[0] < r.box[2]
                                           for x in boxes))
            r.frames = None
        log.append(entry)
        print(f"shot {k + 1:2d} {a:6.2f}-{b:6.2f} {kind:<12} {asset}", flush=True)

    inputs, graph, last = [], [], "0:v"
    for k, seg in enumerate(segs):
        inputs += ["-i", str(seg)]
        if k:
            graph.append(f"[{last}][{k}:v]xfade=transition=fade:duration={XF}:offset={spans[k][0]:.4f}[x{k}]")
            last = f"x{k}"
    video_only = build_dir / "video.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(graph), "-map", f"[{last}]",
                    "-c:v", "libx264", "-crf", "15", "-preset", "medium", "-pix_fmt", "yuv420p", str(video_only)],
                   check=True)

    sr = sf.info(VOICE / "lines" / f"{LINES[0]}.wav").samplerate
    track = np.zeros(int(END * sr), np.float32)
    for ln in LINES:
        a, _ = sf.read(VOICE / "lines" / f"{ln}.wav", dtype="float32")
        i = int(L[ln]["start"] * sr)
        track[i:i + len(a)] += a
    raw = build_dir / "voice_raw.wav"
    sf.write(raw, track, sr)
    gain = -16.0 - bp.lufs(raw)  # house loudness target (config voice.target_lufs)
    voice = out / "postponing_life_short_voice.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af",
                    f"volume={gain:.2f}dB,alimiter=limit=0.84:attack=5:release=50:level=false,aresample=48000",
                    "-c:a", "pcm_s16le", str(voice)], check=True)
    final = out / "postponing_life_short.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(video_only), "-i", str(voice), "-map", "0:v", "-map", "1:a",
                    "-c:v", "libx264", "-crf", "20", "-preset", "slow", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a",
                    "192k", "-shortest", "-movflags", "+faststart", str(final)], check=True)

    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
                                         "csv=p=0", str(final)]))
    probe = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries",
                                     "stream=width,height,r_frame_rate", "-of", "csv=p=0", str(final)]).decode().strip()
    report = {"video": str(final), "voice_only": str(voice), "duration_s": round(dur, 2), "format": probe,
              "narration_lufs": bp.lufs(voice), "narration_true_peak_dbtp": bp.true_peak(voice),
              "lines": LINES, "issues": [f"shot {e['shot']}: text outside the safe area" for e in log
                                         if e["text_outside_safe_area"]] +
                                        [f"shot {e['shot']}: text touches Ren" for e in log if e.get("text_over_ren")],
              "shots": log}
    (out / "postponing_life_short_report.json").write_text(json.dumps(report, indent=1, ensure_ascii=False) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k not in ("shots", "lines")}, indent=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent / "renders"))
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    build(out)


if __name__ == "__main__":
    main()
