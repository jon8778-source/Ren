"""Technical QA for the Black Friday pilot (run on the final MP4 and layout.json). Checks: stream facts, full decode (errors fatal), hard cuts only on shot starts, shot caps, text layout (min size, margins,
no card/text over Ren), displayed figures against assumptions, audio level and length. Writes qa_report.md next to the video. Visual checks (contact sheets, 100% crops, mouths) are separate and manual."""
import json, re, subprocess, sys
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE)); import bf_ui as B
out = Path(sys.argv[1]); mp4 = out / "pilot.mp4"; lay = json.loads((out / "layout.json").read_text()); shots = lay["shots"]; FPS = 24; res = []; fail = 0
def ok(name, cond, detail=""):
    global fail; fail += 0 if cond else 1; res.append(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")
pr = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-count_frames", "-show_entries", "stream=codec_name,width,height,r_frame_rate,nb_read_frames,duration", "-of", "json", str(mp4)]))["streams"]
v = next(s for s in pr if s["codec_name"] == "h264"); a = next(s for s in pr if s["codec_name"] == "aac"); total = shots[-1]["end"]
ok("video 1280x720 24 fps", (v["width"], v["height"], v["r_frame_rate"]) == (1280, 720, "24/1"), f'{v["width"]}x{v["height"]} {v["r_frame_rate"]}')
ok("frame count = shot table", int(v["nb_read_frames"]) == total, f'{v["nb_read_frames"]} vs {total}'); ok("audio/video length within 0.05 s", abs(float(a["duration"]) - float(v["duration"])) < 0.05, f'{a["duration"]} vs {v["duration"]}')
dec = subprocess.run(["ffmpeg", "-v", "error", "-xerror", "-i", str(mp4), "-f", "null", "-"], capture_output=True, text=True); ok("full decode, errors fatal", dec.returncode == 0 and not dec.stderr.strip(), dec.stderr[:120])
ok("shots contiguous from frame 0", shots[0]["start"] == 0 and all(a_["end"] == b_["start"] for a_, b_ in zip(shots, shots[1:])))
CAP = {"R": 5.5, "S": 2.5, "G": 3.5}; over = [s["id"] for s in shots if (s["end"] - s["start"]) / FPS > CAP[s["kind"]] + 1e-9]; ok("shot caps (Ren 5.5 / still 2.5 / graphic 3.5 s)", not over, str(over))
raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(mp4), "-vf", "scale=160:90,format=gray", "-f", "rawvideo", "-"]); fr = np.frombuffer(raw, np.uint8).reshape(-1, 90, 160).astype(np.float32)
d = np.abs(np.diff(fr, axis=0)).mean((1, 2)); starts = {s["start"] for s in shots}; med = np.median(d); cuts = [i + 1 for i, x in enumerate(d) if x > max(6.0, 8 * med)]
near = [c for c in cuts if c in starts or c - 1 in starts or c + 1 in starts]; ent = [c for c in cuts if c not in near and any(0 < c - st <= 13 for st in starts)]; bad = [c for c in cuts if c not in near and c not in ent]
ok("hard cuts only at shot starts; other large changes only inside a 13-frame entrance animation (pop/slide) after a cut", not bad, f"{len(cuts)} large frame changes: {len(near)} at cuts, {len(ent)} in entrance animations, unexplained: {bad}")
ok("no 1-2 frame shots", all(s["end"] - s["start"] > 2 for s in shots), str([s["id"] for s in shots if s["end"] - s["start"] <= 2]))
items = lay["items"]; small = [i for i in items if i[7] < 36]; ok("all text >= 36 px at 1080p (= 24 px in the 720p file)", not small, str([(i[0], i[6]) for i in small][:5]))
marg = [i for i in items if i[2] < 55 or i[3] < 40 or i[4] > 1920 - 55 or i[5] > 1080 - 40]; ok("text inside 55 px side / 40 px vertical margins", not marg, str([(i[0], i[6]) for i in marg][:5]))
ren = {}
for k, sid, T_, x0, y0, x1, y1 in lay["ren"]: r = ren.setdefault(sid, [1e9, 1e9, -1, -1]); r[0] = min(r[0], x0); r[1] = min(r[1], y0); r[2] = max(r[2], x1); r[3] = max(r[3], y1)
ov = []
for i in items:
    r = ren.get(i[0])
    if r and not (i[4] < r[0] or i[2] > r[2] or i[5] < r[1] or i[3] > r[3]) and i[6] not in ("Educational only, not financial advice.", "Example figures"): ov.append((i[0], i[6]))
ok("no card text overlaps Ren's bounding box", not ov, str(ov))
shown = " ".join(i[6] for i in items); nums = sorted(set(re.findall(r"\$[\d,]+", shown))); allowed = {B.usd(x) for x in B.ALLOWED}
ok("every displayed dollar figure is in the checked table", set(nums) <= allowed, f"shown {nums}, allowed {sorted(allowed)}")
ok("figure values: 158+183=341, 158+105=263, 341-263=78, 48+30=78, 300", B.V["list_sale"] + B.V["impulse"] == B.V["all_in"] and B.V["list_sale"] + B.V["earbuds"] == B.V["rule_path"] and B.V["all_in"] - B.V["rule_path"] == 78 == B.V["airfryer"] + B.V["bundle"])
e = subprocess.run(["ffmpeg", "-nostats", "-i", str(mp4), "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr; I = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", e)[-1]); P = float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", e)[-1])
ok("loudness -17..-15 LUFS, true peak <= -1 dBFS", -17 <= I <= -15 and P <= -1, f"{I} LUFS, {P} dBFS")
(out / "qa_report.md").write_text("# Pilot technical QA\n\n" + "\n".join(f"- {r}" for r in res) + f"\n\n{len(res) - fail}/{len(res)} checks passed.\n"); print("\n".join(res)); print(len(res) - fail, "/", len(res)); sys.exit(1 if fail else 0)
