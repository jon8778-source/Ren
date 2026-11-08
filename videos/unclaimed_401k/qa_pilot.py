"""QA for the 401(k) pilot MP4. Writes reports/hybrid_qc.md and exits 1 on any FAIL. Supplements visual review, never replaces it.

  project/.tools/venv/bin/python videos/unclaimed_401k/qa_pilot.py OUT_DIR/pilot.mp4
Checks: shot list (contiguous, frame-aligned, v3 caps), phrases tile the approved narration in order, assets exist, full decode (errors fatal),
format, A/V length, loudness, silence gaps, hard cuts only on shot boundaries, no A-B-A inserts or flashes, on-screen text inside the safe area and
large enough, every on-screen number is a checked claim, Maya placement jitter (sub-pixel limit 0.12 px).
"""
import json, re, subprocess, sys
from pathlib import Path
import numpy as np
from PIL import Image
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parents[1] / "project" / "cliplib"))
mp4 = Path(sys.argv[1]).resolve(); rep = json.loads((mp4.parent / (mp4.stem + "_report.json")).read_text())
import render_pilot as R, pilot_ui as U, pilot_assets as A
from ren_stage import paste_smooth
FPS = 24; res = []; lines = []
def check(name, ok, detail="", status=None):
    st = status or ("PASS" if ok else "FAIL"); res.append((name, st, detail)); print(f"{st} {name}" + (f"  [{detail}]" if detail else ""), flush=True)
def run(c): return subprocess.run(c, capture_output=True, text=True)
shots = rep["shots"]; fr = lambda x: round(x * FPS)
# 1 shot list
gaps = [(a["id"], b["id"]) for a, b in zip(shots, shots[1:]) if fr(a["end"]) != fr(b["start"])]
check("1a shots contiguous", not gaps, str(gaps))
check("1b shot frames add up to the video", sum(fr(s["end"]) - fr(s["start"]) for s in shots) == rep["frames"], f"{sum(fr(s['end']) - fr(s['start']) for s in shots)} vs {rep['frames']}")
over = [(s["id"], round(s["end"] - s["start"], 2)) for s in shots if s["end"] - s["start"] > R.CAPS[s["type"]] + 1e-6]
check("1c v3 shot caps (CHARACTER_ACTION 5.5, STORY_STILL 2.5, GRAPHIC 3.5)", not over, str(over))
cnt = [sum(1 for s in shots if s["type"] == t) for t in ("CHARACTER_ACTION", "GRAPHIC", "STORY_STILL", "REN_ANIMATED")]
check("1d shot mix: 14 Maya action, 2 graphic, 1 story still, 2 Ren cutaways", cnt == [14, 2, 1, 2], str(cnt))
check("1e one or two Ren cutaways, each within the 5.5 s cap", 1 <= cnt[3] <= 2)
# 2 order
tm = json.loads((R.VOICE / "timings.json").read_text())
norm = lambda t: re.findall(r"[a-z0-9$']+", t.lower().replace("’", "'"))
want = norm(tm["P1"]["text"] + " " + tm["P2"]["text"]); got = norm(" ".join(s["phrase"] for s in shots))
fixed = lambda ws: [w.replace("$", "") for w in ws]
check("2 phrases tile the approved narration in order", fixed(want) == fixed(got) or " ".join(want).replace("$", "") == " ".join(got).replace("$", ""), f"{len(want)} vs {len(got)} words")
def _script_secs():
    t = (HERE / "script" / "narration_v3.md").read_text(); parts = re.split(r"\*\*\[(S\d+): [^\]]*\]\*\*", t)
    return {parts[i]: " ".join(parts[i + 1].split()) for i in range(1, len(parts), 2)}
