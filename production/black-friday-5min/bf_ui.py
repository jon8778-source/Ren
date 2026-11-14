"""Cards for the Black Friday long-form, drawn in code (Fredoka; navy / sage / cream / gold / red), 1920x1080 internal canvas. Every figure comes from data/assumptions.csv.
Each builder returns pilot_ui.Img(im, texts) with texts = [(x0, y0, x1, y1, string, px)] relative to the card. All text >= 44 px at 1080p."""
import csv, sys
from pathlib import Path
from PIL import Image, ImageDraw
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "videos" / "unclaimed_401k")); sys.path.insert(0, str(ROOT / "videos" / "three_bills"))
from pilot_ui import NAVY, SAGE, CREAM, GREEN, MUTED, GOLD, RED, font, txt, rrect, check, card, ease, back, clamp, Img
from tb_ui import _t
_a = {r["id"]: float(r["value"]) for r in csv.DictReader(open(HERE / "data" / "assumptions.csv"))}
def off(full, pct): return round(full * (1 - pct / 100), 2)
V = {"budget": int(_a["budget"]), "coat": off(_a["coat_full"], _a["coat_off"]), "gift": off(_a["gift_full"], _a["gift_off"]), "charger": off(_a["charger_full"], _a["charger_off"])}
V["list_sale"] = V["coat"] + V["gift"] + V["charger"]; V["airfryer"] = off(_a["airfryer_full"], _a["airfryer_off"]); V["earbuds"] = off(_a["earbuds_was"], _a["earbuds_off"]); V["bundle"] = off(_a["bundle_full"], _a["bundle_off"])
V["impulse"] = V["airfryer"] + V["earbuds"] + V["bundle"]; V["all_in"] = V["list_sale"] + V["impulse"]; V["rule_path"] = V["list_sale"] + V["earbuds"]; V["diff"] = V["all_in"] - V["rule_path"]
assert (V["list_sale"], V["impulse"], V["all_in"], V["rule_path"], V["diff"]) == (158, 183, 341, 263, 78) and V["diff"] == V["airfryer"] + V["bundle"]
def usd(x): return f"${int(round(x)):,}"
GOLDL = (246, 222, 160); WHITE = (255, 255, 255)
def title_card(top, big, sub=None, w=780, tone="sage"):
    h = 420 if sub else 360; fill = {"sage": SAGE, "cream": CREAM, "gold": GOLDL}[tone]; im, d = card(w, h, fill=fill); L = []
    _t(d, L, (w // 2, 100), top, 64, 600, NAVY, "mm"); _t(d, L, (w // 2, 230), big, 100, 700, NAVY, "mm")
    if sub: _t(d, L, (w // 2, 345), sub, 48, 500, NAVY, "mm")
    return Img(im, L)
def total_card(label, amount, colour=NAVY, w=720, sub=None):
    h = 330 if not sub else 400; im, d = card(w, h, fill=CREAM); L = []
    _t(d, L, (w // 2, 82), label, 56, 600, MUTED, "mm"); _t(d, L, (w // 2, 215), amount, 140, 700, colour, "mm")
    if sub: _t(d, L, (w // 2, 340), sub, 50, 600, NAVY, "mm")
    return Img(im, L)
def plans_card(p=1.0, w=860):
    im, d = card(w, 420, fill=CREAM); L = []; rows = [("Plan A", "Impulse Alex", RED), ("Plan B", "Rule-following Alex", GREEN)]
    for i, (a, b, col) in enumerate(rows):
        y = 40 + 180 * i; rrect(d, (30, y, w - 30, y + 150), 30, (*WHITE, 255), (*col, 255), 6); _t(d, L, (64, y + 52), a, 56, 700, col, "lm"); _t(d, L, (64, y + 112), b, 48, 600, NAVY, "lm")
    return Img(im, L)
def apart_card(p, w=980):
    im, d = card(w, 520, fill=CREAM); L = []
    _t(d, L, (w // 4, 70), "Plan A", 52, 600, MUTED, "mm"); _t(d, L, (3 * w // 4, 70), "Plan B", 52, 600, MUTED, "mm")
    _t(d, L, (w // 4, 190), usd(V["all_in"]), 130, 700, RED, "mm"); _t(d, L, (3 * w // 4, 190), usd(V["rule_path"]), 130, 700, GREEN, "mm")
    q = clamp(p); d.line((w // 4 - 120, 300, w // 4 - 120 + (3 * w // 4 + 120 - w // 4 + 120) * q, 300), fill=(*NAVY, 255), width=8)
    if q > 0.6: rrect(d, (w // 2 - 190, 340, w // 2 + 190, 460), 40, (*GOLDL, 255), (*NAVY, 255), 5); _t(d, L, (w // 2, 400), f"{usd(V['diff'])} apart", 64, 700, NAVY, "mm")
    return Img(im, L)
def rules_chip(n=5, w=760):
    im, d = card(w, 360, fill=GOLDL); L = []; _t(d, L, (w // 2, 100), "5 simple rules", 80, 700, NAVY, "mm")
    for i in range(5):
        cx = 100 + i * 140; col = NAVY if i < n else (200, 190, 150); d.ellipse((cx - 50, 200, cx + 50, 300), fill=(*col, 255)); _t(d, L, (cx, 252), str(i + 1), 60, 700, CREAM, "mm")
    return Img(im, L)
def never_card(p, w=900):
    im, d = card(w, 260, fill=CREAM); L = []; b = _t(d, L, (w // 2, 130), "Never buy anything", 84, 700, NAVY, "mm")
    q = clamp(p)
    if q > 0: d.line((b[0] - 20, 132, b[0] - 20 + (b[2] - b[0] + 40) * q, 132), fill=(*RED, 255), width=12)
    return Img(im, L)
def tag_flip(p, w=980):
    """A big price-tag shape; the label crossfades Spending -> Saving."""
    im = Image.new("RGBA", (w, 420), (0, 0, 0, 0)); d = ImageDraw.Draw(im); L = []
    d.polygon([(150, 0), (w - 1, 0), (w - 1, 419), (150, 419), (0, 210)], fill=(*GOLDL, 255), outline=(*NAVY, 255), width=7); d.ellipse((110, 180, 170, 240), fill=(*CREAM, 255), outline=(*NAVY, 255), width=6)
    s = "Spending" if p < 0.5 else "Saving"; col = RED if p < 0.5 else GREEN; _t(d, L, (w // 2 + 80, 210), s, 150, 700, col, "mm"); return Img(im, L)
def needs_card(k=0, w=700):
    im, d = card(w, 430, fill=CREAM); L = []; _t(d, L, (w // 2, 70), "Needs", 64, 700, NAVY, "mm"); d.line((40, 120, w - 40, 120), fill=(*GOLD, 255), width=6)
    for i in range(3):
        y = 175 + 80 * i; d.rounded_rectangle((50, y - 26, 102, y + 26), 10, outline=(*NAVY, 255), width=5); d.line((130, y + 30, w - 50, y + 30), fill=(*SAGE, 255), width=6)
    return Img(im, L)
def charger_card(w=760):
    im, d = card(w, 440, fill=CREAM); L = []; d.rounded_rectangle((110, 110, 230, 330), 22, fill=(*NAVY, 255)); d.rounded_rectangle((122, 128, 218, 300), 12, fill=(*SAGE, 255))
    d.line((230, 270, 330, 330, 430, 250, 560, 330), fill=(*NAVY, 255), width=9); d.rounded_rectangle((545, 300, 610, 360), 10, fill=(*NAVY, 255))
    _t(d, L, (w // 2, 70), "Charger", 60, 700, NAVY, "mm"); _t(d, L, (w // 2, 395), "Only at one angle", 54, 600, MUTED, "mm"); return Img(im, L)
def chip(label, w=800, tone="cream", px=60):
    fill = {"cream": CREAM, "sage": SAGE, "gold": GOLDL}[tone]; im, d = card(w, 160, fill=fill); L = []; _t(d, L, (w // 2, 82), label, px, 700, NAVY, "mm"); return Img(im, L)
def tick_chip(label, w=800):
    im, d = card(w, 170, fill=CREAM); L = []; check(d, 80, 88, 36, GREEN, 10); _t(d, L, (130, 88), label, 56, 700, NAVY, "lm"); return Img(im, L)
def decisions_card(w=1000):
    im, d = card(w, 280, fill=CREAM); L = []; rrect(d, (30, 70, 390, 210), 32, (*GOLDL, 255), (*NAVY, 255), 5); rrect(d, (590, 70, w - 30, 210), 32, (*SAGE, 255), (*NAVY, 255), 5)
    _t(d, L, (210, 140), "The sale", 58, 700, NAVY, "mm"); _t(d, L, ((590 + w - 30) // 2, 140), "Your choices", 56, 700, NAVY, "mm"); d.polygon([(420, 120), (500, 120), (500, 90), (565, 140), (500, 190), (500, 160), (420, 160)], fill=(*NAVY, 255)); return Img(im, L)

# ---- full-film cards (sections 3-8) ------------------------------------------------------------------------------------------------------
def rule_chip(n, text, w=980):
    im, d = card(w, 190, fill=GOLDL); L = []; d.ellipse((30, 35, 150, 155), fill=(*NAVY, 255)); _t(d, L, (90, 96), str(n), 80, 700, CREAM, "mm"); _t(d, L, (190, 70), f"RULE {n}", 46, 700, MUTED, "lm"); _t(d, L, (190, 130), text, 64, 700, NAVY, "lm"); return Img(im, L)
def price_tag(label, old, new, p=1.0, w=760):
    """Price tag: label, old price struck through (strike animates with p), new price."""
    im, d = card(w, 330, fill=CREAM); L = []; _t(d, L, (w // 2, 66), label, 58, 700, NAVY, "mm"); b = _t(d, L, (w // 3, 200), usd(old), 100, 700, MUTED, "mm"); q = clamp(p)
    d.line((b[0] - 10, 202, b[0] - 10 + (b[2] - b[0] + 20) * q, 202), fill=(*RED, 255), width=10); d.polygon([(w // 2 + 20, 175), (w // 2 + 90, 175), (w // 2 + 90, 150), (w // 2 + 150, 200), (w // 2 + 90, 250), (w // 2 + 90, 225), (w // 2 + 20, 225)], fill=(*NAVY, 255))
    if q > 0.8: _t(d, L, (w - 170, 200), usd(new), 110, 700, GREEN, "mm")
    return Img(im, L)
def tag_single(label, price, w=620):
    im, d = card(w, 300, fill=CREAM); L = []; _t(d, L, (w // 2, 70), label, 62, 700, NAVY, "mm"); _t(d, L, (w // 2, 195), usd(price), 120, 700, NAVY, "mm"); return Img(im, L)
def two_tags(a, b, w=820):
    im, d = card(w, 460, fill=CREAM); L = []
    for i, (lab, old, new) in enumerate((a, b)):
        y = 30 + 215 * i; rrect(d, (28, y, w - 28, y + 190), 28, (*WHITE, 255), (*SAGE, 255), 5); _t(d, L, (60, y + 55), lab, 54, 700, NAVY, "lm"); _t(d, L, (60, y + 135), usd(old), 64, 600, MUTED, "lm"); d.line((60, y + 138, 60 + 150, y + 138), fill=(*RED, 255), width=7)
        _t(d, L, (w - 70, y + 100), usd(new), 100, 700, GREEN, "rm")
    return Img(im, L)
def sum_card(sale, full, w=840):
    im, d = card(w, 420, fill=CREAM); L = []; _t(d, L, (w // 2, 70), "The whole list", 58, 600, MUTED, "mm"); _t(d, L, (60, 190), "On sale", 58, 600, NAVY, "lm"); _t(d, L, (w - 60, 190), usd(sale), 110, 700, GREEN, "rm"); _t(d, L, (60, 330), "Full price", 58, 600, NAVY, "lm"); _t(d, L, (w - 60, 330), usd(full), 100, 700, MUTED, "rm")
    d.line((60 + 330, 332, w - 60 - 250, 332), fill=(*RED, 255), width=7) if False else None; return Img(im, L)
def saved_badge(amount, label="saved", w=700):
    im, d = card(w, 260, fill=GOLDL); L = []; _t(d, L, (w // 2, 100), usd(amount), 130, 700, GREEN, "mm"); _t(d, L, (w // 2, 205), label, 64, 700, NAVY, "mm"); return Img(im, L)
def ticks_card(items, k=None, w=820):
    k = len(items) if k is None else k; im, d = card(w, 90 + 120 * len(items), fill=CREAM); L = []
    for i, s in enumerate(items):
        y = 70 + 120 * i; d.rounded_rectangle((40, y - 38, 116, y + 38), 14, outline=(*NAVY, 255), width=6)
        if i < k: check(d, 78, y + 2, 28, GREEN, 9)
        _t(d, L, (150, y), s, 66, 700, NAVY, "lm")
    return Img(im, L)
def clock_card(sec, w=760):
    im, d = card(w, 300, fill=(24, 36, 70)); L = []; s = max(0, sec); hh, mm, ss = s // 3600, s % 3600 // 60, s % 60; _t(d, L, (w // 2, 80), "Sale ends in", 56, 600, CREAM, "mm"); _t(d, L, (w // 2, 195), f"{hh:02d}:{mm:02d}:{ss:02d}", 130, 700, (255, 120, 110), "mm"); return Img(im, L)
def badge_red(text, w=760):
    im, d = card(w, 190, fill=(214, 40, 52)); L = []; _t(d, L, (w // 2, 98), text, 96, 700, CREAM, "mm"); return Img(im, L)
def counter_card(n, w=620):
    im, d = card(w, 280, fill=CREAM); L = []; _t(d, L, (w // 2, 70), "Cart", 60, 600, MUTED, "mm"); _t(d, L, (w // 2, 190), f"{n} items", 110, 700, NAVY, "mm"); return Img(im, L)
def banner(text, sub=None, w=900):
    im, d = card(w, 200 if not sub else 280, fill=GREEN); L = []; _t(d, L, (w // 2, 100), text, 92, 700, CREAM, "mm")
    if sub: _t(d, L, (w // 2, 215), sub, 54, 600, CREAM, "mm")
    return Img(im, L)
def parts_card(title, parts, total, colour=NAVY, w=900, strike=0.0):
    im, d = card(w, 440, fill=CREAM); L = []; _t(d, L, (w // 2, 64), title, 62, 700, MUTED, "mm"); x = 60; cw = (w - 120) // 3
    for i, (lab, v) in enumerate(parts): cx = 60 + cw * i + cw // 2; _t(d, L, (cx, 160), lab, 48, 600, NAVY, "mm"); _t(d, L, (cx, 235), usd(v), 80, 700, NAVY, "mm")
    d.line((60, 300, w - 60, 300), fill=(*NAVY, 255), width=6); b = _t(d, L, (w // 2, 375), f"Total {usd(total)}", 96, 700, colour, "mm")
    if strike > 0: d.line((b[0] - 15, 378, b[0] - 15 + (b[2] - b[0] + 30) * clamp(strike), 378), fill=(*RED, 255), width=11)
    return Img(im, L)
def email_card(text="Sale ends at midnight", w=900):
    im, d = card(w, 260, fill=CREAM); L = []; d.rounded_rectangle((40, 55, 200, 185), 16, outline=(*NAVY, 255), width=7); d.line((40, 60, 120, 125, 200, 60), fill=(*NAVY, 255), width=7); d.ellipse((176, 36, 218, 78), fill=(214, 40, 52, 255))
    _t(d, L, (250, 90), "New email", 50, 600, MUTED, "lm"); _t(d, L, (250, 175), text, 56, 700, NAVY, "lm"); return Img(im, L)
def equation_card(a, b, c, w=1000):
    im, d = card(w, 300, fill=CREAM); L = []; _t(d, L, (w // 2, 150), f"{usd(a)} + {usd(b)} = {usd(c)}", 108, 700, NAVY, "mm"); return Img(im, L)
def budget_bar(total, budget, w=1000, p=1.0):
    im, d = card(w, 440, fill=CREAM); L = []; _t(d, L, (w // 2, 66), "Budget", 58, 600, MUTED, "mm"); full = w - 120; bw = int(full * budget / (total * 1.0)); rrect(d, (60, 130, 60 + full, 220), 24, (*WHITE, 255), (*NAVY, 255), 5)
    q = clamp(p); rrect(d, (64, 134, 64 + int((bw - 8) * min(1, q * 1.4)), 216), 20, (*SAGE, 255)); over = int((full - bw) * clamp((q - 0.5) * 2))
    if over > 0: rrect(d, (60 + bw, 134, 60 + bw + over - 4, 216), 20, (214, 40, 52, 255))
    _t(d, L, (60 + bw // 2, 285), f"Budget {usd(budget)}", 56, 700, NAVY, "mm"); _t(d, L, (w - 40, 285), f"Cart {usd(total)}", 56, 700, RED, "rm")
    if q > 0.8: rrect(d, (w // 2 - 190, 330, w // 2 + 190, 415), 34, (*GOLDL, 255), (*NAVY, 255), 5); _t(d, L, (w // 2, 373), f"{usd(total - budget)} over", 64, 700, RED, "mm")
    return Img(im, L)
def history_card(was, usual, sale, p=1.0, w=1000):
    im, d = card(w, 560, fill=CREAM); L = []; _t(d, L, (w // 2, 60), "Price history", 58, 600, MUTED, "mm"); x0, x1, ytop, ybot = 120, w - 80, 130, 440
    def yy(v): return ybot - (v - 90) / (160 - 90) * (ybot - ytop)
    d.line((x0, ytop, x0, ybot, x1, ybot), fill=(*MUTED, 255), width=4); q = clamp(p); xe = x0 + (x1 - 120 - x0) * q
    d.line((x0, yy(usual), xe, yy(usual)), fill=(*NAVY, 255), width=9); _t(d, L, (x0 + 20, yy(usual) - 40), f"Usually {usd(usual)}", 52, 700, NAVY, "lm")
    if q > 0.95: d.line((x1 - 120, yy(sale) - 8, x1 - 70, yy(sale) - 8), fill=(*GREEN, 255), width=12); d.ellipse((x1 - 95, yy(sale) - 28, x1 - 55, yy(sale) + 12), fill=(*GREEN, 255)); _t(d, L, (x1 - 20, yy(sale) + 40), f"Sale {usd(sale)}", 52, 700, GREEN, "rm")
    return Img(im, L)
def real_card(real, adv, w=900):
    im, d = card(w, 330, fill=CREAM); L = []; _t(d, L, (w // 4 + 20, 80), "Real saving", 52, 600, MUTED, "mm"); _t(d, L, (w // 4 + 20, 210), usd(real), 130, 700, GREEN, "mm"); _t(d, L, (3 * w // 4, 80), "Advertised", 52, 600, MUTED, "mm"); b = _t(d, L, (3 * w // 4, 210), usd(adv), 120, 700, MUTED, "mm")
    d.line((b[0] - 10, 212, b[2] + 10, 212), fill=(*RED, 255), width=10); return Img(im, L)
def item_card(name, state=0, w=760):
    """state 0 plain, 1 ticked (keep), 2 crossed (remove), 3 question mark."""
    im, d = card(w, 260, fill=CREAM); L = []; b = _t(d, L, (w // 2, 130), name, 90, 700, NAVY, "mm")
    if state == 1: check(d, 90, 130, 44, GREEN, 12)
    if state == 2: d.line((b[0] - 20, 132, b[2] + 20, 132), fill=(214, 40, 52, 255), width=12)
    if state == 3: _t(d, L, (w - 100, 130), "?", 130, 700, GOLD, "mm")
    return Img(im, L)
def cart_items(items, states, w=900):
    im, d = card(w, 90 + 120 * len(items), fill=CREAM); L = []
    for i, (s, st) in enumerate(zip(items, states)):
        y = 70 + 120 * i; b = _t(d, L, (60, y), s, 68, 700, NAVY, "lm")
        if st == 1: check(d, w - 90, y, 34, GREEN, 10)
        if st == 2: d.line((b[0] - 15, y + 2, b[2] + 15, y + 2), fill=(214, 40, 52, 255), width=10)
    return Img(im, L)
def moon_sun(p, w=860):
    im, d = card(w, 330, fill=CREAM); L = []; q = ease(p); d.ellipse((140, 80, 300, 240), fill=(*(36, 48, 100), 255)); d.ellipse((190, 70, 330, 210), fill=(*CREAM, 255)); d.ellipse((560, 80, 720, 240), fill=(*GOLD, 255))
    d.polygon([(340, 160), (440, 160), (440, 130), (520, 175), (440, 220), (440, 190), (340, 190)], fill=(*NAVY, 255)); _t(d, L, (w // 2, 290), "Still want it in the morning?", 52, 700, NAVY, "mm"); return Img(im, L)
def tally_card(stage, w=1100):
    """stage 1: impulse $341 + $41 over; 2: rules path 158 + 105 = 263; 3: +$37 under; 4: $78 less."""
    im, d = card(w, 600, fill=CREAM); L = []; _t(d, L, (w // 4, 62), "Impulse Alex", 56, 700, RED, "mm"); _t(d, L, (3 * w // 4, 62), "Rule-following Alex", 56, 700, GREEN, "mm"); d.line((w // 2, 40, w // 2, 560), fill=(*MUTED, 255), width=4)
    _t(d, L, (w // 4, 190), usd(V["all_in"]), 130, 700, RED, "mm")
    if stage >= 2: _t(d, L, (3 * w // 4, 140), f"{usd(V['list_sale'])} + {usd(V['earbuds'])}", 70, 700, NAVY, "mm"); _t(d, L, (3 * w // 4, 245), usd(V["rule_path"]), 130, 700, GREEN, "mm")
    if stage >= 1: rrect(d, (w // 4 - 190, 300, w // 4 + 190, 385), 34, (*GOLDL, 255), (*NAVY, 255), 5); _t(d, L, (w // 4, 343), f"{usd(V['all_in'] - _a['budget'])} over", 60, 700, RED, "mm")
    if stage >= 3: rrect(d, (3 * w // 4 - 190, 330, 3 * w // 4 + 190, 415), 34, (*GOLDL, 255), (*NAVY, 255), 5); _t(d, L, (3 * w // 4, 373), f"{usd(_a['budget'] - V['rule_path'])} under", 60, 700, GREEN, "mm")
    if stage >= 4: rrect(d, (w // 2 - 330, 460, w // 2 + 330, 560), 40, (*GREEN, 255), (*NAVY, 255), 5); _t(d, L, (w // 2, 510), f"{usd(V['diff'])} less", 72, 700, CREAM, "mm")
    return Img(im, L)
def less_card(w=1000):
    im, d = card(w, 330, fill=CREAM); L = []; _t(d, L, (w // 2, 80), "The difference", 56, 600, MUTED, "mm"); _t(d, L, (w // 2, 210), f"{usd(V['airfryer'])} + {usd(V['bundle'])} = {usd(V['diff'])}", 120, 700, NAVY, "mm"); return Img(im, L)
def envelope_card(w=860):
    im, d = card(w, 330, fill=CREAM); L = []; d.rounded_rectangle((70, 80, 330, 240), 18, outline=(*NAVY, 255), width=8); d.line((70, 88, 200, 175, 330, 88), fill=(*NAVY, 255), width=8); _t(d, L, (w - 60, 160), "Room", 100, 700, GREEN, "rm"); return Img(im, L)
def transfer_card(p, w=980):
    im, d = card(w, 330, fill=CREAM); L = []; _t(d, L, (200, 120), usd(_a["budget"] - V["rule_path"]), 120, 700, GREEN, "mm"); q = clamp(p); d.line((360, 130, 360 + 280 * q, 130), fill=(*NAVY, 255), width=12)
    if q > 0.9: d.polygon([(640, 100), (700, 130), (640, 160)], fill=(*NAVY, 255))
    _t(d, L, (w - 190, 130), "Savings", 84, 700, NAVY, "mm"); _t(d, L, (w // 2, 260), "Straight away", 58, 600, MUTED, "mm"); return Img(im, L)
def recap_card(k, w=1000):
    items = ["List first", "Do the math", "Check the usual price", "Wait 24 hours", "Move what's left to savings"]; im, d = card(w, 90 + 100 * 5, fill=CREAM); L = []
    for i, s in enumerate(items):
        y = 75 + 100 * i; col = NAVY if i < k else (200, 190, 150); d.ellipse((40, y - 34, 108, y + 34), fill=(*col, 255)); _t(d, L, (74, y), str(i + 1), 46, 700, CREAM, "mm"); _t(d, L, (140, y), s, 56, 700, col, "lm")
    return Img(im, L)
def end_card(w=1000):
    px = 68 if w >= 1000 else 60; im, d = card(w, 360, fill=GOLDL); L = []; _t(d, L, (w // 2, 110), "Money Leak Audit Workbook", px, 700, NAVY, "mm"); _t(d, L, (w // 2, 230), "See the description", 70 if w >= 1000 else 60, 600, NAVY, "mm"); return Img(im, L)
def treat_card(w=1000):
    im, d = card(w, 330, fill=CREAM); L = []; rrect(d, (30, 70, 480, 250), 34, (*GREEN, 255), (*NAVY, 255), 5); rrect(d, (520, 70, w - 30, 250), 34, (200, 195, 170, 255), (*NAVY, 255), 5)
    _t(d, L, (255, 160), "Planned treat", 48, 700, CREAM, "mm"); _t(d, L, (760, 160), "Countdown pick", 48, 700, NAVY, "mm"); return Img(im, L)
def mini_icons(w=760):
    im, d = card(w, 300, fill=CREAM); L = []; rrect(d, (40, 60, 360, 240), 24, (24, 36, 70, 255)); _t(d, L, (200, 150), "02:59:59", 62, 700, (255, 120, 110), "mm"); rrect(d, (400, 60, w - 40, 240), 24, (214, 40, 52, 255)); _t(d, L, (580, 150), "3 left", 66, 700, CREAM, "mm"); return Img(im, L)

# every dollar figure that may appear on screen, derived from the checked table (QA rejects anything else)
ALLOWED = {int(v) for k, v in _a.items() if k.endswith(("_full", "_was", "_usual")) or k == "budget"} | {int(x) for x in V.values()} | {int(_a["airfryer_full"] - V["airfryer"]), int(_a["earbuds_was"] - V["earbuds"]), int(_a["bundle_full"] - V["bundle"]), int(_a["coat_full"] + _a["gift_full"] + _a["charger_full"]), int(V["list_sale"] + 0), int(_a["earbuds_usual"] - V["earbuds"]), int(V["all_in"] - _a["budget"]), int(_a["budget"] - V["rule_path"]), int(_a["airfryer_full"] - V["airfryer"] + _a["earbuds_was"] - V["earbuds"] + _a["bundle_full"] - V["bundle"])}
