"""Cut out the second set of hands (owner's generated sheets in rig/ren/source/hands-v2/), recolour them to
Ren's skin and outline, and save right and mirrored left versions.

  .tools/venv/bin/python rig/build_hands_v2.py

Writes rig/ren/parts/hand2-<name>-r.png and -l.png, rig/ren/parts/parts-v2.json (sizes, wrist direction,
grip line) and rig/ren/checks/hands-v2-on-magenta.png. The sheets are generated art, not Ren's locked art.
Colour: skin gets a per-channel gain to Ren's hand skin (as build_parts.py does for the hands sheet); the
outline is pulled from the sheets' brown to Ren's near-black in proportion to how dark each pixel is.
The left hand is the mirror image of the right (a mirrored right hand is a left hand seen from the same side).
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = Path(__file__).resolve().parent
SRC = HERE / "ren" / "source" / "hands-v2"
OUT = HERE / "ren" / "parts"
CHECKS = HERE / "ren" / "checks"

ren = np.array(Image.open(OUT / "hand-relaxed-r.png").convert("RGBA")).astype(float)
rp = ren[ren[..., 3] > 200][:, :3]
SKIN = np.median(rp[(rp.mean(1) > 150) & (rp[:, 0] - rp[:, 2] > 30)], axis=0)  # Ren's hand skin
LINE = np.median(rp[rp.mean(1) < 70], axis=0)                                   # Ren's outline

# (name, sheet, index of the hand from the left, mirror the source first, wrist direction in the saved
# right-hand image: the way the wrist end points, None = no wrist drawn)
HANDS = [
    ("point-down", "sheet1-pointing-right", 0, False, (0, -1)),
    ("point-45", "sheet1-pointing-right", 1, False, (0.45, -1)),
    ("point-viewer", "sheet1-pointing-right", 2, False, None),
    ("point-curl", "sheet1-pointing-right", 3, False, (0, -1)),
    ("point-up", "sheet2-pointing-left", 4, False, (0, 1)),   # the right-hand palm view came out on the left sheet
    ("thumbs-front", "sheet3-thumbs", 0, True, (0, 1)),        # mirrored so the thumb sits on the same side as 3 and 4
    ("thumbs-side", "sheet3-thumbs", 1, False, (-1, 0)),
    ("thumbs-tuck", "sheet3-thumbs", 2, False, (0, 1)),
    ("thumbs-half", "sheet3-thumbs", 3, False, (0, 1)),
    ("half-closed", "sheet5-extras", 0, False, (0, 1)),
    ("grip-front", "sheet6-grip-green", 0, False, (-1, 0)),
]


def cut(rgb):
    """Alpha from distance to the white background; green (the grip rod) removed and returned separately."""
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    green = (g > 170) & (r < 140) & (b < 140) & (g - np.maximum(r, b) > 60)
    green = ndimage.binary_dilation(green, iterations=2)
    whiteness = np.clip((rgb.min(axis=2) - 215) / 32, 0, 1)
    alpha = 1 - whiteness
    alpha[green] = 0
    return alpha, green


def recolour(rgb, alpha):
    a = alpha > 0.9
    px = rgb[a]
    lum = px.mean(1)
    skin = np.median(px[(lum > 140) & (px[:, 0] - px[:, 2] > 30)], axis=0)
    line = np.median(px[lum < 90], axis=0)
    out = np.clip(rgb * (SKIN / skin), 0, 255)  # skin and its shading
    # darkness 0 at skin, 1 at the sheet's outline: blend towards Ren's outline
    t = np.clip((skin.mean() - rgb.mean(axis=2)) / (skin.mean() - line.mean()), 0, 1)[..., None] ** 1.5
    return out * (1 - t) + LINE * t


def hands_on(sheet):
    rgb = np.array(Image.open(SRC / f"{sheet}.jpg").convert("RGB")).astype(float)
    alpha, green = cut(rgb)
    lab, n = ndimage.label(ndimage.binary_closing(alpha > 0.5, iterations=3))
    sizes = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
    keep = sorted([i + 1 for i, s in enumerate(sizes) if s > 20000], key=lambda i: np.nonzero(lab == i)[1].mean())
    return rgb, alpha, green, lab, keep


meta, previews = {}, []
cache = {}
for name, sheet, idx, mirror, wrist in HANDS:
    if sheet not in cache:
        cache[sheet] = hands_on(sheet)
    rgb, alpha, green, lab, keep = cache[sheet]
    m = ndimage.binary_dilation(lab == keep[idx], iterations=3)
    ys, xs = np.nonzero(m)
    y0, y1, x0, x1 = max(0, ys.min() - 6), ys.max() + 7, max(0, xs.min() - 6), xs.max() + 7
    a = (alpha * m)[y0:y1, x0:x1]
    col = recolour(rgb[y0:y1, x0:x1], a)
    img = np.dstack([col, a * 255]).astype(np.uint8)
    gr = green[y0:y1, x0:x1]
    if mirror:
        img, gr = img[:, ::-1], gr[:, ::-1]
    entry = {"w": int(img.shape[1]), "h": int(img.shape[0]), "sheet": sheet, "wrist": list(wrist) if wrist else None}
    if gr.any():  # grip rod: its centre line and width, in the right hand's image px
        gy, gx = np.nonzero(gr)
        entry["rod"] = {"x": round(float(np.median(gx)), 1), "width": int(np.percentile(gx, 95) - np.percentile(gx, 5))}
    for side, im in (("r", img), ("l", img[:, ::-1])):
        Image.fromarray(np.ascontiguousarray(im)).save(OUT / f"hand2-{name}-{side}.png")
        e = dict(entry)
        if side == "l":
            e["wrist"] = [-wrist[0], wrist[1]] if wrist else None
            if "rod" in e:
                e["rod"] = {**e["rod"], "x": round(entry["w"] - 1 - entry["rod"]["x"], 1)}
        meta[f"hand2-{name}-{side}"] = e
    previews.append(img)

(OUT / "parts-v2.json").write_text(json.dumps({"skin": SKIN.round(1).tolist(), "line": LINE.round(1).tolist(), "parts": meta}, indent=1) + "\n")

# Check sheet: every right hand on magenta (any leftover background or fringe shows up), with Ren's relaxed hand first
row = [ren.astype(np.uint8)] + previews
H = max(p.shape[0] for p in row) + 40
canvas = Image.new("RGBA", (sum(p.shape[1] + 30 for p in row) + 30, H), (255, 0, 255, 255))
x = 30
for p in row:
    canvas.alpha_composite(Image.fromarray(np.ascontiguousarray(p)), (x, 20))
    x += p.shape[1] + 30
canvas.convert("RGB").save(CHECKS / "hands-v2-on-magenta.png")
print(len(meta), "hand images; skin", SKIN.round(), "outline", LINE.round())
