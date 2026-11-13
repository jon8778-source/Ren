"""Portrait (1080x1920, 24 fps) renderer for the Three Bills Short, under the Shorts launcher (project/pipeline/shorts_standards.py).

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
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent)); sys.path.insert(0, str(HERE.parents[1] / "unclaimed_401k")); sys.path.insert(0, str(ROOT / "project" / "cliplib"))
import tb_render as TR, tb_ui as T, pilot_ren as PR, pilot_ui as U, render_pilot as RP, short_ui as S
from ren_stage import paste_smooth, contact_shadow, height_px

W, H, FPS = 1080, 1920, 24; ease, clamp = U.ease, U.clamp; DISCLAIMER = "Educational content only, not financial advice."
GRADE = {"eve": (40, 50, 110, 56), "morn": (255, 222, 150, 34), "sun": (255, 150, 90, 46)}
class PCam:
    """Portrait camera over a 1672x941 approved plate: canvas = (plate - (cx, cy)) * k + (540, 960), k = 1920/941 * zoom. The view never leaves the plate."""
    def __init__(self, z, cx, cy=470.5):
        self.z = max(1.0, z); self.k = 1920 / 941.0 * self.z; self.cx = clamp(cx, 540 / self.k, 1672 - 540 / self.k); self.cy = clamp(cy, 960 / self.k, 941 - 960 / self.k)
    def pt(self, x, y): return ((x - self.cx) * self.k + 540, (y - self.cy) * self.k + 960)
_pl = {}
def plate(name, cam, blur=0, veil=False):
    if name not in _pl: _pl[name] = Image.open(TR.LIB / f"{TR.PLATE_FILE[name]}.png").convert("RGB")
    a = 1.0 / cam.k; f = _pl[name].transform((W, H), Image.AFFINE, (a, 0, cam.cx - 540 / cam.k, 0, a, cam.cy - 960 / cam.k), Image.BICUBIC).convert("RGBA")
    if blur: f = f.filter(ImageFilter.GaussianBlur(blur))
    if veil: f.alpha_composite(Image.new("RGBA", f.size, (*U.CREAM, 120)))
    return f
def grade(c, g):
    if g: c.f.alpha_composite(Image.new("RGBA", c.f.size, GRADE[g]))

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

# ---- Maya on an approved plate ---------------------------------------------------------------------------------------------------
PL = {"LOT": dict(x=700, y=800, cx=860), "PORCH": dict(x=640, y=780, cx=760), "OFFICE": dict(x=760, y=820, cx=850)}
def maya_scene(pl, poses, z0=1.0, z1=None, g=None, extra=None, cy=470.5, closeup=False):
    z1 = z0 if z1 is None else z1; P = PL[pl]
    def fn(c):
        z = z0 + (z1 - z0) * ease(c.t / max(c.d, 1e-6)); cam = PCam(z, P["cx"], cy + 0 * z); c.f.alpha_composite(plate(pl, cam)); RP.REC["poses"] = []
        TR.maya(c.f, cam, pl, poses, c.t, P["x"], P["y"], None); r = RP.REC["maya"][2] if RP.REC["maya"] else None; grade(c, g)
        if extra: extra(c, r)
    fn.closeup = closeup; return fn

# ---- Ren on the sage office (portrait: Ren left, cards right) --------------------------------------------------------------------
class SCam:
    """Portrait camera over the 1920x1080 sage plate (SAGE_4k is 3840x2160): canvas = (plate - (cx, cy)) * z + (540, 960)."""
    z, cx, cy = 1.85, 330, 540
    def pt(self, x, y): return ((x - self.cx) * self.z + 540, (y - self.cy) * self.z + 960)
_sage = {}
def sage_plate():
    if "p" not in _sage: _sage["p"] = Image.open(ROOT / "videos" / "unclaimed_401k" / "art" / "plates" / "SAGE_4k.png").convert("RGB")
    z = SCam.z; a = 2.0 / z; return _sage["p"].transform((W, H), Image.AFFINE, (a, 0, 2 * (SCam.cx - 540 / z), 0, a, 2 * (SCam.cy - 960 / z)), Image.BICUBIC).convert("RGBA")
class RCam:
    PK = 1920 / 1672.0; k = SCam.z * PK
    def pt(self, x, y): return SCam().pt(x * self.PK, y * self.PK)
_rc = {}
def ren_draw(c, clip, start, mirror):
    key = (c.sid, clip)
    if key not in _rc: _rc.clear(); _rc[key] = PR.RenClip(clip, start, c.d + 0.1, mirror=mirror)
    rc = _rc[key]; i = min(max(int(c.t * FPS + 1e-6), 0), rc.n - 1); im = rc.imgs[i]; x0, y0, _, _ = rc.box; feet = (225, 770); cam = RCam(); X, Y = cam.pt(*feet); s = height_px("OFFICE_SAGE", feet[1]) * cam.k / rc.h_clip
    contact_shadow(c.f, cam, feet[0], feet[1], 230); left = X - rc.cx * s + x0 * s; top = Y - rc.feet * s + y0 * s; paste_smooth(c.f, im, left, top, im.width * s, im.height * s)
    a = np.asarray(im)[..., 3]; ys, xs = np.where(a > 128); return (left + xs.min() * s, top + ys.min() * s, left + xs.max() * s, top + ys.max() * s)
def ren_scene(clip, start, mirror, panel, y=400, x=480, delay=0.25):
    def fn(c): c.f.alpha_composite(sage_plate()); ren_draw(c, clip, start, mirror); c.slide(panel(c), x, y, delay, key="rc")
    return fn

# ---- graphic scenes ----------------------------------------------------------------------------------------------------------------
def veil_bg(pl, g=None, blur=9):
    def fn(c):
        P = PL[pl]; c.f.alpha_composite(plate(pl, PCam(1.0, P["cx"]), blur=blur, veil=True)); grade(c, g)
    return fn
def table(c, pl):
    c.f.alpha_composite(plate(pl, PCam(1.0, PL[pl]["cx"]), blur=9, veil=True)); d = ImageDraw.Draw(c.f); d.rectangle((0, 1290, W, H), fill=(178, 124, 88, 255)); d.line((0, 1290, W, 1290), fill=(*U.NAVY, 255), width=6)
    for x in range(-100, W + 200, 230): d.line((x, 1300, x - 60, H), fill=(160, 110, 78, 255), width=3)

def b_hook(c): ren_scene("ren_present_palm_left", 1.3, True, lambda c: S.sign_p("3 bills, 30 days", 420, "sage", 64), y=420)(c)
def b_car(c):
    def extra(c, r):
        p = ease(c.t / 1.6); ang = 720 * (1 - (1 - p) ** 3); TR.put_prop(c.f, "car_key", 780, 470, 260, rot=-ang + 20)
    maya_scene("LOT", [(0, "neutral"), (0.9, "surprised")], 1.0, 1.1, extra=extra)(c)
def b_invoice(c):
    table(c, "LOT"); q = clamp(c.t / 0.42); y = -950 + (320 + 950) * q * q
    if c.t > 0.42: y = 320 - 30 * math.sin(clamp((c.t - 0.42) / 0.24) * math.pi)
    inv = S.invoice_p("Dental bill", T.A["dental_bill"], "After insurance", urgent=c.t > 0.9); rot = inv.im.rotate(-4, Image.BICUBIC, expand=True); c.f.alpha_composite(rot, (170, int(y)))
    if y > 120: [c.rec.note(c.sid, f"inv{s_}", (190 + a, y + 20 + b, 190 + cc, y + 20 + e, ), px, "text", s_, c.T) for (a, b, cc, e, s_, px) in inv.texts]
def b_porch_worse(c): maya_scene("PORCH", [(0, "worried"), (1.4, "neutral")], 1.08, 1.16)(c)
BOX_A = (905, 0, 1434, 941); BOX_B = (925, 50, 1405, 903)
def b_kitchen(c):
    p = ease(c.t / max(c.d, 1e-6)); box = tuple(BOX_A[i] + (BOX_B[i] - BOX_A[i]) * p for i in range(4)); x0, y0, x1, y1 = box; s = H / (y1 - y0)
    c.f.alpha_composite(TR.kit().transform((W, H), Image.AFFINE, (1 / s, 0, x0, 0, 1 / s, y0), Image.BICUBIC).convert("RGBA")); TR.kit_drip(c.f, (lambda x, y: ((x - x0) * s, (y - y0) * s)), s, c.t)
def b_total(c): ren_scene("ren_shrug", 1.3, False, lambda c: S.equation_p(420), y=380)(c)
def b_savings(c):
    def extra(c, r):
        big = ("$2,600", U.NAVY) if c.t < 1.9 else (T.usd(T.A["fund_final"]), U.RED); c.slide(S.phone_p([("title", "Savings"), ("big", big[0], big[1]), ("gap", 20), ("row", "Fell", "-$2,200", U.RED)], 440, 560), 470, 230, 1.0, key="sv")
    maya_scene("OFFICE", [(0, "neutral"), (0.6, "worried")], 1.35, 1.42, g="eve", extra=extra)(c)
def b_backwards(c):
    maya_scene("PORCH", [(0, "worried")], 1.28, 1.34, g="eve", extra=lambda c, r: c.slide(S.bubble_p("I've gone backwards", 520), 400, 330, 0.3, frm=30, key="bb"), closeup=True)(c)
def b_why(c): ren_scene("ren_point_right", 1.3, False, lambda c: S.sign_p("Not backwards", 420, "gold", 64), y=420)(c)
def b_paid(c):
    def extra(c, r):
        cc_ = T.credit_card(400); c.slide(cc_, 500, 420, 0.3, key="cc")
        if c.t > 1.3:
            k = U.back((c.t - 1.3) / 0.3); s_ = max(0.05, k); im = Image.new("RGBA", (300, 120), (0, 0, 0, 0)); dd = ImageDraw.Draw(im); U.rrect(dd, (0, 0, 299, 119), 40, (*U.GREEN, 255), (*U.NAVY, 255), 5); dd.text((150, 62), "Paid off", font=U.font(64, 700), fill=U.CREAM, anchor="mm")
            im = im.resize((int(300 * s_), int(120 * s_)), Image.LANCZOS).rotate(-8, Image.BICUBIC, expand=True); c.f.alpha_composite(im, (int(760 - im.width / 2), int(470 - im.height / 2)))
            if k > 0.97: c.rec.note(c.sid, "paid", (630, 440, 890, 500), 64, "text", "Paid off", c.T)
    maya_scene("PORCH", [(0, "worried"), (0.8, "relief")], 1.08, 1.14, extra=extra)(c)
def b_auto(c):
    veil_bg("OFFICE")(c); on = clamp((c.t - 1.1) / 0.35); img = S.phone_p([("title", "Automatic transfer"), ("big", T.usd(T.A["weekly_transfer"]), U.NAVY, 110), ("row", "Every", "week"), ("toggle", "Automatic", on)], 640, 560); p = ease(c.t / 0.4)
    c.put(img, 220, 400 + 260 * (1 - p), alpha=min(1, p * 1.6), rec=p > 0.99)
def b_fifty(c): ren_scene("ren_open_arms", 1.5, False, lambda c: S.sign_p("$50 x 52 = $2,600", 420, "gold", 64), y=400)(c)
def b_answer(c): maya_scene("LOT", [(0, "surprised"), (0.7, "relief")], 1.0, 1.1, extra=lambda c, r: c.slide(S.sign_p("The money was already there", 440, "gold", 54), 460, 300, 0.7, key="mw"))(c)
def _fund_phone(c, p):
    return S.phone_p([("title", "Emergency fund"), ("bar", 1.0 - (1.0 - T.A["fund_final"] / T.A["fund_start"]) * ease(p), U.SAGE, "$2,600 to $400"), ("gap", 20), ("check", "Used on purpose") if p > 0.95 else ("gap", 10)], 440, 560)
def b_gone(c): maya_scene("OFFICE", [(0, "worried")], 1.35, 1.42, g="eve", extra=lambda c, r: c.slide(_fund_phone(c, clamp((c.t - 0.5) / 2.2)), 470, 250, 0.2, key="fp"))(c)
def b_400(c):
    veil_bg("OFFICE", "eve")(c); p = ease(c.t / 0.4); c.put(S.phone_p([("title", "Savings"), ("big", T.usd(T.A["fund_final"]), U.RED, 120)], 620, 420), 230, 520 + 240 * (1 - p), alpha=min(1, p * 1.6), rec=p > 0.99)
def b_smaller(c): ren_scene("ren_nod_yes", 1.3, False, lambda c: _fund_phone(c, clamp((c.t - 0.4) / 2.2)), y=330)(c)
def b_using(c): maya_scene("PORCH", [(0, "neutral"), (0.9, "relief")], 1.28, 1.34, extra=lambda c, r: c.slide(S.cross_p("Failure", clamp((c.t - 0.7) / 0.6), 440), 470, 340, 0.2, key="fl"), closeup=True)(c)
def b_job(c): maya_scene("LOT", [(0, "neutral"), (1.0, "relief")], 1.0, 1.08, g="morn", extra=lambda c, r: c.slide(S.sign_p("Its job: pay for emergencies", 440, "gold", 52), 460, 300, 0.4, key="jb"))(c)
def b_question(c): ren_scene("ren_thinking", 1.5, False, lambda c: S.sign_p("Which bill feels more manageable today?", 440, "cream", 50), y=360)(c)
def b_closing(c): maya_scene("PORCH", [(0, "relief")], 1.08, 1.14, g="sun")(c)

BEAT = {"ren-hook": b_hook, "car-breakdown": b_car, "dental-invoice": b_invoice, "porch-worse": b_porch_worse, "kitchen-leak": b_kitchen, "ren-total": b_total, "savings-app": b_savings, "gone-backwards": b_backwards,
        "ren-why": b_why, "card-paid-off": b_paid, "auto-transfer": b_auto, "ren-fifty-two": b_fifty, "money-was-there": b_answer, "three-bills-gone": b_gone, "four-hundred": b_400, "ren-smaller": b_smaller,
        "using-it": b_using, "its-the-job": b_job, "ren-question": b_question, "closing": b_closing}

class Short:
    def __init__(self, spec, rec, proto_end=0): self.spec, self.rec, self.proto_end = spec, rec, proto_end; self.beats = spec["beats"]; self.total = spec["frames"] / FPS
    def beat_at(self, k): return next(b for b in self.beats if b["start_frame"] <= k < b["end_frame"])
    def frame(self, k):
        b = self.beat_at(k); t = (k - b["start_frame"]) / FPS; d = (b["end_frame"] - b["start_frame"]) / FPS; T_ = k / FPS
        c = Ctx(b["id"], t, d, T_, self.rec, Image.new("RGBA", (W, H))); RP.REC["poses"] = []; RP.REC["maya"] = None; BEAT[b["id"]](c)
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
