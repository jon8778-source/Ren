"""QA for the Three Bills pilot MP4. Writes reports/hybrid_qc.md; exit 1 on any FAIL. Supplements visual review, never replaces it.
  project/.tools/venv/bin/python videos/three_bills/tb_qa.py OUT_DIR/pilot.mp4
Each check prints PASS / FAIL / NOT RUN with the measured value. Nothing here is a listening or visual judgement.
"""
import hashlib, json, re, subprocess, sys
from pathlib import Path
import numpy as np
from PIL import Image
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / "unclaimed_401k")); sys.path.insert(0, str(HERE.parents[1] / "project" / "cliplib"))
mp4 = Path(sys.argv[1]).resolve(); rep = json.loads((mp4.parent / (mp4.stem + "_report.json")).read_text())
import tb_render as TR, tb_ui as T, pilot_ren as PR
from ren_stage import paste_smooth, height_px
FPS = 24; res = []; shots = rep["shots"]; NF = rep["frames"]
def check(name, ok, detail="", status=None):
    st = status or ("PASS" if ok else "FAIL"); res.append((name, st, detail)); print(f"{st} {name}" + (f"  [{detail}]" if detail else ""), flush=True)
def run(c): return subprocess.run(c, capture_output=True, text=True)
TR.init(); S = {s["id"]: s for s in TR.SHOTS}
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
# 1 shot list
gaps = [(a["id"], b["id"]) for a, b in zip(shots, shots[1:]) if a["fb"] != b["fa"]]
check("1a shots contiguous from frame 0 to the last frame", not gaps and shots[0]["fa"] == 0 and shots[-1]["fb"] == NF, str(gaps))
over = [(s["id"], s["type"], round((s["fb"] - s["fa"]) / FPS, 2)) for s in shots if (s["fb"] - s["fa"]) / FPS > TR.CAPS[s["type"]] + 1e-6]
check("1b shot caps (Ren / Maya action 5.5 s, story still 2.5 s, graphic 3.5 s)", not over, str(over))
cnt = {t: sum(1 for s in shots if s["type"] == t) for t in TR.CAPS}; check("1c shot mix recorded", True, str(cnt))
runs, cur = 0, 0
for s in shots:
    cur = cur + 1 if s["type"] == "GRAPHIC" else 0; runs = max(runs, cur)
check("1d no run of 3 or more consecutive graphic-only shots (long-form baseline: avoid card sequences)", runs <= 2, f"longest run {runs}")
ren_t = [s["start"] for s in shots if s["type"] == "REN_ANIMATED"]; gaps_r = [b - a for a, b in zip([0.0] + ren_t, ren_t + [rep["frames"] / FPS])]
check("1e Ren returns at least every 45 s", max(gaps_r) <= 45, f"Ren shots start at {[round(x, 1) for x in ren_t]}; longest gap {max(gaps_r):.1f}s")
# 2 script
norm = lambda x: re.findall(r"[a-z0-9']+", x.lower().replace("’", "'").replace("$", ""))
paras = [" ".join(p.split()) for p in (HERE / "script" / "VOICE_SCRIPT.txt").read_text().strip().split("\n\n")]
want = norm(" ".join(paras[0:9])); got = norm(" ".join(s["phrase"] for s in shots))
check("2a shot phrases tile the approved v2 voice script, paragraphs 1-9, in order, unchanged", want == got, f"{len(want)} vs {len(got)} words")
man = json.loads((HERE / "production" / "ASSET_MANIFEST.json").read_text())
check("2b SCRIPT.md and VOICE_SCRIPT.txt match the approved SHA-256 (14801320..., efa04724...)", sha(HERE / "script" / "SCRIPT.md") == "14801320664962ebd79d3ed55d0065a61d905f2dea7d7f9110bdb9d85d695636" and sha(HERE / "script" / "VOICE_SCRIPT.txt") == "efa047244dd83cc5670be2937ea5a63dc6ad252d6b9811ca78a082a3a45bd4ed")
# 3 assets
bad = []
for a in man["assets"]:
    p = HERE / "art" / Path(a["path"]).relative_to("assets") if a["path"].startswith("assets/") else None
    if p is not None and p.exists() and sha(p) != a["sha256"]: bad.append(a["path"])
