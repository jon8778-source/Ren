"""Black Friday long-form: ~60 s PILOT (script sections 1-2), internal 1920x1080, delivered 1280x720, 24 fps. Long-form baseline rules.
  project/.tools/venv/bin/python production/black-friday-5min/bf_pilot.py --plan                  # shot table from the narration alignment
  project/.tools/venv/bin/python production/black-friday-5min/bf_pilot.py --stills OUT_DIR      # one still per shot midpoint
  project/.tools/venv/bin/python production/black-friday-5min/bf_pilot.py --out OUT_DIR --jobs 4 # render (local only)
Shot timing: each shot starts at the first narrated word of its phrase (Whisper medium.en word times aligned to the approved script, voice/words_pilot.json). Narration = voice/S1.wav + S2.wav
joined exactly as generated. Ren: genuine library clips (pilot_ren.RenClip: native decode + matting) in windows the mouth scan judged closed (evidence/mouth_scan.json), on the approved sage office plate
via the calibrated OFFICE_SAGE geometry. Alex: approved coffee-v3 art plus the owner-picked candidates (all unapproved stills are labelled so in the report). All text and figures are drawn in code (bf_ui.py)."""
import argparse, difflib, json, re, subprocess, sys
from pathlib import Path
import numpy as np, soundfile as sf
from PIL import Image, ImageDraw, ImageFilter
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(ROOT / "videos" / "unclaimed_401k")); sys.path.insert(0, str(ROOT / "project" / "cliplib")); sys.path.insert(0, str(ROOT / "videos" / "three_bills"))
import pilot_ren as PR, pilot_ui as U, bf_ui as B
from tools import shot_plan as SP
W, H, FPS = 1920, 1080, 24; ease, clamp = U.ease, U.clamp; VOICE = HERE / "voice"; A = HERE / "assets"; TAIL = 0.25
REN_X, REN_FEET = 470, 805      # plate coordinates (1672x941): nearer the camera and right of the chair, on the rug, so the shoes clear the chair legs
DISC = "Educational only, not financial advice."; CAP = {"R": 5.5, "S": 2.5, "G": 3.5}
STILL = {"S1c2": A / "stills_batch2/candidates/S1_shop_entrance_c2.png", "CAFE": A / "approved_alex/alex-cafe.png", "HOME": A / "approved_alex/alex-home.png", "M1": A / "stills/02_M1_old_coat.png", "M2": A / "stills/03_M2_gift.png"}
EV = json.loads((HERE / "evidence" / "mouth_scan.json").read_text()) if (HERE / "evidence" / "mouth_scan.json").exists() else {}
# pilot shots: (plan section, index in that section, kind, source, card builder name or None)   Ren source = (clip, mirror)
PL = [(1, 0, "R", ("ren_wave_hello", False), "title"), (1, 1, "S", "S1c2", None), (1, 2, "G", None, "tagflip"), (1, 3, "R", ("ren_point_right", False), "budget"), (1, 4, "G", None, "plans"),
      (1, 5, "R", ("ren_present_palm_left", True), "a341"), (1, 6, "G", None, "a263"), (1, 7, "R", ("ren_idle_calm", False), "apart"), (1, 8, "R", ("ren_point_down_right", False), "rules"), (1, 9, "G", None, "never"),
      (1, 10, "R", ("ren_nod_yes", False), "plansmall"), (2, 0, "S", "CAFE", None), (2, 1, "G", None, "reckless"), (2, 2, "S", "HOME", None), (2, 3, "G", None, "budget2"), (2, 4, "R", ("ren_idle_listen", False), "needs"),
      (2, 5, "S", "M1", None), (2, 6, "S", "M2", None), (2, 7, "G", None, "charger"), (2, 8, "R", ("ren_shrug", False), "angle"), (2, 9, "R", ("ren_nod_yes", False), "sensible"),
      (2, 10, "G", None, "sales"), (2, 11, "G", None, "notsale"), (2, 12, "R", ("ren_thinking", False), "decisions")]