sc = _script_secs(); s2 = sc["S2"]; cut = s2.index("so she moved on.") + len("so she moved on.")
check("2b spoken text equals the approved script (S1 + S2 up to 'so she moved on.'), unchanged", norm(sc["S1"] + " " + s2[:cut]) == want)
# 3 assets
need = [R.A.ART / "plates" / p for p in ("H1.png", "O1.png", "O2.png")] + [R.VOICE / "P1.wav", R.VOICE / "P2.wav", R.A.ART / "props" / "coin_front.png"]
miss = [p.name for p in need if not p.exists() or p.stat().st_size < 1000]; check("3 plates, voice and props exist", not miss, str(miss))
# 4 decode / format
r = run(["ffmpeg", "-v", "error", "-xerror", "-i", str(mp4), "-f", "null", "-"]); check("4a full decode clean (-xerror)", r.returncode == 0 and not r.stderr.strip(), r.stderr[:200])
pr = json.loads(run(["ffprobe", "-v", "error", "-show_streams", "-of", "json", str(mp4)]).stdout); v = next(s for s in pr["streams"] if s["codec_type"] == "video"); a = next(s for s in pr["streams"] if s["codec_type"] == "audio")
check("4b format 1920x1080 24 fps h264 + aac", (v["width"], v["height"], v["r_frame_rate"], v["codec_name"], a["codec_name"]) == (1920, 1080, "24/1", "h264", "aac"), f"{v['width']}x{v['height']} {v['r_frame_rate']} {v['codec_name']}/{a['codec_name']}")
nb = int(run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0", str(mp4)]).stdout.strip())
check("4c frame count equals shot frames", nb == rep["frames"], f"{nb} vs {rep['frames']}")
dv, da = float(v["duration"]), float(a["duration"]); check("4d video and audio lengths within 0.1 s", abs(dv - da) < 0.1, f"video {dv:.3f}s audio {da:.3f}s")
check("4e narration length equals P1+P2 as generated", abs(rep["audio_s"] - (tm["P1"]["duration"] + tm["P2"]["duration"])) < 0.01, f"{rep['audio_s']:.3f}s")
p = run(["ffmpeg", "-nostats", "-i", str(mp4), "-af", "ebur128=peak=true", "-f", "null", "-"]).stderr
lufs = float(p[p.rindex("I:") + 2:].split()[0]); tp = float(p[p.rindex("Peak:") + 5:].split()[0]); check("4f loudness -23..-12 LUFS, true peak <= -1 dBTP", -23 <= lufs <= -12 and tp <= -1.0, f"{lufs} LUFS, {tp} dBTP")
sd = run(["ffmpeg", "-nostats", "-i", str(mp4), "-af", "silencedetect=n=-45dB:d=0.6", "-f", "null", "-"]).stderr
sil = [(float(s), float(e)) for s, e in zip(re.findall(r"silence_start: ([\d.]+)", sd), re.findall(r"silence_end: ([\d.]+)", sd))]
check("4g no silence gap over 1.2 s inside the narration (natural 0.6-1.0 s sentence pauses allowed)", all(e - s <= 1.2 for s, e in sil if e < dv - 1), str([(round(s, 2), round(e - s, 2)) for s, e in sil]))
# 5 frames: cuts, inserts, flashes
raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(mp4), "-vf", "scale=240:135,format=gray", "-f", "rawvideo", "-"]); F = np.frombuffer(raw, np.uint8).reshape(-1, 135, 240).astype(np.float32)
d = np.abs(np.diff(F, axis=0)).mean((1, 2)); bounds = {s["fa"] for s in R.SHOTS[1:]}
big = [i + 1 for i, x in enumerate(d) if x > 14]; off = [i for i in big if i not in bounds]
check("5a hard cuts (mean diff > 14) land only on shot boundaries", not off, f"off-boundary: {off}; detected {len(big)} cuts")
miss_cut = [(s['id'], round(float(d[s['fa'] - 1]), 1)) for s in R.SHOTS[1:] if d[s['fa'] - 1] < 2.0]
check("5b every shot boundary is a visible cut (diff >= 2 (pose-only changes are small); the portal label swap P06->P07 is allowed to be small)", all(x[0] == "P07" for x in miss_cut), str(miss_cut), "PASS" if all(x[0] == "P07" for x in miss_cut) else "FAIL")
aba = [i + 1 for i in range(1, len(F) - 1) if np.abs(F[i + 1] - F[i - 1]).mean() < 0.35 * np.abs(F[i] - F[i - 1]).mean() and np.abs(F[i] - F[i - 1]).mean() > 3.0]
check("5c no A-B-A one-frame inserts", not aba, str(aba[:10]))
br = F.mean((1, 2)); fl = [i for i in range(1, len(br) - 2) if abs(br[i] - br[i - 1]) > 12 and abs(br[i + 1] - br[i - 1]) < 5]
check("5d no single-frame brightness flashes", not fl, str(fl[:10]))
# 6 layout (re-render sample frames in-process; text boxes come from the renderer)
bad, small_px, nums, nb_samples = [], [], set(), 0
for i in range(0, rep["frames"], 6):
    _, sh, B = R.frame_at(i); nb_samples += 1
    for (x0, y0, x1, y1, s, px) in B:
        if x0 < 40 or x1 > 1880 or y0 < 20 or y1 > 950: bad.append((i, s, [round(v) for v in (x0, y0, x1, y1)]))
        if px < 32: small_px.append((i, s, px))
        nums.update(re.findall(r"\$?\d[\d,]*%?", s))
