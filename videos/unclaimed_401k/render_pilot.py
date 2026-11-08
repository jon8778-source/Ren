"""Pilot (about 53 s) of "Ren | Unclaimed 401(k) match" - Maya-led story, 1920x1080, 24 fps, v3 rules.

  project/.tools/venv/bin/python videos/unclaimed_401k/render_pilot.py --stills OUT_DIR        # one still per shot midpoint
  project/.tools/venv/bin/python videos/unclaimed_401k/render_pilot.py --out OUT_DIR --jobs 4   # render (local only)

Shot times come from the Whisper word times of the real Qwen narration (voice/words_P1.json, words_P2.json): each shot starts
when its first word starts. The narration is joined exactly as generated (P1 then P2). Maya is the approved cut-out art, placed
with ren_stage.paste_smooth (sub-pixel), anchored on the stool (or trousers) so pose changes do not jump. All text, numbers,
cards and the finance UI are drawn in code (Fredoka, navy / sage / cream).
"""
import argparse, json, math, subprocess, sys, time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(ROOT / "project" / "cliplib"))
import pilot_assets as A
import pilot_ui as U
import pilot_ren as PR
from ren_stage import paste_smooth, _shadow_patch

W, H, FPS = 1920, 1080, 24
S0 = 1.25                       # global Maya scale; per-sheet factors come from pilot_assets.scale_of
BLEND = 3 / FPS                 # pose-to-pose cross-fade: 3 frames
VOICE = HERE / "voice"
OFF = 31.717                    # P2 starts where P1 ends (the narration is joined exactly as generated)
CAPS = {"CHARACTER_ACTION": 5.5, "STORY_STILL": 2.5, "GRAPHIC": 3.5, "REN_ANIMATED": 5.5}

# ---- shot list (cut times = first narrated word of each phrase, from voice/words_P*.json) -----------------------------------
def _shots():
    p1 = [0.00, 2.64, 5.50, 9.24, 11.72, 14.98, 16.74, 18.56, 21.64, 23.84, 26.48, 29.00, OFF]
    p2 = [OFF + x for x in (0.00, 3.88, 6.78, 9.84, 13.10, 14.56, 18.52, 21.378)]
    cuts = p1[:-1] + p2
    ids = [("P01", "CHARACTER_ACTION", "Maya saved twelve dollars last night."),
           ("P02", "CHARACTER_ACTION", "She canceled a subscription she barely used,"),
           ("P03", "CHARACTER_ACTION", "checked the confirmation email, and felt pretty good about it."),
           ("P04", "CHARACTER_ACTION", "Then she opened her work benefits portal."),
           ("P05", "CHARACTER_ACTION", "There was a number sitting in there that made the subscription look tiny,"),
           ("P06", "GRAPHIC", "One hundred dollars a month."),
           ("P07", "GRAPHIC", "Twelve hundred dollars a year."),
           ("P08", "REN_ANIMATED", "Her employer was willing to put that into her retirement account,"),
           ("P09", "CHARACTER_ACTION", "but only if she made one change."),
           ("P10", "CHARACTER_ACTION", "She'd worked there for three years and never noticed."),
           ("P11", "REN_ANIMATED", "This isn't a story about a secret investment trick."),
           ("P12", "CHARACTER_ACTION", "It's about a benefit hiding in plain sight."),
           ("P13", "CHARACTER_ACTION", "Meet Maya. She's thirty-one, earns sixty thousand dollars a year,"),
           ("P14", "CHARACTER_ACTION", "and has a pretty normal relationship with money."),
           ("P15", "CHARACTER_ACTION", "She pays her bills, puts something aside when she can,"),
           ("P16", "CHARACTER_ACTION", "and tries not to think about how expensive groceries have become."),
           ("P17", "STORY_STILL", "When she joined her company,"),
           ("P18", "CHARACTER_ACTION", "she ticked the box to contribute two percent to her four-oh-one-k."),
           ("P19", "CHARACTER_ACTION", "The form said she'd been enrolled, so she moved on.")]
    end = OFF + 21.378
    out = []
    for i, ((sid, typ, phr), a) in enumerate(zip(ids, cuts)):
        b = cuts[i + 1] if i + 1 < len(cuts) else end
        out.append({"i": i, "id": sid, "type": typ, "phrase": phr, "a": a, "b": b})
    return out