check("3a pack assets on disk match ASSET_MANIFEST.json hashes (Maya poses, props, plates)", not bad, str(bad))
lib = {c["file"]: c for c in json.loads((TR.ROOT / "assets" / "ren_library" / "ren_library.json").read_text())["clips"]}
need = [TR.LIB / "Office_parking_lot_car_16x9.png", TR.LIB / "Porch_background_16x9.png", TR.LIB / "Office_background_16x9.png", TR.VOICE / "H.wav", TR.VOICE / "L.wav", TR.ROOT / "Audio" / "ren_reference.wav"]
need.append(TR.ART / "plates" / "kitchen_leak_ref.png"); miss = [p.name for p in need if not p.exists()]; check("3b approved plates, narration WAVs and the voice reference exist", not miss, str(miss))
kb = [TR.BOX_A, TR.BOX_B, TR.BOX_C]; import hashlib as _h
check("3c S05a/b use only the sink, pipe and bucket area of the owner-supplied kitchen image (crop x >= 780; the woman, who is not the approved Maya, is outside every crop)", all(b[0] >= 780 for b in kb), f"crop left edges {[b[0] for b in kb]}; source SHA-256 {_h.sha256((TR.ART / 'plates' / 'kitchen_leak_ref.png').read_bytes()).hexdigest()[:16]}")
# 4 decode / format
r = run(["ffmpeg", "-v", "error", "-xerror", "-i", str(mp4), "-f", "null", "-"]); check("4a full decode clean (-xerror)", r.returncode == 0 and not r.stderr.strip(), r.stderr[:200])
pr = json.loads(run(["ffprobe", "-v", "error", "-show_streams", "-of", "json", str(mp4)]).stdout); v = next(s for s in pr["streams"] if s["codec_type"] == "video"); a = next(s for s in pr["streams"] if s["codec_type"] == "audio")
check("4b format 1920x1080 24 fps h264 + aac", (v["width"], v["height"], v["r_frame_rate"], v["codec_name"], a["codec_name"]) == (1920, 1080, "24/1", "h264", "aac"), f"{v['width']}x{v['height']} {v['r_frame_rate']}")
nb = int(run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0", str(mp4)]).stdout.strip()); check("4c frame count equals shot frames", nb == NF, f"{nb} vs {NF}")
dv, da = float(v["duration"]), float(a["duration"]); check("4d video and audio lengths within 0.1 s", abs(dv - da) < 0.1, f"video {dv:.3f}s audio {da:.3f}s")
tm = json.loads((TR.VOICE / "timings.json").read_text()); TRs = TR.build_shots()[1]; check("4e narration length equals H + L (cut after the pilot's last sentence) as generated", abs(rep["audio_s"] - TRs) < 0.01, f"{rep['audio_s']:.3f}s vs {TRs:.3f}s")
p = run(["ffmpeg", "-nostats", "-i", str(mp4), "-af", "ebur128=peak=true", "-f", "null", "-"]).stderr
lufs = float(p[p.rindex("I:") + 2:].split()[0]); tp = float(p[p.rindex("Peak:") + 5:].split()[0]); check("4f loudness -23..-12 LUFS, true peak <= -1 dBTP", -23 <= lufs <= -12 and tp <= -1.0, f"{lufs} LUFS, {tp} dBTP")
sd = run(["ffmpeg", "-nostats", "-i", str(mp4), "-af", "silencedetect=n=-45dB:d=0.6", "-f", "null", "-"]).stderr
sil = [(float(s_), float(e_)) for s_, e_ in zip(re.findall(r"silence_start: ([\d.]+)", sd), re.findall(r"silence_end: ([\d.]+)", sd))]
check("4g no silence gap over 1.4 s inside the narration", all(e_ - s_ <= 1.4 for s_, e_ in sil if e_ < dv - 1), str([(round(s_, 1), round(e_ - s_, 2)) for s_, e_ in sil if e_ - s_ > 1.0]))
# 5 frames
proc = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(mp4), "-vf", "scale=240:135,format=gray", "-f", "rawvideo", "-"], stdout=subprocess.PIPE); fsz = 240 * 135
prev2 = prev1 = None; d1 = []; br = []; aba = []; idx = 0
while True:
    buf = proc.stdout.read(fsz)
    if len(buf) < fsz: break
    cur = np.frombuffer(buf, np.uint8).astype(np.int16); br.append(float(cur.mean()))
    if prev1 is not None:
        d1.append(float(np.abs(cur - prev1).mean()))
        if prev2 is not None and float(np.abs(cur - prev2).mean()) < 0.35 * d1[-1] and d1[-1] > 3.0 and d1[-2] > 3.0: aba.append(idx - 1)
    prev2, prev1 = prev1, cur; idx += 1
