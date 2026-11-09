"""Three Bills in 30 Days: ~60 s pilot (script v2 paragraphs 0-9), 1920x1080, 24 fps, v3 / long-form baseline rules.

  project/.tools/venv/bin/python videos/three_bills/tb_render.py --plan                 # shot table + cap check
  project/.tools/venv/bin/python videos/three_bills/tb_render.py --stills OUT_DIR       # one still per shot midpoint
  project/.tools/venv/bin/python videos/three_bills/tb_render.py --out OUT_DIR --jobs 4 # render (local only, never committed)

Shot timing: each shot starts at the first narrated word of its phrase (Whisper words aligned to the script, voice/words_<sec>.json); the narration is joined
exactly as generated (H then L). No synthesis happens here. Maya: owner-approved pose cut-outs placed with ren_stage.stand (calibrated plate geometry, contact
shadow, sub-pixel paste). Ren: genuine library clips (pilot_ren.RenClip, native decode + matting). All text and numbers are drawn in code from production/assumptions.csv.
"""
import argparse, difflib, json, math, re, subprocess, sys, time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import numpy as np, soundfile as sf
from PIL import Image, ImageDraw, ImageFilter
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / "unclaimed_401k")); sys.path.insert(0, str(ROOT / "project" / "cliplib"))
import render_pilot as RP          # 401(k) pilot helpers: Boxes, slide_in, pop_in, blend constants
import pilot_ren as PR, pilot_ui as U, tb_ui as T
from ren_stage import stand, paste_smooth, contact_shadow, height_px

W, H, FPS = 1920, 1080, 24
ART = HERE / "art"; VOICE = HERE / "voice"; LIB = ROOT / "library" / "supporting_assets" / "backgrounds"
CAPS = {"CHARACTER_ACTION": 5.5, "REN_ANIMATED": 5.5, "STORY_STILL": 2.5, "GRAPHIC": 3.5}
BLEND = 3 / FPS
DISC = "Educational only, not financial advice. Illustrative story and figures."
ease, clamp = U.ease, U.clamp
SECS = ["H", "L"]
L_WORDS = 77          # the pilot uses the first 77 words of section L (script paragraphs 6-9 of the voice script, ending '... trying to catch up.'); the audio is cut after that sentence
TAIL = 0.25
TM = json.loads((VOICE / "timings.json").read_text()) if (VOICE / "timings.json").exists() else {}
FAKE = False
if not all(k in TM for k in SECS):        # layout tests before the narration exists: uniform 0.36 s/word, never used for a render
    _p = [" ".join(x.split()) for x in (HERE / "script" / "VOICE_SCRIPT.txt").read_text().strip().split("\n\n")]
    for _k, (_a, _b) in {"H": (0, 4), "L": (5, 9)}.items(): _t = " ".join(_p[_a:_b + 1]); TM[_k] = {"duration": 0.36 * len(_t.split()) + 0.3, "text": _t}
    FAKE = True

PLATE_FILE = {"LOT": "Office_parking_lot_car_16x9", "PORCH": "Porch_background_16x9", "OFFICE": "Office_background_16x9"}
# ---- plates and cameras --------------------------------------------------------------------------------------------------------
class Cam:
    """Plate (1672x941) -> frame (1920x1080) camera with zoom z about plate point (cx, cy); .k and .pt as ren_stage expects."""
    def __init__(self, z=1.0, cx=836, cy=470.5):
        self.z = max(1.0, z); self.cx = clamp(cx, 836 / self.z, 1672 - 836 / self.z); self.cy = clamp(cy, 470.5 / self.z, 941 - 470.5 / self.z); self.k = 1920 / 1672.0 * self.z   # the view never leaves the plate
    def pt(self, x, y): return ((x - self.cx) * self.k + 960, (y - self.cy) * self.k + 540)
_pl = {}
def plate(name, cam, blur=0, dark=0.0):
    if name not in _pl: _pl[name] = Image.open(LIB / f"{PLATE_FILE.get(name, name)}.png").convert("RGB") if name != "SAGE" else Image.open(ROOT / "videos" / "unclaimed_401k" / "art" / "plates" / "SAGE.png").convert("RGB")
    im = _pl[name]; sx = im.width / 1672.0; k = cam.k * (1 / sx) if False else cam.k
    a = 1.0 / (cam.k) * sx
    f = im.transform((W, H), Image.AFFINE, (a, 0, (cam.cx - 960 / cam.k) * sx, 0, a, (cam.cy - 540 / cam.k) * sx), Image.BICUBIC).convert("RGBA")
    if blur: f = f.filter(ImageFilter.GaussianBlur(blur))
    if dark: f.alpha_composite(Image.new("RGBA", f.size, (*U.NAVY, int(255 * dark))))
    return f
def veil(name, cam=None):
    """Soft backdrop for close-ups: the plate blurred under a cream veil (keeps the room's colours, no dark mud)."""
    f = plate(name, cam or Cam(1.0), blur=9); f.alpha_composite(Image.new("RGBA", f.size, (*U.CREAM, 120))); return f
GEOM = {"LOT": "LOT", "PORCH": "PORCH", "OFFICE": "OFFICE"}

