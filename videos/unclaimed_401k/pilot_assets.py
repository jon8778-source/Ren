"""Asset loading for the 401(k) pilot: plates, Maya pose cut-outs (with anchors), props."""
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage
import sys
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from unchair import hsv

ART = HERE / "art"
_cache = {}
def pose(key):
    if key not in _cache:
        _cache[key] = Image.open(ART / "poses" / f"{key}.png").convert("RGBA")
    return _cache[key]
def plate(n):
    k = "plate_" + n
    if k not in _cache:
        _cache[k] = Image.open(ART / "plates" / f"{n}.png").convert("RGBA")
    return _cache[k].copy()
_anch = {}
def anchor(key):
    """(x, y): x = centroid of the navy trousers (stable between poses of one sheet), y = lowest opaque row (stool legs / shoes)."""
    if key not in _anch:
        im = pose(key); a = np.array(im)
        h, s, v = hsv(a[..., :3])
        navy = (a[..., 3] > 200) & (h > 200) & (h < 250) & (s > 0.4) & (v < 0.5)
        ys, xs = np.where(navy)
        x = float(xs.mean()) if len(xs) > 200 else im.width / 2
        _anch[key] = (x, float(im.height))
    return _anch[key]

# --- per-sheet scale (stool height) and stool anchors -----------------------------------------------------------------
import glob, os
def _wood(key):
    im = pose(key); a = np.array(im); h, s, v = hsv(a[..., :3])
    m = (a[..., 3] > 200) & (h > 20) & (h < 40) & (s > 0.3) & (s < 0.7) & (v > 0.6)
    m[: int(im.height * 0.5)] = False
    return m
def _stool_h(key):
    m = _wood(key); rows = np.where(m.sum(1) > 3)[0]
    return float(rows.max() - rows.min()) if len(rows) else 0.0
def _sheet(key): return key.rsplit("_", 1)[0]
MANUAL = {"stool": 1.0, "maya_nochair": 0.85, "receipt_laptop": 1.10, "drawer": 0.95, "overshoulder": 1.05, "walk_sit": 0.95,
          "hr_offer_folder": 0.40, "maya_take_folder": 0.40}      # matched by eye on a comparison sheet (hair/stool metrics disagree)
def scale_of(key):
    """Relative scale that makes every sheet's Maya the same size as the stool sheet (stool height is the yardstick)."""
    key = key[5:] if key.startswith("seat_") else key
    k = "sc_" + _sheet(key)
    if k not in _anch:
        sh = _sheet(key)
        if sh in MANUAL: _anch[k] = MANUAL[sh]
        else:
            keys = sorted(os.path.basename(f)[:-4] for f in glob.glob(str(ART / "poses" / f"{sh}_*.png")))
            hs = [x for x in (_stool_h(q) for q in keys) if x > 0]
            ref = [x for x in (_stool_h(q) for q in sorted(os.path.basename(f)[:-4] for f in glob.glob(str(ART / "poses" / "stool_*.png")))) if x > 0]
            _anch[k] = float(np.median(ref) / np.median(hs)) if hs else 1.0
    return _anch[k]
def stool_anchor(key):
    """(x, y): stool centre x (stable across a sheet) and lowest row; falls back to anchor()."""
    k = "sa_" + key
    if k not in _anch:
        m = _wood(key); ys, xs = np.where(m)
        _anch[k] = (float(xs.mean()), float(pose(key).height)) if len(xs) > 300 else anchor(key)
    return _anch[k]

# --- clipboard + writing hand split into two layers so the pen can really move --------------------------------------------
SHEET_QUAD = [(17, 62), (202, 40), (305, 285), (112, 323)]     # TL, TR, BR, BL of the paper in props_03 (native px)
PEN_TIP = (158, 217)
def clipboard_layers():
    k = "clip_layers"
    if k in _cache: return _cache[k]
    im = pose("props_03"); a = np.array(im); h, s, v = hsv(a[..., :3]); al = a[..., 3] > 40
    skin = al & (h > 12) & (h < 38) & (s > 0.15) & (s < 0.6) & (v > 0.82)
    rust = al & (h > 4) & (h < 20) & (s > 0.55) & (v > 0.35)
    # dark pen + hand outlines + silver pen parts: dark/grey pixels connected to the skin region, right of the board edge line
    dark = al & (v < 0.4); grey = al & (s < 0.12) & (v > 0.4) & (v < 0.85)
    yy, xx = np.mgrid[0:im.height, 0:im.width]
    zone = (xx > 150) & (yy < 330)
    polyim = Image.new("L", im.size, 0); ImageDraw.Draw(polyim).polygon(SHEET_QUAD, fill=255); inpoly = np.array(polyim) > 0
    core = ndimage.binary_opening(skin | rust, iterations=2) & zone
    thick = ndimage.binary_opening(dark & zone, iterations=3)                     # pen body: thick dark strokes, not thin outlines
    pen = ndimage.binary_dilation(thick, iterations=4) & (dark | grey) & zone
    pen |= ndimage.binary_dilation(thick, iterations=7) & (al & (s < 0.15) & (v > 0.8)) & zone & ~inpoly & (yy < 150)   # silver pen clip
    outl = ndimage.binary_dilation(core | pen, iterations=4) & dark & zone                                   # outlines hugging hand / pen
    hand = core | pen | outl
    tip = (xx > 150 - 22) & (xx < 190) & (yy > 175) & (yy < 232) & (grey | dark) & ~hand
    hand |= tip
    hand = ndimage.binary_dilation(hand, iterations=1) & al
    hand_rgba = a.copy(); hand_rgba[..., 3] = np.where(hand, a[..., 3], 0)
    # clipboard: hand pixels inside the paper polygon become blank paper; elsewhere transparent
    poly = Image.new("L", im.size, 0); ImageDraw.Draw(poly).polygon(SHEET_QUAD, fill=255); poly = np.array(poly) > 0
    base = a.copy(); fill = np.array([250, 248, 244], np.uint8)
    hole = ndimage.binary_dilation(hand, iterations=3)
    base[hole & poly, :3] = fill; base[hole & poly, 3] = 255
    base[hole & ~poly, 3] = 0
    base[rust & ~hand & ~poly, 3] = 0                      # leftover sleeve fragment
    out = (Image.fromarray(base, "RGBA"), Image.fromarray(hand_rgba, "RGBA"), Image.fromarray((poly * 255).astype(np.uint8)))
    _cache[k] = out; return out
from PIL import ImageDraw
