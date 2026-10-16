"""Split a character sheet (several poses on one image) into one transparent PNG per pose.

  python pipeline/split_sheet.py SHEET.png 1x4 characters/<id> neutral happy worried regretful

LAYOUT is ROWSxCOLS. Removes long divider lines, cuts the sheet at its emptiest gutters, keeps the
tallest block in each cell (the figure, not its text label), and saves each crop through cutout.py
as characters/<id>/<pose>.png, in reading order.
"""
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

sheet, layout, out_dir, poses = sys.argv[1], sys.argv[2], Path(sys.argv[3]), sys.argv[4:]
rows, cols = map(int, layout.split("x"))
im = Image.open(sheet).convert("RGB")
a = np.asarray(im).copy()
h, w = a.shape[:2]
dark = a.max(axis=2) < 90  # near-black only: divider lines, not skin or clothing

# Divider lines: long thin straight runs. Erase them so they don't join figures together.
def thin(mask, axis):
    """Keep only line pieces at most 10px thick (hair and clothing runs are much wider)."""
    lab, n = ndimage.label(mask)
    keep = np.zeros_like(mask)
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        if (sl[1].stop - sl[1].start if axis == 0 else sl[0].stop - sl[0].start) <= 10:
            keep |= lab == i
    return keep


vert = thin(ndimage.binary_opening(dark, structure=np.ones((int(h * 0.55), 1))), 0)
horz = thin(ndimage.binary_opening(dark, structure=np.ones((1, int(w * 0.55)))), 1)
lines = ndimage.binary_dilation(vert | horz, iterations=3)
a[lines] = 255
fg = a.min(axis=2) < 235



def cuts(profile, k):
    """k-1 cut positions at the centres of the widest near-empty runs, away from the edges."""
    empty = profile <= max(2, profile.max() * 0.004)
    runs, i = [], 0
    while i < len(empty):
        if empty[i]:
            j = i
            while j < len(empty) and empty[j]:
                j += 1
            if i > 0 and j < len(empty):
                runs.append((j - i, (i + j) // 2))
            i = j
        else:
            i += 1
    best = sorted(sorted(runs, reverse=True)[:k - 1], key=lambda r: r[1])
    if len(best) != k - 1:
        raise SystemExit(f"{sheet}: could not find {k - 1} gutters")
    return [0] + [c for _, c in best] + [len(profile)]


def tallest_block(cell):
    """Row range of the tallest run of non-empty rows: the figure, not the label under or over it."""
    prof = cell.sum(axis=1)
    on = prof > max(2, cell.shape[1] * 0.002)
    best, i = (0, 0), 0
    while i < len(on):
        if on[i]:
            j = i
            while j < len(on) and (on[j] or (j + 3 < len(on) and on[j:j + 3].any())):
                j += 1
            if j - i > best[1] - best[0]:
                best = (i, j)
            i = j
        else:
            i += 1
    return best


boxes = []
ys = cuts(fg.sum(axis=1), rows) if rows > 1 else [0, h]
for r in range(rows):
    band = fg[ys[r]:ys[r + 1]]
    xs = cuts(band.sum(axis=0), cols) if cols > 1 else [0, w]
    for c in range(cols):
        cell = band[:, xs[c]:xs[c + 1]]
        y0, y1 = tallest_block(cell)
        colsum = cell[y0:y1].any(axis=0)
        x0, x1 = int(np.argmax(colsum)), len(colsum) - int(np.argmax(colsum[::-1]))
        boxes.append((slice(ys[r] + y0, ys[r] + y1), slice(xs[c] + x0, xs[c] + x1)))
if len(boxes) != len(poses):
    raise SystemExit(f"{sheet}: {len(boxes)} cells for {len(poses)} poses")
out_dir.mkdir(parents=True, exist_ok=True)
cutout = Path(__file__).with_name("cutout.py")
with tempfile.TemporaryDirectory() as tmp:
    for pose, sl in zip(poses, boxes):
        crop = Image.fromarray(a[sl[0].start:sl[0].stop, sl[1].start:sl[1].stop])
        pad = Image.new("RGB", (crop.width + 60, crop.height + 40), "white")
        pad.paste(crop, (30, 30))  # white margin on top and sides, figure stays on the bottom edge
        src = Path(tmp) / f"{pose}.png"
        pad.save(src)
        subprocess.run([sys.executable, str(cutout), str(src), str(out_dir / f"{pose}.png")], check=True)
        print(f"{out_dir.name}/{pose}.png")