# ---- Maya ------------------------------------------------------------------------------------------------------------------------
_maya = {}
def maya_img(key):
    if key not in _maya:
        im = Image.open(ART / "cast" / ({"neutral": "maya_01_neutral", "surprised": "maya_02_surprised_envelope", "worried": "maya_03_worried_phone", "relief": "maya_04_relief_phone"}[key] + ".png")).convert("RGBA")
        _maya[key] = im.crop(im.getbbox())
    return _maya[key]
MAYA_CM = 165
def maya(f, cam, plate_name, seq, t, x, y_feet, boxes=None):
    """Maya poses `seq` = [(t0, key)]: a 3-frame cross-fade between consecutive poses; standing on the plate at calibrated scale with a contact shadow."""
    idx = max(i for i, (t0, _) in enumerate(seq) if t >= t0 - 1e-9); cur = seq[idx][1]; a = (t - seq[idx][0]) / BLEND
    layers = [(seq[idx - 1][1], 1.0), (cur, clamp(a))] if idx > 0 and a < 1 else [(cur, 1.0)]
    RP.REC["poses"].extend([k for k, _ in layers])
    for key, al in layers:
        tgt = f if al >= 1 else Image.new("RGBA", f.size, (0, 0, 0, 0))
        r = stand(tgt, cam, GEOM[plate_name], maya_img(key), x, y_feet, None, cm=MAYA_CM, is_ren=False)
        if al < 1: tgt.putalpha(tgt.getchannel("A").point(lambda v: int(v * al))); f.alpha_composite(tgt)
    RP.REC["maya"] = (x, y_feet, r, plate_name, cam.k)
    return r

# ---- props -----------------------------------------------------------------------------------------------------------------------
_pr = {}
def prop(name):
    if name not in _pr: im = Image.open(ART / "props" / f"{name}.png").convert("RGBA"); _pr[name] = im.crop(im.getbbox())
    return _pr[name]
def put_prop(f, name, cx, cy, h, rot=0.0, alpha=1.0):
    im = prop(name); w = im.width * h / im.height; img = im.resize((max(1, int(w)), max(1, int(h))), Image.LANCZOS)
    if rot: img = img.rotate(rot, Image.BICUBIC, expand=True)
    if alpha < 1: img = img.copy(); img.putalpha(img.getchannel("A").point(lambda v: int(v * alpha)))
    f.alpha_composite(img, (int(cx - img.width / 2), int(cy - img.height / 2)))
    return (cx - img.width / 2, cy - img.height / 2, cx + img.width / 2, cy + img.height / 2)

# ---- shots ------------------------------------------------------------------------------------------------------------------------
SPEC = [
 # id, type, phrase
 ("S01", "REN_ANIMATED", "Three bills. Thirty days."),
 ("S02", "CHARACTER_ACTION", "First, Maya's car broke down."),
 ("S03", "GRAPHIC", "Then came an urgent dental bill."),
 ("S04", "CHARACTER_ACTION", "And just when she thought the month couldn't get worse,"),
 ("S05a", "STORY_STILL", "a pipe leaked"),
 ("S05b", "STORY_STILL", "beneath her kitchen sink."),
 ("S06", "REN_ANIMATED", "The total? Two thousand two hundred dollars."),
 ("S07a", "CHARACTER_ACTION", "Eighteen months earlier,"),
 ("S07b", "GRAPHIC", "one unexpected bill had pushed her into debt."),
 ("S08", "CHARACTER_ACTION", "This time, she handled all three."),
 ("S09a", "CHARACTER_ACTION", "But when Maya opened her savings app afterward,"),
 ("S09b", "CHARACTER_ACTION", "she didn't feel proud."),
 ("S10a", "GRAPHIC", "She saw how much her balance had fallen"),
 ("S10b", "CHARACTER_ACTION", "and thought, I've gone backwards."),
 ("S11", "REN_ANIMATED", "Here's why she hadn't."),
 ("S12", "CHARACTER_ACTION", "To understand that feeling, go back a year and a half."),
 ("S13", "GRAPHIC", "Maya was doing what so many budgets require:"),
 ("S13b", "CHARACTER_ACTION", "making the rent, groceries and gas stretch until payday."),
 ("S14", "CHARACTER_ACTION", "There wasn't much left between deposits."),
 ("S14b", "CHARACTER_ACTION", "Her savings balance was eighty dollars."),
 ("S15", "CHARACTER_ACTION", "Then a six-hundred-dollar car repair landed."),
 ("S16", "CHARACTER_ACTION", "She couldn't just make six hundred dollars appear. So she put the repair on a credit card,"),
 ("S17", "REN_ANIMATED", "postponed a dentist visit, and spent the next few months trying to catch up."),
]
REN = {"S01": ("ren_present_palm_left", 1.2, True), "S06": ("ren_shrug", 1.3, False), "S11": ("ren_point_right", 1.3, False), "S17": ("ren_thinking", 1.5, False)}
_rc = {}
def ren_clip(c):
    if c.sid not in _rc: _rc.clear(); clip, st, mir = REN[c.sid]; _rc[c.sid] = PR.RenClip(clip, st, c.d + 0.1, mirror=mir)
    return _rc[c.sid]

