"""Portrait (1080x1920) cards for the 401(k) Short. Fredoka, navy / sage / cream. Every string is >= 42 px when drawn at 1:1.
Each builder returns pilot_ui.Img(im, texts) with texts = [(x0, y0, x1, y1, string, px)] relative to the card."""
import math, sys
from pathlib import Path
from PIL import Image, ImageDraw
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from pilot_ui import NAVY, SAGE, CREAM, GREEN, MUTED, GOLD, RED, font, txt, rrect, check, card, ease, back, clamp, Img, CLAIMS

def _t(d, L, xy, s, px, wt=700, fill=NAVY, anchor="la"):
    b = txt(d, xy, s, px, wt, fill, anchor); L.append((*b, s, px)); return b

def email_card(w=620):
    im, d = card(w, 250); L = []
    d.ellipse((26, 30, 106, 110), fill=(*GREEN, 255)); check(d, 66, 72, 22, CREAM, 9)
    _t(d, L, (128, 34), "Plan canceled", 48); _t(d, L, (128, 100), "Confirmation email", 42, 500, MUTED)
    _t(d, L, (30, 170), "Ends today", 46, 600)
    return Img(im, L)

def alert_card(w=660):
    im, d = card(w, 270); L = []
    d.ellipse((24, 26, 104, 106), fill=(*GOLD, 255)); d.polygon([(64, 40), (86, 92), (42, 92)], fill=(*NAVY, 255)); d.ellipse((57, 96, 71, 108), fill=(*NAVY, 255))
    _t(d, L, (128, 30), "Benefits alert", 50); _t(d, L, (30, 128), "Employer contribution", 48, 600); _t(d, L, (30, 192), "available", 48, 600)
    return Img(im, L)

