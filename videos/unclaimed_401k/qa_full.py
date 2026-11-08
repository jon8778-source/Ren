"""QA for the full 401(k) episode MP4. Writes reports/full_qc.md; exit 1 on any FAIL. Supplements visual review, never replaces it.
  project/.tools/venv/bin/python videos/unclaimed_401k/qa_full.py OUT_DIR/episode.mp4
"""
import hashlib, json, re, subprocess, sys
from pathlib import Path
import numpy as np
from PIL import Image
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parents[1] / "project" / "cliplib"))
mp4 = Path(sys.argv[1]).resolve(); rep = json.loads((mp4.parent / (mp4.stem + "_report.json")).read_text())
import render_full as RF, render_pilot as R, pilot_ui as U, pilot_assets as A, pilot_ren as PR
from ren_stage import paste_smooth, height_px
FPS = 24; res = []; shots = rep["shots"]; NF = rep["frames"]
def check(name, ok, detail="", status=None):
    st = status or ("PASS" if ok else "FAIL"); res.append((name, st, detail)); print(f"{st} {name}" + (f"  [{detail}]" if detail else ""), flush=True)
def run(c): return subprocess.run(c, capture_output=True, text=True)
sh = RF.build_shots(); RF.SHOTS = sh; by_id = {s["id"]: s for s in sh}
CAPS = RF.CAPS
# 1 shot list
gaps = [(a["id"], b["id"]) for a, b in zip(shots, shots[1:]) if a["fb"] != b["fa"]]
check("1a shots contiguous from frame 0 to the last frame", not gaps and shots[0]["fa"] == 0 and shots[-1]["fb"] == NF, str(gaps[:5]))
over = [(s["id"], s["type"], round((s["fb"] - s["fa"]) / FPS, 2)) for s in shots if (s["fb"] - s["fa"]) / FPS > CAPS[s["type"]] + 1e-6]
check("1b v3 shot caps (Maya action / Ren 5.5, story still 2.5, graphic 3.5)", not over, str(over))
cnt = {t: sum(1 for s in shots if s["type"] == t) for t in ("CHARACTER_ACTION", "REN_ANIMATED", "GRAPHIC", "STORY_STILL")}
check("1c shot mix recorded", True, str(cnt) + f", {len(shots)} shots")
longest_still = max(((s["fb"] - s["fa"]) / FPS for s in shots if s["type"] == "GRAPHIC"), default=0)
# 2 script order: all phrases tile the whole approved script (S1 + S2 + ... + S8)
t = (HERE / "script" / "narration_v3.md").read_text(); parts = re.split(r"\*\*\[(S\d+): [^\]]*\]\*\*", t); secs = {parts[i]: " ".join(parts[i + 1].split()) for i in range(1, len(parts), 2)}
norm = lambda x: re.findall(r"[a-z0-9']+", x.lower().replace("’", "'").replace("$", ""))
want = norm(" ".join(secs[k] for k in ("S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8"))); got = norm(" ".join(s["phrase"] for s in shots))
check("2 shot phrases tile the whole approved script in order (S1-S8), unchanged", want == got, f"{len(want)} vs {len(got)} words")
tmw = sum(len(secs[k].split()) for k in secs); check("2b script is the approved v3 text (1001 words)", tmw == 1001, str(tmw))
# 3 assets
need = [A.ART / "plates" / p for p in ("H1.png", "O1_4k.png", "O2.png", "SAGE.png")] + [A.ART / "stills" / "D_alex_laptop.png"] + [R.VOICE / f"{k}.wav" for k in ["P1", "P2"] + RF.SECS]
miss = [p.name for p in need if not p.exists() or p.stat().st_size < 1000]; check("3 plates, stills and all narration WAVs exist", not miss, str(miss))
# 4 decode / format
r = run(["ffmpeg", "-v", "error", "-xerror", "-i", str(mp4), "-f", "null", "-"]); check("4a full decode clean (-xerror)", r.returncode == 0 and not r.stderr.strip(), r.stderr[:200])
pr = json.loads(run(["ffprobe", "-v", "error", "-show_streams", "-of", "json", str(mp4)]).stdout); v = next(s for s in pr["streams"] if s["codec_type"] == "video"); a = next(s for s in pr["streams"] if s["codec_type"] == "audio")
check("4b format 1920x1080 24 fps h264 + aac", (v["width"], v["height"], v["r_frame_rate"], v["codec_name"], a["codec_name"]) == (1920, 1080, "24/1", "h264", "aac"), f"{v['width']}x{v['height']} {v['r_frame_rate']}")
nb = int(run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0", str(mp4)]).stdout.strip())
check("4c frame count equals shot frames", nb == NF, f"{nb} vs {NF}")
dv, da = float(v["duration"]), float(a["duration"]); check("4d video and audio lengths within 0.1 s", abs(dv - da) < 0.1, f"video {dv:.3f}s audio {da:.3f}s")
check("4e narration length equals all sections joined as generated", abs(rep["audio_s"] - RF.TOTAL) < 0.01, f"{rep['audio_s']:.3f}s; episode {dv / 60:.2f} min")
p = run(["ffmpeg", "-nostats", "-i", str(mp4), "-af", "ebur128=peak=true", "-f", "null", "-"]).stderr
lufs = float(p[p.rindex("I:") + 2:].split()[0]); tp = float(p[p.rindex("Peak:") + 5:].split()[0]); check("4f loudness -23..-12 LUFS, true peak <= -1 dBTP", -23 <= lufs <= -12 and tp <= -1.0, f"{lufs} LUFS, {tp} dBTP")
sd = run(["ffmpeg", "-nostats", "-i", str(mp4), "-af", "silencedetect=n=-45dB:d=0.6", "-f", "null", "-"]).stderr
sil = [(float(s_), float(e_)) for s_, e_ in zip(re.findall(r"silence_start: ([\d.]+)", sd), re.findall(r"silence_end: ([\d.]+)", sd))]
check("4g no silence gap over 1.4 s inside the narration (sentence pauses and section joins allowed)", all(e_ - s_ <= 1.4 for s_, e_ in sil if e_ < dv - 1), str([(round(s_, 1), round(e_ - s_, 2)) for s_, e_ in sil if e_ - s_ > 1.0]))
# 5 frames: stream the decode in chunks (cuts, A-B-A inserts, flashes)
proc = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(mp4), "-vf", "scale=240:135,format=gray", "-f", "rawvideo", "-"], stdout=subprocess.PIPE)
fsz = 240 * 135; prev2 = prev1 = None; d1 = []; br = []; aba = []; idx = 0
while True:
    buf = proc.stdout.read(fsz)
    if len(buf) < fsz: break
    cur = np.frombuffer(buf, np.uint8).astype(np.int16); br.append(float(cur.mean()))
    if prev1 is not None:
        d1.append(float(np.abs(cur - prev1).mean()))
        if prev2 is not None:
            dab = float(np.abs(cur - prev2).mean())
            if dab < 0.35 * d1[-1] and d1[-1] > 3.0 and d1[-2] > 3.0: aba.append(idx - 1)
    prev2, prev1 = prev1, cur; idx += 1