class Ctx:
    def __init__(self, sid, t, d, T_abs, f, B): self.sid, self.t, self.d, self.T, self.f, self.B = sid, t, d, T_abs, f, B
    def slide(self, img, x, y, t0=0.2, dur=0.4, frm=50): RP.slide_in(self.f, img, x, y, self.t, t0, dur=dur, frm=frm, B=self.B)
    def put(self, img, x, y, alpha=1.0, rec=True): U.put(self.f, img.im, x, y, alpha=alpha, boxes=self.B if rec else None, texts=img.texts)

def s_ren(c):
    f = plate("SAGE", Cam()); c.f.alpha_composite(f)
    rc = ren_clip(c); bx, i = rc.draw(c.f, c.t); c.B.ren, c.B.ren_i = bx, i
    panel = {"S01": lambda: T.title_card("3 bills", "30 days", "Illustrative story"), "S06": lambda: T.equation_card(), "S11": lambda: T.chip_card("Not backwards", 560, "gold", 60),
             "S17": lambda: T.chain(3)}[c.sid]()
    x = 1860 - panel.im.width; y = int(max(60, 520 - panel.im.height / 2))
    if c.sid == "S17":
        stage = 1 + int(c.t / max(c.d, 1e-6) * 3 - 1e-9); panel = T.chain(min(3, stage)); x = 1860 - panel.im.width; y = 300
    RP.slide_in(c.f, panel, x, y, c.t, 0.25, dur=0.0 if False else 0.45, frm=0, B=c.B)

def bg(name, cam, blur=0, dark=0.0): return plate(name, cam, blur, dark)

def s_s02(c):
    z = 1.0 + 0.10 * ease(c.t / c.d); cam = Cam(1.25 + 0.15 * ease(c.t / c.d), 700 + 60 * ease(c.t / c.d), 560); c.f.alpha_composite(plate("LOT", cam))
    maya(c.f, cam, "LOT", [(0, "neutral"), (0.9, "surprised")], c.t, 470, 800, c.B)
    # the car key: spins (ease-out) and stops
    p = ease(c.t / 1.6); ang = 720 * (1 - (1 - p) ** 3); put_prop(c.f, "car_key", 1560, 250, 210, rot=-ang + 20)
def s_s03(c):
    c.f.alpha_composite(veil("LOT"))
    p = ease(c.t / 0.5); inv = T.invoice("Dental bill", T.A["dental_bill"], urgent=c.t > 0.9)
    x = 960 - inv.im.width / 2 + 300 * (1 - p); c.put(inv, x, 190, alpha=min(1, p * 1.5))
def s_s04(c):
    cam = Cam(1.08 + 0.06 * ease(c.t / c.d), 640, 560); c.f.alpha_composite(plate("PORCH", cam))
    maya(c.f, cam, "PORCH", [(0, "worried"), (1.4, "neutral")], c.t, 620, 800, c.B)
def s_s15(c):
    cam = Cam(1.25 + 0.1 * ease(c.t / c.d), 700, 560); c.f.alpha_composite(plate("LOT", cam)); maya(c.f, cam, "LOT", [(0, "surprised")], c.t, 480, 800, c.B)
    c.slide(T.chip_card("Car repair " + T.usd(T.A["story_prev_repair"]), 640, "gold", 54), 1180, 160, 0.4)
def s_s16(c):
    cam = Cam(1.3, 720, 560); c.f.alpha_composite(plate("LOT", cam)); maya(c.f, cam, "LOT", [(0, "surprised"), (0.9, "worried")], c.t, 480, 800, c.B)
    c.slide(T.credit_card(), 1220, 260, 1.7)
# ---- revision 2: story interactions in place of abstract cutaways (shots S05a/b, S07a/b, S08-S10b, S12-S14b) -----------------------------
EVE = (40, 50, 110, 56)
def evening(f): f.alpha_composite(Image.new("RGBA", f.size, EVE))
class _FC:
    k = 1.0
    def pt(self, x, y): return (x, y)
def maya_free(f, seq, t, x, y_feet, hpx):
    """Maya on a coded floor (no plate perspective): pose cross-fade, scaled to `hpx`, contact shadow."""
    idx = max(i for i, (t0, _) in enumerate(seq) if t >= t0 - 1e-9); cur = seq[idx][1]; a = (t - seq[idx][0]) / BLEND
    layers = [(seq[idx - 1][1], 1.0), (cur, clamp(a))] if idx > 0 and a < 1 else [(cur, 1.0)]
    RP.REC["poses"].extend([k for k, _ in layers]); im0 = maya_img(cur); w = im0.width * hpx / im0.height
    contact_shadow(f, _FC(), x, y_feet, w * 0.95)
    for key, al in layers:
        im = maya_img(key); tgt = f if al >= 1 else Image.new("RGBA", f.size, (0, 0, 0, 0)); paste_smooth(tgt, im, x - im.width * hpx / im.height / 2, y_feet - hpx, im.width * hpx / im.height, hpx)
        if al < 1: tgt.putalpha(tgt.getchannel("A").point(lambda v: int(v * al))); f.alpha_composite(tgt)
    return (x - w / 2, y_feet - hpx, x + w / 2, y_feet)