def portal_card(label=None, p=1.0, w=828):
    h = 780; im, d = card(w, h); L = []
    d.rounded_rectangle((0, 0, w - 1, 100), 28, fill=(*NAVY, 255)); d.rectangle((0, 60, w - 1, 100), fill=(*NAVY, 255))
    _t(d, L, (w // 2, 52), "Benefits portal", 48, 700, CREAM, "mm")
    rrect(d, (28, 130, w - 28, 250), 26, (255, 255, 255, 255), (*SAGE, 255), 3)
    _t(d, L, (56, 190), "You contribute", 46, 500, MUTED, "lm"); _t(d, L, (w - 56, 190), "2%", 60, 700, NAVY, "rm")
    rrect(d, (28, 280, w - 28, h - 28), 26, (255, 255, 255, 255), (*SAGE, 255), 3)
    _t(d, L, (56, 340), "Employer match available", 46, 500, MUTED, "lm")
    if label and p > 0.02:
        lw, lh = w - 110, 220; lay = Image.new("RGBA", (lw, lh), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        rrect(ld, (0, 0, lw - 1, lh - 1), 44, (*SAGE, 255), (*NAVY, 255), 5); ld.text((lw // 2, lh // 2 + 2), label, font=font(104, 700), fill=NAVY, anchor="mm")
        s = max(0.05, p); lay = lay.resize((max(1, int(lw * s)), max(1, int(lh * s))), Image.LANCZOS)
        cx, cy = w // 2, 530; im.alpha_composite(lay, (cx - lay.width // 2, cy - lay.height // 2))
        if p > 0.95: L.append((cx - lw // 2 + 50, cy - 60, cx + lw // 2 - 50, cy + 60, label, 104))
    _t(d, L, (w // 2, h - 50), "Illustrative example", 42, 500, MUTED, "mm")
    return Img(im, L)

def flow_card(t, w=380, h=560):
    """Employer token travels into the 401(k) account (portrait: top to bottom)."""
    im, d = card(w, h); L = []
    rrect(d, (50, 30, w - 50, 130), 30, (*SAGE, 255), (*NAVY, 255), 4); _t(d, L, (w // 2, 80), "Employer", 46, 700, NAVY, "mm")
    rrect(d, (50, h - 160, w - 50, h - 30), 30, (255, 255, 255, 255), (*NAVY, 255), 4); _t(d, L, (w // 2, h - 120), "401(k)", 54, 700, NAVY, "mm"); _t(d, L, (w // 2, h - 68), "account", 42, 500, MUTED, "mm")
    a, b = (w // 2, 140), (w // 2, h - 175)
    d.line((*a, *b), fill=(*NAVY, 255), width=8); d.polygon([(b[0], b[1] + 18), (b[0] - 18, b[1] - 14), (b[0] + 18, b[1] - 14)], fill=(*NAVY, 255))
    p = ease(t)
    if 0 < t < 1.02:
        y = a[1] + (b[1] - a[1]) * p; d.ellipse((w // 2 - 30, y - 30, w // 2 + 30, y + 30), fill=(*GOLD, 255), outline=(*NAVY, 255), width=4); d.text((w // 2, y + 1), "$", font=font(34, 700), fill=NAVY, anchor="mm")
    return Img(im, L)

def field_card(p=0.0, w=600):
    im, d = card(w, 260, fill=(255, 255, 255)); L = []
    _t(d, L, (30, 24), "Contribution %", 46, 600, MUTED)
    rrect(d, (28, 104, w - 28, 224), 24, (*CREAM, 255), (*NAVY, 255), 4); _t(d, L, (66, 164), "2%", 72, 700, NAVY, "lm")
    if p > 0: d.rounded_rectangle((20, 96, w - 20, 232), 30, outline=(*GOLD, int(255 * clamp(p))), width=9)
    return Img(im, L)

def match_card(w=380):
    """Maya and Employer each put in $1,200 a year."""
    im, d = card(w, 470); L = []
    for k, (lab, col, y) in enumerate((("Maya", SAGE, 30), ("Employer", CREAM, 250))):
        rrect(d, (28, y, w - 28, y + 190), 30, (*col, 255), (*NAVY, 255), 4); _t(d, L, (w // 2, y + 55), lab, 50, 700, NAVY, "mm"); _t(d, L, (w // 2, y + 128), "$1,200 / yr", 50, 700, NAVY, "mm")
    return Img(im, L)

def half_card(stage, w=380):
    """Match meter: stage 0 half full ('getting'), stage 1 the missing half lit."""
    im, d = card(w, 560); L = []
    x0, x1, y0, y1 = 150, w - 150, 60, 380
    d.rectangle((x0, y0, x1, y1), fill=(255, 255, 255, 255), outline=(*NAVY, 255), width=5)
    ym = (y0 + y1) // 2
    d.rectangle((x0 + 3, ym, x1 - 3, y1 - 3), fill=(*SAGE, 255))
    if stage >= 1: d.rectangle((x0 + 3, y0 + 3, x1 - 3, ym - 3), fill=(*GOLD, 255))
    d.line((x0 - 14, ym, x1 + 14, ym), fill=(*NAVY, 255), width=4)
    _t(d, L, (w // 2, 440), "Missing half" if stage >= 1 else "Getting half", 46, 700, NAVY, "mm")
    _t(d, L, (w // 2, 504), "$1,200 / year", 46, 700, NAVY, "mm")
    return Img(im, L)

def big_card(label, value, w=828, tone="sage", vpx=110):
    h = 380; fill = {"sage": SAGE, "gold": (246, 222, 160), "cream": CREAM}[tone]
    im, d = card(w, h, fill=fill); L = []
    _t(d, L, (w // 2, 90), label, 50, 600, NAVY, "mm"); _t(d, L, (w // 2, 230), value, vpx, 700, NAVY, "mm")
    _t(d, L, (w // 2, h - 46), "Illustrative example", 42, 500, NAVY, "mm")
    return Img(im, L)

def years_card(n, w=828):
    """Ten more years of the missing $1,200: tiles 1..10 fill in."""
    im, d = card(w, 560); L = []
    _t(d, L, (w // 2, 56), "Ten more years", 54, 700, NAVY, "mm")
    for i in range(10):
        r, c = divmod(i, 5); x = 34 + c * 152; y = 120 + r * 190
        on = i < n; rrect(d, (x, y, x + 136, y + 170), 24, (*(SAGE if on else CREAM), 255), (*NAVY, 255), 4)
        _t(d, L, (x + 68, y + 66), str(i + 1), 62, 700, NAVY, "mm")
        if on: check(d, x + 68, y + 126, 22, GREEN, 8, p=clamp((n - i) * 1.0))
    return Img(im, L)

def chips(items, hi=None, w=828, title=None):
    h = 60 + 120 * len(items) + (80 if title else 0); im, d = card(w, h); L = []
    if title: _t(d, L, (w // 2, 56), title, 50, 700, NAVY, "mm")
    for i, s in enumerate(items):
        y = (110 if title else 30) + 120 * i
        rrect(d, (28, y, w - 28, y + 100), 46, (*(SAGE if hi == i else CREAM), 255), (*NAVY, 255), 4); _t(d, L, (w // 2, y + 50), s, 48, 700, NAVY, "mm")
    return Img(im, L)

def _wrap(d, text, px, wt, maxw):
    lines, cur = [], ""
    for w_ in text.split():
        t_ = (cur + " " + w_).strip()
        if d.textlength(t_, font=font(px, wt)) <= maxw or not cur: cur = t_
        else: lines.append(cur); cur = w_
    return lines + [cur]

def side_card(title, value, w=380, tone="sage", vpx=64):
    fill = {"sage": SAGE, "gold": (246, 222, 160), "cream": CREAM}[tone]
    d0 = ImageDraw.Draw(Image.new("RGBA", (4, 4))); tl = _wrap(d0, title, 46, 600, w - 50); vl = _wrap(d0, value, vpx, 700, w - 50)
    h = 50 + 58 * len(tl) + 30 + int(vpx * 1.2) * len(vl) + 30
    im, d = card(w, h, fill=fill); L = []; y = 40
    for s_ in tl: _t(d, L, (w // 2, y + 26), s_, 46, 600, NAVY, "mm"); y += 58
    y += 20
    for s_ in vl: _t(d, L, (w // 2, y + int(vpx * 0.6)), s_, vpx, 700, NAVY, "mm"); y += int(vpx * 1.2)
    return Img(im, L)

def cta_card(w=380):
    im, d = card(w, 470, fill=SAGE); L = []
    for i, s in enumerate(("Money Leak", "Audit Workbook", "in the", "description")): _t(d, L, (w // 2, 70 + 96 * i), s, 46, 700, NAVY, "mm")
    return Img(im, L)

def phone_screen(state, w=300, h=560):
    """Subscription app screen, drawn at 300x560 and warped onto the phone in the hand close-up. Returns (image, [(ui_box, string, nominal_px)])."""
    im = Image.new("RGBA", (w, h), (*CREAM, 255)); d = ImageDraw.Draw(im); L = []
    def T_(xy, s_, px, wt, fill, anchor):
        d.text(xy, s_, font=font(px, wt), fill=fill, anchor=anchor); L.append((d.textbbox(xy, s_, font=font(px, wt), anchor=anchor), s_, px))
    d.rectangle((0, 0, w, 64), fill=(*NAVY, 255)); T_((w // 2, 34), "My plans", 40, 600, CREAM, "mm")
    rrect(d, (14, 90, w - 14, 290), 18, (255, 255, 255, 255), (*SAGE, 255), 3)
    T_((28, 124), "Premium plan", 40, 600, NAVY, "lm"); T_((28, 190), f"${CLAIMS['subscription']} / month", 48, 700, NAVY, "lm")
    T_((28, 252), "Active" if state < 2 else "Ended", 40, 500, GREEN if state < 2 else RED, "lm")
    if state < 2:
        col = NAVY if state == 0 else (60, 80, 120); rrect(d, (14, 330, w - 14, 424), 46, (*col, 255)); T_((w // 2, 377), "Cancel plan", 40, 600, CREAM, "mm")
    else:
        rrect(d, (14, 330, w - 14, 440), 44, (*GREEN, 255)); check(d, 62, 385, 20, CREAM, 7); T_((100, 385), "Canceled", 40, 700, CREAM, "lm")
    return im, L
