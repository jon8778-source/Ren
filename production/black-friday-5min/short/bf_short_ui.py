"""Portrait (1080x1920) cards for the Black Friday Short, drawn in code. Fredoka; navy / sage / cream / gold / red. Every string >= 44 px at 1:1. Figures come from data/assumptions.csv (bf_ui.V).
Each builder returns pilot_ui.Img(im, texts) with texts = [(x0, y0, x1, y1, string, px)] relative to the card. Narrow cards (w <= 420) sit in the right column beside Ren; wide ones (w <= 828) are full-screen."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw
HERE = Path(__file__).resolve().parent; BF = HERE.parent
sys.path.insert(0, str(BF)); sys.path.insert(0, str(BF.parents[1] / "videos" / "unclaimed_401k")); sys.path.insert(0, str(BF.parents[1] / "videos" / "three_bills"))
import bf_ui as B
from pilot_ui import NAVY, SAGE, CREAM, GREEN, MUTED, GOLD, RED, font, txt, rrect, check, card, ease, back, clamp, Img
from tb_ui import _t
GOLDL = B.GOLDL; WHITE = (255, 255, 255); V = B.V; usd = B.usd
def _lines(d, L, cx, y, lines, px, wt=700, fill=NAVY, gap=1.18):
    for i, s in enumerate(lines): _t(d, L, (cx, y + int(i * px * gap)), s, px, wt, fill, "mm")
def sign(lines, w=420, tone="gold", px=56):
    fill = {"gold": GOLDL, "sage": SAGE, "cream": CREAM}[tone]; h = int(len(lines) * px * 1.2 + 70); im, d = card(w, h, fill=fill); L = []; _lines(d, L, w // 2, 35 + px // 2 + 4, lines, px); return Img(im, L)
def total(label, amount, colour=NAVY, w=420):
    im, d = card(w, 270, fill=CREAM); L = []; _t(d, L, (w // 2, 66), label, 50, 600, MUTED, "mm"); _t(d, L, (w // 2, 175), amount, 120, 700, colour, "mm"); return Img(im, L)
def apart(w=420):
    im, d = card(w, 520, fill=CREAM); L = []; _t(d, L, (w // 2, 60), "Plan A", 48, 600, MUTED, "mm"); _t(d, L, (w // 2, 140), usd(V["all_in"]), 104, 700, RED, "mm"); _t(d, L, (w // 2, 250), "Plan B", 48, 600, MUTED, "mm"); _t(d, L, (w // 2, 330), usd(V["rule_path"]), 104, 700, GREEN, "mm")
    rrect(d, (30, 405, w - 30, 490), 34, (*GOLDL, 255), (*NAVY, 255), 5); _t(d, L, (w // 2, 448), f"{usd(V['diff'])} apart", 56, 700, NAVY, "mm"); return Img(im, L)
def plans(w=760):
    im, d = card(w, 330, fill=CREAM); L = []
    for i, (a, b, col) in enumerate((("Plan A", "Impulse Alex", RED), ("Plan B", "Rule-following Alex", GREEN))):
        y = 28 + 150 * i; rrect(d, (24, y, w - 24, y + 130), 28, (*WHITE, 255), (*col, 255), 6); _t(d, L, (54, y + 42), a, 52, 700, col, "lm"); _t(d, L, (54, y + 94), b, 48, 600, NAVY, "lm")
    return Img(im, L)
def tag_flip(p, w=700):
    im = Image.new("RGBA", (w, 300), (0, 0, 0, 0)); d = ImageDraw.Draw(im); L = []; d.polygon([(110, 0), (w - 1, 0), (w - 1, 299), (110, 299), (0, 150)], fill=(*GOLDL, 255), outline=(*NAVY, 255), width=6); d.ellipse((72, 124, 116, 176), fill=(*CREAM, 255), outline=(*NAVY, 255), width=5)
    s = "Spending" if p < 0.5 else "Saving"; _t(d, L, (w // 2 + 60, 150), s, 104, 700, RED if p < 0.5 else GREEN, "mm"); return Img(im, L)
def clock(sec, w=780):
    im, d = card(w, 300, fill=(24, 36, 70)); L = []; s = max(0, sec); _t(d, L, (w // 2, 76), "Sale ends in", 54, 600, CREAM, "mm"); _t(d, L, (w // 2, 195), f"{s // 3600:02d}:{s % 3600 // 60:02d}:{s % 60:02d}", 124, 700, (255, 120, 110), "mm"); return Img(im, L)
def badge(text, w=780):
    im, d = card(w, 200, fill=(214, 40, 52)); L = []; _t(d, L, (w // 2, 102), text, 104, 700, CREAM, "mm"); return Img(im, L)
def saved(w=420, strike=0.0, q=False):
    im, d = card(w, 330, fill=GOLDL if not q else CREAM); L = []; _t(d, L, (w // 2, 70), "Store says" if not q else "Really?", 52, 600, NAVY, "mm"); b = _t(d, L, (w // 2, 170), usd(107), 120, 700, GREEN if not q else MUTED, "mm"); _t(d, L, (w // 2, 270), "saved" if not q else "saved?", 54, 700, NAVY, "mm")
    if q and strike > 0: d.line((b[0] - 10, 172, b[0] - 10 + (b[2] - b[0] + 20) * clamp(strike), 172), fill=(*RED, 255), width=11)
    return Img(im, L)
def parts(w=800):
    im, d = card(w, 470, fill=CREAM); L = []; _t(d, L, (w // 2, 64), "About to spend", 60, 700, MUTED, "mm"); cw = (w - 80) // 3
    for i, (lab, v) in enumerate((("Fryer", 48), ("Earbuds", 105), ("Bundle", 30))): cx = 40 + cw * i + cw // 2; _t(d, L, (cx, 160), lab, 48, 600, NAVY, "mm"); _t(d, L, (cx, 240), usd(v), 80, 700, NAVY, "mm")
    d.line((50, 310, w - 50, 310), fill=(*NAVY, 255), width=6); _t(d, L, (w // 2, 395), f"Total {usd(V['impulse'])}", 108, 700, RED, "mm"); return Img(im, L)
def rule(n, l1, l2, w=420):
    im, d = card(w, 330, fill=GOLDL); L = []; d.ellipse((w // 2 - 50, 22, w // 2 + 50, 122), fill=(*NAVY, 255)); _t(d, L, (w // 2, 74), str(n), 70, 700, CREAM, "mm"); _t(d, L, (w // 2, 164), f"RULE {n}", 46, 700, MUTED, "mm"); _t(d, L, (w // 2, 220), l1, 54, 700, NAVY, "mm"); _t(d, L, (w // 2, 280), l2, 54, 700, NAVY, "mm"); return Img(im, L)
def chip(lines, w=780, tone="gold", px=76): return sign(lines, w, tone, px)
def eq(w=828):
    im, d = card(w, 300, fill=CREAM); L = []; _t(d, L, (w // 2, 90), f"{usd(V['list_sale'])} + {usd(V['impulse'])}", 100, 700, NAVY, "mm"); _t(d, L, (w // 2, 215), f"= {usd(V['all_in'])}", 110, 700, RED, "mm"); return Img(im, L)
def bar(p, w=800):
    im, d = card(w, 470, fill=CREAM); L = []; _t(d, L, (w // 2, 64), "Budget", 60, 600, MUTED, "mm"); full = w - 100; bw = int(full * 300 / V["all_in"]); rrect(d, (50, 120, 50 + full, 210), 24, (*WHITE, 255), (*NAVY, 255), 5); q = clamp(p)
    rrect(d, (54, 124, 54 + int((bw - 8) * min(1, q * 1.5)), 206), 20, (*SAGE, 255)); over = int((full - bw) * clamp((q - 0.5) * 2))
    if over > 0: rrect(d, (50 + bw, 124, 50 + bw + over - 4, 206), 20, (214, 40, 52, 255))
    _t(d, L, (50 + bw // 2, 265), "Budget $300", 52, 700, NAVY, "mm"); _t(d, L, (w - 50, 265), "Cart $341", 52, 700, RED, "rm")
    if q > 0.8: rrect(d, (w // 2 - 190, 330, w // 2 + 190, 430), 40, (*GOLDL, 255), (*NAVY, 255), 5); _t(d, L, (w // 2, 380), f"{usd(V['all_in'] - 300)} over", 66, 700, RED, "mm")
    return Img(im, L)
def question(w=420):
    im, d = card(w, 360, fill=SAGE); L = []; _lines(d, L, w // 2, 70, ["Need it,", "or did the", "timer?"], 70); return Img(im, L)
def moon(p, w=780):
    im, d = card(w, 360, fill=CREAM); L = []; d.ellipse((120, 70, 280, 230), fill=(36, 48, 100, 255)); d.ellipse((170, 60, 310, 200), fill=(*CREAM, 255)); d.ellipse((520, 70, 680, 230), fill=(*GOLD, 255))
    d.polygon([(330, 150), (420, 150), (420, 120), (490, 160), (420, 205), (420, 175), (330, 175)], fill=(*NAVY, 255)); _t(d, L, (w // 2, 295), "Still want it tomorrow?", 56, 700, NAVY, "mm"); return Img(im, L)
def under(amount_label, amount, colour, w=420, px=50):
    im, d = card(w, 270, fill=CREAM); L = []; _t(d, L, (w // 2, 66), amount_label, px, 600, MUTED, "mm"); _t(d, L, (w // 2, 175), amount, 120, 700, colour, "mm"); return Img(im, L)
def end(w=420):
    im, d = card(w, 420, fill=GOLDL); L = []; _lines(d, L, w // 2, 70, ["Money Leak", "Audit", "Workbook"], 66); _t(d, L, (w // 2, 325), "See description", 50, 600, NAVY, "mm"); return Img(im, L)