SHOTS = _shots()
NFRAMES = int(math.ceil((OFF + 21.378) * FPS - 1e-6))
for s in SHOTS:
    s["fa"] = round(s["a"] * FPS); s["fb"] = round(s["b"] * FPS)
SHOTS[-1]["fb"] = NFRAMES
SCENE = {"P01": "H1", "P02": "H1", "P03": "H1", "P04": "H1", "P05": "H1", "P06": "H1", "P07": "H1", "P08": "SAGE", "P09": "H1", "P10": "H1",
         "P11": "SAGE", "P12": "H1", "P13": "O1", "P14": "O1", "P15": "O1", "P16": "O1", "P17": "O2", "P18": "O1", "P19": "O1"}

# ---- drawing helpers --------------------------------------------------------------------------------------------------------
class Boxes(list):
    ren = None; ren_i = None; poses = None; maya = None; tip = None
REC = {"poses": [], "maya": None, "tip": None}

_bl = {}
def backdrop(name, r=16, dark=0.58):
    k = (name, r, dark)
    if k not in _bl:
        im = A.plate(name).filter(ImageFilter.GaussianBlur(r)); ov = Image.new("RGBA", im.size, (*U.NAVY, int(255 * (1 - dark)))); im.alpha_composite(ov); _bl[k] = im
    return _bl[k].copy()

def anch(key):
    return A.anchor(key) if key.startswith(("seat_", "walk_sit_01", "walk_sit_02", "walk_sit_03", "walk_sit_04", "maya_nochair")) else A.stool_anchor(key)

def draw_pose(f, key, X, Yb, S=S0, alpha=1.0, shadow=True):
    im = A.pose(key); sc = S * A.scale_of(key); ax, ay = anch(key)
    w, h = im.width * sc, im.height * sc
    tgt = f if alpha >= 1 else Image.new("RGBA", f.size, (0, 0, 0, 0))
    if shadow and not key.startswith("maya_nochair"):
        sw = 330 * sc; sh = sw * 0.2; paste_smooth(tgt, _shadow_patch(), X - sw / 2, Yb - sh * 0.5, sw, sh)
    paste_smooth(tgt, im, X - ax * sc, Yb - ay * sc, w, h)
    REC["maya"] = (round(X, 2), round(Yb, 2), round(sc, 4))
    if alpha < 1:
        tgt.putalpha(tgt.getchannel("A").point(lambda v: int(v * alpha))); f.alpha_composite(tgt)
    return (X - ax * sc, Yb - ay * sc, X - ax * sc + w, Yb)

SOFT = {("stool_01", "stool_02"), ("stool_02", "stool_03"), ("receipt_laptop_04", "receipt_laptop_05"), ("receipt_laptop_01", "receipt_laptop_02"),
        ("receipt_laptop_02", "receipt_laptop_03"), ("overshoulder_01", "overshoulder_02"), ("overshoulder_02", "overshoulder_03"),
        ("drawer_01", "drawer_02"), ("drawer_02", "drawer_03"), ("drawer_03", "drawer_04"), ("drawer_04", "drawer_05"),
        ("stool_03", "stool_04"), ("stool_04", "stool_05"), ("maya_nochair_03", "maya_nochair_02"),
        ("seat_stool_03", "seat_stool_04"), ("seat_stool_04", "seat_stool_05"), ("seat_receipt_laptop_04", "seat_receipt_laptop_05")}   # small changes cross-fade over 3 frames; big ones cut
def track(f, tl, t, X, Yb, **kw):
    idx = max(i for i, (t0, _) in enumerate(tl) if t >= t0 - 1e-9)
    cur = tl[idx][1]; REC["poses"].append(cur)
    if idx > 0 and (tl[idx - 1][1], cur) in SOFT:
        a = (t - tl[idx][0]) / BLEND
        if a < 1:
            draw_pose(f, tl[idx - 1][1], X, Yb, **kw); draw_pose(f, cur, X, Yb, alpha=max(a, 0.0), **kw); return cur
    draw_pose(f, cur, X, Yb, **kw); return cur

