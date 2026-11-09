"""Code-drawn graphics for the Three Bills pilot (Fredoka, navy / sage / cream). Every number comes from production/assumptions.csv via A.* below
(never typed into a graphic), so labels cannot drift from the checked figures. Each builder returns pilot_ui.Img(im, texts)."""
import csv, math, sys
from pathlib import Path
from PIL import Image, ImageDraw
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "unclaimed_401k"))
from pilot_ui import NAVY, SAGE, CREAM, GREEN, MUTED, GOLD, RED, font, txt, rrect, check, card, ease, back, clamp, Img

def _load():
    v = {}
    for r in csv.DictReader(open(HERE / "production" / "assumptions.csv")): v[r["key"]] = float(r["value"])
    return {k: int(x) if x == int(x) else x for k, x in v.items()}
A = _load()
assert A["car_bill"] + A["dental_bill"] + A["plumber_bill"] == A["total_emergencies"] and A["fund_start"] - A["total_emergencies"] == A["fund_final"] and A["weekly_transfer"] * A["contribution_weeks"] == A["fund_start"]
def usd(n): return f"${n:,}"

def _t(d, L, xy, s, px, wt=700, fill=NAVY, anchor="la"):
    b = txt(d, xy, s, px, wt, fill, anchor); L.append((*b, s, px)); return b

