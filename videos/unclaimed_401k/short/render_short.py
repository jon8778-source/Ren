"""Portrait (1080x1920, 24 fps) renderer for the 401(k) Short, under the Shorts launcher (project/pipeline/shorts_standards.py).

  project/.tools/venv/bin/python videos/unclaimed_401k/short/render_short.py --output OUT.mp4            (the launcher calls this; honours REN_SHORTS_STAGE / REN_SHORTS_MAX_FRAMES)
  project/.tools/venv/bin/python videos/unclaimed_401k/short/render_short.py --output OUT.mp4 --stills 1 5 12

Reuses the episode's approved pieces: Maya pose cut-outs (render_pilot.track / draw_pose, sub-pixel paste_smooth), library Ren clips (pilot_ren.RenClip,
placed with the ren_stage OFFICE_SAGE scale standard), code-drawn cards. Beat timing comes from short_spec.json; the narration is cut from the approved
audio (short_audio.py). Writes layout.json (measured text bounds in final-canvas coordinates).
"""
import argparse, json, math, os, subprocess, sys
from pathlib import Path
import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent)); sys.path.insert(0, str(ROOT / "project" / "cliplib"))
import render_pilot as R, pilot_assets as A, pilot_ren as PR, pilot_ui as U, short_ui as S
from ren_stage import paste_smooth, contact_shadow, height_px

W, H, FPS = 1080, 1920, 24
ease, clamp = U.ease, U.clamp
DISCLAIMER = "Educational content only, not financial advice."

class Cam:
    """Portrait camera over a 1920x1080 plate space: canvas = (plate - (cx, cy)) * z + (540, 960). Full height needs z >= 1920/1080."""
    def __init__(self, z, cx, cy=540): self.z, self.cx, self.cy = z, cx, cy; self.k = z
    def pt(self, x, y): return ((x - self.cx) * self.z + 540, (y - self.cy) * self.z + 960)
_big = {}
def plate(name, cam, blur=0, dark=0.0):
    if name not in _big: _big[name] = Image.open(A.ART / "plates" / f"{name}.png").convert("RGB")
    z = cam.z; a = 2.0 / z
    f = _big[name].transform((W, H), Image.AFFINE, (a, 0, 2 * (cam.cx - 540 / z), 0, a, 2 * (cam.cy - 960 / z)), Image.BICUBIC).convert("RGBA")
    if blur: f = f.filter(ImageFilter.GaussianBlur(blur))
    if dark: f.alpha_composite(Image.new("RGBA", f.size, (*U.NAVY, int(255 * dark))))
    return f

class Recorder:
    """Measured text bounds in final-canvas coordinates, per scene (union over frames, so motion extrema are covered)."""
    def __init__(self): self.items = {}
    def note(self, sid, key, bbox, px, role, text, t):
        k = (sid, key); it = self.items.get(k)
        if it is None: self.items[k] = dict(text=text, bbox=[float(v) for v in bbox], font_px=float(px), role=role, start=t)
        else:
            b = it["bbox"]; it["bbox"] = [min(b[0], bbox[0]), min(b[1], bbox[1]), max(b[2], bbox[2]), max(b[3], bbox[3])]; it["start"] = min(it["start"], t); it["font_px"] = min(it["font_px"], float(px))

