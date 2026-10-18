"""Side-by-side check of the assembled rig against ren-original.

  .tools/venv/bin/python rig/compare.py

Reads rig/ren/checks/rig-neutral.png (the Remotion still), scales it so the hair matches the original's
width, and writes rig/ren/checks/rig-vs-original.png: original | rig | 50% overlay | full rig, plus a
face close-up row, and prints the shoulder widths at a few rows.
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

C = Path(__file__).resolve().parent / "ren"
orig = Image.open(C / "source" / "ren-original.jpg").convert("RGB")
rig = Image.open(C / "checks" / "rig-neutral.png").convert("RGB")


def hair(im, ymax):
    m = np.array(im.convert("L")) < 70
    m[ymax:] = False
    lab, n = ndimage.label(m)
    s = ndimage.sum(m, lab, range(1, n + 1))
    ys, xs = np.nonzero(lab == (np.argmax(s) + 1))
    return xs.min(), xs.max(), ys.min()


ox0, ox1, oy0 = hair(orig, 372)
rx0, rx1, ry0 = hair(rig, 430)
f = (ox1 - ox0) / (rx1 - rx0)
big = rig.resize((int(rig.width * f), int(rig.height * f)), Image.LANCZOS)
X, Y = int(rx0 * f - ox0), int(ry0 * f - oy0)
rc = big.crop((X, Y, X + orig.width, Y + orig.height))
a = np.array(rc).astype(int)
a[np.abs(a - np.array([243, 245, 248])).sum(axis=2) < 6] = 255  # same white background as the original
rc = Image.fromarray(a.astype(np.uint8))
over = Image.blend(orig, rc, 0.5)
full = rig.resize((int(rig.width * orig.height / rig.height), orig.height))
face = (300, 160, 680, 600)
fo, fr, fv = (im.crop(face).resize((760, 880)) for im in (orig, rc, over))

W, pad, top = orig.width, 30, 80
canvas = Image.new("RGB", (W * 3 + full.width + pad * 5, orig.height + top + 880 + top), "white")
d = ImageDraw.Draw(canvas)
fnt = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 34)
for i, (im, lab) in enumerate([(orig, "ren-original"), (rc, "Rig (same head size)"), (over, "50% overlay"), (full, "Full rig, neutral pose")]):
    x = pad + i * (W + pad)
    canvas.paste(im, (x, top))
    d.text((x, 20), lab, fill=(19, 35, 63), font=fnt)
y2 = top + orig.height + top
for i, (im, lab) in enumerate([(fo, "Face: original"), (fr, "Face: rig"), (fv, "Face: overlay")]):
    x = pad + i * (760 + pad)
    canvas.paste(im, (x, y2))
    d.text((x, y2 - 50), lab, fill=(19, 35, 63), font=fnt)
canvas.save(C / "checks" / "rig-vs-original.png")


def widest(im, y):
    xs = np.nonzero(np.array(im).astype(int).mean(axis=2)[y] < 120)[0]
    return int(xs.max() - xs.min()) if len(xs) else 0


print(f"scale {f:.3f}; shoulder width rig/original:", {y: round(widest(rc, y) / widest(orig, y), 3) for y in (700, 800, 900)})