def zoom(f, z, cx, cy):
    if abs(z - 1) < 1e-4: return f
    return f.transform((W, H), Image.AFFINE, (1 / z, 0, cx - cx / z, 0, 1 / z, cy - cy / z), Image.BICUBIC)

def homog(src, dst):
    A_, b = [], []
    for (x, y), (u, v) in zip(src, dst):
        A_ += [[x, y, 1, 0, 0, 0, -u * x, -u * y], [0, 0, 0, x, y, 1, -v * x, -v * y]]; b += [u, v]
    return np.linalg.solve(np.array(A_, float), np.array(b, float))
def warp(img, quad, size):
    """Warp img (RGBA) so its corners land on quad (TL,TR,BR,BL) in an image of `size`."""
    w, h = img.size
    c = homog(quad, [(0, 0), (w, 0), (w, h), (0, h)])      # output pixel -> source pixel
    return img.transform(size, Image.PERSPECTIVE, tuple(c), Image.BICUBIC)
def apply_h(quad, w, h, u, v):
    c = homog([(0, 0), (w, 0), (w, h), (0, h)], quad)       # source pixel -> output pixel
    d = c[6] * u + c[7] * v + 1
    return ((c[0] * u + c[1] * v + c[2]) / d, (c[3] * u + c[4] * v + c[5]) / d)

def chip_edu(f, T, B):
    if T < 3.0:
        a = min(U.clamp(T / 0.4), U.clamp((3.0 - T) / 0.4))
        U.pill(f, "Educational only. Illustrative example.", 60, 48, px=32, weight=500, alpha=a, boxes=B, pad=(22, 10))

def slide_in(f, img, x_to, y, t, t0, dur=0.45, frm=60, B=None, fade=True):
    p = 1.0 if dur <= 0 else U.ease((t - t0) / dur)       # dur <= 0: appears at once (a hard cut to the graphic)
    if t < t0: return
    x = x_to + frm * (1 - p)
    U.put(f, img.im, x, y, alpha=min(1.0, p * 1.6) if fade else 1.0, boxes=B, texts=img.texts)
def pop_in(f, img, cx, cy, t, t0, dur=0.4, B=None):
    if t < t0: return
    p = U.back((t - t0) / dur); s = max(0.05, p); im = img.im.resize((max(1, int(img.im.width * s)), max(1, int(img.im.height * s))), Image.LANCZOS)
    U.put(f, im, cx - im.width / 2, cy - im.height / 2, alpha=min(1, (t - t0) / 0.15))
    if p > 0.97 and B is not None:
        for (a, b, c, e, s_, px) in img.texts: B.append((cx - img.im.width / 2 + a, cy - img.im.height / 2 + b, cx - img.im.width / 2 + c, cy - img.im.height / 2 + e, s_, px))

_front = {}
def front_h1():
    if "h1" not in _front:
        m = Image.new("L", (W, H), 0); d = ImageDraw.Draw(m)
        d.polygon([(660, 1080), (660, 975), (905, 822), (1235, 815), (1920, 795), (1920, 1080)], fill=255)
        d.polygon([(1236, 870), (1240, 780), (1270, 700), (1330, 640), (1420, 590), (1500, 590), (1590, 660), (1595, 740), (1560, 800), (1540, 860), (1500, 880), (1400, 900), (1300, 920), (1245, 915)], fill=255)
        fr = A.plate("H1"); fr.putalpha(m.filter(ImageFilter.GaussianBlur(1.2))); _front["h1"] = fr
    return _front["h1"]
def over_h1(f): f.alpha_composite(front_h1())

class Cam:
    """Plate-space camera: zoom z about plate point (cx, cy) of the 1920x1080 plate; plate points map to frame points."""
    def __init__(self, z=1.0, cx=960, cy=540): self.z, self.cx, self.cy = z, cx, cy
    def pt(self, x, y): return ((x - self.cx) * self.z + 960, (y - self.cy) * self.z + 540)