check(f"6a all on-screen text inside the safe area (x 40..1880, y 20..950; bottom 12% empty), {nb_samples} sampled frames", not bad, str(bad[:5]))
check("6b on-screen text at least 32 px (device screens inside props are exempt)", not small_px, str(small_px[:5]))
allowed = {"$100", "$1,200", "$60,000", "2%", "31", "401", "3", "1", "2", "4", "100", "0"}
check("6c every on-screen number is a checked claim", all(n.strip("$%,") and n in allowed or n.strip("$%") in allowed for n in nums), str(sorted(nums)))
# 7 maths of the claims
C = U.CLAIMS; ok = (C["salary"] * 0.02 == 1200 and C["salary"] * 0.04 == 2400 and C["salary"] * 0.04 - C["salary"] * 0.02 == C["unclaimed_year"] == 12 * C["unclaimed_month"] and 12 + 40 + 48 == 100)
check("7 claim arithmetic (60,000 x 2% = 1,200; match gap 1,200/yr = 100/mo)", ok)
# 8 Maya placement jitter (same method as videos/free_money/jitter_check.py: residual noise after removing the smooth trend, drawn centroid vs exact)
def jitter(key, n=60):
    im0 = A.pose(key); im = Image.new("RGBA", (im0.width + 80, im0.height + 80), (0, 0, 0, 0)); im.paste(im0, (40, 40))
    al = np.asarray(im)[..., 3].astype(float) / 255; sy, sx = np.mgrid[0:im.height, 0:im.width]
    cxs, cys = (al * sx).sum() / al.sum() / im.width, (al * sy).sum() / al.sum() / im.height
    ex, ey = [], []
    for k in range(n):
        t = k / (n - 1); h = 480 + 120 * t; w = im.width * h / im.height; x, y = 300 + 40.37 * t, 90 + 13.9 * t
        fr_ = Image.new("RGBA", (900, 900), (0, 0, 0, 0)); paste_smooth(fr_, im, x, y, w, h)
        a = np.asarray(fr_)[..., 3].astype(float) / 255; gy, gx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
        ex.append((a * gx).sum() / a.sum() - (x + cxs * w)); ey.append((a * gy).sum() / a.sum() - (y + cys * h))
    tt = np.arange(n); resid = lambda v: float(np.std(np.array(v) - np.polyval(np.polyfit(tt, v, 3), tt)))
    return resid(ex), resid(ey)
worst = 0.0; det = []
for key in ("stool_01", "stool_05", "maya_nochair_02", "walk_sit_01", "receipt_laptop_04"):
    jx, jy = jitter(key); worst = max(worst, jx, jy); det.append(f"{key} x={jx:.3f} y={jy:.3f}")
check("8 Maya sub-pixel placement noise <= 0.12 px over a 60-frame move and scale (jitter_check method)", worst <= 0.12, f"worst {worst:.3f}px; " + "; ".join(det))