FIG = {"budget", "a341", "a263", "apart", "budget2", "plansmall"}      # shots showing example figures
def norm(s): return SP.norm(s)
def phrases(): return [(SP.P[s][i][2], SP.P[s][i][3]) for s, i, *_ in PL]
def narration():
    a, sr = sf.read(VOICE / "S1.wav", dtype="float32"); b, sr2 = sf.read(VOICE / "S2.wav", dtype="float32"); assert sr == sr2; return np.concatenate([a, b]), sr
def words():
    p = VOICE / "words_pilot.json"; return json.loads(p.read_text()) if p.exists() else None
def shot_times():
    """(start, end) seconds per pilot shot from the aligned narration; uniform 0.36 s/word only when no narration exists (layout tests, never rendered)."""
    ph = [norm(p) for p, _ in phrases()]; flat = [w for p in ph for w in p]; n = len(flat); W_ = words()
    if W_ is None or not (VOICE / "S2.wav").exists(): t = 0.0; out = []; [out.append((t, t := t + 0.36 * len(p))) for p in ph]; return out, True
    hyp = [(norm(x["w"]) or [""])[0] for x in W_]; sm = difflib.SequenceMatcher(None, flat, hyp, autojunk=False); idx = {}
    for a, b, k in sm.get_matching_blocks():
        for j in range(k): idx[a + j] = b + j
    known = sorted(idx); tm = {}
    for i in range(n):
        if i in idx: tm[i] = W_[idx[i]]["s"]
        else:
            lo = max([k for k in known if k < i], default=None); hi = min([k for k in known if k > i], default=None)
            tm[i] = W_[idx[lo]]["e"] + 0.05 * (i - lo) if lo is not None else (W_[idx[hi]]["s"] - 0.05 * (hi - i) if hi is not None else 0.0)
    starts, c = [], 0
    for p in ph: starts.append(0.0 if c == 0 else max(0.0, tm[c] - 0.04)); c += len(p)
    dur = sum(len(sf.read(VOICE / f"S{k}.wav", dtype="float32")[0]) for k in (1, 2)) / 24000.0 + TAIL; ends = starts[1:] + [dur]; return list(zip(starts, ends)), False
def ren_window(clip, d):
    """Clip start (s) whose [start, start + d + 0.15] lies inside a mouth-closed interval; prefer the library window start."""
    e = EV.get(clip) or EV.get(clip.replace("palm_left", "palm_right")); lib = {x['source_name'].split(' (')[0]: x for x in json.load(open(ROOT / 'assets/ren_library/ren_library.json'))['clips']}
    lk = lib.get(clip) or lib[clip.replace("palm_left", "palm_right")]
    if not e: return lk["in_s"]
    for a, b in e["closed_intervals"]:
        if b - a >= d + 0.15: return a
    raise SystemExit(f"no mouth-closed window of {d + 0.15:.2f} s in {clip}: {e['closed_intervals']}")

class Cam:
    def __init__(self, z=1.0, cx=836, cy=470.5):
        self.z = max(1.0, z); self.cx = clamp(cx, 836 / self.z, 1672 - 836 / self.z); self.cy = clamp(cy, 470.5 / self.z, 941 - 470.5 / self.z); self.k = 1920 / 1672.0 * self.z
    def pt(self, x, y): return ((x - self.cx) * self.k + 960, (y - self.cy) * self.k + 540)
_pl = {}
def sage(blur=0, veil=False):
    if "S" not in _pl: _pl["S"] = Image.open(ROOT / "videos" / "unclaimed_401k" / "art" / "plates" / "SAGE.png").convert("RGB")
    im = _pl["S"]; sx = im.width / 1672.0; cam = Cam(); a = 1.0 / cam.k * sx
    f = im.transform((W, H), Image.AFFINE, (a, 0, (cam.cx - 960 / cam.k) * sx, 0, a, (cam.cy - 540 / cam.k) * sx), Image.BICUBIC).convert("RGBA")
    if blur: f = f.filter(ImageFilter.GaussianBlur(blur))
    if veil: f.alpha_composite(Image.new("RGBA", f.size, (*U.CREAM, 120)))
    return f
