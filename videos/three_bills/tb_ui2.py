"""Extra code-drawn graphics for the Three Bills full episode (Fredoka, navy / sage / cream). Figures come from production/assumptions.csv through tb_ui.A;
the only other numbers shown ($5, $20 in the 'manageable amount' beat) are quoted from the approved script. Each builder returns pilot_ui.Img(im, texts)."""
import math, sys
from pathlib import Path
from PIL import Image, ImageDraw
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / "unclaimed_401k"))
from pilot_ui import NAVY, SAGE, CREAM, GREEN, MUTED, GOLD, RED, font, txt, rrect, check, card, ease, back, clamp, Img
from tb_ui import A, usd, _t

def phone_ui(elems, w=520, h=900):
    """Generic phone: elems = [('title', s), ('big', s, colour), ('row', label, value, colour), ('toggle', label, on, p), ('check', s), ('bar', frac, colour, label), ('gap', px)]. Drawn top to bottom."""
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im); L = []
    rrect(d, (0, 0, w - 1, h - 1), 64, (*NAVY, 255)); rrect(d, (24, 60, w - 25, h - 76), 34, (*CREAM, 255))
    d.rounded_rectangle((w // 2 - 62, 22, w // 2 + 62, 40), 9, fill=(*SAGE, 255)); d.ellipse((w // 2 - 24, h - 62, w // 2 + 24, h - 16), fill=(*SAGE, 255))
    y = 110
    for e in elems:
        k = e[0]
        if k == "title": _t(d, L, (w // 2, y + 20), e[1], 46, 600, MUTED, "mm"); y += 70
        elif k == "big": _t(d, L, (w // 2, y + 55), e[1], 100, 700, e[2] if len(e) > 2 else NAVY, "mm"); y += 130
        elif k == "row":
            rrect(d, (44, y, w - 45, y + 100), 28, (255, 255, 255, 255), (*(e[3] if len(e) > 3 else SAGE), 255), 4); _t(d, L, (68, y + 50), e[1], 40, 600, NAVY, "lm"); _t(d, L, (w - 68, y + 50), e[2], 46, 700, e[3] if len(e) > 3 else NAVY, "rm"); y += 120
        elif k == "toggle":
            _t(d, L, (60, y + 40), e[1], 42, 600, NAVY, "lm"); on, p = e[2], e[3]; q = p if on else 1 - p if False else p
            tx, ty = w - 190, y + 6; col = GREEN if q > 0.5 else (176, 180, 190); rrect(d, (tx, ty, tx + 130, ty + 70), 35, (*col, 255)); kx = tx + 8 + 52 * q; d.ellipse((kx, ty + 8, kx + 54, ty + 62), fill=(255, 255, 255, 255)); y += 100
        elif k == "check": rrect(d, (44, y, w - 45, y + 100), 28, (*GREEN, 255)); check(d, 100, y + 52, 22, CREAM, 8); _t(d, L, (146, y + 50), e[1], 44, 700, CREAM, "lm"); y += 120
        elif k == "bar":
            rrect(d, (44, y, w - 45, y + 60), 20, (230, 232, 236, 255), (*NAVY, 255), 4); fw = int((w - 100) * clamp(e[1])); rrect(d, (48, y + 4, 48 + max(fw, 1), y + 56), 16, (*e[2], 255)); _t(d, L, (w // 2, y + 100), e[3], 40, 600, NAVY, "mm"); y += 140
        elif k == "gap": y += e[1]
    return Img(im, L)

def day_card(n, w=720):
    im, d = card(w, 360); L = []
    d.rounded_rectangle((0, 0, w - 1, 110), 28, fill=(*NAVY, 255)); d.rectangle((0, 70, w - 1, 110), fill=(*NAVY, 255)); _t(d, L, (w // 2, 58), "Day", 54, 700, CREAM, "mm")
    _t(d, L, (w // 2, 235), str(n), 150, 700, NAVY, "mm"); return Img(im, L)

def cross_chip(text, p, w=620, tone="cream"):
    """A chip whose text gets struck through by a red line that draws to progress p."""
    im, d = card(w, 150, fill={"cream": CREAM, "white": (255, 255, 255)}[tone]); L = []
    _t(d, L, (w // 2, 76), text, 56, 700, MUTED if p > 0.6 else NAVY, "mm")
    if p > 0: x1 = 40 + (w - 80) * clamp(p); d.line((40, 112, x1, 40), fill=(*RED, 255), width=12)
    return Img(im, L)

def fund_bar(levels, p, w=860, h=560, title="Emergency fund", scale_max=None):
    """Vertical fund tank: level moves from levels[0] to levels[1] (dollars) with progress p; the dollar label is the true interpolated STEP value (shown only at the ends)."""
    a, b = levels; mx = scale_max or A["fund_start"]; cur = a + (b - a) * ease(p)
    im, d = card(w, h); L = []; _t(d, L, (w // 2, 50), title, 46, 600, MUTED, "mm")
    x0, x1, y0, y1 = 120, 360, 100, 470; d.rectangle((x0, y0, x1, y1), fill=(255, 255, 255, 255), outline=(*NAVY, 255), width=6)
    fy = y1 - (y1 - y0) * cur / mx; d.rectangle((x0 + 4, fy, x1 - 4, y1 - 4), fill=(*SAGE, 255))
    d.line((x0 - 14, fy, x1 + 14, fy), fill=(*NAVY, 255), width=5)
    _t(d, L, (560, 190), usd(a), 64, 600, MUTED, "mm"); d.polygon([(560, 290), (520, 240), (600, 240)], fill=(*(RED if b < a else GREEN), 255)) if False else None
    _t(d, L, (560, 330), usd(b) if p >= 0.98 else "", 80, 700, RED if b < a else GREEN, "mm")
    _t(d, L, (w // 2, h - 40), "Illustrative", 40, 500, MUTED, "mm"); return Img(im, L)

def tooth(p, state="pain", w=520):
    """Tooth icon: pain lines pulse (state 'pain') or a green tick (state 'ok')."""
    im = Image.new("RGBA", (w, w), (0, 0, 0, 0)); d = ImageDraw.Draw(im); L = []
    d.polygon([(130, 120), (210, 90), (260, 110), (310, 90), (390, 120), (400, 230), (370, 400), (320, 440), (290, 300), (260, 300), (230, 300), (200, 440), (150, 400), (120, 230)], fill=(255, 255, 250, 255), outline=(*NAVY, 255))
    d.line((130, 120, 210, 90, 260, 110, 310, 90, 390, 120, 400, 230, 370, 400, 320, 440, 290, 300, 230, 300, 200, 440, 150, 400, 120, 230, 130, 120), fill=(*NAVY, 255), width=8, joint="curve")
    if state == "pain":
        a = int(255 * (0.4 + 0.6 * abs(math.sin(p * 6)))); 
        for (x, y, dx, dy) in ((90, 90, -40, -40), (430, 90, 40, -40), (60, 250, -50, 0), (460, 250, 50, 0)): d.line((x, y, x + dx, y + dy), fill=(*RED, a), width=10)
    else: d.ellipse((330, 330, 450, 450), fill=(*GREEN, 255)); check(d, 390, 392, 36, CREAM, 12, p=clamp(p))
    return Img(im, L)

def dominoes(p, w=1200, h=420):
    """Repair > Credit card > Dentist postponed tiles tipping over one after another (progress p 0..1)."""
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im); L = []
    labs = ["Car repair", "Credit card", "Dentist"]; fall = [clamp((p * 3) - k) for k in range(3)]
    for k, lab in enumerate(labs):
        x = 120 + 380 * k; ang = 80 * ease(fall[k]); t = Image.new("RGBA", (300, 340), (0, 0, 0, 0)); td = ImageDraw.Draw(t); rrect(td, (10, 10, 290, 330), 30, (*(SAGE if k != 1 else NAVY), 255), (*NAVY, 255), 6)
        _t(td, [], (150, 170), lab, 52, 700, CREAM if k == 1 else NAVY, "mm"); r = t.rotate(-ang, Image.BICUBIC, expand=True, center=(290, 330)); im.alpha_composite(r, (x - 10 - int(ang * 0.3), 60 + int(ang * 0.5)))
        L.append((x, 160, x + 280, 240, lab, 52)) if ang < 5 else None
    return Img(im, L)

def two_accounts(p, w=980, h=520):
    """Checking -> Savings with a coin travelling along the arrow (p 0..1, loops through the beat)."""
    im, d = card(w, h); L = []
    rrect(d, (40, 150, 330, 330), 34, (*CREAM, 255), (*NAVY, 255), 5); _t(d, L, (185, 215), "Checking", 48, 700, NAVY, "mm"); _t(d, L, (185, 275), "Easy to spend", 36, 500, MUTED, "mm")
    rrect(d, (w - 330, 150, w - 40, 330), 34, (*SAGE, 255), (*NAVY, 255), 5); _t(d, L, (w - 185, 215), "Savings", 48, 700, NAVY, "mm"); _t(d, L, (w - 185, 275), "Separate", 40, 600, NAVY, "mm")
    a, b = (340, 240), (w - 345, 240); d.line((*a, *b), fill=(*NAVY, 255), width=8); d.polygon([(b[0] + 16, b[1]), (b[0] - 14, b[1] - 20), (b[0] - 14, b[1] + 20)], fill=(*NAVY, 255))
    q = (p * 2) % 1.0; x = a[0] + (b[0] - a[0]) * ease(q); d.ellipse((x - 26, 240 - 26, x + 26, 240 + 26), fill=(*GOLD, 255), outline=(*NAVY, 255), width=4); d.text((x, 241), "$", font=font(30, 700), fill=NAVY, anchor="mm")
    _t(d, L, (w // 2, 420), "Automatic, every week", 46, 600, NAVY, "mm"); return Img(im, L)

def sign(text, w=900, tone="sage", px=64):
    d0 = ImageDraw.Draw(Image.new("RGBA", (4, 4))); lines, cur = [], ""
    for wd in text.split():
        t = (cur + " " + wd).strip()
        if d0.textlength(t, font=font(px, 700)) <= w - 80 or not cur: cur = t
        else: lines.append(cur); cur = wd
    lines.append(cur); h = 60 + 86 * len(lines); fill = {"sage": SAGE, "cream": CREAM, "gold": (246, 222, 160), "red": (238, 196, 186)}[tone]
    im, d = card(w, h, fill=fill); L = []
    for i, s in enumerate(lines): _t(d, L, (w // 2, 30 + 43 + 86 * i), s, px, 700, NAVY, "mm")
    return Img(im, L)

def tiles(items, ticks, w=560):
    """Vertical list of labelled tiles each with a tick drawn to progress ticks[i]."""
    h = 40 + 140 * len(items); im, d = card(w, h); L = []
    for i, s in enumerate(items):
        y = 30 + 140 * i; rrect(d, (30, y, w - 30, y + 110), 30, (255, 255, 255, 255), (*SAGE, 255), 4); _t(d, L, (60, y + 55), s, 46, 700, NAVY, "lm")
        if ticks[i] > 0: check(d, w - 90, y + 58, 28, GREEN, 11, p=clamp(ticks[i]))
    return Img(im, L)

def cup(w=220, h=240, steam=0.0):
    im = Image.new("RGBA", (w, h + 120), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for k in range(3):
        x = 60 + 50 * k; ph = (steam * 1.3 + k * 0.33) % 1.0; y = 110 - 90 * ph; d.line((x, y + 70, x - 12, y + 35, x + 12, y, x, y - 30), fill=(*MUTED, int(200 * (1 - ph))), width=7, joint="curve")
    rrect(d, (20, 130, w - 50, h + 100), 24, (*SAGE, 255), (*NAVY, 255), 6); d.arc((w - 100, 170, w - 10, 250), -90, 90, fill=(*NAVY, 255), width=10); return im

def suitcase(w=360, h=300):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im); rrect(d, (20, 70, w - 20, h - 20), 30, (*SAGE, 255), (*NAVY, 255), 6); rrect(d, (w // 2 - 50, 20, w // 2 + 50, 80), 18, (0, 0, 0, 0), (*NAVY, 255), 8)
    d.line((70, 120, 70, h - 50), fill=(*NAVY, 255), width=6); d.line((w - 70, 120, w - 70, h - 50), fill=(*NAVY, 255), width=6); return im

def compare_card(p, w=980, h=520):
    """$400 (the fund) against a long stretch without pay: a short bar against weeks that keep going (no new figures)."""
    im, d = card(w, h); L = []; _t(d, L, (w // 2, 60), "Four hundred dollars", 52, 700, NAVY, "mm")
    d.rectangle((60, 130, 60 + 150, 190), fill=(*SAGE, 255), outline=(*NAVY, 255), width=5); _t(d, L, (60 + 75, 160), usd(A["fund_final"]), 40, 700, NAVY, "mm")
    n = int(14 * clamp(p)); 
    for k in range(n): x = 240 + 52 * k; d.rectangle((x, 130, x + 44, 190), fill=(*CREAM, 255), outline=(*MUTED, 255), width=3)
    _t(d, L, (w // 2, 320), "A long stretch without a paycheck", 48, 600, NAVY, "mm"); _t(d, L, (w // 2, 410), "is more than this fund covers", 44, 500, MUTED, "mm"); return Img(im, L)