d = np.array(d1); bounds = {s["fa"] for s in shots[1:]}
big = [i + 1 for i, x in enumerate(d) if x > 14]; off = [i for i in big if i not in bounds]
check("5a hard cuts (mean diff > 14) land only on shot boundaries", not off, f"off-boundary: {off[:10]}; {len(big)} cuts detected")
flat = [(s["id"], round(float(d[s["fa"] - 1]), 2)) for s in shots[1:] if d[s["fa"] - 1] < 0.25]
check("5b every shot boundary changes the picture (progressive graphics and pose changes count; nothing identical across a cut)", not flat, str(flat[:10]))
check("5c no A-B-A one-frame inserts", not aba, str(aba[:10]))
brr = np.array(br); fl = [i for i in range(1, len(brr) - 2) if abs(brr[i] - brr[i - 1]) > 12 and abs(brr[i + 1] - brr[i - 1]) < 5]
check("5d no single-frame brightness flashes", not fl, str(fl[:10]))
# 6 layout on sampled + boundary frames
bad, small_px, nums, ns = [], [], set(), 0
sample = sorted(set(list(range(FA0 := RF.FA0, NF, 12)) + [s["fa"] for s in shots if s["fa"] >= FA0] + [s["fb"] - 1 for s in shots if s["fa"] >= FA0 and s["fb"] - 1 < NF]))
for i in sample:
    _, sht, B = RF.frame_at(i); ns += 1
    for (x0, y0, x1, y1, s_, px) in B:
        if x0 < 40 or x1 > 1880 or y0 < 20 or y1 > 950: bad.append((i, s_, [round(v) for v in (x0, y0, x1, y1)]))
        if px < 32: small_px.append((i, s_, round(px)))
        nums.update(re.findall(r"\$?\d[\d,]*%?", s_))
