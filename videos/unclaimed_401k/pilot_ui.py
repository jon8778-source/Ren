"""Code-drawn UI and graphics for the 401(k) pilot (Fredoka, navy / sage / cream). All numbers come from CLAIMS."""
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
ROOT = Path(__file__).resolve().parents[2]
FONTS = ROOT / "project" / "remotion" / "public" / "fonts"
NAVY, SAGE, CREAM, GREEN, MUTED = (19, 35, 63), (127, 160, 138), (251, 246, 234), (30, 158, 90), (122, 132, 150)
GOLD = (232, 176, 52)
RED = (196, 78, 58)
_f = {}
def font(px, weight=600):
    k = (px, weight)
    if k not in _f: _f[k] = ImageFont.truetype(str(FONTS / f"fredoka-latin-{weight}-normal.woff2"), px)
    return _f[k]
def ease(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def back(x):
    x = max(0.0, min(1.0, x)); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))

# --- the numbers that appear on screen (checked in qa_pilot.py) --------------------------------------------------------
CLAIMS = {"salary": 60000, "defer_pct": 2, "match_cap_pct": 4, "unclaimed_month": 100, "unclaimed_year": 1200, "subscription": 12, "age": 31, "years": 3}
assert CLAIMS["salary"] * CLAIMS["match_cap_pct"] / 100 - CLAIMS["salary"] * CLAIMS["defer_pct"] / 100 == CLAIMS["unclaimed_year"]
assert CLAIMS["unclaimed_year"] / 12 == CLAIMS["unclaimed_month"]

def txt(d, xy, s, px, weight=600, fill=NAVY, anchor="la"):
    d.text(xy, s, font=font(px, weight), fill=fill, anchor=anchor)
    b = d.textbbox(xy, s, font=font(px, weight), anchor=anchor)
    return b
def rrect(d, box, r, fill, outline=None, width=3):
    d.rounded_rectangle(box, r, fill=fill, outline=outline, width=width)
def shadowed(img, off=(0, 10), blur=14, alpha=70):
    sh = Image.new("RGBA", (img.width + 80, img.height + 80), (0, 0, 0, 0))
    a = img.getchannel("A").point(lambda v: int(v * alpha / 255))
    sh.paste(Image.new("RGBA", img.size, (*NAVY, 255)), (40 + off[0], 40 + off[1]), a)
    sh = sh.filter(ImageFilter.GaussianBlur(blur)); sh.alpha_composite(img, (40, 40)); return sh
def check(d, cx, cy, r, fill=GREEN, width=8, p=1.0):
    pts = [(cx - r * .9, cy), (cx - r * .25, cy + r * .65), (cx + r * .95, cy - r * .7)]
    segs = [(pts[0], pts[1]), (pts[1], pts[2])]
    tot = sum(math.dist(a, b) for a, b in segs); run = tot * clamp(p)
    for a, b in segs:
        L = math.dist(a, b); f = clamp(run / L); run -= L
        if f > 0: d.line((a[0], a[1], a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f), fill=fill, width=width, joint="curve")
        if run <= 0: break