_big = {}
def plate4k(name, cam):
    if name not in _big: _big[name] = Image.open(A.ART / "plates" / f"{name}.png").convert("RGB")
    z = cam.z; a = 2.0 / z
    c = ((cam.cx - 960 / z) * 2, (cam.cy - 540 / z) * 2)
    return _big[name].transform((W, H), Image.AFFINE, (a, 0, c[0], 0, a, c[1]), Image.BICUBIC).convert("RGBA")

# ---- placements ------------------------------------------------------------------------------------------------------------
ARM = (640, 885)                  # armchair poses (Maya sits in the plate's own chair)
H1S = (1130, 830)                 # stool beside the coffee table, home plate
O1S = (900, 935)                  # stool on the open office floor
PX = 1.0

# phone-in-hand close-up: the screen mask and quad come from the art; the UI is warped under the thumb
_hu = {}
PH_SCALE = 2.4
PH_QUAD = {"props_01": [(27, 21), (126, 16), (152, 241), (63, 249)], "props_02": [(29, 22), (128, 17), (151, 243), (64, 251)]}
def hand_ui(key, state):
    k = (key, state)
    if k in _hu: return _hu[k]
    im = A.pose(key); a = np.array(im); rgb = a[..., :3].astype(int)
    light = (a[..., 3] > 200) & (rgb.min(2) > 238); lab, n = ndimage.label(light); sz = ndimage.sum(light, lab, range(1, n + 1)); m = lab == (1 + int(np.argmax(sz)))
    sw, shh = int(im.width * PH_SCALE), int(im.height * PH_SCALE)
    base = im.resize((sw, shh), Image.LANCZOS)
    mk = Image.fromarray((m * 255).astype(np.uint8)).resize((sw, shh), Image.BILINEAR).point(lambda v: 255 if v > 110 else 0).filter(ImageFilter.MaxFilter(3))
    quad = [(x * PH_SCALE, y * PH_SCALE) for x, y in PH_QUAD[key]]
    ui = U.phone_ui(state, 300, 680); wp = warp(ui, quad, (sw, shh))
    out = base.copy(); out.paste(wp, (0, 0), mk); _hu[k] = out; return out

def blend_images(f, seq, t, x, y):
    """seq: [(t0, image)], cross-faded over BLEND."""
    idx = max(i for i, (t0, _) in enumerate(seq) if t >= t0 - 1e-9); REC["poses"].append(f"img{idx}")
    if idx > 0 and (t - seq[idx][0]) / BLEND < 1:
        f.alpha_composite(seq[idx - 1][1], (int(x), int(y)))
        im = seq[idx][1].copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * max(0, (t - seq[idx][0]) / BLEND)))); f.alpha_composite(im, (int(x), int(y)))
    else:
        f.alpha_composite(seq[idx][1], (int(x), int(y)))

# ---- shots ------------------------------------------------------------------------------------------------------------------
def p01(f, t, d, B):
    track(f, [(0, "maya_nochair_01"), (0.9, "maya_nochair_02")], t, *ARM)
def p02(f, t, d, B):
    h = hand_ui("props_01", 0); h2 = hand_ui("props_02", 1); h3 = hand_ui("props_01", 2)
    seq = [(0, h), (1.15, h2), (1.45, h3)]
    blend_images(f, seq, t, 960 - h.width / 2, 540 - h.height / 2)
def p03(f, t, d, B):
    track(f, [(0, "maya_nochair_03"), (1.4, "maya_nochair_02")], t, *ARM)
    slide_in(f, U.email_card(), 1020, 130, t, 0.5, B=B)
def p04(f, t, d, B):
    track(f, [(0, "seat_stool_03"), (0.8, "seat_stool_04")], t, *ARM)

def p05(f, t, d, B):
    track(f, [(0, "seat_stool_05"), (1.5, "seat_receipt_laptop_04")], t, *ARM)
    pop_in(f, U.alert_card(), 1530, 130, t, 0.9, B=B)

def p06(f, t, d, B):
    pass  # drawn by graphic()
