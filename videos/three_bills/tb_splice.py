"""Targeted re-render: replace only the changed shots of an existing episode, copying every other GOP unchanged.

  project/.tools/venv/bin/python videos/three_bills/tb_splice.py OLD.mp4 NEW_DIR F08 F38 F81 F86

Changed shots' frame ranges are widened to the enclosing keyframes of OLD.mp4 (g=48), re-rendered with the same encoder settings, and joined to the stream-copied
untouched parts; the audio is the old file's audio track, copied (no new narration, no re-encode of unchanged video).
"""
import json, subprocess, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / "unclaimed_401k")); sys.path.insert(0, str(HERE.parents[1] / "project" / "cliplib"))
import tb_full as TF
old = Path(sys.argv[1]).resolve(); out = Path(sys.argv[2]).resolve(); ids = sys.argv[3:]; out.mkdir(parents=True, exist_ok=True); FPS = 24; NF = TF.NFR
pk = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "packet=pts_time,flags", "-of", "csv=p=0", str(old)]).decode().split()
kf = sorted(round(float(l.split(",")[0]) * FPS) for l in pk if "K" in l.split(",")[1])
S = {s["id"]: s for s in TF.SHOTS}; rngs = []
for i in ids:
    lo = max(k for k in kf if k <= S[i]["fa"]); hi = min([k for k in kf if k >= S[i]["fb"]] + [NF]); rngs.append([lo, hi])
rngs.sort(); merged = []
for r in rngs:
    if merged and r[0] <= merged[-1][1]: merged[-1][1] = max(merged[-1][1], r[1])
    else: merged.append(r)
print("re-render ranges (frames):", merged, "of", NF, f"= {sum(b - a for a, b in merged)} frames")
parts = []; cur = 0
for a, b in merged:
    if a > cur: parts.append(("old", cur, a))
    parts.append(("new", a, b)); cur = b
if cur < NF: parts.append(("old", cur, NF))
files = []
for k, (kind, a, b) in enumerate(parts):
    f = out / f"_p{k}_{kind}.mp4"
    if kind == "old": subprocess.check_call(["ffmpeg", "-y", "-v", "error", "-ss", f"{a / FPS:.6f}", "-i", str(old), "-frames:v", str(b - a), "-an", "-c:v", "copy", "-avoid_negative_ts", "make_zero", str(f)])
    else:
        p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1920x1080", "-r", "24", "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "15", "-pix_fmt", "yuv420p", "-g", "48", str(f)], stdin=subprocess.PIPE)
        for i in range(a, b): fr, _, _ = TF.frame_at(i); p.stdin.write(fr.convert("RGB").tobytes())
        p.stdin.close(); assert p.wait() == 0
    files.append(f); print(kind, a, b, flush=True)
lst = out / "_parts.txt"; lst.write_text("".join(f"file '{f}'\n" for f in files)); vid = out / "_video.mp4"
subprocess.check_call(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(vid)])
mp4 = out / "episode.mp4"; subprocess.check_call(["ffmpeg", "-y", "-v", "error", "-i", str(vid), "-i", str(old), "-map", "0:v", "-map", "1:a", "-c", "copy", "-movflags", "+faststart", str(mp4)])
for f in files + [lst, vid]: f.unlink()
rep = json.loads((old.parent / (old.stem + "_report.json")).read_text()); rep["video"] = mp4.name; rep["revision"] = {"replaced_shots": ids, "rerendered_frames": merged}; (out / "episode_report.json").write_text(json.dumps(rep, indent=1)); print("done", mp4)
