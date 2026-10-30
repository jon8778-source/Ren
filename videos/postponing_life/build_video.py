"""Build the full video (S1-S12) of "What If You Keep Postponing the Life You're Saving For?".

  project/.tools/venv/bin/python videos/postponing_life/build_video.py [--out videos/postponing_life/renders]

Same inputs and house style as build_pilot.py (whose helpers it reuses, so S1 and S2 match the approved
pilot), plus voice/S3.wav ... S12.wav and every still in stills/. Output: renders/postponing_life.mp4,
renders/postponing_life_voice.wav and renders/postponing_life_report.json.

Each shot covers whole narration lines; cuts sit midway through the pause after its last line, with a
0.25s dissolve. Ren presents from the approved office still; story stills get slow camera moves; every
graphic, label, tick and screen is drawn here in code. No dollar figures appear in the budget, and the
"Example only, not financial advice" caption shows whenever the budget or plan is on screen.
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
from build_pilot import (FPS, H, LINE, MUTED, NAVY, STILLS, VOICE, W, WHITE, XF, GREEN, camera, ease, fade, font,
                         lerp, plain_text, text_card)

LEAD, SECTION_GAP, TAIL = bp.LEAD, bp.SECTION_GAP, 1.2
SECTIONS = [f"S{i}" for i in range(1, 13)]
RED, GOLD = "#E23D3D", "#F5B82E"
EXAMPLE = "Example only, not financial advice"
EDU = "Educational only, not financial advice"
PHONE = [(638, 150), (889, 133), (956, 688), (691, 714)]   # F_phone_in_hand screen below the notch


# ---------------------------------------------------------------------------------------------
# Timeline


def timeline():
    tm = json.loads((VOICE / "timings.json").read_text())
    words = json.loads((VOICE / "word_times.json").read_text())
    offs, t = {}, LEAD
    for s in SECTIONS:
        offs[s] = t
        t += tm[s]["duration"] + SECTION_GAP
    end = t - SECTION_GAP + TAIL
    L = {f"{s}_{l['line']:02d}": {"start": offs[s] + l["start"], "end": offs[s] + l["end"], "text": l["text"]}
         for s in SECTIONS for l in tm[s]["lines"]}

    def word(line, w):
        for x in words[line]:
            if x["word"].lower().strip(",.?!“”\"").startswith(w):
                return L[line]["start"] + x["start"]
        raise KeyError(f"{w!r} not in {line}: {[x['word'] for x in words[line]]}")

    return tm, offs, L, end, word


# ---------------------------------------------------------------------------------------------
# Screens and stills


def screen_ui(kind, progress=0.0):
    """Code-built laptop screens with shapes only: 'accounts' (savings rising) or 'sheet' (a budget grid)."""
    w, h = 640, 460
    im = Image.new("RGB", (w, h), "#FBFAF6")
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w, 40), fill=NAVY)
    if kind == "accounts":
        d.rounded_rectangle((30, 70, w - 30, h - 30), 18, fill=WHITE, outline=LINE, width=3)
        pts = [(70 + i * 50, 380 - 26 * i - 14 * np.sin(i)) for i in range(11)]
        n = max(2, int(2 + progress * 9))
        d.line(pts[:n], fill=GREEN, width=8, joint="curve")
        d.line((70, 120, 570, 120), fill=LINE, width=4)
        fx, fy = pts[min(n - 1, 8)]
        d.line((fx, fy, fx, fy - 70), fill=NAVY, width=5)
        d.polygon([(fx, fy - 70), (fx + 46, fy - 56), (fx, fy - 42)], fill=GOLD)
    else:
        for r in range(7):
            y = 60 + r * 54
            d.rectangle((24, y, w - 24, y + 48), fill=WHITE if r else "#DCE3EC", outline=LINE, width=2)
            if r:
                d.rounded_rectangle((36, y + 14, 60, y + 34), 6, fill=[GREEN, GOLD, NAVY, RED, MUTED, GREEN][r - 1])
                d.rounded_rectangle((76, y + 18, 76 + 90 + (r * 37) % 120, y + 30), 6, fill=LINE)
                d.rounded_rectangle((440, y + 18, 440 + 60 + (r * 23) % 70, y + 30), 6, fill=LINE)
    return im


def warp_onto(base, ui, quad, feather=0.8):
    src = [(0, 0), (ui.width, 0), (ui.width, ui.height), (0, ui.height)]
    warped = ui.transform(base.size, Image.PERSPECTIVE, bp.perspective_coeffs(quad, src), Image.BICUBIC)
    mask = Image.new("L", base.size, 0)
    ImageDraw.Draw(mask).polygon(quad, fill=255)
    out = base.copy()
    out.paste(warped, (0, 0), mask.filter(ImageFilter.GaussianBlur(feather)))
    return out


def phone_message():
    """The friend's message on Alex's phone: a trail photo and one line of text, drawn in code."""
    w, h = 500, 1100
    im = Image.new("RGB", (w, h), "#F4F1EA")
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w, 90), fill=WHITE)
    d.ellipse((24, 22, 70, 68), fill="#9DB59A")
    d.rounded_rectangle((90, 36, 260, 54), 8, fill=LINE)
    trail = Image.open(STILLS / "H_trail.png").convert("RGB")
    ph = trail.resize((380, round(380 * trail.height / trail.width)), Image.LANCZOS)
    card = Image.new("RGB", (400, ph.height + 20), WHITE)
    card.paste(ph, (10, 10))
    im.paste(card, (30, 140))
    y = 140 + card.height + 30
    lines = ["You’d love this.", "Only a couple of", "hours away."]
    d.rounded_rectangle((30, y, 470, y + 40 + 58 * len(lines)), 30, fill=WHITE)
    for i, s in enumerate(lines):
        d.text((56, y + 22 + 58 * i), s, font=font(46, 500), fill=NAVY)
    return im


def tick_badge(f, cx, cy, r, on):
    if on <= 0:
        return
    g = Image.new("RGBA", f.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(g)
    rr = r * (0.7 + 0.3 * on)
    gd.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=GREEN)
    s = r / 110
    gd.line([(cx - 48 * s, cy + 4 * s), (cx - 12 * s, cy + 42 * s), (cx + 56 * s, cy - 40 * s)], fill=WHITE,
            width=max(6, int(22 * s)), joint="curve")
    g.putalpha(g.getchannel("A").point(lambda v: int(v * on)))
    f.alpha_composite(g)


def caption(f, text=EXAMPLE, alpha=1.0):
    return text_card(f, [(text, 30, 500, MUTED)], W - 60, H - 50, "rb", pad=22, alpha=alpha)


def cabin(d, cx, base_y, size, windows=False):
    """A simple code-drawn cabin icon: navy roof, white walls, gold windows."""
    s = size
    d.polygon([(cx - 0.62 * s, base_y - 0.55 * s), (cx, base_y - 1.05 * s), (cx + 0.62 * s, base_y - 0.55 * s)],
              fill=NAVY)
    d.rectangle((cx - 0.5 * s, base_y - 0.55 * s, cx + 0.5 * s, base_y), fill=WHITE, outline=NAVY, width=6)
    d.rectangle((cx - 0.09 * s, base_y - 0.3 * s, cx + 0.09 * s, base_y), fill=NAVY)
    if windows:
        for x0 in (-0.42, 0.14):
            d.rectangle((cx + x0 * s, base_y - 0.48 * s, cx + (x0 + 0.26) * s, base_y - 0.12 * s), fill=GOLD,
                        outline=NAVY, width=4)
    else:
        d.rectangle((cx - 0.36 * s, base_y - 0.42 * s, cx - 0.2 * s, base_y - 0.28 * s), fill=GOLD)


def icon(d, kind, cx, cy, s=90):
    """Small code-drawn icons for the list graphics."""
    if kind == "sun":
        d.ellipse((cx - s * .45, cy - s * .45, cx + s * .45, cy + s * .45), fill=GOLD)
        for a in range(0, 360, 45):
            r = np.radians(a)
            d.line((cx + np.cos(r) * s * .6, cy + np.sin(r) * s * .6, cx + np.cos(r) * s * .85,
                    cy + np.sin(r) * s * .85), fill=GOLD, width=8)
    elif kind == "cup":
        d.rounded_rectangle((cx - s * .45, cy - s * .35, cx + s * .3, cy + s * .5), 14, fill=NAVY)
        d.ellipse((cx + s * .18, cy - s * .15, cx + s * .62, cy + s * .3), outline=NAVY, width=10)
        for x in (-.2, .05):
            d.arc((cx + x * s - 12, cy - s * .85, cx + x * s + 12, cy - s * .45), 90, 270, fill=MUTED, width=6)
    elif kind == "house":
        d.polygon([(cx - s * .6, cy), (cx, cy - s * .6), (cx + s * .6, cy)], fill=NAVY)
        d.rectangle((cx - s * .45, cy, cx + s * .45, cy + s * .5), fill=WHITE, outline=NAVY, width=7)
        d.ellipse((cx + s * .2, cy - s * .2, cx + s * .7, cy + s * .3), fill=GREEN)
        d.line((cx + s * .33, cy + s * .05, cx + s * .43, cy + s * .15, cx + s * .6, cy - s * .08), fill=WHITE,
               width=6)
    elif kind == "tree":
        d.polygon([(cx, cy - s * .7), (cx - s * .45, cy + s * .1), (cx + s * .45, cy + s * .1)], fill=GREEN)
        d.polygon([(cx, cy - s * .45), (cx - s * .55, cy + s * .4), (cx + s * .55, cy + s * .4)], fill=GREEN)
        d.rectangle((cx - s * .08, cy + s * .4, cx + s * .08, cy + s * .7), fill="#7A5236")
    elif kind == "path":
        d.line([(cx - s * .6, cy + s * .5), (cx - s * .1, cy + s * .1), (cx + s * .2, cy + s * .25),
                (cx + s * .6, cy - s * .4)], fill=GREEN, width=16, joint="curve")
        d.ellipse((cx + s * .45, cy - s * .6, cx + s * .75, cy - s * .3), fill=GOLD)
    elif kind == "star":
        pts = [(cx + np.cos(np.radians(-90 + i * 36)) * (s * .6 if i % 2 == 0 else s * .26),
                cy + np.sin(np.radians(-90 + i * 36)) * (s * .6 if i % 2 == 0 else s * .26)) for i in range(10)]
        d.polygon(pts, fill=GOLD)
    elif kind == "people":
        for x in (-.28, .28):
            d.ellipse((cx + x * s - s * .2, cy - s * .55, cx + x * s + s * .2, cy - s * .15), fill=NAVY)
            d.rounded_rectangle((cx + x * s - s * .3, cy - s * .08, cx + x * s + s * .3, cy + s * .5), 20, fill=NAVY)
        d.ellipse((cx - s * .14, cy + s * .55, cx + s * .14, cy + s * .8), fill=RED)


# ---------------------------------------------------------------------------------------------


def build(out):
    tm, offs, L, END, word = timeline()
    lib = bp.rs.load_library()
    fridge, photo_box = bp.fridge_still()
    px, py = (photo_box[0] + photo_box[2]) / 2, (photo_box[1] + photo_box[3]) / 2
    selfie = bp.cutout_photo(STILLS / "C_weekend_selfie.png", bg=(250, 240, 225))
    fridge_rgba = fridge.convert("RGBA")
    both = fridge_rgba.copy()
    sbox = bp.pin_photo(both, selfie, (1085, 385), 330, 3)
    both = both.convert("RGB")
    car = Image.open(STILLS / "E_car.png").convert("RGB")
    mug = Image.open(STILLS / "G_empty_mug.png").convert("RGB")
    trail = Image.open(STILLS / "H_trail.png").convert("RGB")
    selfie_still = Image.open(STILLS / "C_weekend_selfie.png").convert("RGB")
    phone = warp_onto(Image.open(STILLS / "F_phone_in_hand.png").convert("RGB"), phone_message(), PHONE, 1.0)
    cache = {}

    def laptop(kind, x=0.0):
        key = (kind, round(x * 40))
        if key not in cache:
            if len(cache) > 6:
                cache.clear()
            if kind == "listings":
                cache[key] = bp.laptop_still(round(x * 760 / 4) * 4)
            else:
                cache[key] = warp_onto(Image.open(STILLS / "D_alex_laptop.png").convert("RGB"),
                                       screen_ui(kind, key[1] / 40), bp.SCREEN)
        return cache[key]

    def S(line):
        return L[line]["start"]

    def E(line):
        return L[line]["end"]

    # --- shot helpers ------------------------------------------------------------------------
    # Each shot is (last_line, kind, asset, fn(t, a, b) -> (frame, text boxes)); a shot runs from the
    # previous cut to the pause after its last line.
    ren = {}

    def presenter(clip, cards=(), mirror=False, end_on=None, extra=None):
        def fn(t, a, b, k):
            if k not in ren:
                ren[k] = bp.RenShot(lib, clip, b - a, mirror=mirror, end_on=end_on)
            r = ren[k]
            f = r.frame(t - a)
            x0 = max(r.bbox[2] + 90, 980)
            boxes = []
            for c in cards:
                al = fade(t, c["at"] - 0.1) * (1 - fade(t, c["until"], 0.3) if "until" in c else 1)
                if c.get("plain"):
                    boxes.append(plain_text(f, c["text"], x0, c["y"], c.get("px", 64), c.get("wt", 600),
                                            c.get("col", NAVY), al))
                else:
                    boxes.append(text_card(f, c["lines"], x0, c["y"], alpha=al))
            if extra:
                boxes += extra(f, t, x0)
            return f, boxes
        fn.clip = clip
        return fn

    def still(img, cam0, cam1, cards=(), cap=None):
        def fn(t, a, b, k):
            x = ease((t - a) / (b - a))
            src = img(t) if callable(img) else img
            f = camera(src, lerp(cam0[0], cam1[0], x), lerp(cam0[1], cam1[1], x),
                       lerp(cam0[2], cam1[2], x)).convert("RGBA")
            boxes = []
            for c in cards:
                al = fade(t, c["at"] - 0.1) * (1 - fade(t, c["until"], 0.3) if "until" in c else 1)
                boxes.append(text_card(f, c["lines"], c["x"], c["y"], anchor=c.get("anchor", "la"), alpha=al))
            if cap:
                boxes.append(caption(f, cap))
            return f, boxes
        return fn

    def alex_quote(lines):
        return [("Alex:", 40, 600, MUTED)] + [(s, 56, 600, NAVY) for s in lines]

    def white(draw, cap=None):
        def fn(t, a, b, k):
            f = Image.new("RGBA", (W, H), WHITE)
            draw(f, t)
            if cap:
                caption(f, cap)
            return f, []
        return fn

    def tick_list(title, items, at_title, cap=None):
        """A vertical list on white; each item's tick lands on its word."""
        def draw(f, t):
            plain_text(f, title, 260, 170, 68, 700, NAVY, fade(t, at_title))
            d = ImageDraw.Draw(f)
            for i, (label, when) in enumerate(items):
                y = 360 + i * 170
                on = fade(t, when, 0.25)
                d.ellipse((260, y - 55, 370, y + 55), outline=LINE, width=8, fill=WHITE)
                tick_badge(f, 315, y, 55, on)
                plain_text(f, label, 420, y - 40, 60, 600, NAVY if on > 0.5 else MUTED, 0.35 + 0.65 * on)
        return white(draw, cap)

    def icon_row(title, items, at_title):
        """Three icons with labels on white, each appearing on its word."""
        def draw(f, t):
            plain_text(f, title, 160, 150, 64, 600, MUTED, fade(t, at_title))
            for i, (kind, l1, l2, when) in enumerate(items):
                on = fade(t, when, 0.3)
                if on <= 0:
                    continue
                cx = 360 + i * 600
                g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                gd = ImageDraw.Draw(g)
                gd.ellipse((cx - 150, 330, cx + 150, 630), fill="#F4F6F9")
                icon(gd, kind, cx, 480, 150)
                for j, s in enumerate((l1, l2)):
                    if s:
                        tw = gd.textlength(s, font=font(50, 600))
                        gd.text((cx - tw / 2, 690 + j * 64), s, font=font(50, 600), fill=NAVY)
                g.putalpha(g.getchannel("A").point(lambda v: int(v * on)))
                f.alpha_composite(g)
        return white(draw)

    # --- S1 and S2: the approved pilot ------------------------------------------------------------
    def p_fridge_open(t, a, b, k):
        x = ease((t - a) / (b - a))
        f = camera(fridge, lerp(836, px, x), lerp(470, py, x), lerp(1.0, 1.7, x)).convert("RGBA")
        return f, [text_card(f, [(EDU, 30, 500, MUTED)], W - 60, H - 50, "rb", pad=22, alpha=1 - fade(t, 2.8, 0.4))]

    def p_four_years(t, a, b, k):
        x = (t - a) / (b - a)
        f = camera(fridge, px + 150, py + 10, lerp(2.0, 2.15, x)).convert("RGBA")
        return f, [text_card(f, [("4 years", 120, 700, NAVY), ("and still waiting", 44, 500, MUTED)], 1290, 330,
                             alpha=fade(t, S("S1_04") - 0.1))]

    def p_quote(t, a, b, k):
        x = ease((t - a) / (b - a))
        f = camera(laptop("listings", 1.0), lerp(760, 780, x), lerp(380, 360, x), lerp(1.45, 1.6, x)).convert("RGBA")
        al = fade(t, S("S1_06") - 0.15, 0.25) * (1 - fade(t, E("S1_06") + 0.5, 0.3))
        return f, [text_card(f, alex_quote(["“Next year. I’ll be in", "a better position.”"]), 1190, 300,
                             alpha=al)]

    def p_title(f, t, x0):
        al = fade(t, S("S1_10") + 1.0)
        return [plain_text(f, s, x0, 330 + i * 110, 84, 700, NAVY, al)
                for i, s in enumerate(["What If You Keep", "Postponing the Life", "You’re Saving For?"])]

    def p_debt(f, t, x0):
        out = [plain_text(f, s, x0, 300 + i * 120, 60, 600, NAVY, fade(t, word("S2_02", w) - 0.1))
               for i, (s, w) in enumerate([("Credit card debt", "credit"), ("Very little savings", "very"),
                                           ("A vacation budget that was", "vacation")])]
        out.append(plain_text(f, "mostly optimism", x0, 620, 60, 600, MUTED, fade(t, word("S2_02", "optimism") - 0.1)))
        return out

    def p_steps(f, t):
        plain_text(f, "So he waited.", 160, 150, 64, 600, MUTED, fade(t, S("S2_03") - 0.1))
        d = ImageDraw.Draw(f)
        for i, (l1, l2, w) in enumerate([("Pay down", "the card", "card"), ("Emergency", "savings", "emergency"),
                                         ("Save for", "retirement", "retirement")]):
            cx, cy = 400 + i * 560, 520
            on = fade(t, word("S2_04", w), 0.25)
            if i:
                d.line((cx - 420, cy, cx - 130, cy), fill=LINE, width=10)
            d.ellipse((cx - 110, cy - 110, cx + 110, cy + 110), outline=LINE, width=10, fill=WHITE)
            tick_badge(f, cx, cy, 110, on)
            for j, s in enumerate((l1, l2)):
                tw = d.textlength(s, font=font(52, 600))
                d.text((cx - tw / 2, cy + 160 + j * 66), s, font=font(52, 600), fill=NAVY if on > 0.5 else MUTED)

    # --- S3-S12 graphics ------------------------------------------------------------------------
    def g_target(f, t):
        """Savings grow, and the "ready" target keeps moving up just ahead of them."""
        d = ImageDraw.Draw(f)
        ev = [word("S3_06", "raise"), word("S3_07", "target"), word("S3_08", "neither")]
        lvl = sum(fade(t, e, 0.6) for e in ev)
        bar_h = 220 + 120 * lvl
        tgt_h = 330 + 125 * sum(fade(t, e + 0.5, 0.6) for e in ev[1:]) + 30 * fade(t, ev[0], 0.6)
        base = 900
        d.line((560, base, 1360, base), fill=LINE, width=6)
        d.rounded_rectangle((760, base - bar_h, 1000, base), 18, fill=GREEN)
        plain_text(f, "Savings", 790, base + 20, 50, 600, NAVY)
        y = base - tgt_h
        for x in range(600, 1320, 40):
            d.line((x, y, x + 22, y), fill=NAVY, width=8)
        plain_text(f, "“Ready”", 1340, y - 38, 56, 700, NAVY)
        plain_text(f, "Another year passed.", 160, 130, 64, 600, MUTED, fade(t, S("S3_06") - 0.1))

    def g_emergency(f, t):
        d = ImageDraw.Draw(f)
        on = fade(t, word("S5_03", "emergency"), 0.35)
        d.rounded_rectangle((220, 380, 820, 640), 30, fill=WHITE, outline=NAVY, width=8)
        tw = d.textlength("Planned expense", font=font(58, 700))
        d.text((520 - tw / 2, 475), "Planned expense", font=font(58, 700), fill=NAVY)
        d.line((870, 510, 1050, 510), fill=MUTED, width=10)
        d.polygon([(1050, 480), (1100, 510), (1050, 540)], fill=MUTED)
        if on > 0:
            g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            gd = ImageDraw.Draw(g)
            gd.rounded_rectangle((1150, 380, 1700, 640), 30, fill=RED)
            tw = gd.textlength("Emergency?", font=font(66, 700))
            gd.text((1425 - tw / 2, 470), "Emergency?", font=font(66, 700), fill=WHITE)
            g.putalpha(g.getchannel("A").point(lambda v: int(v * on)))
            f.alpha_composite(g)

    def g_cabin(f, t):
        d = ImageDraw.Draw(f)
        plain_text(f, "The trip itself has grown.", 160, 130, 64, 600, MUTED, fade(t, S("S5_07") - 0.1))
        cabin(d, 520, 760, 230)
        plain_text(f, "Two nights", 400, 800, 56, 600, NAVY, fade(t, S("S5_08") - 0.1))
        on = fade(t, word("S5_08", "week"), 0.4)
        win = fade(t, word("S5_08", "windows"), 0.4)
        if on > 0:
            g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            gd = ImageDraw.Draw(g)
            cabin(gd, 1300, 760, 230 + 190 * on, windows=win > 0.5)
            g.putalpha(g.getchannel("A").point(lambda v: int(v * on)))
            f.alpha_composite(g)
            plain_text(f, "A week, huge windows" if win > 0.5 else "A week", 1120, 800, 56, 700, NAVY, on)
            d.line((760, 640, 960, 640), fill=MUTED, width=8)
            d.polygon([(960, 615), (1000, 640), (960, 665)], fill=MUTED)

    def g_budget(f, t):
        d = ImageDraw.Draw(f)
        plain_text(f, "Price the whole weekend", 260, 120, 68, 700, NAVY, fade(t, S("S7_06") - 0.1))
        cats = [("Somewhere to stay", "somewhere"), ("Gas", "gas"), ("Food", "food"), ("Park fees", "park"),
                ("A little extra for whatever he forgot", "extra")]
        for i, (label, w) in enumerate(cats):
            y = 290 + i * 118
            on = fade(t, word("S7_06", w), 0.25)
            d.rounded_rectangle((260, y - 44, 1660, y + 44), 22, fill="#F4F6F9" if on > 0.5 else WHITE,
                                outline=LINE, width=4)
            tick_badge(f, 320, y, 34, on)
            plain_text(f, label, 380, y - 34, 52, 600, NAVY if on > 0.5 else MUTED, 0.3 + 0.7 * on)
        for i, (s, w) in enumerate([("Two nights nearby", "two"), ("Packed lunches", "packed"),
                                    ("No fancy cabin", "no")]):
            plain_text(f, s, 260 + i * 520, 900, 50, 600, GREEN, fade(t, word("S7_07", w) - 0.05))

    def g_book(f, t):
        d = ImageDraw.Draw(f)
        plain_text(f, "Then the hardest part.", 160, 150, 64, 600, MUTED, fade(t, S("S8_01") - 0.1))
        click = word("S8_02", "book")
        pressed = fade(t, click, 0.12)
        done = fade(t, click + 0.35, 0.3)
        s = 1 - 0.05 * pressed * (1 - done)
        cx, cy, bw, bh = 960, 560, 560 * s, 170 * s
        d.rounded_rectangle((cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2), 40, fill=GREEN if done > 0.5 else NAVY)
        label = "Booked" if done > 0.5 else "Book"
        tw = d.textlength(label, font=font(84, 700))
        d.text((cx - tw / 2, cy - 52), label, font=font(84, 700), fill=WHITE)
        k = ease((t - (click - 1.2)) / 1.1)
        mx, my = lerp(1500, cx + 120, k), lerp(900, cy + 30, k)
        d.polygon([(mx, my), (mx, my + 70), (mx + 18, my + 54), (mx + 34, my + 88), (mx + 46, my + 82),
                   (mx + 30, my + 48), (mx + 54, my + 46)], fill=WHITE, outline=NAVY)

    # --- the shot list -------------------------------------------------------------------------
    shots = [
        # S1
        ("S1_02", "story still", "A_fridge + B_mountain_photo", p_fridge_open),
        ("S1_03", "story still", "D_alex_laptop + listings", lambda t, a, b, k: (camera(
            laptop("listings", ease((t - a) / (b - a))), lerp(836, 860, ease((t - a) / (b - a))),
            lerp(470, 440, ease((t - a) / (b - a))), lerp(1.0, 1.22, ease((t - a) / (b - a)))).convert("RGBA"), [])),
        ("S1_04", "detail crop", "fridge photo close; 4 years", p_four_years),
        ("S1_06", "story still", "D_alex_laptop close; Alex: tag", p_quote),
        ("S1_09", "presenter", "ren_thinking", presenter("ren_thinking", [
            dict(lines=[("Some of those reasons", 64, 600, NAVY), ("are very good.", 64, 600, NAVY)], y=400,
                 at=S("S1_09"))])),
        ("S1_10", "presenter", "ren_wave_hello", presenter("ren_wave_hello", extra=p_title)),
        # S2
        ("S2_01", "story still", "E_car", still(car, (860, 470, 1.05), (900, 500, 1.25))),
        ("S2_02", "presenter", "ren_worried", presenter("ren_worried", extra=p_debt)),
        ("S2_04", "infographic", "three steps", white(p_steps)),
        ("S2_05", "presenter", "ren_nod_yes", presenter("ren_nod_yes", [
            dict(lines=[("Waiting helped.", 84, 700, NAVY)], y=440, at=S("S2_05"))], end_on=8.0)),
        # S3
        ("S3_02", "story still", "D_alex_laptop + accounts screen", still(
            lambda t: laptop("accounts", min(1, max(0, (t - S("S3_02")) / 2.5))), (820, 450, 1.12), (860, 440, 1.3))),
        ("S3_03", "presenter", "ren_shake_no", presenter("ren_shake_no", [
            dict(lines=[("He could afford it now.", 60, 600, NAVY)], y=330, at=S("S3_03")),
            dict(lines=[("But spending it felt", 60, 600, NAVY), ("like going backward.", 60, 600, NAVY)], y=520,
                 at=word("S3_03", "spending"))])),
        ("S3_04", "story still", "D_alex_laptop close; Alex: tag", still(
            laptop("accounts", 1.0), (760, 380, 1.5), (780, 360, 1.62),
            [dict(lines=alex_quote(["“Let me get a little more", "comfortable first.”"]), x=1150, y=300,
                  at=S("S3_04") - 0.05)])),
        ("S3_05", "story still", "fridge (anchor: still waiting)", still(fridge, (836, 470, 1.15), (px, py, 1.55))),
        ("S3_08", "infographic", "savings vs a moving target", white(g_target)),
        ("S3_10", "presenter", "ren_point_up", presenter("ren_point_up", [
            dict(lines=[("Whenever his finances improved,", 52, 600, NAVY), ("“ready” moved too.", 52, 600, NAVY)],
                 y=400, at=S("S3_10"))])),
        ("S3_11", "detail crop", "fridge photo close: a moving summit", still(
            fridge, (px + 150, py + 10, 2.0), (px + 140, py, 2.2),
            [dict(lines=[("A moving summit.", 84, 700, NAVY)], x=W - 60, y=380, anchor="ra", at=S("S3_11"))])),
        # S4
        ("S4_02", "story still", "D_alex_laptop + listings", still(
            lambda t: laptop("listings", min(1, max(0, (t - S("S4_01")) / 6))), (820, 450, 1.12), (860, 430, 1.3))),
        ("S4_03", "story still", "D_alex_laptop close; Alex: tag", still(
            laptop("listings", 1.0), (700, 380, 1.55), (720, 360, 1.7),
            [dict(lines=alex_quote(["“What would have to happen", "for me to actually", "book this?”"]),
                  x=W - 50, y=260, anchor="ra", at=word("S4_03", "what") - 0.1)])),
        ("S4_05", "presenter", "ren_count_fingers", presenter("ren_count_fingers", [
            dict(lines=[("He started listing numbers.", 60, 600, NAVY)], y=380, at=S("S4_04")),
            dict(lines=[("Then he stopped.", 60, 600, MUTED)], y=560, at=S("S4_05"))], end_on=8.17)),
        ("S4_06", "story still", "D_alex_laptop, face; Alex: tag", still(
            laptop("listings", 1.0), (620, 320, 1.9), (630, 310, 2.0),
            [dict(lines=alex_quote(["“And if I reach those numbers,", "will I feel comfortable", "spending it?”"]),
                  x=W - 50, y=240, anchor="ra", at=S("S4_06") - 0.05)])),
        ("S4_08", "presenter", "ren_shrug", presenter("ren_shrug", [
            dict(lines=[("He wasn’t sure.", 72, 700, NAVY)], y=440, at=S("S4_08"))])),
        # S5
        ("S5_02", "presenter", "ren_walk_in_left", presenter("ren_walk_in_left", [
            dict(lines=[("Alex isn’t foolish.", 64, 700, NAVY)], y=300, at=word("S5_02", "alex")),
            dict(lines=[("Money in the bank", 56, 600, NAVY), ("means options.", 56, 600, NAVY)], y=500,
                 at=word("S5_02", "money"))], end_on=7.21)),
        ("S5_03", "infographic", "planned expense → emergency?", white(g_emergency)),
        ("S5_05", "presenter", "ren_open_arms", presenter("ren_open_arms", [
            dict(lines=[("Saving for the trip", 58, 600, NAVY)], y=330, at=S("S5_04")),
            dict(lines=[("Permission to take it", 58, 600, NAVY)], y=520, at=S("S5_05"))],
            extra=lambda f, t, x0: [tick_badge(f, x0 - 50, 395, 34, fade(t, S("S5_04") + 0.8)),
                                    plain_text(f, "?", x0 - 66, 548, 80, 700, RED, fade(t, S("S5_05") + 1.2))])),
        ("S5_08", "infographic", "the cabin grows", white(g_cabin)),
        ("S5_10", "presenter", "ren_confused", presenter("ren_confused", [
            dict(lines=[("He wanted it to feel", 60, 600, NAVY), ("worth the wait.", 60, 600, NAVY)], y=330,
                 at=S("S5_09")),
            dict(lines=[("The bigger it gets,", 60, 600, NAVY), ("the harder it is to say yes.", 60, 600, NAVY)],
                 y=540, at=S("S5_10"))])),
        ("S5_11", "story still", "D_alex_laptop + listings, slow push", still(
            laptop("listings", 1.0), (836, 470, 1.05), (860, 450, 1.25),
            [dict(lines=[("Harder to say yes.", 64, 700, NAVY)], x=W - 60, y=120, anchor="ra", at=S("S5_11"))])),
        # S6
        ("S6_03", "story still", "F_phone_in_hand + friend's message", still(
            phone, (836, 470, 1.15), (820, 420, 1.45))),
        ("S6_05", "presenter", "ren_idle_listen", presenter("ren_idle_listen", [
            dict(lines=[("Alex:", 40, 600, MUTED), ("“It’s not really the", 56, 600, NAVY),
                        ("trip I planned.”", 56, 600, NAVY)], y=200, at=word("S6_04", "it")),
            dict(lines=[("Alex:", 40, 600, MUTED), ("“I know. But what part", 56, 600, NAVY),
                        ("am I waiting for?”", 56, 600, NAVY)], y=560, at=word("S6_05", "know") - 0.3)])),
        ("S6_06", "infographic", "what he actually wants", icon_row("What he actually wants", [
            ("sun", "A few days", "outside", word("S6_06", "few")),
            ("cup", "Breakfast without", "work messages", word("S6_06", "breakfast")),
            ("house", "Time off from", "fixing the house", word("S6_06", "time"))], S("S6_06") - 0.1)),
        ("S6_08", "presenter", "ren_present_palm_left (mirrored)", presenter("ren_present_palm_left", [
            dict(lines=[("Same wants,", 72, 700, NAVY), ("smaller size.", 72, 700, NAVY)], y=420, at=S("S6_08"))],
            mirror=True)),
        # S7
        ("S7_02", "story still", "D_alex_laptop + budget sheet", still(
            laptop("sheet"), (820, 450, 1.12), (860, 430, 1.3), cap=EXAMPLE)),
        ("S7_04", "presenter", "ren_rub_hands", presenter("ren_rub_hands", [
            dict(lines=[("There’s a spreadsheet.", 64, 600, NAVY)], y=360, at=S("S7_03")),
            dict(lines=[("Alex is delighted.", 64, 700, GREEN)], y=540, at=S("S7_04"))], end_on=7.88)),
        ("S7_05", "infographic", "checks before spending", tick_list("Before he spends anything", [
            ("Bills checked", word("S7_05", "bills")), ("Goals checked", word("S7_05", "goals")),
            ("No borrowing", word("S7_05", "borrowing")), ("Emergency fund untouched", word("S7_05", "emergency"))],
            S("S7_05") - 0.1, cap=EXAMPLE)),
        ("S7_07", "infographic", "weekend budget categories (no $)", white(g_budget, cap=EXAMPLE)),
        ("S7_09", "presenter", "ren_point_down_right", presenter("ren_point_down_right", [
            dict(lines=[("The trade-off: that money", 54, 600, NAVY), ("won’t be saved or invested.", 54, 600, NAVY)],
                 y=330, at=S("S7_08")),
            dict(lines=[("Worth it.", 72, 700, GREEN)], y=560, at=S("S7_09"))])),
        # S8
        ("S8_02", "infographic", "the Book button", white(g_book)),
        ("S8_04", "presenter", "ren_celebrate_fist_pump", presenter("ren_celebrate_fist_pump", [
            dict(lines=[("Excited…", 64, 700, GREEN), ("for about three seconds.", 52, 600, NAVY)], y=330,
                 at=S("S8_03")),
            dict(lines=[("Then: cancel?", 64, 700, RED)], y=580, at=S("S8_04"))])),
        ("S8_05", "story still", "D_alex_laptop + budget sheet, closer", still(
            laptop("sheet"), (760, 380, 1.5), (780, 360, 1.62), cap=EXAMPLE)),
        ("S8_06", "infographic", "the plan, checked again", tick_list("He looks at the plan again", [
            ("Bills covered", word("S8_06", "bills")), ("Savings on track", word("S8_06", "savings")),
            ("Nothing has changed", word("S8_06", "nothing"))], S("S8_05") - 0.1, cap=EXAMPLE)),
        ("S8_08", "presenter", "ren_point_camera", presenter("ren_point_camera", [
            dict(lines=[("The discomfort is real.", 60, 600, NAVY)], y=330, at=S("S8_07")),
            dict(lines=[("It isn’t evidence", 64, 700, NAVY), ("booking was a mistake.", 64, 700, NAVY)], y=520,
                 at=S("S8_08"))])),
        # S9
        ("S9_01", "presenter", "ren_point_right", presenter("ren_point_right", [
            dict(lines=[("No room in the", 64, 700, NAVY), ("budget right now?", 64, 700, NAVY)], y=420, at=S("S9_01"))])),
        ("S9_03", "presenter", "ren_open_arms", presenter("ren_open_arms", [
            dict(lines=[("You might be where", 58, 600, NAVY), ("Alex had to wait.", 58, 600, NAVY)], y=300,
                 at=S("S9_02")),
            dict(lines=[("That deserves", 64, 700, NAVY), ("respect.", 64, 700, NAVY)], y=540, at=S("S9_03"))])),
        ("S9_04", "infographic", "free things to look forward to", icon_row("Something to look forward to", [
            ("tree", "A local walk", "", word("S9_04", "local")),
            ("star", "A free event", "", word("S9_04", "free")),
            ("people", "An afternoon with", "someone you care about", word("S9_04", "afternoon"))],
            S("S9_04") - 0.1)),
        # S10
        ("S10_02", "story still", "G_empty_mug (cropped clear of the French press)", still(
            mug, (700, 470, 1.25), (720, 450, 1.4))),
        ("S10_04", "story still", "G_empty_mug, close on Alex and the mug", still(mug, (740, 420, 1.75), (735, 410, 1.9))),
        ("S10_05", "story still", "H_trail, wide", still(trail, (836, 470, 1.0), (880, 450, 1.12))),
        ("S10_06", "story still", "H_trail, closer on Alex", still(trail, (700, 520, 1.6), (720, 500, 1.75))),
        # S11
        ("S11_01", "story still", "fridge, mountain photo", still(fridge, (836, 470, 1.0), (900, 400, 1.18))),
        ("S11_02", "story still", "fridge: the weekend photo goes up (anchor)", None),
        ("S11_04", "detail crop", "C_weekend_selfie", still(selfie_still, (836, 455, 1.3), (820, 430, 1.55),
                                                            [dict(lines=[("He looks happy.", 64, 700, NAVY)], x=1320, y=880,
                                                                  anchor="lb", at=S("S11_04"))])),
        ("S11_06", "story still", "D_alex_laptop + accounts screen, a month later", still(
            laptop("accounts", 1.0), (836, 470, 1.05), (850, 450, 1.2),
            [dict(lines=[("A month later", 56, 600, MUTED)], x=W - 60, y=110, anchor="ra", at=S("S11_05")),
             dict(lines=[("Not everything is fixed.", 56, 600, NAVY)], x=W - 60, y=250, anchor="ra",
                  at=word("S11_05", "some")),
             dict(lines=[("But he stuck to the plan.", 60, 700, GREEN)], x=W - 60, y=390, anchor="ra",
                  at=S("S11_06"))])),
        ("S11_07", "presenter", "ren_thumbs_up", presenter("ren_thumbs_up", [
            dict(lines=[("Proof he can spend", 60, 700, NAVY), ("on purpose and still", 60, 700, NAVY),
                        ("be a responsible saver.", 60, 700, NAVY)], y=380, at=word("S11_07", "proof"))])),
        # S12
        ("S12_02", "presenter", "ren_point_camera", presenter("ren_point_camera", [
            dict(lines=[("My challenge:", 56, 600, MUTED)], y=330, at=S("S12_01")),
            dict(lines=[("Pick one thing you", 60, 700, NAVY), ("keep postponing.", 60, 700, NAVY)], y=470,
                 at=S("S12_02"))])),
        ("S12_04", "infographic", "challenge steps", tick_list("Your next step", [
            ("Pick one thing you keep postponing", S("S12_02") - 0.6), ("Ask what you actually want from it", S("S12_03")),
            ("Find a version that fits your life now", S("S12_04"))], S("S12_03") - 2.5)),
        ("S12_05", "presenter", "ren_count_fingers", presenter("ren_count_fingers", [
            dict(text="Book it", plain=True, y=300, px=64, at=word("S12_05", "book")),
            dict(text="Set a date and start saving", plain=True, y=420, px=64, at=word("S12_05", "set")),
            dict(text="Make the free phone call", plain=True, y=540, px=64, at=word("S12_05", "make"))])),
        ("S12_06", "presenter", "ren_nod_yes", presenter("ren_nod_yes", [
            dict(lines=[("Give “someday”", 76, 700, NAVY), ("a next step.", 76, 700, NAVY)], y=420,
                 at=S("S12_06"))], end_on=8.0)),
        ("S12_08", "story still", "fridge: both photos", still(both, (890, 390, 1.6), (880, 385, 1.4))),
        ("S12_09", "presenter", "ren_hold_phone", presenter("ren_hold_phone", [
            dict(lines=[("What’s still sitting", 64, 700, NAVY), ("on your fridge?", 64, 700, NAVY),
                        ("Tell me in the comments.", 44, 500, MUTED)], y=360, at=S("S12_09"))])),
        ("S12_10", "story still", "fridge: both photos (final shot)", None),
    ]

    def f_second_photo(t, a, b, k):
        """The weekend photo goes up beside the mountain photo."""
        x = ease((t - a) / (b - a))
        land = word("S11_02", "puts")
        p = ease((t - land) / 0.8)
        img = fridge_rgba.copy()
        if p > 0:
            ph = selfie.resize((330, round(330 * selfie.height / selfie.width)), Image.LANCZOS)
            ph = ph.rotate(3 * p, resample=Image.BICUBIC, expand=True)
            ph.putalpha(ph.getchannel("A").point(lambda v: int(v * min(1, p * 1.6))))
            cx, cy = 1085, lerp(220, 385, p)
            sh = Image.new("RGBA", ph.size, (0, 0, 0, 0))
            sh.putalpha(ph.getchannel("A").point(lambda v: int(v * 0.35 * p)))
            img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)), (int(cx - ph.width / 2 + 6), int(cy - ph.height / 2 + 10)))
            img.alpha_composite(ph, (int(cx - ph.width / 2), int(cy - ph.height / 2)))
        f = camera(img.convert("RGB"), lerp(900, 890, x), lerp(400, 390, x), lerp(1.3, 1.4, x)).convert("RGBA")
        return f, []

    def f_final(t, a, b, k):
        x = ease((t - a) / (b - a))
        f = camera(both, lerp(880, 836, x), lerp(385, 470, x), lerp(1.4, 1.0, x)).convert("RGBA")
        boxes = [text_card(f, [("Subscribe", 64, 700, NAVY), ("for more on building wealth", 40, 500, MUTED),
                               ("and making room for your life", 40, 500, MUTED)], W - 70, 930, "rb",
                           alpha=fade(t, S("S12_10") + 0.5)),
                 caption(f, EDU, fade(t, S("S12_10") + 0.5))]
        return f, boxes

    shots = [(l, kd, asset, f_second_photo if l == "S11_02" else f_final if l == "S12_10" else fn)
             for l, kd, asset, fn in shots]

    # --- cuts and render -----------------------------------------------------------------------
    order = list(L)
    cuts = [0.0]
    for last, *_ in shots[:-1]:
        nxt = order[order.index(last) + 1]
        cuts.append((L[last]["end"] + L[nxt]["start"]) / 2)
    cuts.append(END)
    spans = [(max(0.0, cuts[k] - XF / 2), min(END, cuts[k + 1] + XF / 2)) for k in range(len(shots))]
    firsts = [order[0]] + [order[order.index(s[0]) + 1] for s in shots[:-1]]

    build_dir = out / "build"
    shutil.rmtree(build_dir, ignore_errors=True)
    build_dir.mkdir(parents=True)
    segs, log = [], []
    for k, (last, kind, asset, fn) in enumerate(shots):
        a, b = spans[k]
        n = round((b - a) * FPS)
        seg = build_dir / f"shot{k:02d}.mp4"
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                                "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "15", "-preset", "medium",
                                "-pix_fmt", "yuv420p", str(seg)], stdin=subprocess.PIPE)
        boxes = []
        for i in range(n):
            f, bx = fn(a + i / FPS, a, b, k)
            boxes += [x for x in bx if x]
            enc.stdin.write(f.convert("RGB").tobytes())
        enc.stdin.close()
        enc.wait()
        segs.append(seg)
        entry = {"shot": k + 1, "start": round(a, 2), "end": round(b, 2), "type": kind, "asset": asset,
                 "lines": f"{firsts[k]}–{last}" if firsts[k] != last else last}
        if k in ren:
            r = ren[k]
            entry.update(clip=r.clip, clip_plan=r.note, pieces=r.used, ren_bbox=r.bbox,
                         clip_notes=lib[r.clip + ".mp4"].get("notes", ""),
                         text_over_ren=any(not (x[0] >= r.bbox[2] + 20 or x[2] <= r.bbox[0] - 20) for x in boxes))
            r.frames = None  # free memory before the next Ren shot
        log.append(entry)
        print(f"shot {k + 1:2d} {a:7.2f}-{b:7.2f}  {kind:<12} {asset}", flush=True)

    # Join: chained dissolves in groups, then the groups, to keep each ffmpeg graph small
    def join(parts, starts, dst):
        inputs, graph, last = [], [], "0:v"
        for k, p in enumerate(parts):
            inputs += ["-i", str(p)]
            if k:
                graph.append(f"[{last}][{k}:v]xfade=transition=fade:duration={XF}:offset={starts[k] - starts[0]:.4f}[x{k}]")
                last = f"x{k}"
        cmd = ["ffmpeg", "-v", "error", "-y", *inputs]
        cmd += (["-filter_complex", ";".join(graph), "-map", f"[{last}]"] if graph else ["-map", "0:v"])
        subprocess.run(cmd + ["-c:v", "libx264", "-crf", "15", "-preset", "medium", "-pix_fmt", "yuv420p", str(dst)],
                       check=True)

    starts = [s[0] for s in spans]
    groups, gstarts = [], []
    for g in range(0, len(segs), 10):
        part = build_dir / f"group{g // 10:02d}.mp4"
        join(segs[g:g + 10], starts[g:g + 10], part)
        groups.append(part)
        gstarts.append(starts[g])
    video_only = build_dir / "video.mp4"
    join(groups, gstarts, video_only)

    # Narration: every section on the timeline, normalised to -16 LUFS with a ceiling
    sr = sf.info(VOICE / "S1.wav").samplerate
    track = np.zeros(int(END * sr), np.float32)
    for s in SECTIONS:
        a, _ = sf.read(VOICE / f"{s}.wav", dtype="float32")
        i = int(offs[s] * sr)
        track[i:i + len(a)] += a
    raw = build_dir / "voice_raw.wav"
    sf.write(raw, track, sr)
    gain = -16.0 - bp.lufs(raw)
    voice = out / "postponing_life_voice.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af",
                    f"volume={gain:.2f}dB,alimiter=limit=0.84:attack=5:release=50:level=false,aresample=48000",
                    "-c:a", "pcm_s16le", str(voice)], check=True)
    final = out / "postponing_life.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(video_only), "-i", str(voice), "-map", "0:v", "-map",
                    "1:a", "-c:v", "libx264", "-crf", "20", "-preset", "slow", "-pix_fmt", "yuv420p", "-c:a", "aac",
                    "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(final)], check=True)
    return final, voice, log, L, END, offs