def graphic_portal(f, t, d, B, mode):
    if mode == "p06":
        lab, s = "$100 / month", U.back((t - 0.2) / 0.45)
        pt = U.portal(lab, s)
    elif mode == "p07":
        if t < 0.22: pt = U.portal("$100 / month", 1 - U.ease(t / 0.22))
        else: pt = U.portal("$1,200 / year", U.back((t - 0.2) / 0.45))
    U.put(f, pt.im, 210, 90, boxes=B, texts=pt.texts)
def p08(f, t, d, B):
    c = ren_clip("p08"); bx, i = c.draw(f, t); B.ren, B.ren_i = bx, i
    U.pill(f, "Ren", 60, 56, px=40, weight=700, boxes=B, pad=(28, 12))
    slide_in(f, U.flow_card(U.clamp((t - 0.9) / 1.6)), 1010, 320, t, 0.3, B=B)

def p09(f, t, d, B):
    track(f, [(0, "seat_receipt_laptop_04"), (1.3, "seat_receipt_laptop_05")], t, *ARM)
    pulse = U.clamp(1 - abs(t - 1.4) / 0.5) if t > 0.9 else 0
    slide_in(f, U.field_card(pulse), 1160, 150, t, 0.2, B=B)

def p10(f, t, d, B):
    track(f, [(0, "seat_receipt_laptop_06"), (0.6, "seat_stool_06")], t, *ARM)
    slide_in(f, U.years_card(U.clamp((t - 0.3) / 1.9) * 3), 1160, 150, t, 0.1, B=B)

def p11(f, t, d, B):
    c = ren_clip("p11"); bx, i = c.draw(f, t); B.ren, B.ren_i = bx, i
    pn = U.trick_panel(icons=1 - U.ease((t - 0.35) / 0.9), glow=U.ease((t - 1.4) / 0.5))
    U.put(f, pn.im, 980, 230, boxes=B, texts=pn.texts)

def p12(f, t, d, B):
    scene = f.copy()
    track(scene, [(0, "seat_stool_05"), (1.2, "seat_receipt_laptop_06")], t, *ARM)
    z = 1.0 + 0.5 * (1 - U.ease(t / d))
    scene = zoom(scene, z, 700, 600); f.alpha_composite(scene)
    slide_in(f, U.line_card(), 1010, 110, t, 0.15, B=B)

def p13(f, t, d, B):
    cam = CAMS["P13"]; ST = O1S; sc5 = S0 * A.scale_of("walk_sit_05")
    # walk-in: x_end is where Maya's trousers sit in the 'reach for the stool' pose, relative to the stool
    nx5 = A.anchor("walk_sit_05")[0]; sx5 = A.stool_anchor("walk_sit_05")[0]
    x_end = ST[0] + (nx5 - sx5) * sc5
    tw, v, cyc = 1.30, 780.0, 0.125
    if t < tw:
        x = x_end - v * (tw - t); k = int(t / cyc) % 4; REC["poses"].append(f"walk_sit_0{k + 1}")
        draw_pose(f, f"walk_sit_0{k + 1}", x, 940, shadow=True)
    else:
        track(f, [(tw, "walk_sit_05"), (tw + 0.5, "walk_sit_06"), (tw + 0.95, "stool_01")], t, *ST)
    slide_in(f, U.chips_card(), 1190, 120, t, 1.0, B=B)

def p14(f, t, d, B):
    cam = CAMS["P14"]; X, Y = cam.pt(*O1S)
    track(f, [(0, "stool_01"), (0.9, "stool_02"), (1.9, "stool_03")], t, X, Y, S=S0 * cam.z)

def _jar(f, t, cam):
    jar = A.pose("props_08"); z = cam.z; jh = 150 * z; jw = jar.width * jh / jar.height; jx, jy = cam.pt(1320, 650)       # jar sits on the table top
    paste_smooth(f, jar, jx - jw / 2, jy - jh, jw, jh)
    t0, t1 = 1.7, 2.4
    if t >= t0:
        p = U.clamp((t - t0) / (t1 - t0)); y = 250 + (650 - 40 - 250) * p * p      # accelerating fall into the jar (plate px)
        coin = A.ART / "props" / ("coin_front.png" if int(t * 12) % 2 == 0 and p < 1 else "coin_side.png")
        key = str(coin)
        if key not in A._cache: A._cache[key] = Image.open(coin).convert("RGBA")
        c = A._cache[key]; ch = 46 * z; cw = c.width * ch / c.height; cx_, cy_ = cam.pt(1320, y)
        paste_smooth(f, c, cx_ - cw / 2, cy_ - ch / 2, cw, ch)

