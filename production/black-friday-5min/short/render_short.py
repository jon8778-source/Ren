"""Portrait (1080x1920, 24 fps) renderer for the Black Friday Short, under the Shorts launcher (project/pipeline/shorts_standards.py).

  project/.tools/venv/bin/python videos/three_bills/short/render_short.py --output OUT.mp4        (the launcher calls this; honours REN_SHORTS_STAGE / REN_SHORTS_MAX_FRAMES)
  project/.tools/venv/bin/python videos/three_bills/short/render_short.py --output OUT.mp4 --stills 1 5 12

Reuses the full episode's approved pieces: Maya cut-outs placed with ren_stage.stand (plate geometry LOT / PORCH / OFFICE), library Ren clips (pilot_ren.RenClip on the sage office,
OFFICE_SAGE scale standard), the sink-leak illustration, code-drawn cards. Beat timing comes from short_spec.json; narration is cut from the approved audio (short_audio.py).
Writes layout.json (measured text bounds in final-canvas coordinates).
"""
import argparse, json, math, os, subprocess, sys
from pathlib import Path
import numpy as np, soundfile as sf
from PIL import Image, ImageDraw, ImageFilter
HERE = Path(__file__).resolve().parent; BF = HERE.parent; ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(BF)); sys.path.insert(0, str(ROOT / "videos" / "unclaimed_401k")); sys.path.insert(0, str(ROOT / "project" / "cliplib")); sys.path.insert(0, str(ROOT / "videos" / "three_bills"))
import pilot_ren as PR, pilot_ui as U, bf_short_ui as S
from ren_stage import paste_smooth, contact_shadow, height_px

W, H, FPS = 1080, 1920, 24; ease, clamp = U.ease, U.clamp; DISCLAIMER = "Educational content only, not financial advice."
GRADE = {"eve": (40, 50, 110, 56), "morn": (255, 222, 150, 34), "sun": (255, 150, 90, 46)}
class Recorder:
    def __init__(self): self.items = {}
    def note(self, sid, key, bbox, px, role, text, t):
        k = (sid, key); it = self.items.get(k)
        if it is None: self.items[k] = dict(text=text, bbox=[float(v) for v in bbox], font_px=float(px), role=role, start=t)
        else:
            b = it["bbox"]; it["bbox"] = [min(b[0], bbox[0]), min(b[1], bbox[1]), max(b[2], bbox[2]), max(b[3], bbox[3])]; it["start"] = min(it["start"], t); it["font_px"] = min(it["font_px"], float(px))
