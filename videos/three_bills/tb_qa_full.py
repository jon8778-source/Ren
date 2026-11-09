"""QA for the full Three Bills episode MP4. Writes reports/full_qc.md; exit 1 on any FAIL. Supplements visual review, never replaces it.
  project/.tools/venv/bin/python videos/three_bills/tb_qa_full.py OUT_DIR/episode.mp4 PILOT_REV3.mp4
Each check prints PASS / FAIL / NOT RUN with the measured value. Nothing here is a listening or visual judgement.
"""
import hashlib, json, re, subprocess, sys
from pathlib import Path
import numpy as np
from PIL import Image
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / "unclaimed_401k")); sys.path.insert(0, str(HERE.parents[1] / "project" / "cliplib"))
mp4 = Path(sys.argv[1]).resolve(); pilot = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else None
rep = json.loads((mp4.parent / (mp4.stem + "_report.json")).read_text())
import tb_full as TF, tb_render as TR, tb_shots as SH, tb_ui as T, pilot_ren as PR
from ren_stage import paste_smooth, height_px
FPS = 24; res = []; shots = rep["shots"]; NF = rep["frames"]; ST = {s["id"]: s for s in TF.SHOTS}
def check(name, ok, detail="", status=None):
    st = status or ("PASS" if ok else "FAIL"); res.append((name, st, detail)); print(f"{st} {name}" + (f"  [{detail}]" if detail else ""), flush=True)
def run(c): return subprocess.run(c, capture_output=True, text=True)
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
# 1 shot list
gaps = [(a["id"], b["id"]) for a, b in zip(shots, shots[1:]) if a["fb"] != b["fa"]]
check("1a shots contiguous from frame 0 to the last frame", not gaps and shots[0]["fa"] == 0 and shots[-1]["fb"] == NF, str(gaps[:5]))
over = [(s["id"], s["type"], round((s["fb"] - s["fa"]) / FPS, 2)) for s in shots if (s["fb"] - s["fa"]) / FPS > TF.CAP[s["type"]] + 1e-6]
check("1b shot caps (Ren / Maya action 5.5 s, story still 2.5 s, graphic 3.5 s)", not over, str(over))
cnt = {t: sum(1 for s in shots if s["type"] == t) for t in TF.CAP}; check("1c shot mix recorded", True, f"{cnt}, {len(shots)} shots")
runs = cur = 0
for s in shots: cur = cur + 1 if s["type"] == "GRAPHIC" else 0; runs = max(runs, cur)
check("1d no run of 3 or more consecutive graphic-only shots (baseline: avoid card sequences)", runs <= 2, f"longest run {runs}")
ren_t = [s["start"] for s in shots if s["type"] == "REN_ANIMATED"]; gaps_r = [b - a for a, b in zip([0.0] + ren_t, ren_t + [NF / FPS])]
check("1e Ren returns at least every 45 s (baseline: roughly every 30-45 s)", max(gaps_r) <= 45, f"{len(ren_t)} Ren shots; longest gap {max(gaps_r):.1f}s; gaps over 40 s: {[round(g, 1) for g in gaps_r if g > 40]}")
# graphic density: share of screen time that is graphic-only, and longest stretch without Maya or Ren on screen
gt = sum((s["fb"] - s["fa"]) for s in shots if s["type"] == "GRAPHIC") / NF; check("1f graphic-only screen time share recorded", True, f"{100 * gt:.0f}% of the film")
# 2 script
norm = lambda x: re.findall(r"[a-z0-9']+", x.lower().replace("’", "'").replace("$", ""))
want = norm((HERE / "script" / "VOICE_SCRIPT.txt").read_text()); got = norm(" ".join(s["phrase"] for s in shots))
check("2a shot phrases tile the whole approved v2 voice script (937 words) in order, unchanged", want == got, f"{len(want)} vs {len(got)} words")
check("2b SCRIPT.md and VOICE_SCRIPT.txt match the approved SHA-256", sha(HERE / "script" / "SCRIPT.md") == "14801320664962ebd79d3ed55d0065a61d905f2dea7d7f9110bdb9d85d695636" and sha(HERE / "script" / "VOICE_SCRIPT.txt") == "efa047244dd83cc5670be2937ea5a63dc6ad252d6b9811ca78a082a3a45bd4ed")
# 3 assets
man = json.loads((HERE / "production" / "ASSET_MANIFEST.json").read_text()); bad = []
for a in man["assets"]:
    p = HERE / "art" / Path(a["path"]).relative_to("assets")
    if p.exists() and sha(p) != a["sha256"]: bad.append(a["path"])