check(f"6a all on-screen text inside the safe area (x 40..1880, y 20..950; bottom 12% empty), {ns} frames incl. every shot's first and last", not bad, str(bad[:5]))
check("6b on-screen text at least 32 px (device screens inside props are exempt)", not small_px, str(small_px[:5]))
allowed = {"$100", "$1,200", "$60,000", "$2,400", "$200", "$12", "$40", "$48", "$3,600", "$12,000", "$0", "2%", "4%", "100%", "50", "31", "401", "3", "1", "2", "4", "100", "0", "10", "1,200", "60,000", "2,400", "200", "12", "40", "48", "3,600", "12,000"}
check("6c every on-screen number is a checked claim", all(n in allowed or n.strip("$%") in allowed for n in nums), str(sorted(nums)))
# 7 arithmetic of every claim shown
ok = (60000 * 0.04 == 2400 and 60000 * 0.02 == 1200 and 2400 - 1200 == 1200 == 12 * 100 and 2400 / 12 == 200 and 12 + 40 + 48 == 100 and 3 * 1200 == 3600 and 10 * 1200 == 12000)
check("7 claim arithmetic (60,000 x 4% = 2,400; 2% = 1,200; gap 1,200 = 100/mo; 12+40+48 = 100; 3 x 1,200 = 3,600; 10 x 1,200 = 12,000)", ok)
# 8 jitter
def jitter(key, n=60):
    im0 = A.pose(key); im = Image.new("RGBA", (im0.width + 80, im0.height + 80), (0, 0, 0, 0)); im.paste(im0, (40, 40))
    al = np.asarray(im)[..., 3].astype(float) / 255; sy, sx = np.mgrid[0:im.height, 0:im.width]; cxs, cys = (al * sx).sum() / al.sum() / im.width, (al * sy).sum() / al.sum() / im.height
    ex, ey = [], []
    for k in range(n):
        t_ = k / (n - 1); h = 480 + 120 * t_; w = im.width * h / im.height; x, y = 300 + 40.37 * t_, 90 + 13.9 * t_
        fr_ = Image.new("RGBA", (900, 900), (0, 0, 0, 0)); paste_smooth(fr_, im, x, y, w, h); a_ = np.asarray(fr_)[..., 3].astype(float) / 255; gy, gx = np.mgrid[0:a_.shape[0], 0:a_.shape[1]]
        ex.append((a_ * gx).sum() / a_.sum() - (x + cxs * w)); ey.append((a_ * gy).sum() / a_.sum() - (y + cys * h))
    tt = np.arange(n); rs_ = lambda v_: float(np.std(np.array(v_) - np.polyval(np.polyfit(tt, v_, 3), tt))); return rs_(ex), rs_(ey)
worst = 0.0
for key in ("stool_01", "stool_05", "receipt_laptop_04", "receipt_laptop_06"):
    jx, jy = jitter(key); worst = max(worst, jx, jy)
check("8 Maya sub-pixel placement noise <= 0.12 px (jitter_check method)", worst <= 0.12, f"worst {worst:.3f}px")
# 9 Ren cutaways (all, pilot + new): library clips, movement, no camera move, grounding, layout
lib = {c["file"]: c for c in json.loads((R.ROOT / "assets" / "ren_library" / "ren_library.json").read_text())["clips"]}
exp_h = height_px("OFFICE_SAGE", 770) * PR.PK
ren_all = [s for s in shots if s["type"] == "REN_ANIMATED"]
def spec_of(sid):
    if sid in by_id: r_ = by_id[sid]["ren"]; return r_["clip"], r_["start"], r_["mirror"]
    c, st = R.REN_SPEC[sid.lower()]; return c, st, False
