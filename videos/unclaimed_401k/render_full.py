"""Full 401(k) match episode: the approved 53 s pilot (unchanged) followed by scenes 2 (rest) - 8 from full_plan.py.

  project/.tools/venv/bin/python videos/unclaimed_401k/render_full.py --plan                   # shot table + cap check, no video
  project/.tools/venv/bin/python videos/unclaimed_401k/render_full.py --stills OUT_DIR         # one still per new shot
  project/.tools/venv/bin/python videos/unclaimed_401k/render_full.py --out OUT_DIR --jobs 4   # render (local only)

Timing: each new shot starts at the first narrated word of its phrase (Whisper words aligned to the script, voice/words_<sec>.json);
the narration is joined exactly as generated (P1, P2, P3, S3 ... S8). No synthesis happens here.
"""
import argparse, difflib, json, math, re, subprocess, sys, time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import numpy as np, soundfile as sf
from PIL import Image, ImageFilter
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parents[1] / "project" / "cliplib"))
import render_pilot as R, pilot_assets as A, pilot_ui as U, pilot_ren as PR, full_ui as F, full_plan as P
W, H, FPS = R.W, R.H, 24
VOICE = R.VOICE
TM = json.loads((VOICE / "timings.json").read_text())
SECS = ["P3", "S3", "S4", "S5", "S6", "S7", "S8"]
NOWORDS = []
FAKE = []                                     # sections without real audio yet (layout tests only, never used for a render)
def _fake_missing():
    t = (HERE / "script" / "narration_v3.md").read_text(); parts = re.split(r"\*\*\[(S\d+): [^\]]*\]\*\*", t)
    secs = {parts[i]: " ".join(parts[i + 1].split()) for i in range(1, len(parts), 2)}; s2 = secs["S2"]; secs["P3"] = s2[s2.index("so she moved on.") + len("so she moved on."):].strip()
    for k in SECS:
        if k not in TM: TM[k] = {"duration": 0.42 * len(secs[k].split()) + 0.3, "text": secs[k]}; FAKE.append(k)
_fake_missing()
BASE = TM["P1"]["duration"] + TM["P2"]["duration"]
OFFS = {}; _o = BASE
for _s in SECS: OFFS[_s] = _o; _o += TM[_s]["duration"]
TOTAL = _o
FA0 = round(BASE * FPS)                       # first frame of the new material = the pilot's last frame boundary

def aligned_word_times(sec):
    """Per script word (whitespace-split): (start, end) in the section audio, from Whisper words by sequence alignment."""
    text = TM[sec]["text"].split()
    if sec in FAKE or not (VOICE / f"words_{sec}.json").exists():
        NOWORDS.append(sec); return [(0.42 * i, 0.42 * i + 0.3) for i in range(len(text))]
    words = json.loads((VOICE / f"words_{sec}.json").read_text())
    def toks(s):
        s = s.lower().replace("’", "'").replace("-", " ").replace(",", "").replace("$", " $ ")
        return [t for t in re.findall(r"[a-z0-9']+", s) if t != "and"]
    st, sidx = [], []
    for i, w in enumerate(text):
        for t in toks(w) or ["."]: st.append(t); sidx.append(i)
    wt, widx = [], []
    for j, w in enumerate(words):
        for t in toks(w["word"]) or ["."]: wt.append(t); widx.append(j)
    sm = difflib.SequenceMatcher(None, st, wt, autojunk=False)
    start = [None] * len(text); end = [None] * len(text)
    for blk in sm.get_matching_blocks():
        for k in range(blk.size):
            i, j = sidx[blk.a + k], widx[blk.b + k]
            if start[i] is None: start[i] = words[j]["start"]
            end[i] = words[j]["end"]
    known = [i for i, v in enumerate(start) if v is not None]
    for i in range(len(text)):
        if start[i] is None:
            lo = max([k for k in known if k < i], default=None); hi = min([k for k in known if k > i], default=None)
            a = end[lo] if lo is not None else 0.0; b = start[hi] if hi is not None else words[-1]["end"]
            n_lo = lo if lo is not None else -1; n_hi = hi if hi is not None else len(text); frac = (i - n_lo) / (n_hi - n_lo)
            start[i] = a + (b - a) * (frac - 0.5 / (n_hi - n_lo)); end[i] = a + (b - a) * frac
    return list(zip(start, end))

# Ren library windows (usable in/out from ren_library.json) and the second at which each clip's gesture starts (from the motion profile)
ROT = [("ren_thinking", 1.25, 9.12, False, 1.5), ("ren_open_arms", 1.38, 7.0, False, 1.5), ("ren_present_palm_left", 1.12, 7.88, True, 1.5), ("ren_nod_yes", 1.12, 9.0, False, 1.5),
       ("ren_shrug", 1.12, 10.0, False, 1.5), ("ren_point_up", 1.12, 9.0, False, 1.5), ("ren_point_right", 1.0, 6.38, False, 1.5)]      # thumbs_up left out: toothy grin at its peak
