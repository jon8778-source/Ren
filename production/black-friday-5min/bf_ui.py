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