vf = lambda a_, b_: np.frombuffer(subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(mp4), "-vf", f"select='between(n,{a_},{b_ - 1})',format=rgb24", "-vsync", "0", "-f", "rawvideo", "-"]), np.uint8).reshape(-1, 1080, 1920, 3)
fails9 = []; last_clip = None; dup_clip = []
for s in ren_all:
    clip, st, mir = spec_of(s["id"]); n = s["fb"] - s["fa"]; ent = lib[clip + ".mp4"]
    if not (ent["status"] == "ok" and ent["in_s"] - 0.001 <= st and st + n / FPS <= ent["out_s"] + 0.01): fails9.append((s["id"], "window", clip, st))
    boxes = [RF.frame_at(i)[2] for i in range(s["fa"], s["fb"])]
    bot = np.array([b.ren[3] for b in boxes]); top = np.array([b.ren[1] for b in boxes]); ids = [b.ren_i for b in boxes]
    if not (bot.std() <= 1.0 and bot.max() - bot.min() <= 3.0): fails9.append((s["id"], "feet", round(float(bot.std()), 2)))
    hh = np.median(bot - top)
    if abs(hh - exp_h) / exp_h > 0.06: fails9.append((s["id"], "scale", round(float(hh))))
    if len(set(ids)) != n: fails9.append((s["id"], "distinct frames", len(set(ids))))
    V = vf(s["fa"], s["fb"]).astype(np.int16); dd = np.abs(np.diff(V, axis=0)).mean(3)
    x0, y0, x1, y1 = [int(v_) for v_ in (min(b.ren[0] for b in boxes) - 6, min(b.ren[1] for b in boxes) - 6, max(b.ren[2] for b in boxes) + 6, max(b.ren[3] for b in boxes) + 6)]
    mv = dd[:, max(y0, 0):y1, max(x0, 0):x1].mean((1, 2))
    if n > 3 and not (mv.mean() > 0.2 and (mv > 0.1).sum() >= 0.5 * len(mv)): fails9.append((s["id"], "movement", round(float(mv.mean()), 2)))
    rf = [np.asarray(RF.frame_at(i)[0].convert("RGB"))[0:200, 1000:1900].astype(np.int16) for i in (s["fa"], s["fa"] + n // 2, s["fb"] - 1)]
    if max(int(np.abs(rf[k + 1] - rf[k]).max()) for k in range(2)) != 0: fails9.append((s["id"], "camera/background changed"))
    mid = boxes[len(boxes) // 2]
    if not ((mid.ren[0] + mid.ren[2]) / 2 < 960 and not [b for b in mid if b[4] != "Ren" and b[0] < mid.ren[2]]): fails9.append((s["id"], "layout"))
    del V
for a_, b_ in zip(shots, shots[1:]):
    if a_["type"] == "REN_ANIMATED" and b_["type"] == "REN_ANIMATED" and spec_of(a_["id"])[0] == spec_of(b_["id"])[0]: dup_clip.append((a_["id"], b_["id"]))
check(f"9a all {len(ren_all)} Ren cutaways: approved library clips inside their usable windows, feet fixed (no bobbing), scale = 175 cm standard, every frame a distinct clip frame, real movement, static camera, Ren left / graphics right", not fails9, str(fails9[:6]))
check("9b consecutive Ren shots never repeat the same clip", not dup_clip, str(dup_clip))
# 10 Maya continuity / acting / grounding in the new shots
pilot_end = RF.FA0
weak, pos_bad = [], []
for s in sh:
    if s["kind"] != "maya": continue
    cam = RF.CAMS[s["camk"]]; X, Y = cam.pt(*R.O1S); seen = []
    for i in range(s["fa"], s["fb"], 2):
        b = RF.frame_at(i)[2]; seen.extend(b.poses)
        if abs(b.maya[0] - X) > 0.01 or abs(b.maya[1] - Y) > 0.01 or abs(b.maya[2] / A.scale_of(b.poses[0]) - R.S0 * cam.z) > 1e-3: pos_bad.append((s["id"], i))
    if len(set(seen)) < 2: weak.append(s["id"])
check("10a Maya sits on the same office floor spot in every new Maya shot; scale follows the camera zoom exactly (grounded)", not pos_bad, str(pos_bad[:4]))
check("10b every new Maya shot changes pose (no shot is only a pan or zoom over a still)", not weak, str(weak))
prev = None; same = []
for s in sh:
    if s["kind"] == "maya":
        first = RF.frame_at(s["fa"])[2].poses[0]; last = RF.frame_at(s["fb"] - 1)[2].poses[-1]
        if prev and prev[0] == s["camk"] and prev[1] == first: same.append(s["id"])
        prev = (s["camk"], last)
    else: prev = None
check("10c no repeated identical pose and framing across consecutive Maya shots", not same, str(same))
# 11 24 fps
pk = [float(x) for x in run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "packet=pts_time", "-of", "csv=p=0", str(mp4)]).stdout.split()]
dpk = np.diff(sorted(pk)); check("11 constant 24 fps: r/avg_frame_rate 24/1, every packet 1/24 s apart, no dropped or duplicated timestamps", (v["r_frame_rate"], v["avg_frame_rate"]) == ("24/1", "24/1") and np.allclose(dpk, 1 / 24, atol=2e-4) and len(pk) == NF, f"{len(pk)} packets, delta {dpk.min():.5f}-{dpk.max():.5f}")
# 12 voice
hs = {f"{k}.wav": hashlib.sha256((R.VOICE / f"{k}.wav").read_bytes()).hexdigest() for k in ["P1", "P2"] + RF.SECS}
ref = json.loads((HERE / "voice_hashes.json").read_text()); pil_ok = all(hs[k] == ref[k] for k in ("P1.wav", "P2.wav"))
check("12a pilot narration WAVs byte-identical to the approved pilot's (not regenerated)", pil_ok)
src = "".join((HERE / f_).read_text() for f_ in ("render_full.py", "render_pilot.py", "pilot_ren.py", "pilot_assets.py", "pilot_ui.py", "full_ui.py", "full_plan.py"))
check("12b renderers import and call no TTS code", not re.search(r"^\s*(import|from)\s+(qwen_tts|torch|transformers)|generate_voice_clone|create_voice_clone_prompt", src, re.M))
au_raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(mp4), "-ac", "1", "-ar", "24000", "-f", "f32le", "-"]); got_a = np.frombuffer(au_raw, np.float32)
ref_a, _ = RF.audio(); m = min(len(got_a), len(ref_a)); cc = float(np.dot(got_a[:m], ref_a[:m]) / (np.linalg.norm(got_a[:m]) * np.linalg.norm(ref_a[:m]) + 1e-9))
check("12c MP4 audio matches the narration waveform (correlation >= 0.95)", cc >= 0.95, f"{cc:.4f}")
out = HERE / "reports"; out.mkdir(exist_ok=True)
md = ["# Full-episode QC - Ren | Unclaimed 401(k) match", "", f"File: `{mp4.name}` | {NF} frames | 1920x1080 @ 24 fps | {dv / 60:.2f} min", "", "Command: `project/.tools/venv/bin/python videos/unclaimed_401k/qa_full.py <mp4>`; thresholds are in the script and were not relaxed.", "", "| Check | Result | Measured |", "|---|---|---|"]
for n_, st, dt in res: md.append(f"| {n_} | {st} | {dt.replace('|', '/')[:220]} |")
md += ["", "## Not run / limits", "- NOT RUN: listening review (pronunciation, accent, tone, joins). Speech-to-text only confirms the words.", "- NOT RUN: the repo's older qa_timeline.py, validate.py, jitter_check.py (wired to the 720p free_money renderer); their checks are re-implemented here.",
       "- Ren: genuine library clips only; mouth-closed windows chosen from library notes, checked by eye on contact sheets, not by an automated mouth detector.",
       "- Maya is limited animation from approved keyframe poses, not a skeletal rig. Alex appears only as the approved story still."]
(out / "full_qc.md").write_text("\n".join(md) + "\n")
fails = [n_ for n_, st, _ in res if st == "FAIL"]; print("\nOVERALL", "FAIL: " + "; ".join(fails) if fails else "PASS"); sys.exit(1 if fails else 0)
