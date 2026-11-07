"""Before/after numbers for pilot v1 and revision 2 (decodes both MP4s; nothing is rendered).

  project/.tools/venv/bin/python videos/free_money/compare.py /output/free_money_S1_S2_pilot.mp4 /output/free_money_S1_S2_pilot_rev02.mp4
"""
import json, subprocess, sys
from pathlib import Path
import numpy as np


def motion(mp4):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(mp4), "-vf", "scale=160:90,format=gray", "-f", "rawvideo", "-"])
    f = np.frombuffer(raw, np.uint8).reshape(-1, 90, 160).astype(np.float32)
    d = np.abs(np.diff(f, axis=0)).mean((1, 2))
    cuts = int((d > 12).sum())
    static = d < 0.12
    run = best = 0
    for s in static:
        run = run + 1 if s else 0
        best = max(best, run)
    return {"frames": len(f), "mean_motion": round(float(d.mean()), 2), "share_static_frames": round(float(static.mean()), 3), "longest_static_s": round(best / 24, 1), "hard_cuts_detected": cuts}


rows = {}
for p in map(Path, sys.argv[1:]):
    rep = json.loads((p.parent / (p.stem + "_report.json")).read_text())
    shots = rep["shots"]
    dur = [s["end"] - s["start"] for s in shots]
    rows[p.stem] = {"shots": len(shots), "avg_shot_s": round(sum(dur) / len(dur), 2), "longest_shot_s": round(max(dur), 2), **motion(p)}
print(json.dumps(rows, indent=1))