def title_card(top, big, sub=None, w=760, tone="sage"):
    """Two-line headline card (e.g. '3 bills' / '30 days')."""
    h = 420 if sub else 360; fill = {"sage": SAGE, "cream": CREAM, "gold": (246, 222, 160)}[tone]
    im, d = card(w, h, fill=fill); L = []
    _t(d, L, (w // 2, 100), top, 64, 600, NAVY, "mm"); _t(d, L, (w // 2, 230), big, 120, 700, NAVY, "mm")
    if sub: _t(d, L, (w // 2, 345), sub, 44, 500, MUTED if tone == "cream" else NAVY, "mm")
    return Img(im, L)

def equation_card(w=800):
    """The finished equation 760 + 390 + 1,050 = 2,200 (all terms at once: no counting beside a partial equation)."""
    rows = [("Car repair", A["car_bill"]), ("Dental bill", A["dental_bill"]), ("Leaking pipe", A["plumber_bill"])]
    h = 150 + 100 * 3 + 140; im, d = card(w, h); L = []
    _t(d, L, (34, 28), "Three bills in thirty days", 42, 600, MUTED)
    for i, (lab, amt) in enumerate(rows):
        y = 100 + 100 * i; rrect(d, (22, y, w - 22, y + 84), 26, (255, 255, 255, 255), (*SAGE, 255), 4)
        _t(d, L, (50, y + 42), lab, 46, 600, NAVY, "lm"); _t(d, L, (w - 50, y + 42), usd(amt), 54, 700, NAVY, "rm")
    y = 100 + 300 + 16; d.line((34, y, w - 34, y), fill=(*NAVY, 255), width=6)
    _t(d, L, (50, y + 62), "Total", 52, 700, NAVY, "lm"); _t(d, L, (w - 50, y + 62), usd(A["total_emergencies"]), 72, 700, NAVY, "rm")
    return Img(im, L)

def phone_inset(balance, sub=None, w=420, h=760, down=False):
    """Blank-phone body drawn in code with a savings screen (the supplied phone prop has no screen content by design)."""
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im); L = []
    rrect(d, (0, 0, w - 1, h - 1), 60, (*NAVY, 255)); rrect(d, (22, 54, w - 23, h - 70), 30, (*CREAM, 255))
    d.rounded_rectangle((w // 2 - 60, 20, w // 2 + 60, 36), 8, fill=(*SAGE, 255)); d.ellipse((w // 2 - 22, h - 56, w // 2 + 22, h - 14), fill=(*SAGE, 255))
    _t(d, L, (w // 2, 120), "Savings", 48, 600, MUTED, "mm"); _t(d, L, (w // 2, 250), usd(balance), 88, 700, NAVY, "mm")
    if down:
        d.polygon([(w // 2, 400), (w // 2 - 54, 330), (w // 2 + 54, 330)], fill=(*RED, 255)); d.rectangle((w // 2 - 20, 300, w // 2 + 20, 332), fill=(*RED, 255))
    if sub: _t(d, L, (w // 2, 470), sub, 44, 600, NAVY, "mm")
    return Img(im, L)

def phone_balance_pair(before, after, w=420, h=760):
    """Savings app showing the fall from `before` to `after` (both from assumptions)."""
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im); L = []
    rrect(d, (0, 0, w - 1, h - 1), 60, (*NAVY, 255)); rrect(d, (22, 54, w - 23, h - 70), 30, (*CREAM, 255))
    d.rounded_rectangle((w // 2 - 60, 20, w // 2 + 60, 36), 8, fill=(*SAGE, 255)); d.ellipse((w // 2 - 22, h - 56, w // 2 + 22, h - 14), fill=(*SAGE, 255))
    _t(d, L, (w // 2, 120), "Savings", 48, 600, MUTED, "mm"); _t(d, L, (w // 2, 215), usd(before), 56, 600, MUTED, "mm")
    d.line((w // 2 - 80, 215, w // 2 + 80, 215), fill=(*RED, 255), width=6)
    d.polygon([(w // 2, 380), (w // 2 - 40, 320), (w // 2 + 40, 320)], fill=(*RED, 255)); d.rectangle((w // 2 - 14, 290, w // 2 + 14, 322), fill=(*RED, 255))
    _t(d, L, (w // 2, 480), usd(after), 92, 700, NAVY, "mm"); _t(d, L, (w // 2, 580), "Illustrative", 42, 500, MUTED, "mm")
    return Img(im, L)

def bubble(text, w=640, tail="left"):
    h = 180; im, d = card(w, h, fill=(255, 255, 255)); L = []
    _t(d, L, (w // 2, h // 2), text, 58, 700, NAVY, "mm")
    return Img(im, L)

def chip_card(label, w=520, tone="cream", px=54):
    im, d = card(w, 150, fill={"cream": CREAM, "sage": SAGE, "gold": (246, 222, 160), "white": (255, 255, 255)}[tone]); L = []
    _t(d, L, (w // 2, 76), label, px, 700, NAVY, "mm"); return Img(im, L)

def invoice(title, amount, urgent=False, w=520, h=680, note="After insurance"):
    """Blank invoice prop look (paper with grey rules) with code-drawn title and amount."""
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im); L = []
    d.polygon([(0, 0), (w - 80, 0), (w, 80), (w, h), (0, h)], fill=(255, 255, 250, 255), outline=(*NAVY, 255)); d.line((w - 80, 0, w - 80, 80, w, 80), fill=(*NAVY, 255), width=4)
    _t(d, L, (40, 70), title, 54, 700, NAVY)
    if amount is not None: _t(d, L, (40, 150), note, 42, 500, MUTED)
    for i in range(3 if amount is not None else 5): d.line((40, 250 + 50 * i, w - 60 - (60 if i == 2 else 0), 250 + 50 * i), fill=(*SAGE, 255), width=8)
    if amount is not None: _t(d, L, (w // 2, 470), usd(amount), 100, 700, NAVY, "mm")
    if urgent: rrect(d, (w // 2 - 130, h - 110, w // 2 + 130, h - 30), 30, (*RED, 255)); _t(d, L, (w // 2, h - 70), "URGENT", 50, 700, CREAM, "mm")
    return Img(im, L)

def credit_card(w=520, label="Credit card"):
    h = 320; im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im); L = []
    rrect(d, (0, 0, w - 1, h - 1), 36, (*NAVY, 255)); d.rectangle((0, 60, w, 130), fill=(*SAGE, 255))
    _t(d, L, (36, 215), label, 56, 700, CREAM, "lm"); _t(d, L, (36, 275), "Balance carried", 42, 500, CREAM, "lm")
    return Img(im, L)

def calendar_card(label, sub=None, flip=1.0, w=640):
    h = 440 if sub else 380; im, d = card(w, h); L = []
    d.rounded_rectangle((0, 0, w - 1, 110), 28, fill=(*NAVY, 255)); d.rectangle((0, 70, w - 1, 110), fill=(*NAVY, 255))
    _t(d, L, (w // 2, 58), "Calendar", 50, 700, CREAM, "mm")
    px = 84
    while d.textlength(label, font=font(px, 700)) > w - 60 and px > 40: px -= 4
    _t(d, L, (w // 2, 240), label, px, 700, NAVY, "mm")
    if sub: _t(d, L, (w // 2, 360), sub, 46, 500, MUTED, "mm")
    return Img(im, L)

def chain(stage, w=640):
    """Repair -> credit card -> postponed dentist, stacked: one surprise becoming a chain (no figures)."""
    items = ["Car repair", "Credit card", "Dentist postponed"]; h = 60 + 150 * len(items); im, d = card(w, h); L = []
    for i, s in enumerate(items):
        y = 40 + 150 * i
        if i < stage:
            rrect(d, (40, y, w - 40, y + 100), 36, (*SAGE, 255), (*NAVY, 255), 4); _t(d, L, (w // 2, y + 50), s, 50, 700, NAVY, "mm")
            if i + 1 < stage and i < len(items) - 1: d.line((w // 2, y + 100, w // 2, y + 150), fill=(*NAVY, 255), width=8); d.polygon([(w // 2, y + 150), (w // 2 - 14, y + 128), (w // 2 + 14, y + 128)], fill=(*NAVY, 255))
    return Img(im, L)

# ---- revision 2 additions: object-interaction graphics -----------------------------------------------------------------------------
def balance_steps(t, w=540, h=940):
    """Savings app: the balance steps 2,600 -> 1,840 -> 1,450 -> 400 as the three bills leave (all values from assumptions.csv)."""
    steps = [(0.0, A["fund_start"], None), (0.45, A["fund_after_car"], ("Car repair", A["car_bill"])), (0.95, A["fund_after_dental"], ("Dental bill", A["dental_bill"])), (1.45, A["fund_final"], ("Leaking pipe", A["plumber_bill"]))]
    cur = max(i for i, s in enumerate(steps) if t >= s[0])
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im); L = []
    rrect(d, (0, 0, w - 1, h - 1), 64, (*NAVY, 255)); rrect(d, (24, 60, w - 25, h - 76), 34, (*CREAM, 255))
    d.rounded_rectangle((w // 2 - 62, 22, w // 2 + 62, 40), 9, fill=(*SAGE, 255)); d.ellipse((w // 2 - 24, h - 62, w // 2 + 24, h - 16), fill=(*SAGE, 255))
    _t(d, L, (w // 2, 130), "Savings", 52, 600, MUTED, "mm")
    _t(d, L, (w // 2, 260), usd(steps[cur][1]), 112, 700, RED if cur == 3 else NAVY, "mm")
    for k in range(1, cur + 1):
        lab, amt = steps[k][2]; y = 380 + 130 * (k - 1); p = ease((t - steps[k][0]) / 0.25)
        rrect(d, (44, y, w - 45, y + 104), 28, (255, 255, 255, 255), (*RED, 255), 4)
        _t(d, L, (70, y + 52), lab, 42, 600, NAVY, "lm"); _t(d, L, (w - 70, y + 52), "-" + usd(amt), 50, 700, RED, "rm")
    return Img(im, L)

def tile(label, w=500, h=190):
    """Empty tile for a prop icon (the icon is composited by the renderer) with a label; the tick is drawn by tick_on()."""
    im, d = card(w, h); L = []
    _t(d, L, (w - 40, h // 2), label, 54, 700, NAVY, "rm"); return Img(im, L)

def tick_on(img, p):
    """Return a copy of a tile with a green tick drawn to progress p (0..1) over the icon area."""
    im = img.im.copy(); d = ImageDraw.Draw(im)
    if p > 0: check(d, 215, im.height // 2 + 6, 44, GREEN, 14, p=clamp(p))
    return Img(im, img.texts)

def sink_cabinet(w=620, h=420):
    """Sink base cabinet drawn in the brand palette (temporary coded set piece, not approved artwork): counter, body, one open door."""
    im = Image.new("RGBA", (w + 200, h + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(im); WOOD = (176, 122, 86)
    rrect(d, (0, 0, w, 56), 14, (*WOOD, 255), (*NAVY, 255), 5)                                  # counter
    rrect(d, (20, 56, w - 20, h), 10, (*SAGE, 255), (*NAVY, 255), 5)                           # body
    rrect(d, (60, 92, w - 60, h - 30), 8, (214, 206, 190, 255), (*NAVY, 255), 4)               # open interior
    d.polygon([(w - 60, 92), (w + 120, 120), (w + 120, h - 6), (w - 60, h - 30)], fill=(*SAGE, 255), outline=(*NAVY, 255))   # open door
    d.ellipse((w + 60, 250, w + 76, 266), fill=(*WOOD, 255)); return im

def bill(w=190, h=96):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im); rrect(d, (0, 0, w - 1, h - 1), 14, (206, 226, 200, 255), (*NAVY, 255), 4)
    d.ellipse((w // 2 - 24, h // 2 - 24, w // 2 + 24, h // 2 + 24), outline=(*NAVY, 255), width=4); d.text((w // 2, h // 2), "$", font=font(34, 700), fill=NAVY, anchor="mm"); return im