_pipe = {}
def pipe_crop():
    if "p" not in _pipe: im = Image.open(ART / "props" / "leaking_pipe.png").convert("RGBA"); _pipe["p"] = im.crop((69, 79, 965, 625))   # the pipe without its baked-in drop (the drop is animated)
    return _pipe["p"]
def kitchen_set(f):
    d = ImageDraw.Draw(f); d.rectangle((0, 0, W, 700), fill=(244, 236, 222, 255)); d.rectangle((0, 700, W, H), fill=(196, 150, 112, 255))
    for x in range(-200, W + 300, 240): d.line((x, 700, x - 90, H), fill=(176, 130, 94, 255), width=3)
    d.line((0, 700, W, 700), fill=(150, 110, 80, 255), width=5)
def puddle(f, cx, cy, rx):
    if rx < 4: return
    lay = Image.new("RGBA", f.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay); ry = max(3, rx * 0.2)
    d.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=(150, 200, 222, 235), outline=(*U.NAVY, 200), width=3)
    d.ellipse((cx - rx * 0.55, cy - ry * 0.55, cx - rx * 0.1, cy - ry * 0.15), fill=(215, 238, 248, 220)); f.alpha_composite(lay)
def drip(f, x0, y0, y_floor, t, period=0.9, lead=0.15):
    """A drop forms at (x0, y0), falls under gravity to y_floor and splashes in a ring; repeating every `period` s."""
    ph = ((t + lead) % period) / period; d = ImageDraw.Draw(f)
    if ph < 0.38: r = 4 + 14 * ph / 0.38; d.ellipse((x0 - r * 0.7, y0 - r * 0.2, x0 + r * 0.7, y0 + r * 1.6), fill=(150, 200, 222, 255), outline=(*U.NAVY, 255), width=3)
    elif ph < 0.62:
        q = (ph - 0.38) / 0.24; y = y0 + (y_floor - y0) * q * q; d.ellipse((x0 - 11, y - 8, x0 + 11, y + 20), fill=(150, 200, 222, 255), outline=(*U.NAVY, 255), width=3)
    else:
        q = (ph - 0.62) / 0.38; rr = 10 + 70 * q; d.arc((x0 - rr, y_floor - rr * 0.22, x0 + rr, y_floor + rr * 0.22), 0, 360, fill=(*U.NAVY, int(255 * (1 - q))), width=4)

def s_s07a(c):
    cam = Cam(1.08 + 0.05 * ease(c.t / c.d), 620, 560); c.f.alpha_composite(plate("PORCH", cam))
    maya(c.f, cam, "PORCH", [(0, "worried")], c.t, 580, 800, c.B)
    c.slide(T.chip_card("18 months earlier", 560, "cream", 56), 1180, 150, 0.3)