def p15(f, t, d, B):
    cam = CAMS["P15"]; X, Y = cam.pt(*O1S)
    track(f, [(0, "stool_05"), (1.4, "receipt_laptop_05")], t, X, Y, S=S0 * cam.z); _jar(f, t, cam)

def p16(f, t, d, B):
    cam = CAMS["P16"]; X, Y = cam.pt(*O1S)
    track(f, [(0, "receipt_laptop_01"), (1.2, "receipt_laptop_02"), (2.2, "receipt_laptop_03")], t, X, Y, S=S0 * cam.z)

def p17(f, t, d, B):
    hr = A.pose("hr_offer_folder_01"); mt = A.pose("maya_take_folder_01")
    for key, X in (("maya_take_folder_01", 1010), ("hr_offer_folder_01", 1420)):
        im = A.pose(key); sc = 1.25 * 0.43; ax, ay = A.stool_anchor(key)
        paste_smooth(f, _shadow_patch(), X - 150, 1010, 300, 60)
        paste_smooth(f, im, X - ax * sc, 1040 - ay * sc, im.width * sc, im.height * sc)
    # the only motion in a STORY_STILL: a slow light shift across the room
    g = np.linspace(0, 1, W, dtype=np.float32)[None, :]; ph = 0.5 + 0.5 * math.sin(t / d * math.pi)
    lay = np.zeros((H, W, 4), np.uint8); lay[..., :3] = (255, 244, 214); lay[..., 3] = (np.clip(1 - np.abs(g - (0.2 + 0.6 * t / d)) * 3.0, 0, 1) * 34 * ph).astype(np.uint8).repeat(H, 0)
    f.alpha_composite(Image.fromarray(lay, "RGBA"))
    U.pill(f, "3 years ago", 60, 48, px=40, weight=600, boxes=B, pad=(26, 12))