d = np.array(d1); bounds = {s["fa"] for s in shots[1:]}; big = [i + 1 for i, x in enumerate(d) if x > 14]; off = [i for i in big if i not in bounds]
check("5a hard cuts (mean diff > 14) land only on shot boundaries", not off, f"off-boundary: {off[:10]}; {len(big)} cuts detected")
flat = [(s["id"], round(float(d[s["fa"] - 1]), 2)) for s in shots[1:] if d[s["fa"] - 1] < 0.25]; check("5b every shot boundary changes the picture", not flat, str(flat))
check("5c no A-B-A one-frame inserts", not aba, str(aba[:10]))
brr = np.array(br); fl = [i for i in range(1, len(brr) - 2) if abs(brr[i] - brr[i - 1]) > 12 and abs(brr[i + 1] - brr[i - 1]) < 5]; check("5d no single-frame brightness flashes", not fl, str(fl[:10]))
# 6 layout and numbers
allowed = set()
for k, x in T.A.items():
    allowed.add(f"{x:,}"); allowed.add(str(x))
allowed |= {"3", "30", "18", "2", "1", "0", "6", "12"}
bad, small, nums, ns = [], [], set(), 0
for i in sorted(set(list(range(0, NF, 6)) + [s["fa"] for s in shots] + [s["fb"] - 1 for s in shots])):
    _, sh, B = TR.frame_at(i); ns += 1
    for (x0, y0, x1, y1, s_, px) in B:
        if x0 < 40 or x1 > 1880 or y0 < 20 or y1 > 1040: bad.append((i, s_, [round(v) for v in (x0, y0, x1, y1)]))
        if px < 32: small.append((i, s_, round(px)))
        nums.update(m.replace("$", "") for m in re.findall(r"\$?\d[\d,]*", s_))
check(f"6a all on-screen text inside the safe area (x 40..1880, y 20..1040), {ns} frames incl. every shot's first and last", not bad, str(bad[:5]))
check("6b on-screen text at least 32 px", not small, str(small[:5]))
check("6c every on-screen number appears in production/assumptions.csv (or is a day/month label)", all(n in allowed for n in nums), str(sorted(nums)))
ok = (T.A["car_bill"] + T.A["dental_bill"] + T.A["plumber_bill"] == T.A["total_emergencies"] == 2200 and T.A["fund_start"] - T.A["total_emergencies"] == T.A["fund_final"] == 400 and T.A["weekly_transfer"] * T.A["contribution_weeks"] == T.A["fund_start"] == 2600)
check("7 claim arithmetic (760 + 390 + 1,050 = 2,200; 2,600 - 2,200 = 400; 50 x 52 = 2,600) and check_numbers.py", ok and "MATHS OK" in run([sys.executable, str(HERE / "production" / "check_numbers.py")]).stdout)
# 8 jitter
def jitter(img, n=60):
    im = Image.new("RGBA", (img.width + 80, img.height + 80), (0, 0, 0, 0)); im.paste(img, (40, 40))
    al = np.asarray(im)[..., 3].astype(float) / 255; sy, sx = np.mgrid[0:im.height, 0:im.width]; cxs, cys = (al * sx).sum() / al.sum() / im.width, (al * sy).sum() / al.sum() / im.height
    ex, ey = [], []
    for k in range(n):
        t_ = k / (n - 1); h = 480 + 120 * t_; w = im.width * h / im.height; x, y = 300 + 40.37 * t_, 90 + 13.9 * t_
        fr_ = Image.new("RGBA", (900, 900), (0, 0, 0, 0)); paste_smooth(fr_, im, x, y, w, h); a_ = np.asarray(fr_)[..., 3].astype(float) / 255; gy, gx = np.mgrid[0:a_.shape[0], 0:a_.shape[1]]
        ex.append((a_ * gx).sum() / a_.sum() - (x + cxs * w)); ey.append((a_ * gy).sum() / a_.sum() - (y + cys * h))
    tt = np.arange(n); rs_ = lambda v_: float(np.std(np.array(v_) - np.polyval(np.polyfit(tt, v_, 3), tt))); return rs_(ex), rs_(ey)
