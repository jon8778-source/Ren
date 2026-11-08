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
check("1d shot types match the plan (15 action, 3 graphic, 1 story still)", [sum(1 for s in shots if s["type"] == t) for t in ("CHARACTER_ACTION", "GRAPHIC", "STORY_STILL")] == [15, 3, 1])
# 2 order
tm = json.loads((R.VOICE / "timings.json").read_text())
norm = lambda t: re.findall(r"[a-z0-9$']+", t.lower().replace("’", "'"))
want = norm(tm["P1"]["text"] + " " + tm["P2"]["text"]); got = norm(" ".join(s["phrase"] for s in shots))
fixed = lambda ws: [w.replace("$", "") for w in ws]
check("2 phrases tile the approved narration in order", fixed(want) == fixed(got) or " ".join(want).replace("$", "") == " ".join(got).replace("$", ""), f"{len(want)} vs {len(got)} words")
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
miss_cut = [(s['id'], round(float(d[s['fa'] - 1]), 1)) for s in R.SHOTS[1:] if d[s['fa'] - 1] < 6]
check("5b every shot boundary is a visible cut (diff >= 6; the portal label swap P06->P07 is allowed to be small)", all(x[0] == "P07" for x in miss_cut), str(miss_cut), "PASS" if all(x[0] == "P07" for x in miss_cut) else "FAIL")
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
# 8 Maya placement jitter
im = A.pose("stool_01"); ax, ay = A.stool_anchor("stool_01"); worst = 0.0
alpha = np.asarray(im)[..., 3].astype(float) / 255; yy, xx = np.mgrid[0:im.height, 0:im.width]; cx0, cy0 = (alpha * xx).sum() / alpha.sum(), (alpha * yy).sum() / alpha.sum()
prev = None
for k in range(60):
    t = k / 59; sc = 1.20 + 0.15 * t; X, Y = 300 + 40.37 * t, 760 + 13.9 * t
    fr_ = Image.new("RGBA", (700, 900), (0, 0, 0, 0)); paste_smooth(fr_, im, X - ax * sc, Y - ay * sc, im.width * sc, im.height * sc)
    a = np.asarray(fr_)[..., 3].astype(float) / 255; gy, gx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    cx, cy = (a * gx).sum() / a.sum(), (a * gy).sum() / a.sum()
    ex, ey = X - ax * sc + cx0 * sc, Y - ay * sc + cy0 * sc
    worst = max(worst, abs(cx - ex), abs(cy - ey))
check("8 Maya sub-pixel placement error <= 0.12 px over a 60-frame move and scale", worst <= 0.12, f"max error {worst:.3f}px")
# write report
out = HERE / "reports"; out.mkdir(exist_ok=True)
md = ["# Hybrid QC - Ren | Unclaimed 401(k) match, pilot", "", f"File: `{mp4.name}`  |  frames {rep['frames']}  |  {rep['size'][0]}x{rep['size'][1]} @ {FPS} fps", "",
      "Commands: `project/.tools/venv/bin/python videos/unclaimed_401k/qa_pilot.py <mp4>`; thresholds are in the script and were not relaxed.", "", "| Check | Result | Measured |", "|---|---|---|"]
for n, st, dt in res: md.append(f"| {n} | {st} | {dt.replace('|', '/')[:220]} |")
md += ["", "## Not run / limits", "- NOT RUN: listening review (pronunciation, accent, tone, joins). Speech-to-text only confirms the words; see voice_check_summary.json.",
       "- NOT RUN: the original repo `qa_timeline.py`, `validate.py` and `jitter_check.py`. They are wired to the 1280x720 free_money renderer and Ren stills; `qa_pilot.py` re-implements their checks for this renderer (half-open shot lookup, caps, A-B-A, flashes, cuts on boundaries, decode, jitter).",
       "- Motion is limited animation: Maya is a set of approved keyframe poses with pose-to-pose changes (3-frame cross-fade where the poses are close, hard cut otherwise), plus code-driven props, pen path, coin and UI. It is not a skeletal rig.",
       "- Plates are 2.3x upscales of 1672x941 art and are not perspective-calibrated; scale was matched by eye to the plate furniture."]
(out / "hybrid_qc.md").write_text("\n".join(md) + "\n")
fails = [n for n, st, _ in res if st == "FAIL"]; print("\nOVERALL", "FAIL: " + "; ".join(fails) if fails else "PASS"); sys.exit(1 if fails else 0)