class Ctx:
    def __init__(self, sid, t, d, T, rec, f): self.sid, self.t, self.d, self.T, self.rec, self.f = sid, t, d, T, rec, f
    def put(self, img, x, y, alpha=1.0, key=""):
        """Alpha-composite a card image at (x, y) and record its text boxes (card-relative -> canvas)."""
        if alpha <= 0.01: return
        im = img.im
        if alpha < 1: im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
        self.f.alpha_composite(im, (int(round(x)), int(round(y))))
        if alpha > 0.5:
            for i, (a, b, c, e, s_, px) in enumerate(img.texts): self.rec.note(self.sid, f"{key}{s_}{i}", (x + a, y + b, x + c, y + e), px, "text", s_, self.T)
    def slide(self, img, x, y, t0, dur=0.4, frm=50, key=""):
        if self.t < t0: return
        p = ease((self.t - t0) / dur); self.put(img, x + frm * (1 - p), y, alpha=min(1.0, p * 1.6), key=key)
    def pill(self, text, x, y, px, role="text", alpha=1.0, fill=U.CREAM):
        f = U.font(px, 600); d0 = ImageDraw.Draw(Image.new("RGBA", (4, 4))); b = d0.textbbox((0, 0), text, font=f); w_, h_ = b[2] - b[0] + 56, b[3] - b[1] + 28
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        d.rounded_rectangle((x + 3, y + 7, x + w_ + 3, y + h_ + 7), h_ // 2, fill=(*U.NAVY, 55)); d.rounded_rectangle((x, y, x + w_, y + h_), h_ // 2, fill=(*fill, 255))
        d.text((x + 28 - b[0], y + 14 - b[1]), text, font=f, fill=U.NAVY)
        if alpha < 1: lay.putalpha(lay.getchannel("A").point(lambda v: int(v * alpha)))
        self.f.alpha_composite(lay)
        if alpha > 0.5: self.rec.note(self.sid, "pill" + text, (x + 28, y + 14, x + w_ - 28, y + h_ - 14), px, role, text, self.T)

# ---- Maya (living room, armchair) ----------------------------------------------------------------------------------------------
HCAM = Cam(1.9, 620, 560)
ARM = R.ARM
def maya(c, tl, **kw):
    X, Y = HCAM.pt(*ARM); R.REC["poses"] = []; R.track(c.f, tl, c.t, X, Y, S=kw.get("S", 1.08) * HCAM.z)

# ---- Ren (sage office) ----------------------------------------------------------------------------------------------------------
SCAM = Cam(1.85, 330, 540)
class RCam:
    """ren_stage camera in 1672x941 plate space for the sage plate shown through SCAM."""
    PK = 1920 / 1672.0
    k = SCAM.z * PK
    def pt(self, x, y): return SCAM.pt(x * self.PK, y * self.PK)
_rc = {}
def ren(c, clip, start, mirror=False, feet=(215, 735)):
    key = (c.sid, clip)
    if key not in _rc:
        _rc.clear(); d = (c.d if c.d else 3.0); _rc[key] = PR.RenClip(clip, start, d + 0.1, mirror=mirror)
    rc = _rc[key]; i = min(max(int(c.t * FPS + 1e-6), 0), rc.n - 1); im = rc.imgs[i]; x0, y0, _, _ = rc.box
    cam = RCam(); X, Y = cam.pt(*feet); s = height_px("OFFICE_SAGE", feet[1]) * cam.k / rc.h_clip
    contact_shadow(c.f, cam, feet[0], feet[1], 150)
    left = X - rc.cx * s + x0 * s; top = Y - rc.feet * s + y0 * s
    paste_smooth(c.f, im, left, top, im.width * s, im.height * s)
    a = np.asarray(im)[..., 3]; ys, xs = np.where(a > 128)
    return (left + xs.min() * s, top + ys.min() * s, left + xs.max() * s, top + ys.max() * s), i

# ---- hand + phone close-up ------------------------------------------------------------------------------------------------------
PH_SCALE = 3.6
PH_QUAD = {"props_01": [(27, 21), (126, 16), (152, 241), (63, 249)], "props_02": [(29, 22), (128, 17), (151, 243), (64, 251)]}
_hu = {}
def hand_ui(key, state):
    k = (key, state)
    if k in _hu: return _hu[k]
    im = A.pose(key); a = np.array(im); rgb = a[..., :3].astype(int)
    light = (a[..., 3] > 200) & (rgb.min(2) > 238); lab, n = ndimage.label(light); sz = ndimage.sum(light, lab, range(1, n + 1)); m = lab == (1 + int(np.argmax(sz)))
    sw, sh = int(im.width * PH_SCALE), int(im.height * PH_SCALE); base = im.resize((sw, sh), Image.LANCZOS)
    mk = Image.fromarray((m * 255).astype(np.uint8)).resize((sw, sh), Image.BILINEAR).point(lambda v: 255 if v > 110 else 0).filter(ImageFilter.MaxFilter(3))
    q0 = [(x * PH_SCALE, y * PH_SCALE) for x, y in PH_QUAD[key]]; cx_ = sum(p[0] for p in q0) / 4; cy_ = sum(p[1] for p in q0) / 4
    quad = [(cx_ + (x - cx_) * 1.07, cy_ + (y - cy_) * 1.05) for x, y in q0]        # slightly oversize so the UI covers the whole screen opening
    ui, L = S.phone_screen(state); wp = R.warp(ui, quad, (sw, sh)); out = base.copy(); out.paste(wp, (0, 0), mk)
    qw = (math.dist(quad[0], quad[1]) + math.dist(quad[3], quad[2])) / 2; fac = qw / ui.width
    texts = []
    for (bx, s_, px) in L:
        pts = [R.apply_h(quad, ui.width, ui.height, u, v) for u, v in ((bx[0], bx[1]), (bx[2], bx[1]), (bx[2], bx[3]), (bx[0], bx[3]))]
        texts.append((min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts), s_, px * fac))
    _hu[k] = (out, texts); return _hu[k]

