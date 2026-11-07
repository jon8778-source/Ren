"""Matte the approved Ren JPG stills (plain white background) into transparent PNGs.

  project/.tools/venv/bin/python videos/free_money/matting.py

Background = near-white pixels connected to the image EDGE (flood fill from the border only), plus any
fully enclosed pure-white pocket larger than MIN_POCKET px (e.g. the gap inside a crossed arm). White inside
the figure (the white tee, ~230-245) is never keyed. The alpha edge is softened ~1px and the white that
bled into edge pixels is removed (decontaminated), so no halo shows on dark or coloured backgrounds.
"""
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "library" / "ren_approved"
OUT = Path(__file__).resolve().parent / "matted"
BG_MIN, POCKET_MIN, MIN_POCKET = 247, 251, 400


def matte(rgb):
    lo, hi = rgb.min(2).astype(int), rgb.max(2).astype(int)
    near = (lo >= BG_MIN) & (hi - lo <= 8)
    lab, _ = ndimage.label(near)
    edge = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    bg = np.isin(lab, edge[edge > 0])
    pure = (lo >= POCKET_MIN) & (hi - lo <= 6) & ~bg
    plab, n = ndimage.label(pure)
    if n:
        sizes = ndimage.sum(pure, plab, range(1, n + 1))
        bg |= np.isin(plab, np.where(sizes > MIN_POCKET)[0] + 1)
    fg = ~bg
    fg = ndimage.binary_opening(fg, iterations=1)      # drop isolated specks of JPG noise
    for _ in range(2):   # shave the light JPG halo off the outline: pale, unsaturated pixels within 3px of the background
        ring = ndimage.binary_dilation(~fg, iterations=3) & fg
        halo = ring & (lo > 170) & (hi - lo < 40)
        fg &= ~halo
    a = ndimage.gaussian_filter(fg.astype(np.float32), 0.8)[..., None]
    c = rgb.astype(np.float32)
    c = np.where(a > 0.02, (c - (1 - a) * 255.0) / np.maximum(a, 0.02), 0)      # remove the white mixed into edge pixels
    return np.concatenate([np.clip(c, 0, 255), a * 255], 2).astype(np.uint8)


def main():
    OUT.mkdir(exist_ok=True)
    for f in sorted(SRC.glob("*.jpg")):
        out = matte(np.array(Image.open(f).convert("RGB")))
        Image.fromarray(out, "RGBA").save(OUT / (f.stem + ".png"))
        print(f.name, "->", (OUT / (f.stem + '.png')).name)


if __name__ == "__main__":
    main()