def validate(final, voice, log, L, END, offs, out):
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
                                         "csv=p=0", str(final)]))
    probe = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries",
                                     "stream=width,height,r_frame_rate", "-of", "csv=p=0", str(final)]).decode().strip()
    clips = [e["clip"] for e in log if "clip" in e]
    repeats = {c: [e["start"] for e in log if e.get("clip") == c] for c in sorted(set(clips)) if clips.count(c) > 1}
    back_to_back = [(a["clip"], a["start"]) for a, b in zip(log, log[1:]) if a.get("clip") and a.get("clip") == b.get("clip")]
    long_shots = [(e["shot"], round(e["end"] - e["start"], 1), e["asset"]) for e in log if e["end"] - e["start"] > 7.25]
    issues = []
    if probe != "1920,1080,24/1":
        issues.append(f"format is {probe}")
    if any(e.get("text_over_ren") for e in log):
        issues.append("text touches Ren: shots " + ", ".join(str(e["shot"]) for e in log if e.get("text_over_ren")))
    if back_to_back:
        issues.append(f"same Ren clip in consecutive shots: {back_to_back}")
    if long_shots:
        issues.append(f"{len(long_shots)} shot(s) over 7s")
    for e in log:
        if e.get("clip_notes") and bp.OPEN_MOUTH.search(e["clip_notes"]):
            e["open_mouth_note_during_voice"] = True
    report = {"video": str(final), "voice_only": str(voice), "duration_s": round(dur, 2), "format": probe,
              "narration_lufs": bp.lufs(voice), "narration_true_peak_dbtp": bp.true_peak(voice),
              "final_mix_lufs": bp.lufs(final), "sections_start_s": {s: round(v, 2) for s, v in offs.items()},
              "repeated_ren_clips": repeats, "long_shots": long_shots, "issues": issues, "shots": log}
    (out / "postponing_life_report.json").write_text(json.dumps(report, indent=1, ensure_ascii=False) + "\n")
    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent / "renders"))
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    rep = validate(*build(out), out)
    print(json.dumps({k: v for k, v in rep.items() if k != "shots"}, indent=1))


if __name__ == "__main__":
    main()
