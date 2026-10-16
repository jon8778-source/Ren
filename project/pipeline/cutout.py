"""Cut a character pose out of its white background and save a transparent PNG.

  python pipeline/cutout.py SRC.png DST.png

Flood-fills the white background from the top edge and from the sides down to the shoulders
(not lower, so white shirts that reach the bottom of the image survive; any white left in the
lower corners is invisible on the white video background), drops stray fragments of other poses that touch the
image border, trims to the figure, and scales to 1000px tall.
"""
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage

src, dst = sys.argv[1], sys.argv[2]
im = Image.open(src).convert("RGB")
w, h = im.size
fill = im.copy()
# Block the bottom rows: a white band under the figure would let the fill leak into white
# shirts. The block covers the band of near-empty rows at the bottom, plus a margin.
rows_dark = (np.asarray(im).min(axis=2) < 200).mean(axis=1)
band = 0
while band < h // 4 and rows_dark[h - 1 - band] < 0.05:
    band += 1
BAR = band + 10
ImageDraw.Draw(fill).rectangle([0, h - BAR, w, h], fill=(0, 0, 0))
SENT = (255, 0, 255)
seeds = [(x, 0) for x in range(0, w, 6)]
px = np.asarray(im)
def first_touch(col):
    # First row where the figure reaches this side edge (usually the shoulders); seeding below it
    # could leak into white shirts through gaps under the garment.
    dark = np.where(px[:, col].min(axis=1) < 200)[0]
    return int(dark[0]) if len(dark) else h - BAR
seeds += [(0, y) for y in range(0, first_touch(0), 6)] + [(w - 1, y) for y in range(0, first_touch(w - 1), 6)]
for p in seeds:
    px = fill.getpixel(p)
    if px != SENT and min(px) > 225:
        ImageDraw.floodfill(fill, p, SENT, thresh=40)
a = np.array(fill)
fg = ~((a[..., 0] == 255) & (a[..., 1] == 0) & (a[..., 2] == 255))
# Blocked rows: the margin above the band copies the mask from the row above; inside the band
# itself only drawn (non-white) pixels are kept, such as hoodie strings.
fg[h - BAR:h - band] = fg[h - BAR - 1]
if band:
    fg[h - band:] = np.asarray(im)[h - band:].min(axis=2) < 235

# Keep the main figure plus detached details inside the frame (sweat drops, shock lines);
# drop small pieces that touch the border (slivers of neighbouring poses from the source sheet).
lab, n = ndimage.label(fg)
sizes = ndimage.sum(fg, lab, range(1, n + 1))
main = int(np.argmax(sizes)) + 1
border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
keep = np.zeros_like(fg)
for i in range(1, n + 1):
    if i == main or (i not in border and sizes[i - 1] > 30):
        keep |= lab == i
mask = Image.fromarray((keep * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1))
out = im.convert("RGBA")
out.putalpha(mask)
out = out.crop(out.getbbox())
out = out.resize((round(out.width * 1000 / out.height), 1000), Image.LANCZOS)
out.save(dst, optimize=True)
