"""Placement-jitter test for Ren (no video needed): move and scale each approved Ren still smoothly over 60 frames, render
only its alpha channel with the OLD whole-pixel placement and the NEW sub-pixel placement, and compare the drawn centroid and
width with the exact analytic values. Rounding error shows up as noise (px). The new placement must stay under --max.

  project/.tools/venv/bin/python videos/free_money/jitter_check.py [--max 0.12]       exit 1 if the new placement is worse
"""
import argparse, sys
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parent))
import fm_rough as fr

W, H = 1280, 720


def old_place(frame, im, x, y, w, h):
    r = im.resize((max(1, round(w)), max(1, round(h))), Image.LANCZOS)
    xi, yi = int(round(x)), int(round(y))
    frame.alpha_composite(r, (max(xi, 0), max(yi, 0)))


def centroid(frame):
    a = np.asarray(frame)[..., 3].astype(float) / 255
    yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    s = a.sum()
    return (a * xx).sum() / s, (a * yy).sum() / s, a.sum(1 if False else 0).__len__() and s


def run(place, im, n=60):
    a = np.asarray(im)[..., 3].astype(float) / 255
    sy_, sx_ = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    cxs, cys = (a * sx_).sum() / a.sum() / im.width, (a * sy_).sum() / a.sum() / im.height     # alpha centroid as a fraction of the image
    area0 = a.sum() / (im.width * im.height)
    errs_x, errs_y, errs_a = [], [], []
    for i in range(n):
        t = i / (n - 1)
        h = 480 + 120 * t
        w = im.width * h / im.height
        x, y = 300 + 40.37 * t, 90 + 13.9 * t
        f = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        place(f, im, x, y, w, h)
        cx, cy, area = centroid(f)
        errs_x.append(cx - (x + cxs * w)); errs_y.append(cy - (y + cys * h)); errs_a.append(area - area0 * w * h)
    t = np.arange(n)
    res = lambda v: float(np.std(np.array(v) - np.polyval(np.polyfit(t, v, 3), t)))
    return res(errs_x), res(errs_y), res(errs_a) / (area0 * 480 * 480 * im.width / im.height)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--max", type=float, default=0.12)
    args = ap.parse_args()
    here = Path(__file__).resolve().parent / "matted"
    worst_old = worst_new = 0.0
    for name in ("Ren_1_neutral", "Ren_3_thinking_bust", "Ren_full_body_standing", "Ren_full_body_presenting"):
        im = Image.open(here / f"{name}.png").convert("RGBA")
        padded = Image.new("RGBA", (im.width + 80, im.height + 80), (0, 0, 0, 0))      # the busts are cropped flat; keep every edge interior so only the silhouette is measured
        padded.paste(im, (40, 40))
        im = padded
        o = run(old_place, im)
        nw = run(fr.paste_smooth, im)
        worst_old = max(worst_old, o[0], o[1]); worst_new = max(worst_new, nw[0], nw[1])
        print(f"{name:26s} OLD x={o[0]:.3f} y={o[1]:.3f}px   NEW x={nw[0]:.3f} y={nw[1]:.3f}px")
    print(f"WORST old {worst_old:.3f}px  new {worst_new:.3f}px  (limit {args.max})")
    sys.exit(0 if worst_new <= args.max else 1)
