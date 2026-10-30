"""Build the 60-second pilot (S1 + S2) of "What If You Keep Postponing the Life You're Saving For?".

  project/.tools/venv/bin/python videos/postponing_life/build_pilot.py [--out videos/postponing_life/renders]

Inputs: voice/S1.wav, voice/S2.wav, voice/timings.json, voice/word_times.json, stills/, and Ren's
approved clips (assets/ren_library, ren_library.json). Output: 1920x1080, 24 fps, H.264 + AAC:
renders/pilot_S1-S2.mp4, renders/pilot_S1-S2_voice.wav and renders/pilot_report.json.

Every shot is a function of global time. Cuts sit midway through the pause between two lines, with a
0.25s dissolve. Ren's clips only have their plain background removed, then are scaled 1.5x and placed in front
of the approved office still; his frames are never redrawn. All text, ticks and screen contents
are drawn here in code (Fredoka, navy on white).
"""
import argparse
import json
import math
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "project" / "cliplib"))
import render_shots as rs  # noqa: E402  (clip library, neutral-frame cuts, background key)

W, H, FPS = 1920, 1080, 24
XF = 0.25                       # dissolve length at each cut
LEAD, SECTION_GAP, TAIL = 0.4, 0.8, 1.0
REN_X_1280 = 347                # Ren's centre in the 1280-wide clip space (x 520 at 1080p)
NAVY, WHITE, MUTED, LINE, GREEN = "#13233F", "#FFFFFF", "#7A8496", "#E3E7EE", "#1E9E5A"
FONTS = ROOT / "project" / "remotion" / "public" / "fonts"
STILLS = HERE / "stills"
VOICE = HERE / "voice"
OPEN_MOUTH = rs.OPEN_MOUTH


def font(px, weight=600):
    return ImageFont.truetype(str(FONTS / f"fredoka-latin-{weight}-normal.woff2"), px)


