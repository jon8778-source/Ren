"""Frame-by-frame mouth-open detector for Ren library clips (heuristic, then confirm by eye). Mouth zone = lower middle of the face; a closed smile is a thin line, an open mouth adds dark interior or white teeth.
Prints, per clip, the clip-time intervals judged mouth-closed (all frames, 2-frame margin) of at least 2.0 s. Writes voice-independent evidence to evidence/mouth_scan.json."""
import sys, json
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "videos" / "unclaimed_401k")); sys.path.insert(0, str(ROOT / "project" / "cliplib"))
import pilot_ren as PR
lib = {e['source_name'].split(' (')[0]: e for e in json.load(open(ROOT / 'assets/ren_library/ren_library.json'))['clips']}
def scan(clip):
    e = lib.get(clip) or lib[clip.replace("palm_left", "palm_right")]; a, b = e['in_s'], min(e['out_s'], 9.95); rc = PR.RenClip(clip, a, b - a); h = rc.h_clip; x0, y0, _, _ = rc.box; fx = int(rc.cx - x0); fy = int(rc.top - y0)
    m = []
    for im in rc.imgs:
        arr = np.asarray(im.convert("RGBA")).astype(float); z = arr[fy + int(0.125 * h):fy + int(0.165 * h), fx - int(0.035 * h):fx + int(0.035 * h)]; al = z[..., 3] > 128; lum = z[..., :3].mean(2)
        m.append(float((((lum < 95) | (lum > 238)) & al).sum()) / max(1, al.sum()))
    m = np.array(m); base = np.median(m); thr = base + max(0.04, 4 * np.median(np.abs(m - base))); bad = m > thr
    ok = ~np.convolve(bad.astype(int), np.ones(5, int), "same").astype(bool); iv = []; s = None
    for i, v in enumerate(list(ok) + [False]):
        if v and s is None: s = i
        if not v and s is not None:
            if (i - s) / 24 >= 2.0: iv.append((round(a + s / 24, 2), round(a + i / 24, 2)))
            s = None
    return dict(window=(a, b), base=round(base, 3), thr=round(float(thr), 3), flagged_frames=int(bad.sum()), n=len(m), closed_intervals=iv)
if __name__ == "__main__":
    ev = HERE / "evidence" / "mouth_scan.json"; ev.parent.mkdir(exist_ok=True); out = json.loads(ev.read_text()) if ev.exists() else {}
    for clip in sys.argv[1:]: out[clip] = scan(clip); print(clip, json.dumps(out[clip]), flush=True); ev.write_text(json.dumps(out, indent=1))
