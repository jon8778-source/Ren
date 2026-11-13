"""Matte the approved Maya sheets (white background) and split each into one transparent PNG per pose.
  project/.tools/venv/bin/python videos/unclaimed_401k/split_sheets.py
Art is local only (art/ is gitignored). Uses videos/free_money/matting.matte (edge flood fill + decontamination)."""
import glob, sys, json, hashlib
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "free_money"))
from matting import matte
UP = Path("/root/.claude/uploads/590afe13-c018-565e-8a11-4e40efc2d5b5")
SHEETS = {  # upload id -> (name, expected pose count, row-band tolerance px)
 "54533bb0": ("props", 9), "fce879d2": ("armchair", 3), "d6b3c413": ("stool", 8), "7a2f49f6": ("standing", 7),
 "5e0c276a": ("maya_take_folder", 1), "7a53db67": ("hr_offer_folder", 1), "3ac05e4b": ("drawer", 5),
 "72200fd0": ("walk_sit", 6), "60b52c83": ("receipt_laptop", 6), "675b8706": ("overshoulder", 4)}
def _runs(mask, min_gap):
    idx = np.where(mask)[0]
    if not len(idx): return []
    runs, st, pv = [], idx[0], idx[0]
    for i in idx[1:]:
        if i - pv > min_gap: runs.append((st, pv + 1)); st = i
        pv = i
    runs.append((st, pv + 1)); return runs
def split(rgba, n):
    """Projection split: horizontal bands separated by empty rows, then figures separated by empty columns."""
    a = rgba[..., 3] > 40
    out = []
    for y0, y1 in _runs(a.sum(1) > 0, 12):
        band = a[y0:y1]
        for x0, x1 in _runs(band.sum(0) > 0, 6):
            if band[:, x0:x1].sum() > 3000: out.append((slice(y0, y1), slice(x0, x1)))
    # touching figures: cut the widest box at the emptiest column in its middle third until n pieces
    while len(out) < n:
        i = max(range(len(out)), key=lambda k: out[k][1].stop - out[k][1].start)
        ys, xs = out[i]; w = xs.stop - xs.start
        prof = a[ys, xs].sum(0).astype(float); lo, hi = int(w * .38), int(w * .62)
        cut = xs.start + lo + int(np.argmin(prof[lo:hi]))
        a2 = a.copy()
        out[i:i + 1] = [(ys, slice(xs.start, cut)), (ys, slice(cut, xs.stop))]
    return out
def main():
    rep = {}
    for uid, (name, n) in SHEETS.items():
        p = glob.glob(str(UP / f"{uid}-image.*"))[0]
        rgb = np.array(Image.open(p).convert("RGB"))
        rgba = matte(rgb)
        Image.fromarray(rgba, "RGBA").save(HERE / "art/sheets" / f"{name}.png")
        boxes = split(rgba, n)
        ordered = [(b, 0) for b in boxes]
        out = []
        for j, (sl, _) in enumerate(ordered, 1):
            crop = Image.fromarray(rgba[sl], "RGBA"); bb = crop.getbbox(); crop = crop.crop(bb)
            f = HERE / "art/poses" / f"{name}_{j:02d}.png"; crop.save(f)
            out.append({"file": f.name, "size": crop.size, "sha256": hashlib.sha256(f.read_bytes()).hexdigest()[:16]})
        rep[name] = {"source": Path(p).name, "sheet_px": list(rgb.shape[1::-1]), "expected": n, "found": len(out), "poses": out}
        print(f"{name:18s} expected {n} found {len(out)}  sizes {[o['size'] for o in out]}")
    (HERE / "art/split_report.json").write_text(json.dumps(rep, indent=1))
main()