# ---- beats ----------------------------------------------------------------------------------------------------------------------------
def b_armchair_phone(c):
    maya(c, [(0, "maya_nochair_01"), (0.9, "maya_nochair_02")])
def b_phone_cancel(c):
    seq = [(0, ("props_01", 0)), (1.15, ("props_02", 1)), (1.5, ("props_01", 2))]
    idx = max(i for i, (t0, _) in enumerate(seq) if c.t >= t0 - 1e-9)
    def draw(k, alpha=1.0):
        im, texts = hand_ui(*seq[k][1]); x, y = 30, 1000 - im.height / 2 + 120
        if alpha < 1: im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
        c.f.alpha_composite(im, (int(x), int(y)))
        if alpha > 0.5:
            for (a, b, cc, e, s_, px) in texts: c.rec.note(c.sid, f"ph{s_}", (x + a, y + b, x + cc, y + e), px, "text", s_, c.T)
    if idx > 0 and (c.t - seq[idx][0]) / R.BLEND < 1: draw(idx - 1); draw(idx, max(0.0, (c.t - seq[idx][0]) / R.BLEND))
    else: draw(idx)
def b_armchair_email(c):
    maya(c, [(0, "maya_nochair_03"), (1.4, "maya_nochair_02")]); c.slide(S.email_card(), 300, 190, 0.5, key="em")
def b_armchair_laptop(c):
    maya(c, [(0, "seat_stool_03"), (0.8, "seat_stool_04")])
def b_armchair_alert(c):
    maya(c, [(0, "seat_stool_05"), (1.5, "seat_receipt_laptop_04")])
    if c.t > 0.7:
        p = U.back((c.t - 0.7) / 0.4); img = S.alert_card(); s = max(0.05, p); im = img.im.resize((max(1, int(img.im.width * s)), max(1, int(img.im.height * s))), Image.LANCZOS)
        c.f.alpha_composite(im, (int(240 + img.im.width / 2 - im.width / 2), int(300 + img.im.height / 2 - im.height / 2)))
        if p > 0.97:
            for (a, b, cc, e, s_, px) in img.texts: c.rec.note(c.sid, "al" + s_, (240 + a, 300 + b, 240 + cc, 300 + e), px, "text", s_, c.T)
def b_portal_numbers(c):
    f = plate("H1_4k", HCAM, blur=18, dark=0.5); c.f.paste(f, (0, 0))
    if c.t < 1.9: img = S.portal_card("$100 / month", U.back((c.t - 0.15) / 0.45))
    elif c.t < 2.15: img = S.portal_card("$100 / month", 1 - ease((c.t - 1.9) / 0.25))
    else: img = S.portal_card("$1,200 / year", U.back((c.t - 2.15) / 0.45))
    c.put(img, 126, 520, key="pt")
def _ren_beat(c, clip, start, panel, mirror=False, px=520, py=420, delay=0.2):
    bx, i = ren(c, clip, start, mirror); c.slide(panel(c), px, py, delay, key="rc")
def b_ren_employer_flow(c): _ren_beat(c, "ren_point_right", 1.3, lambda c: S.flow_card(clamp((c.t - 0.9) / 1.6)), py=330)
def b_armchair_field(c):
    maya(c, [(0, "seat_receipt_laptop_04"), (1.3, "seat_receipt_laptop_05")]); c.slide(S.field_card(clamp(1 - abs(c.t - 1.4) / 0.5) if c.t > 0.9 else 0), 240, 190, 0.2, key="fd")
def b_armchair_two(c):
    maya(c, [(0, "seat_receipt_laptop_06"), (0.6, "seat_stool_06")]); c.slide(S.side_card("Maya puts in", "2%", w=380), 480, 190, 0.3, key="tp")