# 9 Ren cutaways: genuine library clips, real movement, no camera move, grounding, layout (left Ren, right graphics)
lib = {c["file"]: c for c in json.loads((R.ROOT / "assets" / "ren_library" / "ren_library.json").read_text())["clips"]}
ren_shots = [s for s in R.SHOTS if s["type"] == "REN_ANIMATED"]
import pilot_ren as PR
from ren_stage import height_px
exp_h = height_px("OFFICE_SAGE", 770) * PR.PK
vf = lambda a, b: np.frombuffer(subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(mp4), "-vf", f"select='between(n,{a},{b - 1})',format=rgb24", "-vsync", "0", "-f", "rawvideo", "-"]), np.uint8).reshape(-1, 1080, 1920, 3)
for sh in ren_shots:
    key = sh["id"].lower(); clip, st = R.REN_SPEC[key]; ent = lib[clip + ".mp4"]; n = sh["fb"] - sh["fa"]
    ok = ent["status"] == "ok" and ent["in_s"] <= st and st + n / FPS <= ent["out_s"] + 0.01
    check(f"9a {sh['id']} uses approved library clip {clip}.mp4 inside its usable window ({ent['in_s']}-{ent['out_s']} s)", ok, f"plays {st:.2f}-{st + n / FPS:.2f} s; shot {n / FPS:.2f} s <= 5.5")
    boxes = [R.frame_at(i)[2] for i in range(sh["fa"], sh["fb"])]
    bot = np.array([b.ren[3] for b in boxes]); top = np.array([b.ren[1] for b in boxes]); idx = [b.ren_i for b in boxes]
    check(f"9b {sh['id']} Ren feet fixed on the floor (no bobbing): bottom row std {bot.std():.2f}px", bot.std() <= 1.0 and bot.max() - bot.min() <= 3.0, f"min {bot.min():.1f} max {bot.max():.1f}")
    hh = bot - top; check(f"9c {sh['id']} Ren scale matches the plate standard (175 cm = {exp_h:.0f}px): measured {np.median(hh):.0f}px", abs(np.median(hh) - exp_h) / exp_h < 0.05)
    V = vf(sh["fa"], sh["fb"]).astype(np.int16); d = np.abs(np.diff(V, axis=0)).mean(3)
    x0, y0, x1, y1 = [int(v) for v in (min(b.ren[0] for b in boxes) - 6, min(b.ren[1] for b in boxes) - 6, max(b.ren[2] for b in boxes) + 6, max(b.ren[3] for b in boxes) + 6)]
    ren_move = d[:, max(y0, 0):y1, max(x0, 0):x1].mean((1, 2)); bg = d[:, 0:200, 1000:1900].mean((1, 2))
    check(f"9d {sh['id']} Ren genuinely moves: mean in-box change {ren_move.mean():.2f}/255, moving in {int((ren_move > 0.15).sum())} of {len(ren_move)} frame steps, {len(set(idx))} distinct clip frames", ren_move.mean() > 0.3 and (ren_move > 0.15).sum() >= 0.6 * len(ren_move) and len(set(idx)) == n)
    check(f"9e {sh['id']} no camera move: static background region change {bg.max():.3f}", bg.max() < 0.01)
    mid = boxes[len(boxes) // 2]; tb = [b for b in mid if True]
    xs = [b[0] for b in mid]; clash = [b for b in mid if not (b[2] < mid.ren[0] or b[0] > mid.ren[2] or b[3] < mid.ren[1] or b[1] > mid.ren[3])]
    check(f"9f {sh['id']} Ren on the left, graphics on the right, no text over Ren", (mid.ren[0] + mid.ren[2]) / 2 < 960 and not [b for b in mid if b[4] != "Ren" and b[0] < mid.ren[2]] and not [b for b in clash if b[4] != "Ren"], f"Ren x {mid.ren[0]:.0f}-{mid.ren[2]:.0f}")
# 10 Maya continuity, scale, acting
home = [s for s in R.SHOTS if R.SCENE[s["id"]] == "H1" and s["id"] not in ("P06", "P07")]
bad_pose, bad_pos = [], []
for sh in home:
    for i in range(sh["fa"], sh["fb"], 3):
        b = R.frame_at(i)[2]
        if sh["id"] == "P02": continue
        if any(not k.startswith(("maya_nochair", "seat_")) for k in b.poses): bad_pose.append((sh["id"], i, b.poses))
        if b.maya and (abs(b.maya[0] - R.ARM[0]) > 0.01 or abs(b.maya[1] - R.ARM[1]) > 0.01): bad_pos.append((sh["id"], i, b.maya))
check("10a living room: Maya stays in the armchair in every home shot (no stool pose, no repositioning)", not bad_pose and not bad_pos, str((bad_pose[:2], bad_pos[:2])))
off_bad = []
for sh in [s for s in R.SHOTS if s["id"] in ("P14", "P15", "P16", "P19")]:
    cam = R.CAMS[sh["id"]]
    for i in range(sh["fa"], sh["fb"], 3):
        b = R.frame_at(i)[2]; X, Y = cam.pt(*R.O1S)
        if abs(b.maya[0] - X) > 0.01 or abs(b.maya[1] - Y) > 0.01 or abs(b.maya[2] / A.scale_of(b.poses[0]) - R.S0 * cam.z) > 1e-3: off_bad.append((sh["id"], i))
check("10b office: Maya sits on the same floor spot in every shot and her scale follows the camera zoom exactly", not off_bad, str(off_bad[:3]))
sz = {sh["id"]: R.CAMS[sh["id"]].z for sh in R.SHOTS if sh["id"] in R.CAMS}
check("10c office Maya is larger than in the first pilot (zoom 1.25-1.55x on P14-P16, P19 vs 1.0x)", all(sz[k] >= 1.25 for k in ("P14", "P15", "P16", "P19")), str(sz))
weak = []
for sh in R.SHOTS:
    if sh["type"] != "CHARACTER_ACTION": continue
    seen = []; tips = []
    for i in range(sh["fa"], sh["fb"]):
        b = R.frame_at(i)[2]; seen.extend(b.poses)
        if b.tip: tips.append(b.tip)
    ndist = len(set(seen)); mv = (max(t[0] for t in tips) - min(t[0] for t in tips)) if tips else 0
    if ndist < 2 and mv < 100: weak.append((sh["id"], ndist, mv))
check("10d every character shot changes pose or moves a prop/hand (no shot is only a pan or zoom over a still)", not weak, str(weak))
# 11 24 fps playback
pk = [float(x) for x in run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "packet=pts_time", "-of", "csv=p=0", str(mp4)]).stdout.split()]
dpk = np.diff(sorted(pk)); fr_rates = (v["r_frame_rate"], v["avg_frame_rate"])
check("11 constant 24 fps: r_frame_rate and avg_frame_rate 24/1, every packet 1/24 s apart, no dropped or duplicated frame timestamps", fr_rates == ("24/1", "24/1") and np.allclose(dpk, 1 / 24, atol=2e-4) and len(pk) == rep["frames"], f"{fr_rates}, {len(pk)} packets, delta min {dpk.min():.5f} max {dpk.max():.5f}")
# 12 voice reused, not re-synthesised
import hashlib
hs = {f: hashlib.sha256((R.VOICE / f).read_bytes()).hexdigest() for f in ("P1.wav", "P2.wav")}; ref = json.loads((HERE / "voice_hashes.json").read_text())
check("12a narration WAVs are byte-identical to the ones generated for the first pilot (no new synthesis)", hs == ref, f"P1 {hs['P1.wav'][:12]} P2 {hs['P2.wav'][:12]}")
src = "".join((HERE / f).read_text() for f in ("render_pilot.py", "pilot_ren.py", "pilot_assets.py", "pilot_ui.py", "qa_pilot.py"))
check("12b renderer imports no TTS code", not re.search(r"qwen|torch|generate_voice", src, re.I))
au_raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(mp4), "-ac", "1", "-ar", "24000", "-f", "f32le", "-"]); got_a = np.frombuffer(au_raw, np.float32)
ref_a, _ = R.audio(); m = min(len(got_a), len(ref_a)); cc = float(np.dot(got_a[:m], ref_a[:m]) / (np.linalg.norm(got_a[:m]) * np.linalg.norm(ref_a[:m]) + 1e-9))
check("12c MP4 audio matches the original narration waveform (correlation >= 0.95)", cc >= 0.95, f"{cc:.4f}")

