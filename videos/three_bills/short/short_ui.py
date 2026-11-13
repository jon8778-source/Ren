"""Portrait (1080x1920) cards for the Three Bills Short. Fredoka, navy / sage / cream. Every string is >= 44 px at 1:1. Figures come from production/assumptions.csv (tb_ui.A).
Each builder returns pilot_ui.Img(im, texts) with texts = [(x0, y0, x1, y1, string, px)] relative to the card."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent)); sys.path.insert(0, str(HERE.parents[1] / "unclaimed_401k"))
from pilot_ui import NAVY, SAGE, CREAM, GREEN, MUTED, GOLD, RED, font, txt, rrect, check, card, ease, back, clamp, Img
from tb_ui import A, usd, _t
import tb_ui as T

def equation_p(w=420):
    """Three bills and the total, short labels so 44 px text fits a narrow column."""
    rows = [("Car", A["car_bill"]), ("Dental", A["dental_bill"]), ("Pipe", A["plumber_bill"])]; h = 60 + 112 * 3 + 160; im, d = card(w, h); L = []
    for i, (lab, amt) in enumerate(rows):
        y = 30 + 112 * i; rrect(d, (20, y, w - 20, y + 96), 26, (255, 255, 255, 255), (*SAGE, 255), 4); _t(d, L, (44, y + 48), lab, 46, 600, NAVY, "lm"); _t(d, L, (w - 44, y + 48), usd(amt), 48, 700, NAVY, "rm")
    y = 30 + 336 + 14; d.line((30, y, w - 30, y), fill=(*NAVY, 255), width=6); _t(d, L, (44, y + 66), "Total", 50, 700, NAVY, "lm"); _t(d, L, (w - 44, y + 66), usd(A["total_emergencies"]), 58, 700, NAVY, "rm")
    return Img(im, L)

def phone_p(elems, w=440, h=720):
    """Phone: elems = [('title', s), ('big', s, colour), ('row', label, value, colour), ('toggle', label, p), ('bar', frac, colour, label), ('check', s), ('gap', px)]."""
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im); L = []
    rrect(d, (0, 0, w - 1, h - 1), 58, (*NAVY, 255), None); rrect(d, (22, 56, w - 23, h - 72), 30, (*CREAM, 255))
    d.rounded_rectangle((w // 2 - 54, 20, w // 2 + 54, 36), 8, fill=(*SAGE, 255)); d.ellipse((w // 2 - 22, h - 58, w // 2 + 22, h - 16), fill=(*SAGE, 255))
    y = 90
    for e in elems:
        k = e[0]
        if k == "title": _t(d, L, (w // 2, y + 24), e[1], 46, 600, MUTED, "mm"); y += 76
        elif k == "big": _t(d, L, (w // 2, y + 56), e[1], e[3] if len(e) > 3 else 92, 700, e[2] if len(e) > 2 else NAVY, "mm"); y += 124
        elif k == "row":
            col = e[3] if len(e) > 3 else SAGE; rrect(d, (36, y, w - 37, y + 92), 26, (255, 255, 255, 255), (*col, 255), 4); _t(d, L, (56, y + 46), e[1], 44, 600, NAVY, "lm"); _t(d, L, (w - 56, y + 46), e[2], 46, 700, col if col != SAGE else NAVY, "rm"); y += 112
        elif k == "toggle":
            _t(d, L, (52, y + 40), e[1], 46, 600, NAVY, "lm"); q = e[2]; tx, ty = w - 190, y + 6; col = GREEN if q > 0.5 else (176, 180, 190)
            rrect(d, (tx, ty, tx + 130, ty + 70), 35, (*col, 255)); kx = tx + 8 + 52 * q; d.ellipse((kx, ty + 8, kx + 54, ty + 62), fill=(255, 255, 255, 255)); y += 100
        elif k == "bar":
            rrect(d, (36, y, w - 37, y + 56), 20, (230, 232, 236, 255), (*NAVY, 255), 4); fw = int((w - 80) * clamp(e[1])); rrect(d, (40, y + 4, 40 + max(fw, 1), y + 52), 16, (*e[2], 255)); _t(d, L, (w // 2, y + 96), e[3], 44, 600, NAVY, "mm"); y += 140
        elif k == "check": rrect(d, (36, y, w - 37, y + 96), 28, (*GREEN, 255)); check(d, 90, y + 50, 22, CREAM, 8); _t(d, L, (130, y + 48), e[1], 46, 700, CREAM, "lm"); y += 116
        elif k == "gap": y += e[1]
    return Img(im, L)

def tank_p(a, b, p, title="Emergency fund", w=860, h=1000):
    """Vertical fund tank for a full-screen graphic: level moves a -> b (dollars, from assumptions) with progress p; the end value is shown only when it is reached."""
    mx = A["fund_start"]; cur = a + (b - a) * ease(p); im, d = card(w, h); L = []; _t(d, L, (w // 2, 70), title, 58, 700, NAVY, "mm")
    x0, x1, y0, y1 = 130, 390, 160, 760; d.rectangle((x0, y0, x1, y1), fill=(255, 255, 255, 255), outline=(*NAVY, 255), width=7); fy = y1 - (y1 - y0) * cur / mx
    d.rectangle((x0 + 4, fy, x1 - 4, y1 - 4), fill=(*SAGE, 255)); d.line((x0 - 16, fy, x1 + 16, fy), fill=(*NAVY, 255), width=6)
    _t(d, L, (620, 300), usd(a), 64, 600, MUTED, "mm"); _t(d, L, (620, 480), usd(b) if p >= 0.98 else "", 92, 700, RED if b < a else GREEN, "mm"); _t(d, L, (w // 2, h - 90), "Illustrative", 46, 500, MUTED, "mm")
    return Img(im, L)

def sign_p(text, w=560, tone="sage", px=60):
    d0 = ImageDraw.Draw(Image.new("RGBA", (4, 4))); lines, cur = [], ""
    for wd in text.split():
        t = (cur + " " + wd).strip()
        if d0.textlength(t, font=font(px, 700)) <= w - 70 or not cur: cur = t
        else: lines.append(cur); cur = wd
    lines.append(cur); h = 60 + int(px * 1.45) * len(lines); fill = {"sage": SAGE, "cream": CREAM, "gold": (246, 222, 160), "red": (238, 196, 186)}[tone]; im, d = card(w, h, fill=fill); L = []
    for i, s in enumerate(lines): _t(d, L, (w // 2, 30 + int(px * 0.72) + int(px * 1.45) * i), s, px, 700, NAVY, "mm")
    return Img(im, L)

def cross_p(text, p, w=560, px=54):
    im, d = card(w, 150); L = []; _t(d, L, (w // 2, 76), text, px, 700, MUTED if p > 0.6 else NAVY, "mm")
    if p > 0: d.line((36, 114, 36 + (w - 72) * clamp(p), 40), fill=(*RED, 255), width=12)
    return Img(im, L)

def bubble_p(text, w=600, px=56):
    d0 = ImageDraw.Draw(Image.new("RGBA", (4, 4))); lines, cur = [], ""
    for wd in text.split():
        t = (cur + " " + wd).strip()
        if d0.textlength(t, font=font(px, 700)) <= w - 60 or not cur: cur = t
        else: lines.append(cur); cur = wd
    lines.append(cur); h = 50 + int(px * 1.4) * len(lines); im, d = card(w, h, fill=(255, 255, 255)); L = []
    for i, s in enumerate(lines): _t(d, L, (w // 2, 25 + int(px * 0.7) + int(px * 1.4) * i), s, px, 700, NAVY, "mm")
    return Img(im, L)

def invoice_p(title, amount, note="After insurance", urgent=False, w=700, h=900):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im); L = []
    d.polygon([(0, 0), (w - 100, 0), (w, 100), (w, h), (0, h)], fill=(255, 255, 250, 255), outline=(*NAVY, 255)); d.line((w - 100, 0, w - 100, 100, w, 100), fill=(*NAVY, 255), width=5)
    _t(d, L, (50, 90), title, 68, 700, NAVY); _t(d, L, (50, 196), note, 48, 500, MUTED)
    for i in range(3): d.line((50, 330 + 60 * i, w - 70 - (80 if i == 2 else 0), 330 + 60 * i), fill=(*SAGE, 255), width=9)
    _t(d, L, (w // 2, 610), usd(amount), 150, 700, NAVY, "mm")
    if urgent: rrect(d, (w // 2 - 190, h - 150, w // 2 + 190, h - 50), 36, (*RED, 255)); _t(d, L, (w // 2, h - 100), "URGENT", 62, 700, CREAM, "mm")
    return Img(im, L)

def tiles_p(items, ticks, w=420):
    h = 40 + 130 * len(items); im, d = card(w, h); L = []
    for i, s in enumerate(items):
        y = 28 + 130 * i; rrect(d, (22, y, w - 22, y + 104), 28, (255, 255, 255, 255), (*SAGE, 255), 4); _t(d, L, (46, y + 52), s, 48, 700, NAVY, "lm")
        if ticks[i] > 0: check(d, w - 70, y + 54, 26, GREEN, 11, p=clamp(ticks[i]))
    return Img(im, L)