def p18(f, t, d, B):
    base, hand, poly = A.clipboard_layers(); s = 3.0
    ox, oy = 250, 20                                           # clipboard origin in the frame
    quad = [(ox + x * s, oy + y * s) for x, y in A.SHEET_QUAD]
    bw, bh = int(base.width * s), int(base.height * s)
    sheet = Image.new("L", (bw, bh), 0); ImageDraw.Draw(sheet).polygon([(x * s, y * s) for x, y in A.SHEET_QUAD], fill=255)
    # tick geometry in form coordinates -> frame coordinates
    fw, fh = 600, 800; u = fw / 600.0; r = 32 * u; cx, cy = 475 * u, (250 + 110) * u + 38 * u
    pts_ui = [(cx - r * .9, cy), (cx - r * .25, cy + r * .65), (cx + r * .95, cy - r * .7)]
    qf = [(x * s, y * s) for x, y in A.SHEET_QUAD]
    pts = [apply_h(qf, fw, fh, *p) for p in pts_ui]                 # in clipboard-image px at scale s
    tick_t0, tick_t1 = 1.0, 2.3; p = U.clamp((t - tick_t0) / (tick_t1 - tick_t0))
    form = U.form_ui(fw, fh, tick=p)
    layer = Image.new("RGBA", (bw, bh), (0, 0, 0, 0)); wp = warp(form, qf, (bw, bh)); layer.paste(wp, (0, 0), sheet)
    bg = backdrop("O1", 18, 0.5); bg.alpha_composite(Image.new("RGBA", bg.size, (0, 0, 0, 0)))
    f.alpha_composite(bg); sh = Image.new("RGBA", (bw, bh), (0, 0, 0, 0)); sh.paste((*U.NAVY, 70), (0, 0), base.resize((bw, bh), Image.BILINEAR).getchannel("A"))
    f.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)), (ox + 14, oy + 22))
    f.alpha_composite(base.resize((bw, bh), Image.LANCZOS), (ox, oy)); f.alpha_composite(layer, (ox, oy))
    # pen tip path: arrives from the upper right, traces the tick, lifts away
    tip0 = (A.PEN_TIP[0] * s, A.PEN_TIP[1] * s)
    seg = [(0.0, (pts[0][0] + 140, pts[0][1] - 110)), (tick_t0 - 0.3, (pts[0][0] + 60, pts[0][1] - 50)), (tick_t0, pts[0])]
    if t < tick_t0:
        u2 = U.clamp((t - 0.0) / tick_t0); tip = (U.ease(u2) * (pts[0][0] - (pts[0][0] + 140)) + pts[0][0] + 140, U.ease(u2) * (pts[0][1] - (pts[0][1] - 110)) + pts[0][1] - 110)
    elif t <= tick_t1:
        L1, L2 = math.dist(pts[0], pts[1]), math.dist(pts[1], pts[2]); run = (L1 + L2) * p
        if run <= L1: q = run / L1; tip = (pts[0][0] + (pts[1][0] - pts[0][0]) * q, pts[0][1] + (pts[1][1] - pts[0][1]) * q)
        else: q = (run - L1) / L2; tip = (pts[1][0] + (pts[2][0] - pts[1][0]) * q, pts[1][1] + (pts[2][1] - pts[1][1]) * q)
    else:
        u2 = U.ease((t - tick_t1) / 0.6); tip = (pts[2][0] + 90 * u2, pts[2][1] - 70 * u2)
    REC["tip"] = (round(tip[0], 2), round(tip[1], 2)); REC["poses"].append("pen_hand")
    hs = hand.resize((bw, bh), Image.LANCZOS); dx, dy = tip[0] - tip0[0], tip[1] - tip0[1]
    hsh = Image.new("RGBA", (bw, bh), (0, 0, 0, 0)); hsh.paste((*U.NAVY, 60), (0, 0), hs.getchannel("A")); f.alpha_composite(hsh.filter(ImageFilter.GaussianBlur(8)), (int(ox + dx + 10), int(oy + dy + 18)))
    paste_smooth(f, hand, ox + dx, oy + dy, bw, bh)
    return
def p19(f, t, d, B):
    cam = CAMS["P19"]; X, Y = cam.pt(*O1S)
    track(f, [(0, "drawer_01"), (0.55, "drawer_02"), (1.15, "drawer_03"), (1.75, "drawer_04"), (2.3, "drawer_05")], t, X, Y, S=S0 * cam.z)

CAMS = {"P13": Cam(1.0, 960, 540), "P14": Cam(1.3, 1000, 565), "P15": Cam(1.25, 1060, 560), "P16": Cam(1.55, 920, 470), "P19": Cam(1.3, 1000, 565)}
_RC = {}
REN_SPEC = {"p08": ("ren_point_right", 1.3), "p11": ("ren_shrug", 1.3)}       # clip, start second inside the library window
def ren_clip(k):
    if k not in _RC:
        shot = next(x for x in SHOTS if x["id"] == k.upper()); clip, st = REN_SPEC[k]
        _RC[k] = PR.RenClip(clip, st, (shot["fb"] - shot["fa"]) / FPS + 0.05)
    return _RC[k]
FN = {"P01": p01, "P02": p02, "P03": p03, "P04": p04, "P05": p05, "P06": lambda f, t, d, B: graphic_portal(f, t, d, B, "p06"),
      "P07": lambda f, t, d, B: graphic_portal(f, t, d, B, "p07"), "P08": p08, "P09": p09, "P10": p10, "P11": p11, "P12": p12,
      "P13": p13, "P14": p14, "P15": p15, "P16": p16, "P17": p17, "P18": p18, "P19": p19}
GRAPHIC_BG = {"P06", "P07"}
CLOSEUP_BG = {"P02", "P18"}