class Ctx:
    def __init__(self, sid, t, d, T_, rec, f): self.sid, self.t, self.d, self.T, self.rec, self.f = sid, t, d, T_, rec, f
    def put(self, img, x, y, alpha=1.0, key="", scale=1.0, rec=True):
        if alpha <= 0.01: return
        im = img.im if scale == 1 else img.im.resize((max(1, int(img.im.width * scale)), max(1, int(img.im.height * scale))), Image.LANCZOS)
        if alpha < 1: im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
        self.f.alpha_composite(im, (int(round(x)), int(round(y))))
        if alpha > 0.5 and rec:
            for i, (a, b, c_, e, s_, px) in enumerate(img.texts): self.rec.note(self.sid, f"{key}{s_}{i}", (x + a * scale, y + b * scale, x + c_ * scale, y + e * scale), px * scale, "text", s_, self.T)
    def slide(self, img, x, y, t0, dur=0.4, frm=50, key="", scale=1.0):
        if self.t < t0: return
        p = ease((self.t - t0) / dur); self.put(img, x + frm * (1 - p), y, alpha=min(1.0, p * 1.6), key=key, scale=scale, rec=p > 0.99)
    def pill(self, text, x, y, px, role="text", alpha=1.0, fill=U.CREAM):
        f = U.font(px, 600); d0 = ImageDraw.Draw(Image.new("RGBA", (4, 4))); b = d0.textbbox((0, 0), text, font=f); w_, h_ = b[2] - b[0] + 56, b[3] - b[1] + 28
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); d.rounded_rectangle((x + 3, y + 7, x + w_ + 3, y + h_ + 7), h_ // 2, fill=(*U.NAVY, 55)); d.rounded_rectangle((x, y, x + w_, y + h_), h_ // 2, fill=(*fill, 255)); d.text((x + 28 - b[0], y + 14 - b[1]), text, font=f, fill=U.NAVY)
        if alpha < 1: lay.putalpha(lay.getchannel("A").point(lambda v: int(v * alpha)))
        self.f.alpha_composite(lay)
        if alpha > 0.5: self.rec.note(self.sid, "pill" + text, (x + 28, y + 14, x + w_ - 28, y + h_ - 14), px, role, text, self.T)

# ---- Ren on the sage office (portrait: Ren left, cards right) --------------------------------------------------------------------
class SCam:
    """Portrait camera over the 1920x1080 sage plate (SAGE_4k is 3840x2160): canvas = (plate - (cx, cy)) * z + (540, 960)."""
    z, cx, cy = 1.85, 330, 540
    def pt(self, x, y): return ((x - self.cx) * self.z + 540, (y - self.cy) * self.z + 960)
_sage = {}
def sage_plate(blur=0, veil=False):
    if "p" not in _sage: _sage["p"] = Image.open(ROOT / "videos" / "unclaimed_401k" / "art" / "plates" / "SAGE_4k.png").convert("RGB")
    z = SCam.z; a = 2.0 / z; f = _sage["p"].transform((W, H), Image.AFFINE, (a, 0, 2 * (SCam.cx - 540 / z), 0, a, 2 * (SCam.cy - 960 / z)), Image.BICUBIC).convert("RGBA")
    if blur: f = f.filter(ImageFilter.GaussianBlur(blur))
    if veil: f.alpha_composite(Image.new("RGBA", f.size, (*U.CREAM, 120)))
    return f
class RCam:
    PK = 1920 / 1672.0; k = SCam.z * PK
    def pt(self, x, y): return SCam().pt(x * self.PK, y * self.PK)
EV = json.loads((BF / "evidence" / "mouth_scan.json").read_text()); LIB = {x["source_name"].split(" (")[0]: x for x in json.loads((ROOT / "assets/ren_library/ren_library.json").read_text())["clips"]}
def ren_window(clip, d):
    """Clip start (s) whose [start, start + d + 0.15] lies inside a mouth-closed interval from the long film's frame scan (evidence/mouth_scan.json)."""
    e = EV.get(clip) or EV.get(clip.replace("palm_left", "palm_right"))
    for a, b in e["closed_intervals"]:
        if b - a >= d + 0.15: return a
    raise SystemExit(f"no mouth-closed window of {d + 0.15:.2f} s in {clip}: {e['closed_intervals']}")
_rc = {}
def ren_draw(c, clip, mirror):
    key = (c.sid, clip)
    if key not in _rc: _rc.clear(); _rc[key] = PR.RenClip(clip, ren_window(clip, c.d), c.d + 0.1, mirror=mirror)
    rc = _rc[key]; i = min(max(int(c.t * FPS + 1e-6), 0), rc.n - 1); im = rc.imgs[i]; x0, y0, _, _ = rc.box; feet = (185, 770); cam = RCam(); X, Y = cam.pt(*feet); s = height_px("OFFICE_SAGE", feet[1]) * cam.k / rc.h_clip
    contact_shadow(c.f, cam, feet[0], feet[1], 230); left = X - rc.cx * s + x0 * s; top = Y - rc.feet * s + y0 * s; paste_smooth(c.f, im, left, top, im.width * s, im.height * s)
    a = np.asarray(im)[..., 3]; ys, xs = np.where(a > 128); return (left + xs.min() * s, top + ys.min() * s, left + xs.max() * s, top + ys.max() * s)
def ren_scene(clip, mirror, panel, y=400, x=480, delay=0.25):
    def fn(c): c.f.alpha_composite(sage_plate()); ren_draw(c, clip, mirror); c.slide(panel(c), x, y, delay, key="rc")
    return fn
def clock_sec(c): return 3 * 3600 - 1 - int(c.T)

# ---- stills (portrait crops) and graphic scenes ----------------------------------------------------------------------------------
_st = {}
def still_p(path, cx_frac, zoom=1.0, p=0.0):
    """9:16 crop of a landscape still: full height, 607/1080 of it wide (centre at cx_frac of the width), slow push 1.0 -> 1.06 over the beat."""
    if path not in _st: _st[path] = Image.open(path).convert("RGB")
    im = _st[path]; h = im.height; z = zoom * (1 + 0.06 * ease(p)); cw = h * W / H / z; ch = h / z; cx = clamp(cx_frac * im.width, cw / 2, im.width - cw / 2); cy = im.height / 2; a = cw / W
    return im.transform((W, H), Image.AFFINE, (a, 0, cx - cw / 2, 0, a, cy - ch / 2), Image.BICUBIC).convert("RGBA")
ST_S1 = BF / "assets/stills_batch2/candidates/S1_shop_entrance_c2.png"; ST_CAFE = BF / "assets/approved_alex/alex-cafe.png"
def veil(c): c.f.alpha_composite(sage_plate(10, True))
def pop(c, img, cy=900, t0=0.12, dur=0.4, big=1.0, key="g"):
    if c.t < t0: return
    p = U.back((c.t - t0) / dur); s = max(0.05, p) * big; w, h = img.im.size; c.put(img, 540 - w * s / 2, cy - h * s / 2, scale=s, key=key, rec=(c.t - t0) / dur > 0.98)

def b_hook(c): ren_scene("ren_wave_hello", False, lambda c: S.sign(["Black Friday", "a test"], 420, "sage", 62), y=420)(c)
def b_spend(c):
    c.f.alpha_composite(still_p(ST_S1, 0.50, 1.0, c.t / max(c.d, 1e-6)))
    if c.t > 0.3: p = ease((c.t - 0.3) / 0.4); c.put(S.tag_flip(clamp((c.t - 1.1) / 0.5)), 190, 1090 + 60 * (1 - p), alpha=min(1, p * 1.6), key="tf", rec=p > 0.99)
def b_budget(c): ren_scene("ren_point_right", False, lambda c: S.total("Alex's budget", S.usd(S.V["budget"]), S.NAVY), y=400)(c)
def b_plans(c):
    c.f.alpha_composite(still_p(ST_CAFE, 0.38, 1.0, c.t / max(c.d, 1e-6)))
    if c.t > 0.3: p = ease((c.t - 0.3) / 0.4); c.put(S.plans(), 160, 1255 + 70 * (1 - p), alpha=min(1, p * 1.6), key="pl", rec=p > 0.99)
def b_plan_a(c): ren_scene("ren_present_palm_left", True, lambda c: S.total("Plan A ends at", S.usd(S.V["all_in"]), S.RED), y=400)(c)
def b_plan_b(c): veil(c); pop(c, S.total("Plan B ends at", S.usd(S.V["rule_path"]), S.GREEN, 640), 900, big=1.0)
def b_apart(c): ren_scene("ren_idle_calm", False, lambda c: S.apart(), y=300)(c)
def b_website(c): ren_scene("ren_hold_phone", False, lambda c: S.sign(["Shop", "website"], 420, "cream", 70), y=420)(c)
def b_clock(c): veil(c); pop(c, S.clock(clock_sec(c)), 900, key="ck")
def b_badge(c): veil(c); pop(c, S.badge("ONLY 3 LEFT"), 900, key="bd")
def b_saved(c): ren_scene("ren_point_right", False, lambda c: S.saved(), y=330)(c)
def b_notsaved(c): ren_scene("ren_idle_listen", False, lambda c: S.saved(420, clamp((c.t - 1.6) / 0.8), True), y=330)(c)
def b_spend183(c): veil(c); pop(c, S.parts(), 900, key="pt")
def b_rule2(c): ren_scene("ren_thinking", False, lambda c: S.rule(2, "Do the", "math"), y=360)(c)
def b_smaller(c): veil(c); pop(c, S.eq(), 900, key="eq")
def b_341(c): ren_scene("ren_point_right", False, lambda c: S.total("Alex is at", S.usd(S.V["all_in"]), S.RED), y=400)(c)
def b_overbudget(c): veil(c); pop(c, S.bar(clamp((c.t - 0.3) / 1.0)), 900, key="bar")
def b_rule4(c): ren_scene("ren_point_down_right", False, lambda c: S.rule(4, "Wait", "24 hours"), y=360)(c)
def b_question(c): ren_scene("ren_shrug", False, lambda c: S.question(), y=360)(c)
def b_sleep(c): veil(c); pop(c, S.moon(clamp((c.t - 0.4) / 1.5)), 900, key="mn")
def b_tally(c): ren_scene("ren_present_palm_left", True, lambda c: S.under("Under budget by", S.usd(300 - S.V["rule_path"]), S.GREEN) if c.t < 2.2 else S.under("Less than impulse", S.usd(S.V["diff"]), S.GREEN, 420, 44), y=400)(c)
def b_cta(c): ren_scene("ren_thumbs_up", False, lambda c: S.end(), y=330)(c)

BEAT = {"hook": b_hook, "spend-saving": b_spend, "budget": b_budget, "two-plans": b_plans, "plan-a": b_plan_a, "plan-b": b_plan_b, "apart": b_apart, "website": b_website, "clock": b_clock, "badge": b_badge, "saved-107": b_saved, "not-saved": b_notsaved,
        "spend-183": b_spend183, "rule-2": b_rule2, "smaller-bill": b_smaller, "over-341": b_341, "over-budget": b_overbudget, "rule-4": b_rule4, "question": b_question, "sleep": b_sleep, "tally": b_tally, "cta": b_cta}

class Short:
    def __init__(self, spec, rec, proto_end=0): self.spec, self.rec, self.proto_end = spec, rec, proto_end; self.beats = spec["beats"]; self.total = spec["frames"] / FPS
    def beat_at(self, k): return next(b for b in self.beats if b["start_frame"] <= k < b["end_frame"])
    def frame(self, k):
        b = self.beat_at(k); t = (k - b["start_frame"]) / FPS; d = (b["end_frame"] - b["start_frame"]) / FPS; T_ = k / FPS
        c = Ctx(b["id"], t, d, T_, self.rec, Image.new("RGBA", (W, H))); BEAT[b["id"]](c)
        if T_ < 3.0: c.pill("Educational only. Illustrative example.", 90, 1440, 36, role="disclaimer", alpha=min(clamp(T_ / 0.4), clamp((3.0 - T_) / 0.4)))
        end = self.proto_end / FPS if self.proto_end else self.total
        if T_ >= end - 2.3: c.pill(DISCLAIMER, 100, 1440, 32, role="disclaimer", alpha=clamp((T_ - (end - 2.3)) / 0.25))
        return c.f, b

def build_audio(frames, out_wav):
    a, sr = sf.read(HERE / "short_audio_raw.wav", dtype="float32"); raw = out_wav.with_suffix(".raw.wav"); sf.write(raw, a, sr)
    p = subprocess.run(["ffmpeg", "-nostats", "-i", str(raw), "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr; i0 = float(p[p.rindex("I:") + 2:].split()[0])
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af", f"volume={-16 - i0:.2f}dB,alimiter=limit=0.8:level=false,aresample=48000", "-t", f"{frames / FPS:.4f}", str(out_wav)], check=True); raw.unlink()
def merge_layout(parts, spec, frames, path):
    scenes = {b["id"]: [] for b in spec["beats"] if b["start_frame"] < frames}; merged = {}
    for p in parts:
        for it in json.loads(Path(p).read_text()):
            k = (it["scene"], it["key"])
            if k not in merged: merged[k] = it
            else:
                m, b = merged[k], it["bbox"]; m["bbox"] = [min(m["bbox"][0], b[0]), min(m["bbox"][1], b[1]), max(m["bbox"][2], b[2]), max(m["bbox"][3], b[3])]; m["start"] = min(m["start"], it["start"]); m["font_px"] = min(m["font_px"], it["font_px"])
    for (sid, key), it in merged.items(): scenes[sid].append(dict(text=it["text"], bbox=[round(v, 1) for v in it["bbox"]], font_px=round(it["font_px"], 1), role=it["role"], start=it["start"], end=0.0))
    Path(path).write_text(json.dumps({"scenes": scenes}, indent=2) + "\n")

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--output", type=Path, required=True); ap.add_argument("--jobs", type=int, default=4); ap.add_argument("--range", type=int, nargs=2); ap.add_argument("--seg", type=int, default=0); ap.add_argument("--stills", type=float, nargs="*"); args = ap.parse_args()
    spec = json.loads((HERE / "short_spec.json").read_text()); stage = os.environ.get("REN_SHORTS_STAGE", "prototype"); frames = min(int(os.environ.get("REN_SHORTS_MAX_FRAMES", 360 if stage == "prototype" else spec["frames"])), spec["frames"])
    out = args.output.resolve(); layout_path = out.parent / "layout.json"
    if args.stills is not None:
        S_ = Short(spec, Recorder(), frames if frames < spec["frames"] else 0)
        for t in args.stills: S_.frame(int(round(t * FPS)))[0].convert("RGB").save(out.parent / f"still_{t:05.2f}.png")
        return
    if args.range is None:
        build_audio(frames, out.with_suffix(".audio.wav")); jobs = max(1, args.jobs); bounds = [round(frames * k / jobs) for k in range(jobs + 1)]
        procs = [subprocess.Popen([sys.executable, str(Path(__file__)), "--output", str(out), "--range", str(bounds[k]), str(bounds[k + 1]), "--seg", str(k)], env=dict(os.environ)) for k in range(jobs)]
        for pr in procs:
            if pr.wait() != 0: raise SystemExit("a render segment failed")
        lst = out.parent / "segments.txt"; lst.write_text("".join(f"file '{out.parent / f'{out.stem}_seg{k}.mp4'}'\n" for k in range(jobs))); silent = out.with_suffix(".video.mp4")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(silent)], check=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(silent), "-i", str(out.with_suffix(".audio.wav")), "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-t", f"{frames / FPS:.4f}", "-movflags", "+faststart", str(out)], check=True)
        merge_layout([out.parent / f"{out.stem}_seg{k}.layout.json" for k in range(jobs)], spec, frames, layout_path); lay = json.loads(layout_path.read_text())
        for sid, items in lay["scenes"].items():
            b = next(x for x in spec["beats"] if x["id"] == sid)
            for it in items:
                it["end"] = min(b["end_frame"], frames) / FPS
                if it["role"] == "disclaimer" and it["text"] != DISCLAIMER: it["end"] = min(it["end"], 3.0)
        layout_path.write_text(json.dumps(lay, indent=2) + "\n")
        for k in range(jobs):
            for sfx in (".mp4", ".layout.json"): (out.parent / f"{out.stem}_seg{k}{sfx}").unlink()
        for p in (lst, silent, out.with_suffix(".audio.wav")): p.unlink()
        print("rendered", frames, "frames ->", out); return
    rec = Recorder(); S_ = Short(spec, rec, frames if frames < spec["frames"] else 0); a0, a1 = args.range; seg = out.parent / f"{out.stem}_seg{args.seg}.mp4"
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", str(seg)], stdin=subprocess.PIPE)
    for k in range(a0, a1):
        f, b = S_.frame(k); enc.stdin.write(np.asarray(f.convert("RGB"), np.uint8).tobytes())
        if (k - a0) % 60 == 0: print(f"frame {k}/{a1}", flush=True)
    enc.stdin.close(); enc.wait(); (out.parent / f"{out.stem}_seg{args.seg}.layout.json").write_text(json.dumps([dict(scene=sid, key=key, **it, end=0.0) for (sid, key), it in rec.items.items()]))
if __name__ == "__main__": main()