SPECIAL = {"ren_wave_bye": (1.25, 6.12, False, 1.6), "ren_point_camera": (1.12, 5.88, False, 1.5)}      # wave_hello opens its mouth mid-wave; wave_bye keeps it closed
CAMS = {"w": R.Cam(1.0, 960, 540), "m": R.Cam(1.3, 1000, 565), "c": R.Cam(1.55, 920, 470)}

def build_shots():
    shots, pos = [], {s: 0 for s in SECS}
    aligned = {s: aligned_word_times(s) for s in SECS}
    for sp in P.SPEC:
        sec = sp["sec"]; text = TM[sec]["text"].split(); ph = sp["phrase"].split(); i = pos[sec]
        assert text[i:i + len(ph)] == ph, (sp["id"], text[i:i + len(ph)], ph)
        pos[sec] = i + len(ph)
        shots.append(dict(sp, a=OFFS[sec] + (0.0 if i == 0 else aligned[sec][i][0]), widx=i))
    for k, s in enumerate(shots):
        s["b"] = shots[k + 1]["a"] if k + 1 < len(shots) else TOTAL
        s["fa"] = FA0 if k == 0 else round(s["a"] * FPS)
        s["fb"] = round(s["b"] * FPS) if k + 1 < len(shots) else int(math.ceil(TOTAL * FPS - 1e-6))
    for k, s in enumerate(shots[:-1]): assert shots[k + 1]["fa"] == s["fb"]
    # alternate medium / close framing on consecutive Maya shots so each cut is a visible change of shot size
    prev_cam = None; run = 0
    for s in shots:
        if s["kind"] == "maya":
            run = run + 1 if prev_cam else 0
            s["camk"] = "m" if run % 2 == 0 else "c"; prev_cam = s["camk"]
        else: prev_cam = None; run = 0
    # Ren clip + start second per Ren shot
    uses = {}; ri = 0
    for s in shots:
        if s["kind"] != "ren": continue
        d = (s["fb"] - s["fa"]) / FPS
        if s.get("clip"):
            in_s, out_s, mir, onset = SPECIAL[s["clip"]]; clip = s["clip"]
        else:
            clip, in_s, out_s, mir, onset = ROT[ri % len(ROT)]; ri += 1
        n = uses.get(clip, 0); uses[clip] = n + 1
        start = max(in_s, onset - 0.3)          # always the clean part of the clip (the tails of some clips turn Ren sideways)
        if start + d > out_s - 0.12: start = max(in_s, out_s - d - 0.12)
        s["ren"] = dict(clip=clip, start=round(start, 2), mirror=mir, fits=(start + d <= out_s + 0.01 and start >= in_s - 0.001))
    return shots

CAPS = dict(R.CAPS); CAPS["GRAPHIC"] = 3.5
def check_caps(shots):
    bad = [(s["id"], s["type"], round((s["fb"] - s["fa"]) / FPS, 2)) for s in shots if (s["fb"] - s["fa"]) / FPS > CAPS[s["type"]] + 1e-6]
    unfit = [(s["id"], s["ren"]) for s in shots if s["kind"] == "ren" and not s["ren"]["fits"]]
    return bad, unfit

_rc = {}
def ren_for(s):
    k = s["id"]
    if k not in _rc:
        _rc.clear(); r = s["ren"]; n = (s["fb"] - s["fa"]) / FPS
        _rc[k] = PR.RenClip(r["clip"], r["start"], n + 0.05, mirror=r["mirror"])
    return _rc[k]

def scaled(img, s):
    im = img.im.resize((int(img.im.width * s), int(img.im.height * s)), Image.LANCZOS)
    return F.Img(im, [(a * s, b * s, c * s, e * s, t, px * s) for (a, b, c, e, t, px) in img.texts])

def shot_frame(i, s, B):
    t = (i - s["fa"]) / FPS; d = (s["fb"] - s["fa"]) / FPS; T_abs = i / FPS
    R.REC["poses"] = []; R.REC["maya"] = None; R.REC["tip"] = None
    if s["kind"] == "maya":
        cam = CAMS[s["camk"]]; f = R.plate4k("O1_4k", cam); X, Y = cam.pt(*R.O1S)
        R.track(f, s["poses"], t, X, Y, S=R.S0 * cam.z)
        for c in s["cards"]: R.slide_in(f, c["fn"](t - c["t0"]) if False else c["fn"](max(0.0, t - c["t0"])), c["x"], c["y"], t, c["t0"], B=B)
    elif s["kind"] == "ren":
        f = A.plate("SAGE"); c = ren_for(s); bx, idx = c.draw(f, t); B.ren, B.ren_i = bx, idx
        img = s["panel"](t); x = 1880 - img.im.width; y = int(max(40, min(540 - img.im.height / 2 - 20, 950 - img.im.height)))
        R.slide_in(f, img, x, y, t, 0.0, dur=0.5, frm=0, B=B)
    elif s["kind"] == "graphic":
        f = R.backdrop("O1", 16, 0.58); img = s["panel"](t); sc = s["s"] or min(1.45, 1700 / img.im.width, 800 / img.im.height); img = scaled(img, sc)
        x = (W - img.im.width) / 2; y = max(40, min((H - img.im.height) / 2 - 30, 950 - img.im.height))
        R.slide_in(f, img, x, y, t, 0.0, dur=0.0, frm=0, B=B)
    elif s["kind"] == "still":
        im = Image.open(A.ART / "stills" / f"{s['image']}.png").convert("RGB"); z = 1.0 + 0.06 * U.ease(t / d)
        base = im.resize((W, H), Image.LANCZOS).convert("RGBA"); f = R.zoom(base, z, W * 0.45, H * 0.45)
        U.pill(f, "Alex, a colleague", 60, 56, px=40, weight=700, boxes=B, pad=(28, 12))
    B.poses = list(R.REC["poses"]); B.maya = R.REC["maya"]; B.tip = R.REC["tip"]
    return f