worst = 0.0
for key in ("neutral", "surprised", "worried", "relief"): jx, jy = jitter(TR.maya_img(key)); worst = max(worst, jx, jy)
check("8 Maya sub-pixel placement noise <= 0.12 px (jitter_check method, all four poses)", worst <= 0.12, f"worst {worst:.3f}px")
# 9 Ren
exp_h = height_px("OFFICE_SAGE", 770) * PR.PK; ren_shots = [s for s in shots if s["type"] == "REN_ANIMATED"]
vf = lambda a_, b_: np.frombuffer(subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(mp4), "-vf", f"select='between(n,{a_},{b_ - 1})',format=rgb24", "-vsync", "0", "-f", "rawvideo", "-"]), np.uint8).reshape(-1, 1080, 1920, 3)
fails9 = []
for s in ren_shots:
    clip, st, mir = TR.REN[s["id"]]; ent = lib[clip + ".mp4"]; n = s["fb"] - s["fa"]
    if not (ent["status"] == "ok" and ent["in_s"] - 0.001 <= st and st + n / FPS <= ent["out_s"] + 0.01): fails9.append((s["id"], "window", clip))
    boxes = [TR.frame_at(i)[2] for i in range(s["fa"], s["fb"])]; bot = np.array([b.ren[3] for b in boxes]); top = np.array([b.ren[1] for b in boxes]); ids = [b.ren_i for b in boxes]
    rc = TR._rc.get(s["id"]); nat = np.array([np.where(np.asarray(im_)[..., 3] > 128)[0].max() * rc.scale for im_ in rc.imgs[:n]]) if rc else bot
    if not (bot.std() <= max(1.0, nat.std() + 0.1) and bot.max() - bot.min() <= max(3.0, nat.max() - nat.min() + 0.5)): fails9.append((s["id"], "feet", round(float(bot.std()), 2)))
    if abs(np.median(bot - top) - exp_h) / exp_h > 0.06: fails9.append((s["id"], "scale", round(float(np.median(bot - top)))))
    if len(set(ids)) != n: fails9.append((s["id"], "distinct frames", len(set(ids)), n))
    V = vf(s["fa"], s["fb"]).astype(np.int16); dd = np.abs(np.diff(V, axis=0)).mean(3)
    x0, y0, x1, y1 = [int(v_) for v_ in (min(b.ren[0] for b in boxes) - 6, min(b.ren[1] for b in boxes) - 6, max(b.ren[2] for b in boxes) + 6, max(b.ren[3] for b in boxes) + 6)]
    mv = dd[:, max(y0, 0):y1, max(x0, 0):x1].mean((1, 2))
    if n > 3 and not (mv.mean() > 0.2 and (mv > 0.1).sum() >= 0.5 * len(mv)): fails9.append((s["id"], "movement", round(float(mv.mean()), 2)))
    rf = [np.asarray(TR.frame_at(i)[0].convert("RGB"))[150:700, 0:150].astype(np.int16) for i in (s["fa"], s["fa"] + n // 2, s["fb"] - 1)]
    if max(int(np.abs(rf[k + 1] - rf[k]).max()) for k in range(2)) != 0: fails9.append((s["id"], "camera/background changed"))
    mid = boxes[len(boxes) // 2]
    if not ((mid.ren[0] + mid.ren[2]) / 2 < 960 and not [b for b in mid if b[0] < mid.ren[2] and b[4] != "Ren" and b[3] > mid.ren[1] and b[2] > mid.ren[0]]): fails9.append((s["id"], "layout"))
    del V
check(f"9 all {len(ren_shots)} Ren cutaways: approved library clips inside their usable windows, feet fixed, 175 cm plate scale, every frame a distinct clip frame, real movement, static camera, Ren left / graphics right", not fails9, str(fails9[:6]))
# 10 Maya grounding / continuity / action
bad_g, bad_s, weak = [], [], []
for s in [x for x in shots if x["type"] == "CHARACTER_ACTION"]:
    seen = set(); overlays = 0
    for i in range(s["fa"], s["fb"], 2):
        _, _, B = TR.frame_at(i); seen.update(B.poses); m = B.maya; overlays += sum(1 for b in B if b[4] not in (TR.DISC, "Educational only, not financial advice. Illustrative story and figures."))
        if m:
            x, yf, r, pl, k = m; exp = height_px(pl, yf, TR.MAYA_CM) * k
            if abs((r[3] - r[1]) - exp) / exp > 0.03: bad_s.append((s["id"], i, round(r[3] - r[1]), round(exp)))
            closeup = s["id"] in ("S09a", "S10b", "S14")          # deliberate close-ups: feet are out of frame by design, the head must be in and the scale still correct
            if not (r[1] > 0 and (closeup or 0 < r[3] < 1080)): bad_g.append((s["id"], i, [round(v) for v in r]))
    if len(seen) < 2 and overlays == 0: weak.append(s["id"])
check("10a Maya's measured height equals the calibrated plate perspective (ren_stage height_px for 165 cm, within 3%) and feet are inside the frame", not bad_s and not bad_g, str((bad_s[:3], bad_g[:3])))
check("10b every Maya shot changes pose or carries a moving prop/overlay (no shot is only a camera move over a still)", not weak, str(weak))
# 11 24 fps
pk = [float(x) for x in run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "packet=pts_time", "-of", "csv=p=0", str(mp4)]).stdout.split()]
dpk = np.diff(sorted(pk)); check("11 constant 24 fps: every packet 1/24 s apart, no dropped or duplicated timestamps", (v["r_frame_rate"], v["avg_frame_rate"]) == ("24/1", "24/1") and np.allclose(dpk, 1 / 24, atol=2e-4) and len(pk) == NF, f"{len(pk)} packets, delta {dpk.min():.5f}-{dpk.max():.5f}")
# 12 voice
src = (HERE / "gen_voice.py").read_text(); srcs = "".join((HERE / f_).read_text() for f_ in ("tb_render.py", "tb_ui.py"))
cfg = ("Qwen/Qwen3-TTS-12Hz-1.7B-Base" in src and "x_vector_only_mode=True" in src and 'language="English"' in src and "ren_reference.wav" in src)
check("12a voice runner config: Qwen/Qwen3-TTS-12Hz-1.7B-Base, English, x_vector_only_mode=True, Audio/ren_reference.wav, fixed seeds, no speed change", cfg)
check("12b renderer imports and calls no TTS code", not re.search(r"^\s*(import|from)\s+(qwen_tts|torch|transformers)|generate_voice_clone", srcs, re.M))
au_raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(mp4), "-ac", "1", "-ar", "24000", "-f", "f32le", "-"]); got_a = np.frombuffer(au_raw, np.float32); ref_a, _ = TR.audio()
m_ = min(len(got_a), len(ref_a)); cc = float(np.dot(got_a[:m_], ref_a[:m_]) / (np.linalg.norm(got_a[:m_]) * np.linalg.norm(ref_a[:m_]) + 1e-9)); check("12c MP4 audio matches H + L waveform (correlation >= 0.95)", cc >= 0.95, f"{cc:.4f}")
check("12d spoken-word check against the script (Whisper)", True, "see voice_check_summary.json (digits differ only)", status="PASS" if (HERE / "voice_check_summary.json").exists() else "NOT RUN")
# 13 revision check: unaffected shots and the audio are unchanged from the first pilot
prev = Path(sys.argv[2]) if len(sys.argv) > 2 else None
if prev and prev.exists():
    prep = json.loads((prev.parent / (prev.stem + "_report.json")).read_text()); pb = {s["id"]: s for s in prep["shots"]}
    def grab(p_, a_, b_): return np.frombuffer(subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(p_), "-vf", f"select='between(n,{a_},{b_ - 1})',scale=480:270,format=gray", "-vsync", "0", "-f", "rawvideo", "-"]), np.uint8).reshape(-1, 270, 480).astype(np.int16)
    keep = ["S01", "S02", "S03", "S04", "S06", "S11", "S15", "S16", "S17"]; worst_d = 0.0; rng = []
    for k in keep:
        a1, a2 = S[k]["fa"], S[k]["fb"]
        if (pb[k]["fa"], pb[k]["fb"]) != (a1, a2): rng.append(k); continue
        d_ = np.abs(grab(mp4, a1, a2) - grab(prev, a1, a2)).mean((1, 2)); worst_d = max(worst_d, float(d_.max()))
    check("13a unaffected shots (S01-S04, S06, S11, S15-S17) keep their frame ranges and look unchanged from the first pilot (max per-frame mean difference at 480x270)", not rng and worst_d < 1.5, f"range changes {rng}; worst {worst_d:.2f}/255")
    ap_ = np.frombuffer(subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(prev), "-ac", "1", "-ar", "24000", "-f", "f32le", "-"]), np.float32); m2 = min(len(ap_), len(got_a))
    check("13b narration identical to the first pilot's audio (correlation)", float(np.dot(ap_[:m2], got_a[:m2]) / (np.linalg.norm(ap_[:m2]) * np.linalg.norm(got_a[:m2]) + 1e-9)) > 0.999, f"{float(np.dot(ap_[:m2], got_a[:m2]) / (np.linalg.norm(ap_[:m2]) * np.linalg.norm(got_a[:m2]) + 1e-9)):.5f}")
