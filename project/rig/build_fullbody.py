"""Cut Ren's full-body pose drawings out of their white background, for the still-image clip.

  .tools/venv/bin/python rig/build_fullbody.py

Sources: rig/ren/source/fullbody/ren-full-<pose>.jpg (owner-generated, 1792x2400, all drawn at the same size
with the head top and the soles on the same rows). Every pose is cut out on the same canvas and cropped to one
shared box, so the images line up exactly and a pose change never moves Ren's feet or head.

Pointing and presenting were drawn reaching to the left of the image; the clip's graphics are on Ren's right
(screen right), so they are mirrored. Writes remotion/public/rig/fullbody/<pose>.png, fullbody.json (box and
the feet/head positions in image px) and checks/fullbody-on-magenta.png.
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps
from scipy import ndimage

HERE = Path(__file__).parent
SRC = HERE / "ren" / "source" / "fullbody"
OUT = HERE.parent / "remotion" / "public" / "rig" / "fullbody"
POSES = ["neutral", "waving", "presenting", "pointing", "thinking", "worried", "frustrated", "shocked", "shrug", "thumbs-up", "holding-card"]
MIRROR = {"presenting", "pointing"}
BG = 247        # min channel at or above this counts as background white (the T-shirt is about 236)
HOLE_MIN = 3000  # enclosed white areas (between an arm and the body) larger than this are background too
HOLE_ZONE = (600, 2150)  # ...but only below the face (teeth, eye whites) and above the shoes (white soles)
PAD = 12


def cut(name):
    im = Image.open(SRC / f"ren-full-{name}.jpg").convert("RGB")
    px = np.asarray(im).astype(int)
    white = px.min(axis=2) >= BG
    lab, n = ndimage.label(white)
    edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bg = np.isin(lab, list(edge))
    # Enclosed gaps, e.g. between a bent arm and the body
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        region = lab[sl] == i
        cy = sl[0].start + np.argwhere(region)[:, 0].mean()
        if i not in edge and region.sum() > HOLE_MIN and HOLE_ZONE[0] < cy < HOLE_ZONE[1]:
            bg[sl] |= region
    # Keep the figure (largest piece); anti-aliased edge: grow the background by a pixel and soften
    fg = ~bg
    lab2, n2 = ndimage.label(fg)
    sizes = ndimage.sum(fg, lab2, range(1, n2 + 1))
    fg = lab2 == int(np.argmax(sizes)) + 1
    fg = ndimage.binary_fill_holes(fg) & ~bg
    mask = Image.fromarray((fg * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.8))
    out = im.convert("RGBA")
    out.putalpha(mask)
    return ImageOps.mirror(out) if name in MIRROR else out


cuts = {n: cut(n) for n in POSES}
boxes = np.array([c.getbbox() for c in cuts.values()])
box = (int(boxes[:, 0].min()) - PAD, int(boxes[:, 1].min()) - PAD, int(boxes[:, 2].max()) + PAD, int(boxes[:, 3].max()) + PAD)
OUT.mkdir(parents=True, exist_ok=True)
for n, c in cuts.items():
    c.crop(box).save(OUT / f"{n}.png", optimize=True)

# Feet line and head top/centre, in cropped image px (from the neutral pose)
a = np.asarray(cuts["neutral"])[..., 3] > 128
ys, xs = np.nonzero(a)
meta = {"w": box[2] - box[0], "h": box[3] - box[1], "feetY": int(ys.max()) - box[1], "headTopY": int(ys.min()) - box[1],
        "centerX": round(float(xs[ys < ys.min() + 80].mean())) - box[0], "poses": POSES}
(OUT / "fullbody.json").write_text(json.dumps(meta, indent=1))
(HERE.parent / "remotion" / "src" / "rig" / "fullbody.json").write_text(json.dumps(meta, indent=1))

# Check: every cut-out on magenta, so missed background or holes in the figure show up
tw = 300
th = round(meta["h"] * tw / meta["w"])
sheet = Image.new("RGB", (tw * 6, th * 2 + 40), (255, 0, 255))
d = ImageDraw.Draw(sheet)
for i, n in enumerate(POSES):
    t = Image.open(OUT / f"{n}.png").resize((tw, th), Image.LANCZOS)
    x, y = (i % 6) * tw, (i // 6) * (th + 20)
    sheet.paste(t, (x, y), t)
    d.text((x + 8, y + th + 2), n, fill="white")
(HERE / "checks").mkdir(exist_ok=True)
sheet.save(HERE / "checks" / "fullbody-on-magenta.png")
print(json.dumps(meta))