def frame_at(i):
    T = i / FPS
    sh = next(s for s in SHOTS if s["fa"] <= i < s["fb"])          # half-open [start, end): the first frame of a cut belongs to the new shot
    t = (i - sh["fa"]) / FPS; d = (sh["fb"] - sh["fa"]) / FPS; B = Boxes()        # local time is frame-aligned: the first frame of a shot is t = 0
    if sh["id"] in GRAPHIC_BG: f = backdrop("H1", 16, 0.58)
    elif sh["id"] in CLOSEUP_BG: f = backdrop("H1" if sh["id"] != "P18" else "O1", 16, 0.62)
    elif sh["id"] in ("P08", "P11"): f = A.plate("SAGE")
    elif sh["id"] in CAMS: f = plate4k("O1_4k", CAMS[sh["id"]])
    else: f = A.plate(SCENE[sh["id"]])
    REC["poses"] = []; REC["maya"] = None; REC["tip"] = None
    FN[sh["id"]](f, t, d, B)
    B.poses = list(REC["poses"]); B.maya = REC["maya"]; B.tip = REC["tip"]
    chip_edu(f, T, B)
    return f, sh, B

def audio():
    a1, sr = sf.read(VOICE / "P1.wav", dtype="float32"); a2, sr2 = sf.read(VOICE / "P2.wav", dtype="float32"); assert sr == sr2
    return np.concatenate([a1, a2]), sr

def render_range(args):
    lo, hi, out = args
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-c:v", "libx264", "-preset", "medium", "-crf", "15", "-pix_fmt", "yuv420p", "-g", "48", str(out)]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(lo, hi):
        f, _, _ = frame_at(i); p.stdin.write(f.convert("RGB").tobytes())
    p.stdin.close(); assert p.wait() == 0
    return str(out)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--stills"); ap.add_argument("--out"); ap.add_argument("--jobs", type=int, default=4); ap.add_argument("--name", default="pilot")
    ap.add_argument("--frames", help="lo:hi (draft)")
    a = ap.parse_args()
    if a.stills:
        o = Path(a.stills); o.mkdir(parents=True, exist_ok=True)
        for s in SHOTS:
            i = (s["fa"] + s["fb"]) // 2; f, _, _ = frame_at(i); f.convert("RGB").save(o / f"{s['id']}_mid.png")
        print("stills ->", o); return
    o = Path(a.out).resolve(); o.mkdir(parents=True, exist_ok=True)
    lo, hi = (0, NFRAMES) if not a.frames else map(int, a.frames.split(":"))
    n = a.jobs; edges = [lo + round((hi - lo) * k / n) for k in range(n + 1)]
    t0 = time.monotonic(); segs = []
    with ProcessPoolExecutor(n) as ex:
        futs = [ex.submit(render_range, (edges[k], edges[k + 1], o / f"_seg{k}.mp4")) for k in range(n)]
        segs = [f.result() for f in futs]
    lst = o / "_segs.txt"; lst.write_text("".join(f"file '{s}'\n" for s in segs))
    au, sr = audio(); wav = o / f"{a.name}_audio.wav"; sf.write(wav, au, sr)
    mp4 = o / f"{a.name}.mp4"
    subprocess.check_call(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-i", str(wav), "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-af", "apad", "-shortest", "-movflags", "+faststart", str(mp4)])
    for s in segs: Path(s).unlink()
    lst.unlink()
    # layout evidence + shot report
    shots = []
    for s in SHOTS:
        mid = (s["fa"] + s["fb"]) // 2; _, _, B = frame_at(mid)
        shots.append({"i": s["i"], "id": s["id"], "type": s["type"], "phrase": s["phrase"], "scene": SCENE[s["id"]], "start": s["fa"] / FPS, "end": s["fb"] / FPS,
                      "text": [{"box": [round(v, 1) for v in b[:4]], "text": b[4], "px": round(b[5], 1)} for b in B]})
    rep = {"video": mp4.name, "frames": NFRAMES if (lo, hi) == (0, NFRAMES) else hi - lo, "fps": FPS, "size": [W, H], "audio_s": len(au) / sr, "shots": shots, "render_s": round(time.monotonic() - t0)}
    (o / f"{a.name}_report.json").write_text(json.dumps(rep, indent=1)); print("done", mp4, rep["render_s"], "s")

if __name__ == "__main__":
    main()