def ease(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def fade(t, start, dur=0.3):
    return ease((t - start) / dur)


# ---------------------------------------------------------------------------------------------
# Timeline from the narration


def timeline():
    tm = json.loads((VOICE / "timings.json").read_text())
    words = json.loads((VOICE / "word_times.json").read_text())
    offs = {"S1": LEAD, "S2": LEAD + tm["S1"]["duration"] + SECTION_GAP}
    lines = {f"{s}_{l['line']:02d}": {"start": offs[s] + l["start"], "end": offs[s] + l["end"], "text": l["text"]}
             for s in ("S1", "S2") for l in tm[s]["lines"]}
    end = offs["S2"] + tm["S2"]["duration"] + TAIL

    def word(line, w):  # global start time of the first word in `line` beginning with `w`
        for x in words[line]:
            if x["word"].lower().strip(",.?!").startswith(w):
                return lines[line]["start"] + x["start"]
        raise KeyError(f"{w} not in {line}")

    def cut(a, b):  # midway through the pause between line a and line b
        return (lines[a]["end"] + lines[b]["start"]) / 2

    return offs, lines, end, word, cut


# ---------------------------------------------------------------------------------------------
# Stills: fridge composite, laptop screen, camera moves


def cutout_photo(path, bg=(247, 238, 222)):
    """The printed photo (border and tape) from a still on a plain cream background, as RGBA."""
    im = Image.open(path).convert("RGB")
    a = np.asarray(im).astype(int)
    m = np.abs(a - np.array(bg)).sum(2) > 30
    ys, xs = np.where(m)
    box = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
    crop = im.crop(box).convert("RGBA")
    alpha = Image.fromarray((m[box[1]:box[3], box[0]:box[2]] * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(5))
    crop.putalpha(alpha.filter(ImageFilter.GaussianBlur(1)))
    return crop


def pin_photo(base, photo, centre, width, angle):
    """Place a photo on the fridge with a soft shadow, slightly rotated."""
    h = round(photo.height * width / photo.width)
    p = photo.resize((width, h), Image.LANCZOS).rotate(angle, resample=Image.BICUBIC, expand=True)
    shadow = Image.new("RGBA", p.size, (0, 0, 0, 0))
    shadow.putalpha(p.getchannel("A").point(lambda v: v * 0.35))
    shadow = shadow.filter(ImageFilter.GaussianBlur(8))
    x, y = centre[0] - p.width // 2, centre[1] - p.height // 2
    base.alpha_composite(shadow, (x + 6, y + 10))
    base.alpha_composite(p, (x, y))
    return (x, y, x + p.width, y + p.height)


FRIDGE_PHOTO_CENTRE, FRIDGE_PHOTO_WIDTH = (700, 372), 330


def fridge_still():
    base = Image.open(STILLS / "A_fridge.png").convert("RGBA")
    box = pin_photo(base, cutout_photo(STILLS / "B_mountain_photo.png"), FRIDGE_PHOTO_CENTRE, FRIDGE_PHOTO_WIDTH, -2)
    return base.convert("RGB"), box


SCREEN = [(966, 480), (1166, 468), (1114, 680), (907, 650)]  # D_alex_laptop: TL, TR, BR, BL


def perspective_coeffs(dst, src):
    """PIL PERSPECTIVE coefficients mapping output (dst) points to input (src) points."""
    A, b = [], []
    for (x, y), (u, v) in zip(dst, src):
        A += [[x, y, 1, 0, 0, 0, -u * x, -u * y], [0, 0, 0, x, y, 1, -v * x, -v * y]]
        b += [u, v]
    return np.linalg.solve(np.array(A, float), np.array(b, float)).tolist()


def listings_ui(scroll):
    """Code-built cabin-listing page (shapes only, no words), scrolled by `scroll` pixels."""
    w, h = 640, 460
    page = Image.new("RGB", (w, 1400), "#FBFAF6")
    d = ImageDraw.Draw(page)
    for i in range(6):
        y = 20 + i * 220
        d.rounded_rectangle((24, y, w - 24, y + 196), 18, fill=WHITE, outline=LINE, width=3)
        d.rounded_rectangle((40, y + 16, 250, y + 180), 12, fill=["#9DB59A", "#B9C9A7", "#8FAA9B"][i % 3])
        d.polygon([(80, y + 110), (145, y + 55), (210, y + 110)], fill="#B5653F")       # roof
        d.rectangle((95, y + 110, 195, y + 165), fill="#E9DCC4")                           # cabin
        d.rectangle((135, y + 130, 155, y + 165), fill="#7A5236")                          # door
        d.rounded_rectangle((276, y + 30, 560, y + 54), 10, fill=NAVY)                     # title bar
        d.rounded_rectangle((276, y + 74, 500, y + 92), 8, fill=LINE)
        d.rounded_rectangle((276, y + 104, 440, y + 122), 8, fill=LINE)
        for s in range(5):
            d.ellipse((276 + s * 30, y + 144, 298 + s * 30, y + 166), fill="#F5B82E")
    view = Image.new("RGB", (w, h), "#FBFAF6")
    view.paste(page.crop((0, int(scroll), w, int(scroll) + h - 40)), (0, 40))
    ImageDraw.Draw(view).rectangle((0, 0, w, 40), fill=NAVY)
    return view


def laptop_still(scroll):
    base = Image.open(STILLS / "D_alex_laptop.png").convert("RGB")
    ui = listings_ui(scroll)
    src = [(0, 0), (ui.width, 0), (ui.width, ui.height), (0, ui.height)]
    warped = ui.transform(base.size, Image.PERSPECTIVE, perspective_coeffs(SCREEN, src), Image.BICUBIC)
    mask = Image.new("L", base.size, 0)
    ImageDraw.Draw(mask).polygon(SCREEN, fill=255)
    base.paste(warped, (0, 0), mask.filter(ImageFilter.GaussianBlur(0.8)))
    return base


def camera(img, cx, cy, zoom):
    """Crop a still around (cx, cy) at `zoom` (1 = whole image, 16:9) and scale to 1920x1080."""
    iw, ih = img.size
    cw, ch = iw / zoom, ih / zoom
    x0 = min(max(cx - cw / 2, 0), iw - cw)
    y0 = min(max(cy - ch / 2, 0), ih - ch)
    return img.resize((W, H), Image.LANCZOS, box=(x0, y0, x0 + cw, y0 + ch))


def lerp(a, b, x):
    return a + (b - a) * x


# ---------------------------------------------------------------------------------------------
# Text


def text_card(frame, lines, x, y, anchor="la", pad=34, alpha=1.0, max_w=None):
    """White rounded card with navy text. `lines` = [(text, px, weight, colour)]. Returns its box."""
    if alpha <= 0:
        return None
    layer = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    sizes = [d.textbbox((0, 0), t, font=font(px, wt)) for t, px, wt, _ in lines]
    tw = max(b[2] - b[0] for b in sizes)
    th = sum(round(px * 1.25) for _, px, _, _ in lines)
    bw, bh = tw + 2 * pad, th + 2 * pad - round(lines[-1][1] * 0.2)
    bx = x - bw if anchor[0] == "r" else x
    by = y - bh if anchor[1] == "b" else y
    d.rounded_rectangle((bx + 4, by + 8, bx + bw + 4, by + bh + 8), 26, fill=(19, 35, 63, 40))
    d.rounded_rectangle((bx, by, bx + bw, by + bh), 26, fill=WHITE)
    ty = by + pad - 6
    for t, px, wt, col in lines:
        d.text((bx + pad, ty), t, font=font(px, wt), fill=col)
        ty += round(px * 1.25)
    if alpha < 1:
        layer.putalpha(layer.getchannel("A").point(lambda v: int(v * alpha)))
    frame.alpha_composite(layer)
    return (bx, by, bx + bw, by + bh)


def plain_text(frame, text, x, y, px, weight=600, colour=NAVY, alpha=1.0):
    if alpha <= 0:
        return None
    layer = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.text((x, y), text, font=font(px, weight), fill=colour)
    box = d.textbbox((x, y), text, font=font(px, weight))
    if alpha < 1:
        layer.putalpha(layer.getchannel("A").point(lambda v: int(v * alpha)))
    frame.alpha_composite(layer)
    return box


# ---------------------------------------------------------------------------------------------
# Ren


class RenShot:
    """Frames of one approved Ren clip, planned with the library's neutral-frame rules."""

    def __init__(self, lib, clip, seconds, mirror=False, end_on=None):
        self.clip, self.mirror = clip, mirror
        shot = {"clip": clip, "duration": seconds, "mirror": mirror}
        if end_on is not None:  # start partway in so the shot ends on the neutral frame at `end_on` seconds
            c = lib[clip + ".mp4"]
            shot["skip_s"] = max(0.0, end_on - c["in_s"] - seconds)
        pieces, n, note = rs.plan_shot(lib, shot)
        if shot.get("skip_s"):
            note = f"starts {shot['skip_s']:.2f}s into the window (dissolve covers it); " + note
        want = math.ceil(seconds * FPS)
        if n < want:
            rs.hold_idle(lib, pieces, want - n)
            note += f"; held {(want - n) / FPS:.2f}s on ren_idle_calm"
        elif n > want:
            note += f"; ends {(n - want) / FPS:.2f}s before its neutral frame (dissolve covers it)"
        self.note, self.pieces = note, pieces
        # Ren's frames, unshifted; his background is removed below
        inputs, graph, shifts = [], [], []
        for i, (entry, start, cnt, mir) in enumerate(pieces):
            inputs += ["-i", str(rs.LIB / entry["file"])]
            graph.append(f"[{i}:v]trim=start_frame={start}:end_frame={start + cnt},setpts=PTS-STARTPTS,"
                         f"format=rgb24{',hflip' if mir else ''}[s{i}]")
            off = -entry["x_offset_px"] if mir else entry["x_offset_px"]
            shifts += [round(((REN_X_1280 - 640) + off) * 1.5)] * cnt
        graph.append("".join(f"[s{i}]" for i in range(len(pieces))) + f"concat=n={len(pieces)}:v=1:a=0[v]")
        raw = subprocess.check_output(["ffmpeg", "-v", "error", *inputs, "-filter_complex", ";".join(graph),
                                       "-map", "[v]", "-frames:v", str(want), "-f", "rawvideo", "-pix_fmt", "rgb24",
                                       "-"])
        rgb = np.frombuffer(raw, np.uint8).reshape(-1, 720, 1280, 3)
        self.frames = np.stack([cut_out(f) for f in rgb])
        self.shifts = (shifts + shifts[-1:] * want)[:len(self.frames)]
        solid = (self.frames[::4, ..., 3] > 128).any(0)
        cols, rows = np.where(solid.any(0))[0], np.where(solid.any(1))[0]
        self.bbox = (int(cols.min() * 1.5 + min(self.shifts)), int(rows.min() * 1.5),
                     int(cols.max() * 1.5 + max(self.shifts)), int(rows.max() * 1.5))
        feet = np.where(solid[int(rows.max()) - 40:int(rows.max())].any(0))[0]
        self.feet_x = int((feet.min() + feet.max()) / 2 * 1.5 + np.median(self.shifts))
        self.used = [{"file": p[0]["file"], "from_s": round(p[1] / FPS, 2), "len_s": round(p[2] / FPS, 2),
                      "mirror": p[3]} for p in pieces]

    def frame(self, local_t):
        i = min(int(local_t * FPS), len(self.frames) - 1)
        f = office_backdrop().copy()
        ren = Image.fromarray(self.frames[i], "RGBA").resize((W, H), Image.LANCZOS)
        f.alpha_composite(contact_shadow(self.feet_x, self.bbox[3]))
        f.alpha_composite(ren, (self.shifts[i], 0))
        return f


def cut_out(rgb):
    """RGBA Ren from one clip frame: near-white connected to the frame's edge, plus enclosed pure-white
    pockets, is background, so his pale T-shirt (enclosed by the jacket, and greyer) stays solid. Edges are softened by a pixel and the white mixed
    into them is removed, so no light fringe shows against the office."""
    from scipy import ndimage
    lo, hi = rgb.min(2).astype(int), rgb.max(2).astype(int)
    near = (lo > 215) & (hi - lo < 25)
    lab, _ = ndimage.label(near)
    edge = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    bg = np.isin(lab, edge[edge > 0])
    # Background pockets enclosed by an arm (e.g. waving) are near-pure white (~250); the shirt is ~225-238
    pure = (lo > 243) & (hi - lo < 12) & ~bg
    plab, n = ndimage.label(pure)
    if n:
        sizes = ndimage.sum(pure, plab, range(1, n + 1))
        bg |= np.isin(plab, np.where(sizes > 150)[0] + 1)
    a = ndimage.gaussian_filter((~bg).astype(np.float32), 0.7)[..., None]
    c = rgb.astype(np.float32)
    c = np.where(a > 0.02, (c - (1 - a) * 255.0) / np.maximum(a, 0.02), 0)
    return np.concatenate([np.clip(c, 0, 255), a * 255], 2).astype(np.uint8)


_OFFICE = None


def office_backdrop():
    """The approved office still, filling 1920x1080, softly blurred so Ren and the text stand out."""
    global _OFFICE
    if _OFFICE is None:
        img = Image.open(STILLS / "office.png").convert("RGB")
        _OFFICE = camera(img, img.width / 2, img.height / 2, 1.0).filter(ImageFilter.GaussianBlur(4)).convert("RGBA")
    return _OFFICE


def contact_shadow(cx, floor_y):
    """A faint soft shadow under Ren's feet so he stands on the office floor."""
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse((cx - 190, floor_y - 22, cx + 190, floor_y + 22), fill=(60, 40, 20, 70))
    return sh.filter(ImageFilter.GaussianBlur(14))


# ---------------------------------------------------------------------------------------------


def build(out):
    offs, L, END, word, cut = timeline()
    lib = rs.load_library()
    fridge, photo_box = fridge_still()
    car = Image.open(STILLS / "E_car.png").convert("RGB")
    laptop_cache = {}
    cuts = [0.0, cut("S1_02", "S1_03"), cut("S1_03", "S1_04"), cut("S1_04", "S1_05"), cut("S1_06", "S1_07"),
            cut("S1_09", "S1_10"), (L["S1_10"]["end"] + L["S2_01"]["start"]) / 2, cut("S2_01", "S2_02"),
            cut("S2_02", "S2_03"), cut("S2_04", "S2_05"), END]
    spans = [(max(0.0, cuts[k] - XF / 2), min(END, cuts[k + 1] + XF / 2)) for k in range(len(cuts) - 1)]
    ren = {}
    log = []  # (start, end, kind, asset, detail) for the report
    px, py = (photo_box[0] + photo_box[2]) / 2, (photo_box[1] + photo_box[3]) / 2
    text_boxes = {}

    def laptop(scroll):
        key = round(scroll / 4) * 4
        if key not in laptop_cache:
            laptop_cache.clear()
            laptop_cache[key] = laptop_still(key)
        return laptop_cache[key]

    def ren_shot(k, clip, end_on=None):
        a, b = spans[k]
        if k not in ren:
            ren[k] = RenShot(lib, clip, b - a, end_on=end_on)
        return ren[k]

    def panel_x(r):
        return max(r.bbox[2] + 90, 980)

    # One function per shot: global time -> RGBA frame (and text boxes, for the overlap check)
    def s0(t):  # fridge, push in to the photo; opening disclaimer
        a, b = spans[0]
        x = ease((t - a) / (b - a))
        f = camera(fridge, lerp(836, px, x), lerp(470, py, x), lerp(1.0, 1.7, x)).convert("RGBA")
        box = text_card(f, [("Educational only, not financial advice", 30, 500, MUTED)], W - 60, H - 50, "rb",
                        pad=22, alpha=1 - fade(t, 2.8, 0.4))
        return f, [box]

    def s1(t):  # Alex researching cabins: listings scroll on the laptop
        a, b = spans[1]
        x = ease((t - a) / (b - a))
        return camera(laptop(lerp(0, 760, x)), lerp(836, 860, x), lerp(470, 440, x), lerp(1.0, 1.22, x)).convert("RGBA"), []

    def s2(t):  # the photo, close: "4 years"
        a, b = spans[2]
        x = (t - a) / (b - a)
        f = camera(fridge, px + 150, py + 10, lerp(2.0, 2.15, x)).convert("RGBA")
        box = text_card(f, [("4 years", 120, 700, NAVY), ("and still waiting", 44, 500, MUTED)], 1290, 330,
                        alpha=fade(t, L["S1_04"]["start"] - 0.1))
        return f, [box]

    def s3(t):  # Alex, closer; his line on a card with the speaker tag
        a, b = spans[3]
        x = ease((t - a) / (b - a))
        f = camera(laptop(760), lerp(760, 780, x), lerp(380, 360, x), lerp(1.45, 1.6, x)).convert("RGBA")
        q0, q1 = L["S1_06"]["start"], L["S1_06"]["end"]
        al = fade(t, q0 - 0.15, 0.25) * (1 - fade(t, q1 + 0.5, 0.3))
        box = text_card(f, [("Alex:", 40, 600, MUTED), ("“Next year. I’ll be in", 56, 600, NAVY),
                            ("a better position.”", 56, 600, NAVY)], 1190, 300, alpha=al)
        return f, [box]

    def s4(t):  # Ren thinking: some reasons are very good
        a, _ = spans[4]
        r = ren_shot(4, "ren_thinking")
        f = r.frame(t - a)
        box = text_card(f, [("Some of those reasons", 64, 600, NAVY), ("are very good.", 64, 600, NAVY)],
                        panel_x(r), 400, alpha=fade(t, L["S1_09"]["start"] - 0.1))
        return f, [box]

    def s5(t):  # Ren introduces himself: title
        a, _ = spans[5]
        r = ren_shot(5, "ren_wave_hello")
        f = r.frame(t - a)
        al = fade(t, L["S1_10"]["start"] + 1.0)
        b1 = plain_text(f, "What If You Keep", panel_x(r), 330, 84, 700, NAVY, al)
        b2 = plain_text(f, "Postponing the Life", panel_x(r), 440, 84, 700, NAVY, al)
        b3 = plain_text(f, "You’re Saving For?", panel_x(r), 550, 84, 700, NAVY, al)
        return f, [b1, b2, b3]

    def s6(t):  # the car that broke down
        a, b = spans[6]
        x = ease((t - a) / (b - a))
        return camera(car, lerp(860, 900, x), lerp(470, 500, x), lerp(1.05, 1.25, x)).convert("RGBA"), []

    def s7(t):  # Ren worried: debt, savings, optimism
        a, _ = spans[7]
        r = ren_shot(7, "ren_worried")
        f = r.frame(t - a)
        x0, boxes = panel_x(r), []
        for i, (label, w) in enumerate([("Credit card debt", "credit"), ("Very little savings", "very"),
                                        ("A vacation budget that was", "vacation")]):
            boxes.append(plain_text(f, label, x0, 300 + i * 120, 60, 600, NAVY, fade(t, word("S2_02", w) - 0.1)))
        boxes.append(plain_text(f, "mostly optimism", x0, 300 + 3 * 120 - 40, 60, 600, MUTED,
                                fade(t, word("S2_02", "optimism") - 0.1)))
        return f, boxes

    def s8(t):  # three steps, ticked on their words
        f = Image.new("RGBA", (W, H), WHITE)
        plain_text(f, "So he waited.", 160, 150, 64, 600, MUTED, fade(t, L["S2_03"]["start"] - 0.1))
        steps = [("Pay down", "the card", "card"), ("Emergency", "savings", "emergency"),
                 ("Save for", "retirement", "retirement")]
        d = ImageDraw.Draw(f)
        for i, (l1, l2, w) in enumerate(steps):
            cx, cy = 400 + i * 560, 520
            on = fade(t, word("S2_04", w), 0.25)
            if i:
                d.line((cx - 420, cy, cx - 130, cy), fill=LINE, width=10)
            d.ellipse((cx - 110, cy - 110, cx + 110, cy + 110), outline=LINE, width=10, fill=WHITE)
            if on > 0:
                r = 110 * (0.7 + 0.3 * on)
                g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                gd = ImageDraw.Draw(g)
                gd.ellipse((cx - r, cy - r, cx + r, cy + r), fill=GREEN)
                gd.line([(cx - 48, cy + 4), (cx - 12, cy + 42), (cx + 56, cy - 40)], fill=WHITE, width=22,
                        joint="curve")
                g.putalpha(g.getchannel("A").point(lambda v: int(v * on)))
                f.alpha_composite(g)
            col = NAVY if on > 0.5 else MUTED
            for j, s in enumerate((l1, l2)):
                tw = d.textlength(s, font=font(52, 600))
                d.text((cx - tw / 2, cy + 160 + j * 66), s, font=font(52, 600), fill=col)
        return f, []

    def s9(t):  # Ren nods: waiting helped
        a, _ = spans[9]
        r = ren_shot(9, "ren_nod_yes", end_on=8.0)
        f = r.frame(t - a)
        box = text_card(f, [("Waiting helped.", 84, 700, NAVY)], panel_x(r), 440,
                        alpha=fade(t, L["S2_05"]["start"] - 0.1))
        return f, [box]

    shots = [(s0, "story still", "A_fridge.png + B_mountain_photo.png (composited)", "S1_01–02"),
             (s1, "story still", "D_alex_laptop.png + code-built listings on screen", "S1_03"),
             (s2, "detail crop", "A_fridge.png + B_mountain_photo.png, close", "S1_04"),
             (s3, "story still", "D_alex_laptop.png, closer; Alex: tag", "S1_05–06"),
             (s4, "presenter", "ren_thinking", "S1_07–09"),
             (s5, "presenter", "ren_wave_hello", "S1_10"),
             (s6, "story still", "E_car.png", "S2_01"),
             (s7, "presenter", "ren_worried", "S2_02"),
             (s8, "infographic", "code-built three steps", "S2_03–04"),
             (s9, "presenter", "ren_nod_yes", "S2_05")]

    build_dir = out / "build"
    shutil.rmtree(build_dir, ignore_errors=True)
    build_dir.mkdir(parents=True)
    segs = []
    for k, (fn, kind, asset, beats) in enumerate(shots):
        a, b = spans[k]
        n = round((b - a) * FPS)
        seg = build_dir / f"shot{k:02d}.mp4"
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                                "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "14",
                                "-preset", "medium", "-pix_fmt", "yuv420p", str(seg)], stdin=subprocess.PIPE)
        boxes = []
        for i in range(n):
            t = a + i / FPS
            f, bx = fn(t)
            boxes += [x for x in bx if x]
            enc.stdin.write(f.convert("RGB").tobytes())
        enc.stdin.close()
        enc.wait()
        segs.append(seg)
        entry = {"shot": k + 1, "start": round(a, 2), "end": round(b, 2), "type": kind, "asset": asset,
                 "lines": beats}
        if k in ren:
            r = ren[k]
            entry.update(clip_plan=r.note, pieces=r.used, ren_bbox=r.bbox,
                         clip_notes=lib[r.clip + ".mp4"].get("notes", ""))
            overlap = [x for x in boxes if not (x[0] >= r.bbox[2] + 20 or x[2] <= r.bbox[0] - 20)]
            entry["text_over_ren"] = bool(overlap)
        log.append(entry)
        print(f"shot {k + 1:2d} {a:6.2f}-{b:6.2f}  {kind:<12} {asset}", flush=True)

    # Dissolve the shots together
    inputs, graph, last = [], [], "0:v"
    for k, seg in enumerate(segs):
        inputs += ["-i", str(seg)]
        if k:
            graph.append(f"[{last}][{k}:v]xfade=transition=fade:duration={XF}:offset={spans[k][0]:.4f}[x{k}]")
            last = f"x{k}"
    video_only = build_dir / "video.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(graph) or "null",
                    "-map", f"[{last}]" if graph else "0:v", "-frames:v", str(round(END * FPS)), "-c:v", "libx264",
                    "-crf", "16", "-preset", "medium", "-pix_fmt", "yuv420p", str(video_only)], check=True)

    # Narration: S1 and S2 on the timeline, normalised to -16 LUFS with a -1.5 dBTP ceiling
    sr = sf.info(VOICE / "S1.wav").samplerate
    track = np.zeros(int(END * sr), np.float32)
    for s in ("S1", "S2"):
        a, _ = sf.read(VOICE / f"{s}.wav", dtype="float32")
        i = int(offs[s] * sr)
        track[i:i + len(a)] += a
    raw = build_dir / "voice_raw.wav"
    sf.write(raw, track, sr)
    gain = -16.0 - lufs(raw)
    voice = out / "pilot_S1-S2_voice.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af",
                    f"volume={gain:.2f}dB,alimiter=limit=0.84:attack=5:release=50:level=false,aresample=48000",
                    "-c:a", "pcm_s16le", str(voice)], check=True)
    final = out / "pilot_S1-S2.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(video_only), "-i", str(voice), "-map", "0:v",
                    "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags",
                    "+faststart", str(final)], check=True)
    return final, voice, log, L, END


