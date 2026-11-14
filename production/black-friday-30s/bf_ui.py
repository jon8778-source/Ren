"""Cards for the Black Friday Short, drawn in code (Fredoka, navy / cream / gold / red). Every string >= 44 px at 1:1 (captions/rule tags >= 44, disclaimer 30-36).
Each builder returns pilot_ui.Img(im, texts) with texts = [(x0, y0, x1, y1, string, px)] relative to the card."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "videos" / "three_bills")); sys.path.insert(0, str(ROOT / "videos" / "unclaimed_401k")); sys.path.insert(0, str(ROOT / "videos" / "three_bills" / "short"))
from pilot_ui import NAVY, SAGE, CREAM, GREEN, MUTED, GOLD, RED, font, txt, rrect, check, card, ease, back, clamp, Img
from tb_ui import _t
import short_ui as SU
BF_RED = (214, 40, 52); PAPER = (255, 252, 240); GOLDL = (246, 222, 160)

def banner_p(text="BLACK FRIDAY", w=560, px=72):
    im = Image.new("RGBA", (w, px + 70), (0, 0, 0, 0)); d = ImageDraw.Draw(im); L = []; rrect(d, (0, 0, w - 1, px + 69), 24, (*BF_RED, 255), (*NAVY, 255), 5); _t(d, L, (w // 2, (px + 70) // 2 + 2), text, px, 700, CREAM, "mm"); return Img(im, L)
def badge_p(text, w=420, px=50, tone="red"):
    fill = BF_RED if tone == "red" else GOLDL; col = CREAM if tone == "red" else NAVY; im = Image.new("RGBA", (w, px + 50), (0, 0, 0, 0)); d = ImageDraw.Draw(im); L = []
    rrect(d, (0, 0, w - 1, px + 49), (px + 50) // 2, (*fill, 255), (*NAVY, 255), 5); _t(d, L, (w // 2, (px + 50) // 2 + 2), text, px, 700, col, "mm"); return Img(im, L)
def tag_p(text, w=300, px=52): return badge_p(text, w, px, "gold")
def phone_countdown_p(clock, w=520, h=700):
    return SU.phone_p([("title", "Doorbuster"), ("gap", 30), ("big", clock, BF_RED, 84), ("gap", 20), ("row", "Deal ends", "today", BF_RED)], w, h)
def notepad_p(items, shown, w=420, h=620, cross=None, cross_p=0.0, extra=None, extra_p=0.0):
    """Lined notepad: title 'My list', items typed in (shown = float count of characters/items revealed); optional extra unlisted line with a red cross."""
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im); L = []; rrect(d, (0, 14, w - 1, h - 1), 22, (*PAPER, 255), (*NAVY, 255), 5)
    for x in (60, 150, 240, 330): d.ellipse((x - 14, 0, x + 14, 28), fill=(*NAVY, 255))
    _t(d, L, (w // 2, 84), "My list", 52, 700, NAVY, "mm"); d.line((26, 124, w - 26, 124), fill=(*GOLD, 255), width=5); y = 150
    rows = list(items) + ([extra] if extra else [])
    for i, s in enumerate(rows):
        n = int(clamp(shown - i * 1.0) * len(s)) if i < len(items) else int(clamp(extra_p) * len(s)); vis = s[:n]
        if vis:
            if i < len(items): d.rounded_rectangle((34, y + 18, 70, y + 54), 8, outline=(*NAVY, 255), width=4)
            b = txt(d, (88, y + 36), vis, 46, 600, NAVY, "lm"); L.append((*b, vis, 46))
            if extra and i == len(rows) - 1 and cross_p > 0: x1 = 88 + (b[2] - b[0]) * clamp(cross_p); d.line((80, y + 36, x1, y + 36), fill=(*BF_RED, 255), width=9)
        y += 90
    return Img(im, L)
def calc_p(top, bottom, w=520, h=760, active=""):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im); L = []; rrect(d, (0, 0, w - 1, h - 1), 48, (*NAVY, 255), None)
    rrect(d, (28, 30, w - 29, 270), 22, (214, 232, 214, 255), (*MUTED, 255), 4); _t(d, L, (w - 52, 100), top, 58, 600, NAVY, "rm"); (_t(d, L, (w - 52, 200), bottom, 96, 700, NAVY, "rm") if bottom else None)
    for r in range(4):
        for c in range(4):
            x, y = 30 + c * 118, 300 + r * 112; rrect(d, (x, y, x + 100, y + 92), 20, (*(GOLD if c == 3 else CREAM), 255))
    return Img(im, L)
def pricetag_p(price, strike=False, p=1.0, w=330, h=250, new=None):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im); L = []; d.polygon([(0, 80), (60, 0), (w - 1, 0), (w - 1, h - 1), (60, h - 1), (0, h - 80)] if False else [(70, 0), (w - 1, 0), (w - 1, h - 1), (70, h - 1), (0, h // 2)], fill=(*GOLDL, 255), outline=(*NAVY, 255), width=5)
    d.ellipse((60, h // 2 - 14, 88, h // 2 + 14), fill=(*CREAM, 255), outline=(*NAVY, 255), width=4); b = txt(d, (w // 2 + 40, h // 2), price, 96, 700, NAVY, "mm"); L.append((*b, price, 96))
    if strike: x0, x1 = b[0] - 6, b[0] - 6 + (b[2] - b[0] + 12) * clamp(p); d.line((x0, h // 2, x1, h // 2), fill=(*BF_RED, 255), width=10)
    return Img(im, L)
def sign_p(text, w=420, tone="gold", px=54): return SU.sign_p(text, w, tone, px)
def cart_phone_p(clock, w=460, h=620):
    return SU.phone_p([("title", "Cart"), ("gap", 20), ("big", clock, NAVY, 92), ("gap", 10), ("row", "Waiting", "24h", GOLD)], w, h)