def s_s07b(c):
    f = c.f; f.alpha_composite(veil("OFFICE")); d = ImageDraw.Draw(f); d.rectangle((0, 690, W, H), fill=(178, 124, 88, 255)); d.line((0, 690, W, 690), fill=(*U.NAVY, 255), width=6)
    for x in range(-100, W + 200, 260): d.line((x, 700, x - 60, H), fill=(160, 110, 78, 255), width=3)
    inv = T.invoice("Unexpected bill", None, False, 500, 640); q = clamp(c.t / 0.42); y = -660 + (150 + 660) * q * q
    if c.t > 0.42: y = 150 - 26 * math.sin(clamp((c.t - 0.42) / 0.22) * math.pi)
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).ellipse((520, 760, 1120, 840), fill=(*U.NAVY, int(60 * clamp(q)))); f.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
    rot = inv.im.rotate(-5, Image.BICUBIC, expand=True); f.alpha_composite(rot, (int(560 - 20), int(y)))
    if y > 60:
        for (a, b_, cc, e, s_, px) in inv.texts: c.B.append((540 + a, y + b_, 540 + cc, y + e, s_, px))      # text boxes only once the invoice is on screen
    cc_ = T.credit_card(560); p = ease((c.t - 0.9) / 0.35)
    if c.t >= 0.9:
        x = 1920 - (1920 - 880) * p; pop = 1 + 0.06 * math.sin(clamp((c.t - 1.25) / 0.2) * math.pi); im = cc_.im.resize((int(cc_.im.width * pop), int(cc_.im.height * pop)), Image.LANCZOS).rotate(7, Image.BICUBIC, expand=True)
        f.alpha_composite(im, (int(x), 430)); [c.B.append((x + a, 430 + b_, x + cc, 430 + e, s_, px)) for (a, b_, cc, e, s_, px) in cc_.texts if p > 0.95]
    if c.t >= 1.7:
        k = U.back((c.t - 1.7) / 0.3); st = T.chip_card("Debt", 300, "gold", 64).im; st2 = Image.new("RGBA", st.size, (0, 0, 0, 0))
        dd = ImageDraw.Draw(st2); U.rrect(dd, (0, 0, st.width - 1, st.height - 1), 40, (*U.RED, 255), (*U.NAVY, 255), 5); dd.text((st.width // 2, st.height // 2), "Debt", font=U.font(70, 700), fill=U.CREAM, anchor="mm")
        s_ = max(0.05, k); st2 = st2.resize((int(st2.width * s_), int(st2.height * s_)), Image.LANCZOS).rotate(-10, Image.BICUBIC, expand=True); f.alpha_composite(st2, (int(1300 - st2.width / 2), int(300 - st2.height / 2)))
        if k > 0.97: c.B.append((1300 - 90, 300 - 40, 1300 + 90, 300 + 40, "Debt", 70))
def s_s08(c):
    cam = Cam(1.1 + 0.05 * ease(c.t / c.d), 620, 560); c.f.alpha_composite(plate("PORCH", cam))
    maya(c.f, cam, "PORCH", [(0, "worried"), (0.9, "relief")], c.t, 600, 800, c.B)
    for i, (lab, icon) in enumerate((("Car", "car_key"), ("Dental", "blank_invoice"), ("Pipe", "leaking_pipe"))):
        tl = T.tile(lab, 500, 190); x, y = 1260, 170 + 230 * i; t0 = 0.15 + 0.15 * i; pr = ease((c.t - t0) / 0.35)
        if c.t < t0: continue
        tk = T.tick_on(tl, clamp((c.t - (0.5 + 0.55 * i)) / 0.35)); img = tk.im.copy(); ic = prop(icon) if icon != "leaking_pipe" else pipe_crop(); hh = 120; ww = ic.width * hh / ic.height
        if ww > 150: hh = int(120 * 150 / ww); ww = 150
        img.alpha_composite(ic.resize((max(1, int(ww)), hh), Image.LANCZOS), (int(110 - ww / 2 + (0 if i != 0 else 0)), 35)) if False else None
        # icon at the tile's left, tick over it once drawn
        base = tl.im.copy(); base.alpha_composite(ic.resize((max(1, int(ww)), hh), Image.LANCZOS), (int(110 - ww / 2), int(95 - hh / 2))); d_ = ImageDraw.Draw(base)
        p_ = clamp((c.t - (0.5 + 0.55 * i)) / 0.35)
        if p_ > 0: U.check(d_, 215, 100, 44, U.GREEN, 14, p=p_)
        im = F_img(base, tl.texts); RP.slide_in(c.f, im, x, y, c.t, t0, dur=0.35, frm=60, B=c.B)
def F_img(im, texts): return U.Img(im, texts)
def _glow(f, box, t):
    RP.REC["poses"].append("glow_overlay")        # a moving light overlay on Maya (counted as an overlay, not a pose, in the animation inventory)
    cx, cy = (box[0] + box[2]) / 2, box[1] + (box[3] - box[1]) * 0.33; a = 0.5 + 0.5 * math.sin(t * 2.4); lay = Image.new("RGBA", f.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for r_, al in ((260, 18), (170, 26), (90, 34)): d.ellipse((cx - r_, cy - r_, cx + r_, cy + r_), fill=(190, 215, 245, int(al * (0.6 + 0.4 * a))))
    f.alpha_composite(lay)
def s_s09a(c):
    cam = Cam(2.05, 760, 505); c.f.alpha_composite(plate("OFFICE", cam)); maya(c.f, cam, "OFFICE", [(0, "neutral"), (0.9, "worried")], c.t, 760, 820, c.B); evening(c.f)
def s_s09b(c):
    cam = Cam(1.25 + 0.05 * ease(c.t / c.d), 1180, 560); c.f.alpha_composite(plate("OFFICE", cam)); r = maya(c.f, cam, "OFFICE", [(0, "worried")], c.t, 1180, 820, c.B); evening(c.f); _glow(c.f, r, c.t)
def s_s10a(c):
    f = c.f; f.alpha_composite(veil("OFFICE")); evening(f); img = T.balance_steps(c.t); p = ease(c.t / 0.35)
    c.put(img, 690, 70 + int(120 * (1 - p)), alpha=min(1, p * 1.5))
def s_s10b(c):
    cam = Cam(2.05, 900, 505); c.f.alpha_composite(plate("OFFICE", cam)); maya(c.f, cam, "OFFICE", [(0, "worried")], c.t, 900, 820, c.B); evening(c.f)
    c.slide(T.bubble("I've gone backwards", 700), 1000, 230, 0.35)
def s_s12(c):
    cam = Cam(1.12, 640, 560); c.f.alpha_composite(plate("PORCH", cam)); maya(c.f, cam, "PORCH", [(0, "relief"), (1.0, "neutral")], c.t, 560, 800, c.B)
    labs = ["Today", "6 months earlier", "12 months earlier", "18 months earlier"]; x, y = 1130, 240; t0, step = 0.3, 0.5
    k = min(2, max(0, int((c.t - t0) / step))) if c.t >= t0 else -1
    if c.t < t0: pages = [(labs[0], 1.0)]
    elif c.t >= t0 + 3 * step: pages = [(labs[3], 1.0)]
    else:
        ph = clamp((c.t - t0 - k * step) / step); pages = [(labs[k + 1], 1.0), (labs[k], math.cos(ph * math.pi / 2))]
    for lab, sy in pages:
        img = T.calendar_card(lab, None, w=620)
        if sy >= 0.999: c.put(img, x, y)
        elif sy > 0.02: im = img.im.resize((img.im.width, max(2, int(img.im.height * sy))), Image.BILINEAR); c.f.alpha_composite(im, (x, y))
def envelope(f, cx, cy, h, bills, rise=1.0):
    im = prop("savings_envelope"); w = im.width * h / im.height
    for i in range(bills):
        b = T.bill().rotate((-10, 4, 12)[i], Image.BICUBIC, expand=True); f.alpha_composite(b, (int(cx - b.width / 2 + (-40, 10, 50)[i]), int(cy - h / 2 - 95 * rise - 22 * i)))
    f.alpha_composite(im.resize((int(w), int(h)), Image.LANCZOS), (int(cx - w / 2), int(cy - h / 2)))
def s_s13(c):
    f = c.f; f.alpha_composite(veil("OFFICE")); envelope(f, 960, 620, 520, 3, ease(c.t / 0.7))
    c.slide(T.chip_card("Payday", 420, "sage", 64), 740, 120, 0.2, frm=0)
def s_s13b(c):
    cam = Cam(1.5, 870, 620); c.f.alpha_composite(plate("OFFICE", cam)); maya(c.f, cam, "OFFICE", [(0, "neutral"), (1.6, "worried")], c.t, 760, 820, c.B)
    marks = (0.6, 1.7, 2.8); gone = sum(1 for m in marks if c.t >= m + 0.4); envelope(c.f, 1480, 760, 380, 3 - gone)
    for i, lab in enumerate(("Rent", "Groceries", "Gas")):
        if c.t < marks[i]: continue
        p = ease((c.t - marks[i]) / 0.5); x = 1480 + 60 - 300 * p + 0 ; y = 560 - 90 * i - 80 * p
        ch = T.chip_card(lab, 360, "cream", 54); a = 1.0; c.put(ch, 1250 - 40 * (i == 1) + 220 * (1 - p), 150 + 150 * i - 0 * p, alpha=min(1, p * 2))
def s_s14(c):
    cam = Cam(2.05, 860, 505); c.f.alpha_composite(plate("OFFICE", cam)); maya(c.f, cam, "OFFICE", [(0, "worried")], c.t, 860, 820, c.B)
    p = ease(c.t / 0.4); envelope(c.f, 1620, 1000 - int(190 * p), 340, 0); c.slide(T.chip_card("Between deposits", 560, "cream", 54), 1180, 190, 0.3, frm=40)
def s_s14b(c):
    cam = Cam(1.3, 900, 560); c.f.alpha_composite(plate("OFFICE", cam)); maya(c.f, cam, "OFFICE", [(0, "worried")], c.t, 700, 820, c.B)
    img = T.phone_inset(T.A["story_prev_savings"], "Eighty dollars", 460, 720); p = ease(c.t / 0.4); c.put(img, 1240, int(1080 - 880 * p), rec=p > 0.99)

# ---- S05a/b: the owner-supplied sink-leak illustration (art/plates/kitchen_leak_ref.png, received 9 Nov 2026) ------------------------------
# Only the pipe, sink, bucket and cabinet area (x >= 790) is used: the woman at the left of the image is NOT the approved Maya design and is cropped out.
_kit = {}
def kit():
    if "k" not in _kit: _kit["k"] = Image.open(ART / "plates" / "kitchen_leak_ref.png").convert("RGB")
    return _kit["k"]
def kit_view(box):
    """Frame (1920x1080) showing image box (x0, y0, x1, y1) at full height; the sides are filled with a blurred, darkened enlargement of the same crop."""
    x0, y0, x1, y1 = box; k = kit(); s = H / (y1 - y0); w = (x1 - x0) * s
    big = max(W / (x1 - x0), H / (y1 - y0)); cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    bg = k.transform((W, H), Image.AFFINE, (1 / big, 0, cx - W / 2 / big, 0, 1 / big, cy - H / 2 / big), Image.BICUBIC).filter(ImageFilter.GaussianBlur(24)).convert("RGBA")
    bg.alpha_composite(Image.new("RGBA", (W, H), (*U.NAVY, 90)))
    fg = k.transform((int(round(w)), H), Image.AFFINE, ((x1 - x0) / round(w), 0, x0, 0, (y1 - y0) / H, y0), Image.BICUBIC).convert("RGBA")
    bg.alpha_composite(fg, (int((W - round(w)) / 2), 0)); ox = (W - round(w)) / 2
    return bg, (lambda x, y: ((x - x0) * s + ox, (y - y0) * s)), s
def _lerp_box(a, b, p): return tuple(a[i] + (b[i] - a[i]) * p for i in range(4))
def kit_drip(f, m, s, t, period=0.6, lead=0.1):
    """Animated drop from the pipe (image x 1163, y 530) into the bucket (water at y ~710) with an expanding ripple; drawn over the artwork."""
    ph = ((t + lead) % period) / period; d = ImageDraw.Draw(f); X = 1163
    if ph < 0.7:
        q = ph / 0.7; y = 535 + (708 - 535) * q * q; fx, fy = m(X, y); r = 7 * s
        d.ellipse((fx - r * 0.6, fy - r * 1.1, fx + r * 0.6, fy + r * 1.1), fill=(205, 232, 246, 235), outline=(60, 90, 130, 255), width=2); d.ellipse((fx - r * 0.2, fy - r * 0.6, fx + r * 0.05, fy - r * 0.1), fill=(255, 255, 255, 240))
    else:
        q = (ph - 0.7) / 0.3; fx, fy = m(X, 711); rr = (8 + 70 * q) * s
        d.ellipse((fx - rr, fy - rr * 0.22, fx + rr, fy + rr * 0.22), outline=(220, 238, 250, int(240 * (1 - q))), width=max(2, int(3 * s)))
BOX_A = (780, 232, 1672, 734); BOX_B = (800, 262, 1650, 740); BOX_C = (780, 0, 1672, 941)     # A and B are full-width 16:9 crops (about 2.1x enlargement); C is the whole right half (sink, pipe, bucket)
def s_s05a(c):
    f, m, s = kit_view(_lerp_box(BOX_A, BOX_B, ease(c.t / max(c.d, 1e-6)))); c.f.alpha_composite(f); kit_drip(c.f, m, s, c.t)
def s_s05b(c):
    f, m, s = kit_view(_lerp_box(BOX_B, BOX_C, ease(c.t / max(c.d, 1e-6)))); c.f.alpha_composite(f); kit_drip(c.f, m, s, c.t + 0.3)

FN = {"S01": s_ren, "S02": s_s02, "S03": s_s03, "S04": s_s04, "S05a": s_s05a, "S05b": s_s05b, "S06": s_ren, "S07a": s_s07a, "S07b": s_s07b, "S08": s_s08, "S09a": s_s09a, "S09b": s_s09b,
      "S10a": s_s10a, "S10b": s_s10b, "S11": s_ren, "S12": s_s12, "S13": s_s13, "S13b": s_s13b, "S14": s_s14, "S14b": s_s14b, "S15": s_s15, "S16": s_s16, "S17": s_ren}

# ---- timing from the real narration ------------------------------------------------------------------------------------------------
def aligned_word_times(sec):
    text = TM[sec]["text"].split()
    if FAKE: return [(0.36 * i, 0.36 * i + 0.3) for i in range(len(text))]
    words = json.loads((VOICE / f"words_{sec}.json").read_text())
    def toks(s): return [t for t in re.findall(r"[a-z0-9']+", s.lower().replace("’", "'").replace("-", " ").replace(",", "").replace("$", " $ ")) if t != "and"]
    st, sidx = [], []
    for i, w in enumerate(text):
        for t in toks(w) or ["."]: st.append(t); sidx.append(i)
    wt, widx = [], []
    for j, w in enumerate(words):
        for t in toks(w["word"]) or ["."]: wt.append(t); widx.append(j)
    sm = difflib.SequenceMatcher(None, st, wt, autojunk=False); start = [None] * len(text); end = [None] * len(text)
    for blk in sm.get_matching_blocks():
        for k in range(blk.size):
            i, j = sidx[blk.a + k], widx[blk.b + k]
            if start[i] is None: start[i] = words[j]["start"]
            end[i] = words[j]["end"]
    known = [i for i, v in enumerate(start) if v is not None]
    for i in range(len(text)):
        if start[i] is None:
            lo = max([k for k in known if k < i], default=None); hi = min([k for k in known if k > i], default=None)
            a = end[lo] if lo is not None else 0.0; b = start[hi] if hi is not None else words[-1]["end"]
            n_lo = lo if lo is not None else -1; n_hi = hi if hi is not None else len(text); frac = (i - n_lo) / (n_hi - n_lo)
            start[i] = a + (b - a) * (frac - 0.5 / (n_hi - n_lo)); end[i] = a + (b - a) * frac
    return list(zip(start, end))

def l_cut(al):
    """Seconds of L.wav kept: to the end of word L_WORDS plus the original audio's next 0.25 s (never past the next word's start)."""
    end = al["L"][L_WORDS - 1][1]; nxt = al["L"][L_WORDS][0] - 0.03 if len(al["L"]) > L_WORDS else TM["L"]["duration"]
    return min(end + TAIL, nxt, TM["L"]["duration"])

def build_shots():
    text = {s: TM[s]["text"].split() for s in SECS}; al = {s: aligned_word_times(s) for s in SECS}
    text["L"] = text["L"][:L_WORDS]
    dur = dict((s, TM[s]["duration"]) for s in SECS); dur["L"] = l_cut(al)
    offs, o = {}, 0.0
    for s in SECS: offs[s] = o; o += dur[s]
    total = o
    allw = [(s, i) for s in SECS for i in range(len(text[s]))]; pos = 0; shots = []
    for sid, typ, phrase in SPEC:
        ph = phrase.split(); seg = allw[pos:pos + len(ph)]; got = [text[s][i] for s, i in seg]; assert got == ph, (sid, got, ph); pos += len(ph)
        s0, i0 = seg[0]; shots.append(dict(id=sid, type=typ, phrase=phrase, a=0.0 if pos == len(ph) else offs[s0] + al[s0][i0][0]))
    assert pos == len(allw)
    for k, s in enumerate(shots):
        s["b"] = shots[k + 1]["a"] if k + 1 < len(shots) else total
        s["fa"] = 0 if k == 0 else round(s["a"] * FPS); s["fb"] = round(s["b"] * FPS) if k + 1 < len(shots) else int(math.ceil(total * FPS - 1e-6))
    for k, s in enumerate(shots[:-1]): assert shots[k + 1]["fa"] == s["fb"]
    return shots, total

SHOTS = None; TOTAL = 0.0
def init():
    global SHOTS, TOTAL
    if SHOTS is None: SHOTS, TOTAL = build_shots()
def frame_at(i):
    init(); s = next(x for x in SHOTS if x["fa"] <= i < x["fb"]); t = (i - s["fa"]) / FPS; d = (s["fb"] - s["fa"]) / FPS; B = RP.Boxes()
    f = Image.new("RGBA", (W, H)); RP.REC["poses"] = []; RP.REC["maya"] = None; c = Ctx(s["id"], t, d, i / FPS, f, B)
    FN[s["id"]](c); B.poses = list(RP.REC["poses"]); B.maya = RP.REC["maya"]; T_ = i / FPS
    dw = ImageDraw.Draw(Image.new("RGBA", (4, 4))).textbbox((0, 0), DISC, font=U.font(32, 500)); wpx = dw[2] - dw[0] + 44       # right-aligned, clear of Ren and Maya (both stand left of centre)
    if T_ < 3.0: U.pill(f, DISC, 1860 - wpx, 48, px=32, weight=500, alpha=min(clamp(T_ / 0.4), clamp((3.0 - T_) / 0.4)), boxes=B, pad=(22, 10))
    elif T_ > TOTAL - 2.6: U.pill(f, DISC, 1860 - wpx, 980, px=32, weight=500, alpha=clamp((T_ - (TOTAL - 2.6)) / 0.3), boxes=B, pad=(22, 10))
    return f, s, B

def audio():
    parts = []
    for k in SECS:
        a, sr = sf.read(VOICE / f"{k}.wav", dtype="float32")
        if k == "L": a = a[:int(l_cut({s_: aligned_word_times(s_) for s_ in SECS}) * sr)]
        parts.append(a)
    return np.concatenate(parts), sr

def render_range(args):
    lo, hi, out = args; init()
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "15", "-pix_fmt", "yuv420p", "-g", "48", str(out)], stdin=subprocess.PIPE)
    for i in range(lo, hi): f, _, _ = frame_at(i); p.stdin.write(f.convert("RGB").tobytes())
    p.stdin.close(); assert p.wait() == 0; return str(out)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--plan", action="store_true"); ap.add_argument("--stills"); ap.add_argument("--out"); ap.add_argument("--jobs", type=int, default=4); ap.add_argument("--name", default="pilot")
    a = ap.parse_args(); init(); nfr = int(math.ceil(TOTAL * FPS - 1e-6))
    if a.plan:
        for s in SHOTS: print(f"{s['id']} {s['type'][:6]:6s} {s['a']:6.2f}-{s['b']:6.2f} {s['b'] - s['a']:4.1f}s {s['phrase'][:80]}")
        bad = [(s["id"], round(s["b"] - s["a"], 2)) for s in SHOTS if s["b"] - s["a"] > CAPS[s["type"]] + 1e-6]; print(f"total {TOTAL:.2f}s = {nfr} frames; over cap: {bad}"); return
    if a.stills:
        o = Path(a.stills); o.mkdir(parents=True, exist_ok=True)
        for s in SHOTS: i = (s["fa"] + s["fb"]) // 2; f, _, _ = frame_at(i); f.convert("RGB").save(o / f"{s['id']}.png")
        print("stills ->", o); return
    assert not FAKE, 'no real narration yet'
    o = Path(a.out).resolve(); o.mkdir(parents=True, exist_ok=True); n = a.jobs; edges = [round(nfr * k / n) for k in range(n + 1)]; t0 = time.monotonic()
    with ProcessPoolExecutor(n) as ex: futs = [ex.submit(render_range, (edges[k], edges[k + 1], o / f"_seg{k}.mp4")) for k in range(n)]; segs = [f.result() for f in futs]
    lst = o / "_segs.txt"; lst.write_text("".join(f"file '{s}'\n" for s in segs)); au, sr = audio(); wav = o / f"{a.name}_audio.wav"; sf.write(wav, au, sr); mp4 = o / f"{a.name}.mp4"
    subprocess.check_call(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-i", str(wav), "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-af", "apad,volume=-0.3dB", "-shortest", "-movflags", "+faststart", str(mp4)])
    for s in segs: Path(s).unlink()
    lst.unlink()
    rep = dict(video=mp4.name, frames=nfr, fps=FPS, size=[W, H], audio_s=len(au) / sr, shots=[dict(id=s["id"], type=s["type"], phrase=s["phrase"], start=s["fa"] / FPS, end=s["fb"] / FPS, fa=s["fa"], fb=s["fb"]) for s in SHOTS], render_s=round(time.monotonic() - t0))
    (o / f"{a.name}_report.json").write_text(json.dumps(rep, indent=1)); print("done", mp4, rep["render_s"], "s")

if __name__ == "__main__":
    main()