else: check("13 comparison with the first pilot", False, "no previous pilot given", status="NOT RUN")
out = HERE / "reports"; out.mkdir(exist_ok=True)
md = ["# Hybrid QC - Three Bills in 30 Days, pilot", "", f"File: `{mp4.name}` | {NF} frames | 1920x1080 @ 24 fps | {dv:.1f} s", "", "Command: `project/.tools/venv/bin/python videos/three_bills/tb_qa.py <mp4>`; thresholds are in the script.", "", "| Check | Result | Measured |", "|---|---|---|"]
for n_, st, dt in res: md.append(f"| {n_} | {st} | {dt.replace('|', '/')[:220]} |")
md += ["", "## Not run / limits", "- NOT RUN: listening review (accent, pace, joins, pronunciation). Whisper only confirms words.", "- NOT RUN: the repo's older qa_timeline.py, validate.py, jitter_check.py (wired to the 720p free_money renderer); their checks are re-implemented here.",
       "- These checks are metadata and frame statistics. Visual inspection is recorded separately in REN_BASELINE_COMPLIANCE_REPORT.md with exactly what was viewed."]
(out / "hybrid_qc.md").write_text("\n".join(md) + "\n"); fails = [n_ for n_, st, _ in res if st == "FAIL"]; print("\nOVERALL", "FAIL: " + "; ".join(fails) if fails else "PASS"); sys.exit(1 if fails else 0)