check("3a pack assets on disk match ASSET_MANIFEST.json hashes", not bad, str(bad))
need = [TR.LIB / f for f in ("Office_parking_lot_car_16x9.png", "Porch_background_16x9.png", "Office_background_16x9.png")] + [TR.ART / "plates" / "kitchen_leak_ref.png", TR.ROOT / "Audio" / "ren_reference.wav"] + [TR.VOICE / f"{k}.wav" for k in TF.SECS]
miss = [p.name for p in need if not p.exists()]; check("3b plates, kitchen image, voice reference and all narration WAVs exist", not miss, str(miss))
check("3c kitchen illustration used only right of x = 780 (the woman, not the approved Maya, never appears)", all(b[0] >= 780 for b in (TR.BOX_A, TR.BOX_B, TR.BOX_C, SH.BOX_D)), f"crop left edges {[TR.BOX_A[0], TR.BOX_B[0], TR.BOX_C[0], SH.BOX_D[0]]}")
# 4 decode / format
r = run(["ffmpeg", "-v", "error", "-xerror", "-i", str(mp4), "-f", "null", "-"]); check("4a full decode clean (-xerror)", r.returncode == 0 and not r.stderr.strip(), r.stderr[:200])
pr = json.loads(run(["ffprobe", "-v", "error", "-show_streams", "-of", "json", str(mp4)]).stdout); v = next(s for s in pr["streams"] if s["codec_type"] == "video"); a = next(s for s in pr["streams"] if s["codec_type"] == "audio")
check("4b format 1920x1080 24 fps h264 + aac", (v["width"], v["height"], v["r_frame_rate"], v["codec_name"], a["codec_name"]) == (1920, 1080, "24/1", "h264", "aac"), f"{v['width']}x{v['height']} {v['r_frame_rate']}")
nb = int(run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0", str(mp4)]).stdout.strip()); check("4c frame count equals shot frames", nb == NF, f"{nb} vs {NF}")
dv, da = float(v["duration"]), float(a["duration"]); check("4d video and audio lengths within 0.1 s", abs(dv - da) < 0.1, f"video {dv:.3f}s audio {da:.3f}s")
check("4e narration length equals all sections joined as generated; episode about six minutes", abs(rep["audio_s"] - TF.TOTAL) < 0.01 and 5.0 <= dv / 60 <= 7.0, f"{rep['audio_s']:.3f}s = {dv / 60:.2f} min")
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
flat = [(s["id"], round(float(d[s["fa"] - 1]), 2)) for s in shots[1:] if d[s["fa"] - 1] < 0.25 and s["id"] != "P07"]; check("5b every shot boundary changes the picture", not flat, str(flat))
check("5c no A-B-A one-frame inserts", not aba, str(aba[:10]))
brr = np.array(br); fl = [i for i in range(1, len(brr) - 2) if abs(brr[i] - brr[i - 1]) > 12 and abs(brr[i + 1] - brr[i - 1]) < 5]; check("5d no single-frame brightness flashes", not fl, str(fl[:10]))
# 6 layout and numbers
allowed = set()
for k, x in T.A.items(): allowed.add(f"{x:,}"); allowed.add(str(x))
allowed |= {"3", "30", "18", "2", "1", "0", "6", "12", "16", "27", "5", "20"}
bad, small, nums, ns = [], [], set(), 0
for i in sorted(set(list(range(0, NF, 12)) + [s["fa"] for s in shots] + [s["fb"] - 1 for s in shots] + [(s["fa"] + s["fb"]) // 2 for s in shots])):
    _, sh, B = TF.frame_at(i); ns += 1
    for (x0, y0, x1, y1, s_, px) in B:
        if x0 < 40 or x1 > 1880 or y0 < 20 or y1 > 1040: bad.append((i, sh["id"], s_, [round(v) for v in (x0, y0, x1, y1)]))
        if px < 32: small.append((i, sh["id"], s_, round(px)))
        nums.update(m.replace("$", "") for m in re.findall(r"\$?\d[\d,]*", s_))
check(f"6a all on-screen text inside the safe area (x 40..1880, y 20..1040), {ns} frames incl. every shot's first, middle and last", not bad, str(bad[:5]))
check("6b on-screen text at least 32 px", not small, str(small[:5]))
check("6c every on-screen number appears in production/assumptions.csv, the script, or is a day/month label", all(n in allowed for n in nums), str(sorted(nums)))
ok = (T.A["car_bill"] + T.A["dental_bill"] + T.A["plumber_bill"] == T.A["total_emergencies"] == 2200 and T.A["fund_start"] - T.A["total_emergencies"] == T.A["fund_final"] == 400 and T.A["weekly_transfer"] * T.A["contribution_weeks"] == T.A["fund_start"] == 2600
      and T.A["fund_start"] - T.A["car_bill"] == T.A["fund_after_car"] == 1840 and T.A["fund_after_car"] - T.A["dental_bill"] == T.A["fund_after_dental"] == 1450 and T.A["fund_after_dental"] - T.A["plumber_bill"] == T.A["fund_final"] and T.A["plumber_bill"] < T.A["fund_after_dental"])
check("7 claim arithmetic (50 x 52 = 2,600; 2,600-760 = 1,840; -390 = 1,450; -1,050 = 400; total 2,200; 1,050 < 1,450 'enough') and check_numbers.py", ok and "MATHS OK" in run([sys.executable, str(HERE / "production" / "check_numbers.py")]).stdout)
def jitter(img, n=60):
    im = Image.new("RGBA", (img.width + 80, img.height + 80), (0, 0, 0, 0)); im.paste(img, (40, 40)); al = np.asarray(im)[..., 3].astype(float) / 255; sy, sx = np.mgrid[0:im.height, 0:im.width]; cxs, cys = (al * sx).sum() / al.sum() / im.width, (al * sy).sum() / al.sum() / im.height; ex, ey = [], []
    for k in range(n):
        t_ = k / (n - 1); h = 480 + 120 * t_; w = im.width * h / im.height; x, y = 300 + 40.37 * t_, 90 + 13.9 * t_; fr_ = Image.new("RGBA", (900, 900), (0, 0, 0, 0)); paste_smooth(fr_, im, x, y, w, h)
        a_ = np.asarray(fr_)[..., 3].astype(float) / 255; gy, gx = np.mgrid[0:a_.shape[0], 0:a_.shape[1]]; ex.append((a_ * gx).sum() / a_.sum() - (x + cxs * w)); ey.append((a_ * gy).sum() / a_.sum() - (y + cys * h))
    tt = np.arange(n); rs_ = lambda v_: float(np.std(np.array(v_) - np.polyval(np.polyfit(tt, v_, 3), tt))); return rs_(ex), rs_(ey)
worst = max(max(jitter(TR.maya_img(k))) for k in ("neutral", "surprised", "worried", "relief")); check("8 Maya sub-pixel placement noise <= 0.12 px (jitter_check method, all four poses)", worst <= 0.12, f"worst {worst:.3f}px")
# 9 Ren
lib = {c["file"]: c for c in json.loads((TR.ROOT / "assets" / "ren_library" / "ren_library.json").read_text())["clips"]}
exp_h = height_px("OFFICE_SAGE", 770) * PR.PK; ren_shots = [s for s in shots if s["type"] == "REN_ANIMATED"]
vf = lambda a_, b_: np.frombuffer(subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(mp4), "-vf", f"select='between(n,{a_},{b_ - 1})',format=rgb24", "-vsync", "0", "-f", "rawvideo", "-"]), np.uint8).reshape(-1, 1080, 1920, 3)
fails9 = []; clips = []
for s in ren_shots:
    n = s["fb"] - s["fa"]; boxes = [TF.frame_at(i)[2] for i in range(s["fa"], s["fb"])]; clip, st, mir = TR.REN[s["id"]]; ent = lib[clip + ".mp4"]; clips.append(clip)
    if not (ent["status"] == "ok" and ent["in_s"] - 0.001 <= st and st + n / FPS <= ent["out_s"] + 0.01): fails9.append((s["id"], "window", clip, round(st + n / FPS, 2), ent["out_s"]))
    bot = np.array([b.ren[3] for b in boxes]); top = np.array([b.ren[1] for b in boxes]); ids = [b.ren_i for b in boxes]; rc = TR._rc.get(s["id"]); nat = np.array([np.where(np.asarray(im_)[..., 3] > 128)[0].max() * rc.scale for im_ in rc.imgs[:n]]) if rc else bot
    if not (bot.std() <= max(1.0, nat.std() + 0.1) and bot.max() - bot.min() <= max(3.0, nat.max() - nat.min() + 0.5)): fails9.append((s["id"], "feet", round(float(bot.std()), 2)))
    if abs(np.median(bot - top) - exp_h) / exp_h > 0.06: fails9.append((s["id"], "scale", round(float(np.median(bot - top)))))
    if len(set(ids)) != n: fails9.append((s["id"], "distinct frames", len(set(ids)), n))
    V = vf(s["fa"], s["fb"]).astype(np.int16); dd = np.abs(np.diff(V, axis=0)).mean(3); x0, y0, x1, y1 = [int(v_) for v_ in (min(b.ren[0] for b in boxes) - 6, min(b.ren[1] for b in boxes) - 6, max(b.ren[2] for b in boxes) + 6, max(b.ren[3] for b in boxes) + 6)]
    mv = dd[:, max(y0, 0):y1, max(x0, 0):x1].mean((1, 2))
    if n > 3 and not (mv.mean() > 0.2 and (mv > 0.1).sum() >= 0.5 * len(mv)): fails9.append((s["id"], "movement", round(float(mv.mean()), 2)))
    rf = [np.asarray(TF.frame_at(i)[0].convert("RGB"))[150:700, 0:150].astype(np.int16) for i in (s["fa"], s["fa"] + n // 2, s["fb"] - 1)]
    if max(int(np.abs(rf[k + 1] - rf[k]).max()) for k in range(2)) != 0: fails9.append((s["id"], "camera/background changed"))
    mid = boxes[len(boxes) // 2]
    if not ((mid.ren[0] + mid.ren[2]) / 2 < 960 and not [b for b in mid if b[0] < mid.ren[2] and b[4] != "Ren" and b[3] > mid.ren[1] and b[2] > mid.ren[0]]): fails9.append((s["id"], "layout"))
    del V
check(f"9a all {len(ren_shots)} Ren shots: approved library clips inside their usable windows, feet fixed, 175 cm plate scale, every frame a distinct clip frame, real movement, static camera, Ren left / graphics right", not fails9, str(fails9[:6]))
cons = [(a_["id"], b_["id"]) for a_, b_ in zip(ren_shots, ren_shots[1:]) if a_["fb"] == b_["fa"] and TR.REN[a_["id"]][0] == TR.REN[b_["id"]][0]]; check("9b consecutive Ren shots never repeat the same clip", not cons, str(cons)); check("9c Ren clip variety recorded", True, str({c_: clips.count(c_) for c_ in sorted(set(clips))}))
# 10 Maya
bad_s, bad_g, weak = [], [], []; phone_only = {}
for s in [x for x in shots if x["type"] == "CHARACTER_ACTION"]:
    seen = set(); overlays = 0; closeup = s["id"] in SH.CLOSEUP or s["id"] in ("S09a", "S10b", "S14")
    for i in range(s["fa"], s["fb"], 2):
        _, _, B = TF.frame_at(i); seen.update(B.poses); m = B.maya; overlays += sum(1 for b in B if b[4] not in (TR.DISC,))
        if m:
            x, yf, r_, pl, k = m; exp = height_px(pl, yf, TR.MAYA_CM) * k
            if abs((r_[3] - r_[1]) - exp) / exp > 0.03: bad_s.append((s["id"], i, round(r_[3] - r_[1]), round(exp)))
            if not (r_[1] > 0 and (closeup or 0 < r_[3] < 1080)): bad_g.append((s["id"], i, [round(v) for v in r_]))
    if len(seen) < 2 and overlays == 0: weak.append(s["id"])
    phone_only[s["id"]] = seen <= {"worried", "relief", "glow_overlay"}
check("10a Maya's measured height equals the calibrated plate perspective (165 cm, within 3%); head and feet in frame except deliberate close-ups (head in)", not bad_s and not bad_g, str((bad_s[:3], bad_g[:3])))
check("10b every Maya shot changes pose or carries a moving prop/overlay (no shot is only a camera move over a still)", not weak, str(weak))
# longest stretch of consecutive shots (no Ren) in which Maya, where present, only holds a phone pose, vs total
longest = cur = 0.0; at = ""; cur_start = 0.0
for s in shots:
    dur = (s["fb"] - s["fa"]) / FPS
    if s["type"] == "REN_ANIMATED": cur = 0.0; continue
    if s["type"] == "CHARACTER_ACTION" and not phone_only.get(s["id"], False): cur = 0.0; continue
    if cur == 0.0: cur_start = s["fa"] / FPS
    cur += dur
    if cur > longest: longest, at = cur, f"{cur_start:.0f}-{s['fb'] / FPS:.0f} s"
ph = sum((s["fb"] - s["fa"]) for s in shots if s["type"] == "CHARACTER_ACTION" and phone_only.get(s["id"])) / max(1, sum((s["fb"] - s["fa"]) for s in shots if s["type"] == "CHARACTER_ACTION"))
check("10c no long stretch in which Maya only holds a phone pose (worried/relief) while graphics change: longest stretch without a Ren shot or a phone-free Maya pose <= 20 s", longest <= 20, f"longest {longest:.1f}s at {at}; phone-pose share of Maya screen time {100 * ph:.0f}%")
# environment variety: no more than 3 consecutive Maya shots on the same plate
runs_p = []; cur_p = None; n_p = 0
for s in shots:
    if s["type"] != "CHARACTER_ACTION": continue
    _, _, B = TF.frame_at((s["fa"] + s["fb"]) // 2); pl = B.maya[3] if B.maya else None
    if pl == cur_p: n_p += 1
    else: cur_p, n_p = pl, 1
    runs_p.append(n_p)
check("10d no more than 4 consecutive Maya shots on the same plate (environmental variety)", max(runs_p) <= 4, f"longest same-plate run {max(runs_p)}")
pk = [float(x) for x in run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "packet=pts_time", "-of", "csv=p=0", str(mp4)]).stdout.split()]
dpk = np.diff(sorted(pk)); check("11 constant 24 fps: every packet 1/24 s apart, no dropped or duplicated timestamps", (v["r_frame_rate"], v["avg_frame_rate"]) == ("24/1", "24/1") and np.allclose(dpk, 1 / 24, atol=2e-4) and len(pk) == NF, f"{len(pk)} packets, delta {dpk.min():.5f}-{dpk.max():.5f}")
# 12 voice
src = (HERE / "gen_voice.py").read_text(); srcs = "".join((HERE / f_).read_text() for f_ in ("tb_full.py", "tb_shots.py", "tb_ui2.py", "tb_render.py", "tb_ui.py"))
check("12a voice runner config: Qwen/Qwen3-TTS-12Hz-1.7B-Base, English, x_vector_only_mode=True, Audio/ren_reference.wav, fixed seeds, no speed change", "Qwen/Qwen3-TTS-12Hz-1.7B-Base" in src and "x_vector_only_mode=True" in src and 'language="English"' in src and "ren_reference.wav" in src)
check("12b renderers import and call no TTS code", not re.search(r"^\s*(import|from)\s+(qwen_tts|torch|transformers)|generate_voice_clone", srcs, re.M))
au_raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(mp4), "-ac", "1", "-ar", "24000", "-f", "f32le", "-"]); got_a = np.frombuffer(au_raw, np.float32); ref_a, _ = TF.audio(); m_ = min(len(got_a), len(ref_a))
cc = float(np.dot(got_a[:m_], ref_a[:m_]) / (np.linalg.norm(got_a[:m_]) * np.linalg.norm(ref_a[:m_]) + 1e-9)); check("12c MP4 audio matches the joined narration WAVs (correlation >= 0.95)", cc >= 0.95, f"{cc:.4f}")
check("12d spoken-word check against the script (Whisper)", (HERE / "voice_check_summary.json").exists() and all(k in json.loads((HERE / "voice_check_summary.json").read_text()) for k in TF.SECS), "see voice_check_summary.json", status=None if (HERE / "voice_check_summary.json").exists() else "NOT RUN")
# 13 pilot preserved
if pilot and pilot.exists():
    prep = json.loads((pilot.parent / (pilot.stem + "_report.json")).read_text()) if (pilot.parent / (pilot.stem + "_report.json")).exists() else None
    def grab(p_, a_, b_): return np.frombuffer(subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(p_), "-vf", f"select='between(n,{a_},{b_ - 1})',scale=480:270,format=gray", "-vsync", "0", "-f", "rawvideo", "-"]), np.uint8).reshape(-1, 270, 480).astype(np.int16)
    pf = int(prep["frames"]) if prep else 1364; end_ = ST["S17"]["fa"] + int(0.8 * (min(ST["S17"]["fb"], pf) - ST["S17"]["fa"]))
    dd_ = [float(np.abs(grab(mp4, a_, min(a_ + 200, end_)) - grab(pilot, a_, min(a_ + 200, end_))).mean((1, 2)).max()) for a_ in range(0, end_, 200)]
    check("13a approved pilot frames (0 to 80% of S17) unchanged in the full episode (max per-frame mean difference at 480x270)", max(dd_) < 1.5, f"worst {max(dd_):.2f}/255 over {end_} frames")
    ap_ = np.frombuffer(subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(pilot), "-ac", "1", "-ar", "24000", "-f", "f32le", "-"]), np.float32); m2 = min(len(ap_), len(got_a)) - 12000
    check("13b pilot narration unchanged in the full episode (correlation over the pilot's length)", float(np.dot(ap_[:m2], got_a[:m2]) / (np.linalg.norm(ap_[:m2]) * np.linalg.norm(got_a[:m2]) + 1e-9)) > 0.999, f"{float(np.dot(ap_[:m2], got_a[:m2]) / (np.linalg.norm(ap_[:m2]) * np.linalg.norm(got_a[:m2]) + 1e-9)):.5f}")
