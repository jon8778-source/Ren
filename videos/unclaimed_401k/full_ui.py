"""Right-hand panels / full-screen graphics for scenes 2b-8 of the 401(k) episode. Every number is a claim from the approved script.
Baseline text is >= 34 px; GRAPHIC shots draw the same panel scaled up, never smaller."""
import math
from PIL import Image, ImageDraw
from pilot_ui import (NAVY, SAGE, CREAM, GREEN, MUTED, GOLD, RED, font, txt, rrect, check, card, ease, back, clamp, Img, CLAIMS)

def _fit(d, s, px, wt, maxw):
    while px > 30 and d.textlength(s, font=font(px, wt)) > maxw: px -= 2
    return px
def T(d, T_, xy, s, px, wt=600, fill=NAVY, anchor="la", maxw=None):
    if maxw: px = _fit(d, s, px, wt, maxw)
    b = txt(d, xy, s, px, wt, fill, anchor); T_.append((*b, s, px)); return b

def note_card(title, lines, hi=None, w=860, accent=SAGE, sub=None, glow=0.0, hi_p=1.0):
    """A document card: muted title, then lines; line `hi` is highlighted (sage band + gold outline)."""
    h = 120 + 86 * len(lines) + (60 if sub else 0)
    im, d = card(w, h); L = []
    T(d, L, (34, 26), title, 36, 600, MUTED, maxw=w - 68)
    for i, s in enumerate(lines):
        y = 100 + 86 * i
        if hi is not None and i == hi:
            rrect(d, (22, y - 8, w - 22, y + 70), 24, (*accent, 255), (*NAVY, 255), 4)
            if glow > 0: d.rounded_rectangle((14, y - 16, w - 14, y + 78), 30, outline=(*GOLD, int(255 * clamp(glow))), width=8)
        T(d, L, (50, y + 31), s, 46, 600, NAVY, "lm", maxw=w - 100)
    if sub: T(d, L, (34, h - 44), sub, 34, 500, MUTED, "lm")
    return Img(im, L)