# write report
out = HERE / "reports"; out.mkdir(exist_ok=True)
md = ["# Hybrid QC - Ren | Unclaimed 401(k) match, pilot", "", f"File: `{mp4.name}`  |  frames {rep['frames']}  |  {rep['size'][0]}x{rep['size'][1]} @ {FPS} fps", "",
      "Commands: `project/.tools/venv/bin/python videos/unclaimed_401k/qa_pilot.py <mp4>`; thresholds are in the script and were not relaxed.", "", "| Check | Result | Measured |", "|---|---|---|"]
for n, st, dt in res: md.append(f"| {n} | {st} | {dt.replace('|', '/')[:220]} |")
md += ["", "## Not run / limits", "- NOT RUN: listening review (pronunciation, accent, tone, joins). Speech-to-text only confirms the words; see voice_check_summary.json.",
       "- NOT RUN: the original repo `qa_timeline.py`, `validate.py` and `jitter_check.py`. They are wired to the 1280x720 free_money renderer and Ren stills; `qa_pilot.py` re-implements their checks for this renderer (half-open shot lookup, caps, A-B-A, flashes, cuts on boundaries, decode, jitter).",
       "- Ren: genuine library clips only; mouth-closed windows were chosen from the library notes and checked by eye on 100% crops, not by an automated mouth detector.",
       "- Motion is limited animation: Maya is a set of approved keyframe poses with pose-to-pose changes (3-frame cross-fade where the poses are close, hard cut otherwise), plus code-driven props, pen path, coin and UI. It is not a skeletal rig.",
       "- Plates are 2.3x upscales of 1672x941 art and are not perspective-calibrated; scale was matched by eye to the plate furniture."]
(out / "hybrid_qc.md").write_text("\n".join(md) + "\n")
fails = [n for n, st, _ in res if st == "FAIL"]; print("\nOVERALL", "FAIL: " + "; ".join(fails) if fails else "PASS"); sys.exit(1 if fails else 0)