def b_ren_match(c):
    ren(c, "ren_shrug", 1.3)
    c.slide(S.match_card(), 520, 300, 0.2, key="m1")        # card holds Maya then Employer: drawn together, Employer lights later
def b_ren_half(c): _ren_beat(c, "ren_present_palm_left", 1.2, lambda c: S.half_card(0), mirror=True, py=300)
def b_missing_half(c):
    c.f.paste(plate("H1_4k", HCAM, blur=18, dark=0.5), (0, 0)); c.put(S.big_card("Missing half", "$1,200 / year", tone="gold", vpx=96), 126, 700, key="mh")
def b_ten_years(c):
    c.f.paste(plate("H1_4k", HCAM, blur=18, dark=0.5), (0, 0)); c.put(S.years_card(int(clamp(c.t / 1.6) * 10 + 1e-6)), 126, 620, key="ty")
def b_twelve(c):
    c.f.paste(plate("H1_4k", HCAM, blur=18, dark=0.5), (0, 0)); c.put(S.big_card("10 more years", "$12,000", tone="sage", vpx=120), 126, 700, key="tw")
def b_not_included(c):
    c.f.paste(plate("H1_4k", HCAM, blur=18, dark=0.5), (0, 0)); hi = min(2, int(c.t / max(c.d, 1e-6) * 3))
    c.put(S.chips(["Investment growth", "Changes in salary", "Changes to the plan"], hi, title="Not included"), 126, 650, key="ni")
def b_ren_intro(c):
    _ren_beat(c, "ren_wave_bye", 1.3, lambda c: S.side_card("The next useful money move", "isn't earning more", vpx=48, w=380) if c.t > 2.2 else S.chips(["Ren"], 0, w=380), py=420, delay=0.15)
def b_ren_table(c): _ren_beat(c, "ren_open_arms", 1.2, lambda c: S.side_card("What's already on the table", "the match", tone="gold", vpx=60), py=420)
def b_ren_cta(c): _ren_beat(c, "ren_point_camera", 1.2, lambda c: S.cta_card(), py=360)
def b_ren_disclaimer(c):
    ren(c, "ren_nod_yes", 1.2)
    lines = ["Educational content only,", "not financial advice."]; px = 38; y = 1130
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); wmax = max(d.textlength(s_, font=U.font(px, 700)) for s_ in lines)
    x0 = 900 - int(wmax) - 60; d.rounded_rectangle((x0, y - 20, 900, y + 170), 36, fill=(*U.CREAM, 255), outline=(*U.NAVY, 255), width=4)
    for i, s_ in enumerate(lines): d.text((x0 + 30, y + 14 + 70 * i), s_, font=U.font(px, 700), fill=U.NAVY)
    c.f.alpha_composite(lay)
    c.rec.note(c.sid, "disc", (x0 + 30, y + 14, 870, y + 150), px, "disclaimer", DISCLAIMER, c.T)

BEAT = {"armchair-phone": b_armchair_phone, "phone-cancel": b_phone_cancel, "armchair-email": b_armchair_email, "armchair-laptop": b_armchair_laptop, "armchair-alert": b_armchair_alert,
        "portal-numbers": b_portal_numbers, "ren-employer-flow": b_ren_employer_flow, "armchair-field": b_armchair_field, "armchair-two-percent": b_armchair_two, "ren-match-cards": b_ren_match,
        "ren-half-meter": b_ren_half, "missing-half": b_missing_half, "ten-years": b_ten_years, "twelve-thousand": b_twelve, "not-included": b_not_included, "ren-intro": b_ren_intro,
        "ren-table": b_ren_table, "ren-cta": b_ren_cta, "ren-disclaimer": b_ren_disclaimer}
HOME = {"armchair-phone", "armchair-email", "armchair-laptop", "armchair-alert", "armchair-field", "armchair-two-percent"}