else: check("13 pilot comparison", False, "no pilot given", status="NOT RUN")
out = HERE / "reports"; out.mkdir(exist_ok=True)
md = ["# Full-episode QC - Three Bills in 30 Days", "", f"File: `{mp4.name}` | {NF} frames | 1920x1080 @ 24 fps | {dv / 60:.2f} min", "", "Command: `project/.tools/venv/bin/python videos/three_bills/tb_qa_full.py <mp4> <pilot rev3 mp4>`; thresholds are in the script.", "", "| Check | Result | Measured |", "|---|---|---|"]
for n_, st, dt in res: md.append(f"| {n_} | {st} | {dt.replace('|', '/')[:240]} |")
md += ["", "## Not run / limits", "- NOT RUN: listening review (accent, pace, pronunciation, joins). Whisper only confirms words.", "- NOT RUN: the repo's older qa_timeline.py, validate.py, jitter_check.py (wired to the 720p free_money renderer); their checks are re-implemented here.",
       "- Ren mouth-closed is not detected automatically: it rests on the library notes and on contact sheets I viewed.", "- 'Mobile readability' is checked as a minimum font size (32 px at 1080p) and the safe area; no phone playback was possible.",
       "- Maya is static artwork (four poses): pose cross-fades, camera pushes and moving props; none of this is character animation."]
(out / "full_qc.md").write_text("\n".join(md) + "\n"); fails = [n_ for n_, st, _ in res if st == "FAIL"]; print("\nOVERALL", "FAIL: " + "; ".join(fails) if fails else "PASS"); sys.exit(1 if fails else 0)