SHOTS = None
def frame_at(i):
    global SHOTS
    if SHOTS is None: SHOTS = build_shots()
    if i < FA0: return R.frame_at(i)
    s = next(x for x in SHOTS if x["fa"] <= i < x["fb"]); B = R.Boxes()
    f = shot_frame(i, s, B)
    return f, s, B

def audio():
    parts = []
    assert not FAKE, f"no real audio for {FAKE}"
    for k in ["P1", "P2"] + SECS:
        a, sr = sf.read(VOICE / f"{k}.wav", dtype="float32"); parts.append(a)
    return np.concatenate(parts), sr

def render_range(args):
    lo, hi, out = args
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "15", "-pix_fmt", "yuv420p", "-g", "48", str(out)]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(lo, hi):
        f, _, _ = frame_at(i); p.stdin.write(f.convert("RGB").tobytes())
    p.stdin.close(); assert p.wait() == 0
    return str(out)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--plan", action="store_true"); ap.add_argument("--stills"); ap.add_argument("--out"); ap.add_argument("--jobs", type=int, default=4); ap.add_argument("--name", default="episode")
    a = ap.parse_args(); shots = build_shots()
    nfr = int(math.ceil(TOTAL * FPS - 1e-6))
    if a.plan:
        bad, unfit = check_caps(shots)
        for s in shots: print(f"{s['id']} {s['type'][:6]:6s} {s['a']:7.2f}-{s['b']:7.2f} {s['b'] - s['a']:4.1f}s {s['kind']:7s} {(s.get('ren') or {}).get('clip', '')} {s['phrase'][:60]}")
        print(f"\n{len(shots)} new shots, total {TOTAL:.2f}s = {nfr} frames; caps violated: {bad}; Ren windows that do not fit: {unfit}"); return
    if a.stills:
        o = Path(a.stills); o.mkdir(parents=True, exist_ok=True)
        for s in shots:
            i = (s["fa"] + s["fb"]) // 2; global SHOTS; SHOTS = shots; f, _, _ = frame_at(i); f.convert("RGB").save(o / f"{s['id']}.png")
        print("stills ->", o); return
    assert not NOWORDS and not FAKE, f"alignment words missing for {sorted(set(NOWORDS))}, fake audio {FAKE}"
    o = Path(a.out).resolve(); o.mkdir(parents=True, exist_ok=True); n = a.jobs
    edges = [round(nfr * k / n) for k in range(n + 1)]; t0 = time.monotonic()
    with ProcessPoolExecutor(n) as ex:
        futs = [ex.submit(render_range, (edges[k], edges[k + 1], o / f"_seg{k}.mp4")) for k in range(n)]; segs = [f.result() for f in futs]
    lst = o / "_segs.txt"; lst.write_text("".join(f"file '{s}'\n" for s in segs))
    au, sr = audio(); wav = o / f"{a.name}_audio.wav"; sf.write(wav, au, sr); mp4 = o / f"{a.name}.mp4"
    subprocess.check_call(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-i", str(wav), "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-af", "apad,volume=-0.3dB", "-shortest", "-movflags", "+faststart", str(mp4)])
    for s in segs: Path(s).unlink()
    lst.unlink()
    allshots = [dict(id=x["id"], type=x["type"], phrase=x["phrase"], scene=R.SCENE[x["id"]], start=x["fa"] / FPS, end=x["fb"] / FPS, fa=x["fa"], fb=x["fb"], pilot=True) for x in R.SHOTS[:-1]]
    p19 = R.SHOTS[-1]; allshots.append(dict(id=p19["id"], type=p19["type"], phrase=p19["phrase"], scene=R.SCENE[p19["id"]], start=p19["fa"] / FPS, end=FA0 / FPS, fa=p19["fa"], fb=FA0, pilot=True))
    for x in shots: allshots.append(dict(id=x["id"], type=x["type"], phrase=x["phrase"], scene=x["kind"], start=x["fa"] / FPS, end=x["fb"] / FPS, fa=x["fa"], fb=x["fb"], pilot=False, ren=x.get("ren")))
    rep = dict(video=mp4.name, frames=nfr, fps=FPS, size=[W, H], audio_s=len(au) / sr, shots=allshots, render_s=round(time.monotonic() - t0))
    (o / f"{a.name}_report.json").write_text(json.dumps(rep, indent=1)); print("done", mp4, rep["render_s"], "s")

if __name__ == "__main__":
    main()