def lufs(path):
    out = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af", "ebur128=peak=true",
                          "-f", "null", "-"], capture_output=True, text=True).stderr
    vals = [l.split("I:")[1].split("LUFS")[0] for l in out.splitlines() if l.strip().startswith("I:")]
    return float(vals[-1])


def true_peak(path):
    out = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af", "ebur128=peak=true",
                          "-f", "null", "-"], capture_output=True, text=True).stderr
    vals = [l.split("Peak:")[1].split("dBFS")[0] for l in out.splitlines() if "Peak:" in l]
    return float(vals[-1])


def validate(final, voice, log, L, END, out):
    """Checks the pilot against the brief and writes pilot_report.json."""
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                         "-of", "csv=p=0", str(final)]))
    probe = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries",
                                     "stream=width,height,r_frame_rate", "-of", "csv=p=0", str(final)]).decode().strip()
    clips = [e["asset"] for e in log if e["type"] == "presenter"]
    repeats = sorted({c for c in clips if clips.count(c) > 1})
    longest = max(e["end"] - e["start"] for e in log)
    issues = []
    if probe != "1920,1080,24/1":
        issues.append(f"format is {probe}")
    if any(e.get("text_over_ren") for e in log):
        issues.append("text touches Ren")
    if longest > 7.25:
        issues.append(f"a shot holds {longest:.1f}s (limit 7s)")
    for e in log:
        if e.get("clip_notes") and OPEN_MOUTH.search(e["clip_notes"]):
            e["open_mouth_note_during_voice"] = True
    report = {"video": str(final), "voice_only": str(voice), "duration_s": round(dur, 2), "format": probe,
              "narration_lufs": lufs(voice), "narration_true_peak_dbtp": true_peak(voice),
              "final_mix_lufs": lufs(final), "longest_shot_s": round(longest, 2), "repeated_ren_clips": repeats,
              "issues": issues, "shots": log}
    (out / "pilot_report.json").write_text(json.dumps(report, indent=1, ensure_ascii=False) + "\n")
    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(HERE / "renders"))
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    final, voice, log, L, END = build(out)
    rep = validate(final, voice, log, L, END, out)
    print(json.dumps({k: v for k, v in rep.items() if k != "shots"}, indent=1))


if __name__ == "__main__":
    main()