def stat_card(label, value, sub=None, tone="sage", w=860, strike=False, tag=None):
    h = 330 + (50 if sub else 0)
    fill = {"sage": SAGE, "cream": CREAM, "gold": (246, 222, 160), "red": (238, 196, 186)}[tone]
    im, d = card(w, h, fill=fill); L = []
    if tag: T(d, L, (34, 24), tag, 34, 600, MUTED)
    T(d, L, (w // 2, 100 if tag else 80), label, 48, 600, NAVY, "mm", maxw=w - 70)
    T(d, L, (w // 2, 215), value, 112, 700, NAVY, "mm", maxw=w - 70)
    if sub: T(d, L, (w // 2, h - 40), sub, 34, 500, NAVY, "mm", maxw=w - 70)
    if strike: d.line((40, h - 50, w - 40, 50), fill=(*RED, 255), width=12)
    return Img(im, L)

def two_stream(stage, t=0.0, w=900, h=700):
    """Two-stream payroll match diagram: Maya and Employer feed the 401(k) account. Only finished, true values are ever shown."""
    im, d = card(w, h); L = []
    def stream(y, label, col, amt, p, on=True):
        rrect(d, (30, y, 300, y + 110), 30, (*col, 255), (*NAVY, 255), 4); T(d, L, (165, y + 55), label, 44, 700, NAVY, "mm", maxw=240)
        a, b = (300, y + 55), (560, 345)
        if on:
            d.line((*a, *b), fill=(*NAVY, 255), width=8); d.polygon([(b[0] + 14, b[1] + 3), (b[0] - 16, b[1] - 18), (b[0] - 16, b[1] + 22)], fill=(*NAVY, 255))
            q = ease(p % 1.0 if p < 99 else 1.0); x, yy = a[0] + (b[0] - a[0]) * q, a[1] + (b[1] - a[1]) * q
            d.ellipse((x - 22, yy - 22, x + 22, yy + 22), fill=(*GOLD, 255), outline=(*NAVY, 255), width=4); d.text((x, yy + 1), "$", font=font(28, 700), fill=NAVY, anchor="mm")
        if amt: T(d, L, (320, y + 55 - 60 if y < 300 else y + 55 + 62), amt, 38, 700, NAVY, "lm", maxw=240)
    rrect(d, (570, 270, w - 30, 420), 30, (255, 255, 255, 255), (*NAVY, 255), 5)
    T(d, L, ((570 + w - 30) // 2, 318), "401(k)", 50, 700, NAVY, "mm"); T(d, L, ((570 + w - 30) // 2, 380), "account", 36, 500, MUTED, "mm")
    amts = {1: ("$1", None), 2: ("$1", "$1"), 3: ("up to 4%", "up to 4%"), 4: ("$2,400 / yr", "$2,400 / yr"), 5: ("$200 / mo", "up to $200 / mo"), 6: ("$1,200 / yr", "$1,200 / yr"),
            7: ("2% = $1,200", "half the match"), 8: ("2% = $1,200", "missing $1,200"), 9: ("2% = $1,200", "missing $100 / mo"), 10: ("+ $100 / mo", "$100 / mo")}
    m_amt, e_amt = amts.get(stage, (None, None))
    stream(110, "Maya", SAGE, m_amt, t * 0.6, stage >= 1)
    stream(500, "Employer", CREAM, e_amt, t * 0.6 + 0.3, stage >= 2)
    if stage == 4: T(d, L, (w // 2, 640), "$60,000 x 4% = $2,400 a year", 38, 600, NAVY, "mm", maxw=w - 60)
    if stage in (7, 8, 9): d.rounded_rectangle((20, 478, 330, 628), 34, outline=(*GOLD, 255), width=8)
    if stage == 10: T(d, L, (w // 2, 640), "and she must qualify under her plan", 36, 500, MUTED, "mm", maxw=w - 60)
    if stage == 0:
        T(d, L, (w // 2, 80), "Employer match", 54, 700, NAVY, "mm"); T(d, L, (w // 2, 640), "Illustrative example", 34, 500, MUTED, "mm")
    return Img(im, L)

def bubble(text, strike=0.0, w=860, h=330):
    im, d = card(w, h, fill=(255, 255, 255)); L = []
    T(d, L, (w // 2, h // 2 - 10), text, 58, 700, NAVY, "mm", maxw=w - 80)
    d.polygon([(120, h - 4), (190, h - 4), (110, h + 50)], fill=(255, 255, 255, 255), outline=(*NAVY, 255)); d.rectangle((125, h - 8, 186, h + 2), fill=(255, 255, 255, 255))
    if strike > 0: d.line((40, h - 40, 40 + (w - 80) * clamp(strike), h - 40 - (h - 80) * clamp(strike)), fill=(*RED, 255), width=14)
    return Img(im, L)

def outcomes(stage, w=900, h=520):
    """Pre-tax vs Roth: two labelled outcomes, no computed take-home figures. stage 0 both, 1 pre-tax lit, 2 pre-tax value, 3 Roth lit, 4 Roth value."""
    im, d = card(w, h); L = []
    for k, (name, val, y) in enumerate((("Pre-tax", "may be less than $100", 40), ("Roth", "the full $100", 290))):
        lit = (stage in (1, 2) and k == 0) or (stage in (3, 4) and k == 1) or stage == 0
        show = (stage == 2 and k == 0) or (stage == 4 and k == 1)
        rrect(d, (30, y, w - 30, y + 190), 30, (*(SAGE if lit else CREAM), 255), (*NAVY, 255), 5)
        T(d, L, (66, y + 50), name, 54, 700, NAVY, "lm"); T(d, L, (66, y + 125), val if show else "take-home pay", 46 if show else 38, 700 if show else 500, NAVY if show else MUTED, "lm", maxw=w - 130)
    return Img(im, L)

def budget(stage, w=860):
    """Budget lines $12 + $40 + $48 = $100 / month (running total always true). stage 0..4."""
    rows = [("Subscription", 12), ("Delivery habit", 40), ("App plans + gym", 48)]
    n = min(stage, 3); im, d = card(w, 560); L = []
    T(d, L, (34, 26), "Monthly budget", 36, 600, MUTED)
    tot = 0
    for i, (lab, amt) in enumerate(rows):
        y = 100 + 100 * i
        if i < n:
            tot += amt; rrect(d, (22, y - 8, w - 22, y + 76), 24, (255, 255, 255, 255), (*SAGE, 255), 4)
            T(d, L, (50, y + 34), lab, 44, 600, NAVY, "lm"); T(d, L, (w - 50, y + 34), f"${amt}", 52, 700, NAVY, "rm")
    if n:
        T(d, L, (w - 50, 430), f"${tot} so far" if n < 3 else f"= ${tot} / month", 54 if n < 3 else 66, 700, NAVY, "rm")
    if stage >= 4: d.rounded_rectangle((16, 395, w - 16, 475), 30, outline=(*GOLD, 255), width=8)
    T(d, L, (34, 520), "Illustrative example", 34, 500, MUTED, "lm")
    return Img(im, L)

def contrib_ui(pct, p_change=0.0, save_pulse=0.0, saved=False, w=860, h=470):
    """401(k) contribution page. pct shown; during p_change 0..1 the value counts 2 -> 4."""
    shown = 2 if p_change <= 0 else (4 if p_change >= 1 else (2 if p_change < 0.5 else 4))
    im, d = card(w, h); L = []
    T(d, L, (34, 24), "401(k) contribution", 38, 600, MUTED)
    T(d, L, (34, 106), "Contribution %", 40, 500, MUTED)
    rrect(d, (30, 150, w - 30, 250), 26, (*CREAM, 255), (*NAVY, 255), 5); T(d, L, (66, 200), f"{shown}%", 66, 700, NAVY, "lm")
    if p_change > 0 and p_change < 1: d.rounded_rectangle((22, 142, w - 22, 258), 32, outline=(*GOLD, 255), width=8)
    col = GREEN if saved else NAVY
    rrect(d, (w - 330, 300, w - 30, 410), 50, (*col, 255)); T(d, L, (w - 180, 355), "Saved" if saved else "Save", 50, 700, CREAM, "mm")
    if save_pulse > 0 and not saved: d.rounded_rectangle((w - 342, 288, w - 18, 422), 58, outline=(*GOLD, int(255 * clamp(save_pulse))), width=8)
    return Img(im, L)

def vesting(stage, w=900, h=470):
    """Vesting timeline: stage 1 'immediately', 2 'after service years', 3 year-3 marker, 4 + Maya's 3 years."""
    im, d = card(w, h); L = []
    T(d, L, (34, 24), "Employer money becomes yours", 38, 600, MUTED, maxw=w - 68)
    x0, x1, y = 90, w - 90, 250; d.line((x0, y, x1, y), fill=(*NAVY, 255), width=8)
    for i in range(5):
        x = x0 + (x1 - x0) * i / 4; d.ellipse((x - 14, y - 14, x + 14, y + 14), fill=(*CREAM, 255), outline=(*NAVY, 255), width=5)
        T(d, L, (x, y + 52), "Start" if i == 0 else f"Year {i}", 36, 600, NAVY if i != 3 or stage >= 3 else MUTED, "mm")
    if stage == 1: rrect(d, (x0 - 60, 110, x0 + 180, 180), 30, (*SAGE, 255), (*NAVY, 4)); T(d, L, (x0 + 60, 145), "Immediately", 38, 700, NAVY, "mm")
    if stage == 2:
        for i in (1, 2, 3, 4):
            x = x0 + (x1 - x0) * i / 4; d.ellipse((x - 14, y - 14, x + 14, y + 14), fill=(*SAGE, 255), outline=(*NAVY, 255), width=5)
        T(d, L, (w // 2, 150), "Only after service years", 44, 700, NAVY, "mm", maxw=w - 80)
    if stage >= 3:
        x3 = x0 + (x1 - x0) * 3 / 4; d.ellipse((x3 - 24, y - 24, x3 + 24, y + 24), fill=(*GREEN, 255), outline=(*NAVY, 255), width=5)
        rrect(d, (x3 - 150, 120, x3 + 150, 185), 28, (*SAGE, 255), (*NAVY, 255), 4); T(d, L, (x3, 152), "100% vested", 38, 700, NAVY, "mm")
    if stage >= 4:
        rrect(d, (x3 - 200, 340, x3 + 200, 410), 30, (*GOLD, 255), (*NAVY, 255), 4); T(d, L, (x3, 375), "Maya: 3 years of service", 36, 700, NAVY, "mm", maxw=380)
    return Img(im, L)

def chips(items, hi=None, w=860, title=None):
    h = 120 + 100 * len(items) + (40 if title else 0)
    im, d = card(w, h); L = []
    if title: T(d, L, (34, 26), title, 36, 600, MUTED)
    for i, s in enumerate(items):
        y = (100 if title else 40) + 100 * i
        rrect(d, (28, y, w - 28, y + 84), 40, (*(SAGE if hi == i else CREAM), 255), (*NAVY, 255), 4); T(d, L, (w // 2, y + 42), s, 46, 700, NAVY, "mm", maxw=w - 100)
    return Img(im, L)

def trueup(stage, w=900, h=520):
    """Uneven contributions across the year; the true-up tops the match up. stage 0 bars, 1 top-up appears."""
    im, d = card(w, h); L = []
    T(d, L, (34, 24), "Contributions across the year", 36, 600, MUTED)
    vals = [60, 150, 20, 190, 40, 120]; bx = 70
    for i, v in enumerate(vals):
        x = bx + i * 130; d.rectangle((x, 420 - v * 1.5, x + 90, 420), fill=(*SAGE, 255), outline=(*NAVY, 255), width=4)
        if stage >= 1: d.rectangle((x, 420 - 190 * 1.5, x + 90, 420 - v * 1.5), fill=(*GOLD, 255), outline=(*NAVY, 255), width=3)
    T(d, L, (w // 2, 470), "True-up tops up the match" if stage >= 1 else "Uneven months", 38, 700, NAVY, "mm", maxw=w - 60)
    return Img(im, L)

def doc(title, lines, w=860):
    return note_card(title, lines, None, w)

def paystub(stage, w=860, h=470):
    """Next pay stub: the new 401(k) line is highlighted; stage 2 shows a slightly smaller paycheck."""
    im, d = card(w, h); L = []
    T(d, L, (34, 24), "Pay stub", 38, 600, MUTED)
    rows = [("Gross pay", ""), ("401(k) contribution", "4%"), ("Take-home", "a little smaller" if stage >= 2 else "")]
    for i, (a, b) in enumerate(rows):
        y = 100 + 105 * i; hi = (i == 1 and stage in (1, 2)) or (i == 2 and stage >= 2)
        rrect(d, (22, y, w - 22, y + 86), 26, (*(SAGE if hi else (255, 255, 255)), 255), (*NAVY, 255), 4)
        T(d, L, (50, y + 43), a, 44, 600, NAVY, "lm"); 
        if b: T(d, L, (w - 50, y + 43), b, 44, 700, NAVY, "rm", maxw=360)
    return Img(im, L)

def statement(stage, w=860, h=470):
    """401(k) statement: employer match arriving beside the employee contribution; stage 2 deposit bigger."""
    im, d = card(w, h); L = []
    T(d, L, (34, 24), "401(k) statement", 38, 600, MUTED)
    rows = [("Your contribution", ""), ("Employer match", "arrived"), ("Deposit", "bigger" if stage >= 2 else "")]
    for i, (a, b) in enumerate(rows):
        y = 100 + 105 * i; hi = (i == 1 and stage >= 1) or (i == 2 and stage >= 2)
        rrect(d, (22, y, w - 22, y + 86), 26, (*(SAGE if hi else (255, 255, 255)), 255), (*NAVY, 255), 4)
        T(d, L, (50, y + 43), a, 44, 600, NAVY, "lm")
        if b: T(d, L, (w - 50, y + 43), b, 44, 700, NAVY, "rm", maxw=300)
    return Img(im, L)

def streams(t, w=860, h=470):
    """Two money streams moving into the retirement account."""
    im, d = card(w, h); L = []
    for k, (lab, y, col) in enumerate((("You", 90, SAGE), ("Employer", 300, CREAM))):
        rrect(d, (30, y, 250, y + 90), 28, (*col, 255), (*NAVY, 255), 4); T(d, L, (140, y + 45), lab, 42, 700, NAVY, "mm")
        d.line((250, y + 45, 560, 235), fill=(*NAVY, 255), width=7)
        for j in range(3):
            p = ((t * 0.7 + j / 3 + k * 0.15) % 1.0); x, yy = 250 + 310 * p, y + 45 + (235 - y - 45) * p
            d.ellipse((x - 18, yy - 18, x + 18, yy + 18), fill=(*GOLD, 255), outline=(*NAVY, 255), width=3)
    rrect(d, (570, 160, w - 30, 320), 30, (255, 255, 255, 255), (*NAVY, 255), 5); T(d, L, ((570 + w - 30) // 2, 215), "401(k)", 52, 700, NAVY, "mm"); T(d, L, ((570 + w - 30) // 2, 275), "account", 36, 500, MUTED, "mm")
    return Img(im, L)

def calendar(years, label, stage, w=900, h=560):
    """Calendar of years: `years` ticks (3 already worked, or 10 more), each Year = $1,200 left unclaimed (stage shows the total)."""
    im, d = card(w, h); L = []
    T(d, L, (34, 24), label, 38, 600, MUTED, maxw=w - 68)
    cols = 5; n = years
    for i in range(n):
        r, c = divmod(i, cols); x = 40 + c * 168; y = 90 + r * 150
        rrect(d, (x, y, x + 150, y + 120), 22, (255, 255, 255, 255), (*SAGE, 255), 4); T(d, L, (x + 75, y + 60), f"Year {i + 1}", 36, 600, NAVY, "mm")
    return Img(im, L)

def cta(w=900, h=330):
    im, d = card(w, h, fill=SAGE); L = []
    T(d, L, (w // 2, 100), "Money Leak Audit Workbook", 56, 700, NAVY, "mm", maxw=w - 70); T(d, L, (w // 2, 190), "in the description", 46, 600, NAVY, "mm")
    T(d, L, (w // 2, 270), "Educational only, not financial advice", 38, 500, NAVY, "mm", maxw=w - 70)
    return Img(im, L)

def delete_card(p=0.0, w=700, h=230):
    im, d = card(w, h); L = []
    T(d, L, (34, 28), "HR message", 36, 600, MUTED)
    T(d, L, (34, 98), "Review your retirement contributions", 38, 600, NAVY, maxw=w - 68)
    rrect(d, (w - 250, 150, w - 34, 214), 28, (*RED, 255)); T(d, L, (w - 142, 182), "Delete", 38, 700, CREAM, "mm")
    if p > 0: d.rounded_rectangle((w - 262, 140, w - 22, 224), 34, outline=(*GOLD, int(255 * clamp(p))), width=7)
    return Img(im, L)

def notif_card(w=700, h=170):
    im, d = card(w, h); L = []
    d.ellipse((28, 34, 108, 114), fill=(*GOLD, 255)); T(d, L, (134, 52), "New message", 44, 700, NAVY); T(d, L, (134, 108), "HR", 40, 600, MUTED)
    return Img(im, L)