class Short:
    def __init__(self, spec, rec, proto_end=0): self.spec, self.rec, self.proto_end = spec, rec, proto_end; self.beats = spec["beats"]
    def beat_at(self, k): return next(b for b in self.beats if b["start_frame"] <= k < b["end_frame"])
    def frame(self, k):
        b = self.beat_at(k); t = (k - b["start_frame"]) / FPS; d = (b["end_frame"] - b["start_frame"]) / FPS; T = k / FPS
        if b["id"] in HOME: f = plate("H1_4k", HCAM)
        elif b["id"].startswith("ren-"): f = plate("SAGE_4k", SCAM)
        elif b["id"] == "phone-cancel": f = plate("H1_4k", HCAM, blur=18, dark=0.5)
        else: f = Image.new("RGBA", (W, H))
        c = Ctx(b["id"], t, d, T, self.rec, f); R.REC["poses"] = []; R.REC["maya"] = None; R.REC["tip"] = None
        BEAT[b["id"]](c)
        if T < 3.0: c.pill("Educational only. Illustrative example.", 90, 190, 36, role="disclaimer", alpha=min(clamp(T / 0.4), clamp((3.0 - T) / 0.4)))
        if self.proto_end and T >= self.proto_end / FPS - 2.3:        # the prototype stops mid-story: keep the exact end disclaimer visible for its last 2+ s (the full Short ends on its own closing beat)
            c.pill(DISCLAIMER, 100, 1440, 32, role="disclaimer", alpha=clamp((T - (self.proto_end / FPS - 2.3)) / 0.25))
        return f, b

def build_audio(frames, out_wav):
    """Gain the cut narration to -16 LUFS (gain + limiter only); it is cut to the video length, nothing is padded or stretched."""
    a, sr = sf.read(HERE / "short_audio_raw.wav", dtype="float32"); raw = out_wav.with_suffix(".raw.wav"); sf.write(raw, a, sr)
    p = subprocess.run(["ffmpeg", "-nostats", "-i", str(raw), "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
    i0 = float(p[p.rindex("I:") + 2:].split()[0])
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af", f"volume={-16 - i0:.2f}dB,alimiter=limit=0.8:level=false,aresample=48000", "-t", f"{frames / FPS:.4f}", str(out_wav)], check=True); raw.unlink()

def merge_layout(parts, spec, frames, path):
    scenes = {b["id"]: [] for b in spec["beats"] if b["start_frame"] < frames}; merged = {}
    for p in parts:
        for it in json.loads(Path(p).read_text()):
            k = (it["scene"], it["key"])
            if k not in merged: merged[k] = it
            else:
                m, b = merged[k], it["bbox"]; m["bbox"] = [min(m["bbox"][0], b[0]), min(m["bbox"][1], b[1]), max(m["bbox"][2], b[2]), max(m["bbox"][3], b[3])]
                m["start"] = min(m["start"], it["start"]); m["font_px"] = min(m["font_px"], it["font_px"])
    for (sid, key), it in merged.items():
        scenes[sid].append(dict(text=it["text"], bbox=[round(v, 1) for v in it["bbox"]], font_px=round(it["font_px"], 1), role=it["role"], start=it["start"], end=0.0))
    Path(path).write_text(json.dumps({"scenes": scenes}, indent=2) + "\n")

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--output", type=Path, required=True); ap.add_argument("--jobs", type=int, default=4); ap.add_argument("--range", type=int, nargs=2); ap.add_argument("--seg", type=int, default=0)
    ap.add_argument("--stills", type=float, nargs="*"); args = ap.parse_args()
    spec = json.loads((HERE / "short_spec.json").read_text()); stage = os.environ.get("REN_SHORTS_STAGE", "prototype")
    frames = min(int(os.environ.get("REN_SHORTS_MAX_FRAMES", 360 if stage == "prototype" else spec["frames"])), spec["frames"])
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
        lst = out.parent / "segments.txt"; lst.write_text("".join(f"file '{out.parent / f'{out.stem}_seg{k}.mp4'}'\n" for k in range(jobs)))
        silent = out.with_suffix(".video.mp4"); subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(silent)], check=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(silent), "-i", str(out.with_suffix(".audio.wav")), "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                        "-t", f"{frames / FPS:.4f}", "-movflags", "+faststart", str(out)], check=True)
        merge_layout([out.parent / f"{out.stem}_seg{k}.layout.json" for k in range(jobs)], spec, frames, layout_path)
        lay = json.loads(layout_path.read_text())
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
    enc.stdin.close(); enc.wait()
    items = [dict(scene=sid, key=key, **it, end=0.0) for (sid, key), it in rec.items.items()]
    (out.parent / f"{out.stem}_seg{args.seg}.layout.json").write_text(json.dumps(items))

if __name__ == "__main__":
    main()