def pill(frame, text, x, y, px=34, weight=600, fill=CREAM, colour=NAVY, alpha=1.0, boxes=None, pad=(26, 14), outline=None):
    if alpha <= 0: return None
    f = font(px, weight); d0 = ImageDraw.Draw(Image.new("RGBA", (4, 4)))
    b = d0.textbbox((0, 0), text, font=f); w, h = b[2] - b[0] + 2 * pad[0], b[3] - b[1] + 2 * pad[1]
    lay = Image.new("RGBA", frame.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((x + 3, y + 7, x + w + 3, y + h + 7), h // 2, fill=(*NAVY, 55))
    d.rounded_rectangle((x, y, x + w, y + h), h // 2, fill=(*fill, 255), outline=(*NAVY, 255) if outline else None, width=3)
    d.text((x + pad[0] - b[0], y + pad[1] - b[1]), text, font=f, fill=colour)
    if alpha < 1: lay.putalpha(lay.getchannel("A").point(lambda v: int(v * alpha)))
    frame.alpha_composite(lay)
    if boxes is not None and alpha > 0.5: boxes.append((x, y, x + w, y + h, text, px))
    return (x, y, x + w, y + h)

def card(w, h, title=None, tpx=34, fill=CREAM, border=NAVY):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    rrect(d, (0, 0, w - 1, h - 1), 28, (*fill, 255), (*border, 255), 4)
    if title: txt(d, (28, 22), title, tpx, 600, MUTED)
    return im, d

def put(frame, img, x, y, alpha=1.0, boxes=None, texts=None):
    """Alpha-composite img at integer (x, y) with an overall alpha; record its text boxes (relative -> absolute)."""
    if alpha <= 0: return
    if alpha < 1: img = img.copy(); img.putalpha(img.getchannel("A").point(lambda v: int(v * alpha)))
    frame.alpha_composite(img, (int(round(x)), int(round(y))))
    if boxes is not None and texts and alpha > 0.5:
        for (a, b, c, e, s, px) in texts: boxes.append((x + a, y + b, x + c, y + e, s, px))

# ---------------------------------------------------------------------------------------------------------------------
class Img:
    def __init__(self, im, texts=None): self.im, self.texts = im, texts or []

def portal(label, label_scale=1.0, icons=0.0, line_glow=0.0, plain=False, w=1500, h=860):
    """Benefits portal window. label: big sage label text. icons: 0..1 visibility of decorative 'trick' icons.
    plain=True shows only the plain benefits line (P11 end state)."""
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im); T = []
    def t(xy, s, px, wt=600, fill=NAVY, anchor="la"):
        b = txt(d, xy, s, px, wt, fill, anchor); T.append((*b, s, px)); return b
    rrect(d, (0, 0, w - 1, h - 1), 34, (*CREAM, 255), (*NAVY, 255), 5)
    d.rounded_rectangle((0, 0, w - 1, 92), 34, fill=(*NAVY, 255)); d.rectangle((0, 60, w - 1, 92), fill=(*NAVY, 255))
    for i, c in enumerate([(236, 112, 99), (232, 176, 52), (127, 190, 138)]): d.ellipse((38 + i * 44, 34, 62 + i * 44, 58), fill=c)
    t((w // 2, 46), "Employer Benefits Portal", 40, 600, CREAM, "mm")
    d.rectangle((0, 92, 330, h), fill=(*SAGE, 70))
    for i, (s, on) in enumerate([("Pay & taxes", 0), ("Benefits", 0), ("401(k)", 1), ("Documents", 0)]):
        y = 150 + i * 96
        if on: rrect(d, (22, y - 10, 308, y + 62), 24, (*NAVY, 255))
        t((54, y + 26), s, 38, 600, CREAM if on else NAVY, "lm")
    t((390, 140), "401(k) summary", 56, 600, NAVY)
    rrect(d, (390, 240, w - 50, 380), 26, (255, 255, 255, 255), (*SAGE, 255), 3)
    t((430, 310), "You contribute", 40, 500, MUTED, "lm"); t((w - 90, 310), f"{CLAIMS['defer_pct']}% of pay", 52, 600, NAVY, "rm")
    if not plain:
        rrect(d, (390, 410, w - 50, 790), 26, (255, 255, 255, 255), (*SAGE, 255), 3)
        t((430, 466), "Employer match available", 42, 500, MUTED, "lm")
        if label and label_scale > 0.02:
            lw, lh = 700, 190; lay = Image.new("RGBA", (lw, lh), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
            rrect(ld, (0, 0, lw - 1, lh - 1), 40, (*SAGE, 255), (*NAVY, 255), 5)
            ld.text((lw // 2, lh // 2 + 2), label, font=font(104, 700), fill=NAVY, anchor="mm")
            s = max(0.05, label_scale); lay = lay.resize((max(1, int(lw * s)), max(1, int(lh * s))), Image.LANCZOS)
            cx, cy = (390 + w - 50) // 2, 640
            im.alpha_composite(lay, (cx - lay.width // 2, cy - lay.height // 2))
            if label_scale > 0.9: T.append((cx - lw // 2, cy - lh // 2, cx + lw // 2, cy + lh // 2, label, 104))
        t((430, 756), "Illustrative example", 34, 500, MUTED, "lm")
    else:
        g = int(150 * line_glow)
        rrect(d, (390, 430, w - 50, 640), 30, (*SAGE, 255), (*NAVY, 255), 6)
        if g: d.rounded_rectangle((384, 424, w - 44, 646), 34, outline=(*GOLD, g), width=10)
        t((430, 500), "Employer contribution available", 46, 600, NAVY, "lm")
        t((430, 580), f"${CLAIMS['unclaimed_month']} / month", 76, 700, NAVY, "lm")
        t((430, 756), "Illustrative example", 34, 500, MUTED, "lm")
    if icons > 0.01:  # decorative "investment trick" icons that wipe away (own layer so alpha composites, not replaces)
        lay = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); a = int(255 * icons); k = 0.7
        for (cx, cy, kind) in [(1010, 175, "spark"), (1215, 178, "ball"), (1385, 182, "rocket"), (1330, 790, "spark")]:
            if kind == "spark":
                for r, c in ((46 * k, GOLD), (28 * k, CREAM)): d.polygon([(cx, cy - r), (cx + r * .3, cy - r * .3), (cx + r, cy), (cx + r * .3, cy + r * .3), (cx, cy + r), (cx - r * .3, cy + r * .3), (cx - r, cy), (cx - r * .3, cy - r * .3)], fill=(*c, a))
            elif kind == "ball":
                R = 62 * k; d.ellipse((cx - R, cy - R, cx + R, cy + R), fill=(*SAGE, a), outline=(*NAVY, a), width=4); d.ellipse((cx - 36 * k, cy - 44 * k, cx - 8 * k, cy - 18 * k), fill=(*CREAM, a))
                d.rectangle((cx - 50 * k, cy + 60 * k, cx + 50 * k, cy + 80 * k), fill=(*NAVY, a))
            else:
                d.polygon([(cx, cy - 66 * k), (cx + 30 * k, cy + 10 * k), (cx - 30 * k, cy + 10 * k)], fill=(*RED, a), outline=(*NAVY, a)); d.rectangle((cx - 20 * k, cy + 10 * k, cx + 20 * k, cy + 50 * k), fill=(*CREAM, a), outline=(*NAVY, a), width=3)
                d.polygon([(cx - 20 * k, cy + 50 * k), (cx, cy + 88 * k), (cx + 20 * k, cy + 50 * k)], fill=(*GOLD, a))
        im.alpha_composite(lay)
    return Img(im, T)

def phone_ui(state, w, h):
    """Subscription app screen. state: 0 normal, 1 pressed, 2 canceled."""
    im = Image.new("RGBA", (w, h), (*CREAM, 255)); d = ImageDraw.Draw(im); u = w / 300.0
    d.rectangle((0, 0, w, int(70 * u)), fill=(*NAVY, 255)); d.text((w // 2, int(36 * u)), "My plans", font=font(int(30 * u), 600), fill=CREAM, anchor="mm")
    rrect(d, (int(18 * u), int(100 * u), int(282 * u), int(250 * u)), int(18 * u), (255, 255, 255, 255), (*SAGE, 255), 3)
    d.text((int(36 * u), int(128 * u)), "Premium plan", font=font(int(26 * u), 600), fill=NAVY, anchor="lm")
    d.text((int(36 * u), int(186 * u)), f"${CLAIMS['subscription']} / month", font=font(int(40 * u), 700), fill=NAVY, anchor="lm")
    d.text((int(36 * u), int(228 * u)), "Active" if state < 2 else "Ends today", font=font(int(24 * u), 500), fill=GREEN if state < 2 else RED, anchor="lm")
    if state < 2:
        col = NAVY if state == 0 else (60, 80, 120)
        rrect(d, (int(18 * u), int(300 * u), int(282 * u), int(370 * u)), int(34 * u), (*col, 255))
        d.text((w // 2, int(336 * u)), "Cancel plan", font=font(int(30 * u), 600), fill=CREAM, anchor="mm")
        if state == 1: d.ellipse((int(240 * u), int(318 * u), int(262 * u), int(340 * u)), fill=(*CREAM, 120))
    else:
        rrect(d, (int(18 * u), int(300 * u), int(282 * u), int(396 * u)), int(26 * u), (*GREEN, 255))
        check(d, int(58 * u), int(348 * u), int(18 * u), CREAM, int(6 * u))
        d.text((int(96 * u), int(348 * u)), "Canceled", font=font(int(32 * u), 700), fill=CREAM, anchor="lm")
    return im

def email_card(w=760, h=240):
    im, d = card(w, h); T = []
    d.ellipse((30, 30, 102, 102), fill=(*GREEN, 255)); check(d, 66, 68, 20, CREAM, 8)
    T.append((*txt(d, (130, 42), "Subscription canceled", 44, 700, NAVY), "Subscription canceled", 44))
    T.append((*txt(d, (130, 108), "Confirmation email · just now", 34, 500, MUTED), "Confirmation email · just now", 34))
    T.append((*txt(d, (30, 170), "Your Premium plan ends today.", 38, 500, NAVY), "Your Premium plan ends today.", 38))
    return Img(im, T)

def alert_card(w=700, h=210):
    im, d = card(w, h, fill=(255, 255, 255), border=NAVY); T = []
    d.ellipse((28, 34, 108, 114), fill=(*GOLD, 255)); d.polygon([(68, 48), (88, 96), (48, 96)], fill=(*NAVY, 255)); d.ellipse((60, 100, 76, 112), fill=(*NAVY, 255))
    T.append((*txt(d, (136, 44), "Benefits alert", 46, 700, NAVY), "Benefits alert", 46))
    T.append((*txt(d, (136, 112), "Employer contribution available", 36, 500, NAVY), "Employer contribution available", 36))
    return Img(im, T)

def field_card(p=0.0, w=620, h=190):
    im, d = card(w, h, fill=(255, 255, 255)); T = []
    T.append((*txt(d, (28, 22), "Contribution %", 38, 600, MUTED), "Contribution %", 38))
    rrect(d, (28, 84, w - 28, 162), 20, (*CREAM, 255), (*NAVY, 255), 4)
    T.append((*txt(d, (60, 123), f"{CLAIMS['defer_pct']}%", 54, 700, NAVY, "lm"), f"{CLAIMS['defer_pct']}%", 54))
    if p > 0: d.rounded_rectangle((20, 76, w - 20, 170), 26, outline=(*GOLD, int(255 * clamp(p))), width=8)
    return Img(im, T)

def years_card(n, w=640, h=250):
    im, d = card(w, h); T = []
    T.append((*txt(d, (28, 20), "Years at the company", 36, 600, MUTED), "Years at the company", 36))
    for i in range(3):
        x = 38 + i * 196; rrect(d, (x, 84, x + 170, 218), 22, (255, 255, 255, 255), (*SAGE, 255), 4)
        T.append((*txt(d, (x + 85, 112), f"Year {i + 1}", 34, 600, NAVY, "mm"), f"Year {i + 1}", 34))
        if n > i: check(d, x + 85, 168, 26, GREEN, 9, p=clamp((n - i) * 1.0))
    return Img(im, T)

def flow_card(t, w=760, h=330):
    """Employer tag sends a token along an arrow into the 401(k) account tile."""
    im, d = card(w, h); T = []
    rrect(d, (28, 36, 258, 130), 30, (*SAGE, 255), (*NAVY, 255), 4)
    T.append((*txt(d, (143, 83), "Employer", 40, 700, NAVY, "mm"), "Employer", 40))
    rrect(d, (w - 330, 150, w - 28, 296), 30, (255, 255, 255, 255), (*NAVY, 255), 4)
    T.append((*txt(d, (w - 179, 205), "401(k)", 48, 700, NAVY, "mm"), "401(k)", 48))
    T.append((*txt(d, (w - 179, 258), "account", 36, 500, MUTED, "mm"), "account", 36))
    a = (150, 134); b = (w - 340, 224)
    d.line((*a, *b), fill=(*NAVY, 255), width=7); d.polygon([(b[0] + 18, b[1] + 2), (b[0] - 14, b[1] - 18), (b[0] - 14, b[1] + 22)], fill=(*NAVY, 255))
    p = ease(t); x, y = a[0] + (b[0] - a[0]) * p, a[1] + (b[1] - a[1]) * p
    if 0 < t < 1.02:
        d.ellipse((x - 26, y - 26, x + 26, y + 26), fill=(*GOLD, 255), outline=(*NAVY, 255), width=4)
        d.text((x, y + 1), "$", font=font(30, 700), fill=NAVY, anchor="mm")
    return Img(im, T)

def chips_card(w=700, h=210):
    im, d = card(w, h); T = []
    T.append((*txt(d, (32, 30), f"{CLAIMS['age']} years old", 52, 700, NAVY), f"{CLAIMS['age']} years old", 52))
    T.append((*txt(d, (32, 100), f"${CLAIMS['salary']:,} a year", 56, 700, NAVY), f"${CLAIMS['salary']:,} a year", 56))
    T.append((*txt(d, (32, 168), "Illustrative example", 34, 500, MUTED), "Illustrative example", 34))
    return Img(im, T)

def form_ui(w, h, tick=0.0):
    """Enrolment form (drawn flat, then warped onto the clipboard sheet). Boxes are on the right so the pen hand does not hide the labels."""
    im = Image.new("RGBA", (w, h), (255, 255, 255, 255)); d = ImageDraw.Draw(im); u = w / 600.0
    d.text((w // 2, int(130 * u)), "401(k) enrolment", font=font(int(46 * u), 700), fill=NAVY, anchor="mm")
    d.text((int(36 * u), int(200 * u)), "Choose your contribution", font=font(int(30 * u), 500), fill=MUTED, anchor="lm")
    for i, pct in enumerate([0, 2, 4]):
        y = int((250 + i * 110) * u)
        d.text((int(60 * u), y + int(34 * u)), f"{pct}%", font=font(int(52 * u), 700), fill=NAVY, anchor="lm")
        rrect(d, (int(440 * u), y, int(510 * u), y + int(68 * u)), int(10 * u), (255, 255, 255, 255), (*NAVY, 255), max(3, int(4 * u)))
        if pct == 2 and tick > 0: check(d, int(475 * u), y + int(38 * u), int(32 * u), GREEN, max(5, int(9 * u)), p=tick)
    return im

def line_card(w=760, h=200):
    im, d = card(w, h, fill=SAGE, border=NAVY); T = []
    T.append((*txt(d, (30, 26), "Employer contribution available", 40, 600, NAVY), "Employer contribution available", 40))
    T.append((*txt(d, (30, 96), f"${CLAIMS['unclaimed_month']} / month", 76, 700, NAVY), f"${CLAIMS['unclaimed_month']} / month", 76))
    d.rounded_rectangle((-6, -6, w + 5, h + 5), 34, outline=(*GOLD, 255), width=9)
    return Img(im, T)


def trick_panel(icons=1.0, glow=0.0, w=840, h=520):
    """Right-hand graphic for the 'not a secret trick' beat: decorative trick icons (on cream discs) fade away above the plain benefits line."""
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im); T = []
    a = int(255 * clamp(icons)); k = 1.0
    if a > 3:
        lay = Image.new("RGBA", (w, h), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        for cx, cy, kind in ((150, 120, "spark"), (w // 2, 120, "ball"), (w - 150, 120, "rocket")):
            ld.ellipse((cx - 100, cy - 100, cx + 100, cy + 100), fill=(*CREAM, a), outline=(*NAVY, a), width=5)
            if kind == "spark":
                for r, c in ((60, GOLD), (34, CREAM)): ld.polygon([(cx, cy - r), (cx + r * .3, cy - r * .3), (cx + r, cy), (cx + r * .3, cy + r * .3), (cx, cy + r), (cx - r * .3, cy + r * .3), (cx - r, cy), (cx - r * .3, cy - r * .3)], fill=(*c, a), outline=(*NAVY, a) if c == GOLD else None)
            elif kind == "ball":
                R = 48; ld.ellipse((cx - R, cy - R - 8, cx + R, cy + R - 8), fill=(*SAGE, a), outline=(*NAVY, a), width=5); ld.ellipse((cx - 26, cy - 44, cx - 6, cy - 24), fill=(*CREAM, a)); ld.rectangle((cx - 50, cy + R - 8, cx + 50, cy + R + 14), fill=(*NAVY, a))
            else:
                ld.polygon([(cx, cy - 62), (cx + 28, cy + 10), (cx - 28, cy + 10)], fill=(*RED, a), outline=(*NAVY, a)); ld.rectangle((cx - 18, cy + 10, cx + 18, cy + 50), fill=(*CREAM, a), outline=(*NAVY, a), width=4)
                ld.polygon([(cx - 18, cy + 50), (cx, cy + 84), (cx + 18, cy + 50)], fill=(*GOLD, a))
        im.alpha_composite(lay)
    rrect(d, (20, 280, w - 20, h - 20), 30, (*SAGE, 255), (*NAVY, 255), 5)
    T.append((*txt(d, (56, 320), "Employer contribution available", 44, 600, NAVY), "Employer contribution available", 44))
    T.append((*txt(d, (56, 396), f"${CLAIMS['unclaimed_month']} / month", 84, 700, NAVY), f"${CLAIMS['unclaimed_month']} / month", 84))
    if glow > 0: d.rounded_rectangle((12, 272, w - 12, h - 12), 36, outline=(*GOLD, int(255 * clamp(glow))), width=9)
    return Img(im, T)