_st = {}
def still(key, p):
    """Full-bleed still scaled once to 1920x1080 with a slow push (centre crop 1.00 -> 1.06) that only explains the framing."""
    if key not in _st:
        im = Image.open(STILL[key]).convert("RGB"); 
        if im.size == (1920, 1088): im = im.crop((0, 4, 1920, 1084))
        _st[key] = im.resize((W, H), Image.LANCZOS) if im.size != (W, H) else im
    z = 1.0 + 0.06 * ease(p); a = 1 / z; return _st[key].transform((W, H), Image.AFFINE, (a, 0, W * (1 - a) / 2, 0, a, H * (1 - a) / 2), Image.BICUBIC).convert("RGBA")

class Rec:
    def __init__(self): self.items = []; self.ren = None
class Ctx:
    def __init__(self, sid, t, d, T_, f, rec): self.sid, self.t, self.d, self.T, self.f, self.rec = sid, t, d, T_, f, rec
    def put(self, img, x, y, alpha=1.0, scale=1.0, rec=True):
        if alpha <= 0.01: return
        im = img.im if scale == 1 else img.im.resize((max(1, int(img.im.width * scale)), max(1, int(img.im.height * scale))), Image.LANCZOS)
        if alpha < 1: im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
        self.f.alpha_composite(im, (int(round(x)), int(round(y))))
        if rec and alpha > 0.5:
            for (a, b, c_, e, s_, px) in img.texts: self.rec.items.append((self.sid, self.T, x + a * scale, y + b * scale, x + c_ * scale, y + e * scale, s_, px * scale))
    def slide(self, img, t0=0.25, dur=0.45, y=None, frm=70):
        if self.t < t0: return
        p = ease((self.t - t0) / dur); w, h = img.im.size; self.put(img, 1860 - w + frm * (1 - p), (y if y is not None else 520 - h / 2), alpha=min(1, p * 1.6), rec=p > 0.99)
    def pop(self, img, cx=960, cy=540, t0=0.12, dur=0.4, big=1.35):
        """Back-eased scale-in to `big` x the card (full-screen graphics read better on a phone when larger)."""
        if self.t < t0: return
        p = U.back((self.t - t0) / dur); s = max(0.05, p) * big; w, h = img.im.size; self.put(img, cx - w * s / 2, cy - h * s / 2, scale=s, rec=(self.t - t0) / dur > 0.98)
    def pill(self, text, x, y, px, alpha=1.0, anchor="l"):
        f = U.font(px, 600); d0 = ImageDraw.Draw(Image.new("RGBA", (4, 4))); b = d0.textbbox((0, 0), text, font=f); w_, h_ = b[2] - b[0] + 44, b[3] - b[1] + 24; x = x if anchor == "l" else x - w_
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); d.rounded_rectangle((x + 2, y + 5, x + w_ + 2, y + h_ + 5), h_ // 2, fill=(*U.NAVY, 50)); d.rounded_rectangle((x, y, x + w_, y + h_), h_ // 2, fill=(*U.CREAM, 255)); d.text((x + 22 - b[0], y + 12 - b[1]), text, font=f, fill=U.NAVY)
        if alpha < 1: lay.putalpha(lay.getchannel("A").point(lambda v: int(v * alpha)))
        self.f.alpha_composite(lay)
        if alpha > 0.5: self.rec.items.append((self.sid, self.T, x + 22, y + 12, x + w_ - 22, y + h_ - 12, text, px))

_rc = {}
def ren_draw(c, clip, mirror):
    key = (c.sid, clip)
    if key not in _rc: _rc.clear(); _rc[key] = PR.RenClip(clip, ren_window(clip, c.d), c.d + 0.1, cx_plate=REN_X, feet_plate=REN_FEET, mirror=mirror)
    bx, i = _rc[key].draw(c.f, c.t); c.rec.ren = (c.sid, c.T, *bx); return bx
def card_for(name, c):
    t, d = c.t, c.d
    return {"title": lambda: B.title_card("Black Friday", "a test", "Example figures"), "budget": lambda: B.total_card("Alex's budget", B.usd(B.V["budget"]), U.NAVY, 720), "plans": lambda: B.plans_card(), "a341": lambda: B.total_card("Plan A ends at", B.usd(B.V["all_in"]), U.RED),
            "a263": lambda: B.total_card("Plan B ends at", B.usd(B.V["rule_path"]), U.GREEN), "apart": lambda: B.apart_card(clamp((t - 0.5) / 1.2)), "rules": lambda: B.rules_chip(min(5, 1 + int(t / max(d, 1e-6) * 5))), "never": lambda: B.never_card(clamp((t - 0.6) / 0.9)),
            "plansmall": lambda: B.plans_card(), "budget2": lambda: B.total_card("Holiday budget", B.usd(B.V["budget"]), U.NAVY, 720), "needs": lambda: B.needs_card(), "charger": lambda: B.charger_card(), "angle": lambda: B.chip("Just the right angle", 760, "gold", 58),
            "sensible": lambda: B.chip("Waiting can be sensible", 860, "sage", 58), "sales": lambda: B.chip("Sales can be real", 900, "gold", 80), "notsale": lambda: B.tick_chip("The sale itself is fine", 940), "reckless": lambda: B.tick_chip("Alex isn't reckless", 900), "decisions": lambda: B.decisions_card(), "tagflip": lambda: B.tag_flip(clamp((t - 0.6) / 0.6))}[name]()
def draw_shot(c, sh):
    kind = sh["kind"]
    if kind == "R":
        c.f.alpha_composite(sage()); ren_draw(c, *sh["src"]); img = card_for(sh["card"], c); c.slide(img)
    elif kind == "S": c.f.alpha_composite(still(sh["src"], c.t / max(c.d, 1e-6)))
    else:
        c.f.alpha_composite(sage(9, True)); img = card_for(sh["card"], c)
        if sh["card"] in ("tagflip", "apart", "never"): c.pop(img, 960, 540, 0.12, 0.4) if c.t < 0.55 else c.put(img, 960 - img.im.width * 1.35 / 2, 540 - img.im.height * 1.35 / 2, scale=1.35)
        else: c.pop(img)
def build_shots():
    times, fake = shot_times(); out = []
    for k, ((s, i, kind, src, card), (a, b)) in enumerate(zip(PL, times)):
        fa, fb = round(a * FPS), round(b * FPS); out.append(dict(n=k + 1, id=f"P{k + 1:02d}", kind=kind, src=src, card=card, start=fa, end=fb, phrase=SP.P[s][i][2], plan_asset=SP.P[s][i][1]))
    return out, fake
def frame_at(shots, k, rec):
    sh = next(x for x in shots if x["start"] <= k < x["end"]); t = (k - sh["start"]) / FPS; d = (sh["end"] - sh["start"]) / FPS; T_ = k / FPS
    c = Ctx(sh["id"], t, d, T_, Image.new("RGBA", (W, H)), rec); draw_shot(c, sh)
    if T_ < 4.0: c.pill(DISC, 60, 985, 38, alpha=min(clamp(T_ / 0.4), clamp((4.0 - T_) / 0.4)))
    if sh["card"] in FIG: c.pill("Example figures", W - 60, 985, 38, anchor="r")
    return c.f, sh
def build_audio(out_wav, frames):
    a, sr = narration(); raw = out_wav.with_suffix(".raw.wav"); sf.write(raw, a, sr)
    p = subprocess.run(["ffmpeg", "-nostats", "-i", str(raw), "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr; i0 = float(p[p.rindex("I:") + 2:].split()[0])
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af", f"volume={-16 - i0:.2f}dB,alimiter=limit=0.8:level=false,aresample=48000,apad", "-t", f"{frames / FPS:.4f}", str(out_wav)], check=True); raw.unlink()
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--plan", action="store_true"); ap.add_argument("--stills"); ap.add_argument("--out"); ap.add_argument("--jobs", type=int, default=4); ap.add_argument("--range", type=int, nargs=2); ap.add_argument("--seg", type=int, default=0); args = ap.parse_args()
    shots, fake = build_shots(); total = shots[-1]["end"]
    if args.plan:
        print("FAKE (uniform) timing: layout test only" if fake else "timing from the narration alignment", "| frames", total, "=", round(total / FPS, 2), "s")
        for s in shots:
            d = (s["end"] - s["start"]) / FPS; flag = " OVER CAP" if d > CAP[s["kind"]] + 1e-9 else ""; print(f"{s['id']} {s['start'] / FPS:6.2f}-{s['end'] / FPS:6.2f} {d:4.2f}s {s['kind']} {s['card'] or s['src']}{flag} | {s['phrase'][:50]}")
        return
    if args.stills:
        out = Path(args.stills); out.mkdir(parents=True, exist_ok=True); rec = Rec()
        for s in shots: k = (s["start"] + s["end"]) // 2; frame_at(shots, k, rec)[0].convert("RGB").save(out / f"{s['id']}.png")
        return
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    if args.range is None:
        (out / "audio.wav").unlink(missing_ok=True); build_audio(out / "audio.wav", total); jobs = args.jobs; bounds = [round(total * k / jobs) for k in range(jobs + 1)]
        procs = [subprocess.Popen([sys.executable, str(Path(__file__)), "--out", str(out), "--range", str(bounds[k]), str(bounds[k + 1]), "--seg", str(k)]) for k in range(jobs)]
        for p in procs:
            if p.wait() != 0: raise SystemExit("a segment failed")
        (out / "segments.txt").write_text("".join(f"file '{out / f'seg{k}.mp4'}'\n" for k in range(jobs))); subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(out / "segments.txt"), "-c", "copy", str(out / "video.mp4")], check=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(out / "video.mp4"), "-i", str(out / "audio.wav"), "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-t", f"{total / FPS:.4f}", "-movflags", "+faststart", str(out / "pilot.mp4")], check=True)
        items = []; ren = []
        for k in range(jobs): r = json.loads((out / f"layout{k}.json").read_text()); items += r["items"]; ren += r["ren"]
        (out / "layout.json").write_text(json.dumps({"items": items, "ren": ren, "shots": [{k: v for k, v in s.items()} for s in shots]}, indent=1)); print("done", total, "frames"); return
    rec = Rec(); a0, a1 = args.range; ren = {}
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-vf", "scale=1280:720:flags=lanczos", "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", str(out / f"seg{args.seg}.mp4")], stdin=subprocess.PIPE)
    for k in range(a0, a1):
        f, sh = frame_at(shots, k, rec); enc.stdin.write(np.asarray(f.convert("RGB"), np.uint8).tobytes())
        if rec.ren and rec.ren[1] == k / FPS: ren[k] = rec.ren
        if (k - a0) % 48 == 0: print(f"frame {k}/{a1}", flush=True)
    enc.stdin.close(); enc.wait(); seen = {}
    for it in rec.items: seen[(it[0], it[6])] = it       # keep the last record per (shot, text)
    (out / f"layout{args.seg}.json").write_text(json.dumps({"items": list(seen.values()), "ren": [[k, *v] for k, v in ren.items()]}))
if __name__ == "__main__": main()
