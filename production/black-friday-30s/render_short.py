"""Portrait (1080x1920, 24 fps) renderer for the Black Friday Short under the Shorts launcher (project/pipeline/shorts_standards.py).
  project/.tools/venv/bin/python production/black-friday-30s/render_short.py --output OUT.mp4 [--stills t ...]
Ren = genuine library clips matted at native resolution (pilot_ren.RenClip / cut_out), Ren left and content right. Environments E1-E4 and props P1-P2 are the temporary generated pack, upscaled once to 1080x1920.
Every number, phone, notepad, calculator, tag, badge, caption and the end card is drawn in code. Writes layout.json (measured text bounds in final-canvas coordinates)."""
import argparse, json, math, os, subprocess, sys
from pathlib import Path
import numpy as np, soundfile as sf
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(ROOT / "videos" / "unclaimed_401k")); sys.path.insert(0, str(ROOT / "project" / "cliplib")); sys.path.insert(0, str(ROOT / "videos" / "three_bills"))
import bf_ui as UI, pilot_ren as PR, pilot_ui as U
from pilot_ren import cut_out
from ren_stage import paste_smooth
W, H, FPS = 1080, 1920, 24; ease, clamp = U.ease, U.clamp; DISCLAIMER = "Educational content only, not financial advice."
PK = ROOT / "production" / "black-friday-30s" / "assets" / "black-friday"
assert round(100 * (1 - 0.30), 2) == 70.0 and round(100 * 0.70, 2) == 70.0   # the one calculation on screen

_env, _prop = {}, {}
def env(n):
    """Pack environment upscaled once (768x1344 -> 1080x1920, Lanczos)."""
    if n not in _env: _env[n] = Image.open(PK / ({"E1": "E1_shop_street", "E2": "E2_kitchen_table", "E3": "E3_porch_parcels", "E4": "E4_living_room_morning"}[n] + ".png")).convert("RGB").resize((W, H), Image.LANCZOS).convert("RGBA")
    return _env[n].copy()
def prop(n):
    """White-background prop matted at native resolution (pilot_ren.cut_out), cropped to its pixels."""
    if n not in _prop:
        im = np.asarray(Image.open(PK / ({"P1": "P1_piggy_bank", "P2": "P2_hourglass"}[n] + ".png")).convert("RGB")); r = cut_out(im); a = r[..., 3] > 24; ys, xs = np.where(a)
        _prop[n] = Image.fromarray(r[ys.min():ys.max() + 1, xs.min():xs.max() + 1], "RGBA")
    return _prop[n]

class Recorder:
    def __init__(self): self.items = {}
    def note(self, sid, key, bbox, px, role, text, t):
        k = (sid, key); it = self.items.get(k)
        if it is None: self.items[k] = dict(text=text, bbox=[float(v) for v in bbox], font_px=float(px), role=role, start=t)
        else:
            b = it["bbox"]; it["bbox"] = [min(b[0], bbox[0]), min(b[1], bbox[1]), max(b[2], bbox[2]), max(b[3], bbox[3])]; it["start"] = min(it["start"], t); it["font_px"] = min(it["font_px"], float(px))
class Ctx:
    def __init__(self, sid, t, d, T_, rec, f): self.sid, self.t, self.d, self.T, self.rec, self.f = sid, t, d, T_, rec, f
    def put(self, img, x, y, alpha=1.0, key="", scale=1.0, rot=0.0, rec=True):
        """Paste a card (pilot_ui.Img). Text boxes are recorded only for unrotated cards (rotation <= 0.5 deg is treated as flat)."""
        if alpha <= 0.01: return
        im = img.im if scale == 1 else img.im.resize((max(1, int(img.im.width * scale)), max(1, int(img.im.height * scale))), Image.LANCZOS)
        if rot: im = im.rotate(rot, Image.BICUBIC, expand=True)
        if alpha < 1: im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
        self.f.alpha_composite(im, (int(round(x)), int(round(y))))
        if alpha > 0.5 and rec:
            for i, (a, b, c_, e, s_, px) in enumerate(img.texts):
                if rot: a, b, c_, e = (im.width - img.im.width * scale) / 2 + a * scale, (im.height - img.im.height * scale) / 2 + b * scale, (im.width - img.im.width * scale) / 2 + c_ * scale, (im.height - img.im.height * scale) / 2 + e * scale; self.rec.note(self.sid, f"{key}{s_}{i}", (x + a - 6, y + b - 6, x + c_ + 6, y + e + 6), px * scale, "text", s_, self.T)
                else: self.rec.note(self.sid, f"{key}{s_}{i}", (x + a * scale, y + b * scale, x + c_ * scale, y + e * scale), px * scale, "text", s_, self.T)
    def pop(self, img, x, y, t0, dur=0.35, key="", rot=0.0):
        """Back-eased scale-in around the card centre."""
        if self.t < t0: return
        p = U.back((self.t - t0) / dur); s = max(0.05, p); w, h = img.im.width, img.im.height; self.put(img, x + w * (1 - s) / 2, y + h * (1 - s) / 2, key=key, scale=s, rot=rot, rec=(self.t - t0) / dur > 0.98)
    def slide(self, img, x, y, t0, dur=0.4, dy=-60, key="", dx=0):
        if self.t < t0: return
        p = ease((self.t - t0) / dur); self.put(img, x + dx * (1 - p), y + dy * (1 - p), alpha=min(1.0, p * 1.6), key=key, rec=p > 0.99)
    def pill(self, text, x, y, px, role="text", alpha=1.0, fill=U.CREAM):
        f = U.font(px, 600); d0 = ImageDraw.Draw(Image.new("RGBA", (4, 4))); b = d0.textbbox((0, 0), text, font=f); w_, h_ = b[2] - b[0] + 56, b[3] - b[1] + 28
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); d.rounded_rectangle((x + 3, y + 7, x + w_ + 3, y + h_ + 7), h_ // 2, fill=(*U.NAVY, 55)); d.rounded_rectangle((x, y, x + w_, y + h_), h_ // 2, fill=(*fill, 255)); d.text((x + 28 - b[0], y + 14 - b[1]), text, font=f, fill=U.NAVY)
        if alpha < 1: lay.putalpha(lay.getchannel("A").point(lambda v: int(v * alpha)))
        self.f.alpha_composite(lay)
        if alpha > 0.5: self.rec.note(self.sid, "pill" + text, (x + 28, y + 14, x + w_ - 28, y + h_ - 14), px, role, text, self.T)

def shadow(f, cx, cy, w, h=34, a=70):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(lay).ellipse((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), fill=(*U.NAVY, a)); f.alpha_composite(lay.filter(ImageFilter.GaussianBlur(9)))
_rc = {}
def defringe(im):
    """Remove the white fringe of the white-background cut-out: the alpha is pulled in by one pixel, then every edge pixel (anything not in the 1-px-eroded solid core) takes the colour of its nearest solid-core pixel, so no light background colour survives at the silhouette."""
    a = np.asarray(im).copy(); al = a[..., 3]; core = ndimage.grey_erosion(al, size=(3, 3)) >= 250
    idx = ndimage.distance_transform_edt(~core, return_distances=False, return_indices=True); rgb = a[..., :3][idx[0], idx[1]]
    a[..., :3] = np.where(core[..., None], a[..., :3], rgb); a[..., 3] = np.clip(ndimage.gaussian_filter(ndimage.grey_erosion(al, size=(3, 3)).astype(np.float32), 0.6), 0, 255).astype(np.uint8); return Image.fromarray(a, "RGBA")
def ren(c, clip, start, x, feet, h, behind_table=0):
    """Draw the matted library clip: Ren's feet-centre at (x, feet), standing height h px. behind_table > 0: rows below that y are restored from E2 afterwards by the caller."""
    key = (c.sid, clip)
    if key not in _rc:
        _rc.clear(); rc0 = PR.RenClip(clip, start, c.d + 0.1); rc0.imgs = [defringe(im) for im in rc0.imgs]; _rc[key] = rc0
    rc = _rc[key]; i = min(max(int(c.t * FPS + 1e-6), 0), rc.n - 1); im = rc.imgs[i]; x0, y0, _, _ = rc.box; s = h / rc.h_clip
    if not behind_table: shadow(c.f, x, feet, h * 0.34, 38)
    left = x - rc.cx * s + x0 * s; top = feet - rc.feet * s + y0 * s; paste_smooth(c.f, im, left, top, im.width * s, im.height * s)
    a = np.asarray(im)[..., 3]; ys, xs = np.where(a > 128); return (left + xs.min() * s, top + ys.min() * s, left + xs.max() * s, top + ys.max() * s)
def table_front(c, e2):
    """Restore the E2 table (y >= 1223) over Ren so he stands behind it."""
    c.f.alpha_composite(e2.crop((0, 1223, W, H)), (0, 1223))
def clock(t):
    s = max(0, 3 * 3600 - 1 - int(t)); return f"{s // 3600:02d}:{s % 3600 // 60:02d}:{s % 60:02d}"

# ---- beats --------------------------------------------------------------------------------------------------------------------------
REN = dict(x=330, feet=1710, h=1300)
def b_hook(c):
    c.f.alpha_composite(env("E1")); ren(c, "ren_point_camera", 1.12, **REN)
    p = U.back(c.t / 0.5); c.put(UI.banner_p(), 80, int(-30 + 250 * clamp(p, 0, 1.15)) if c.t < 0.5 else 220, key="bn", rec=c.t > 0.55)
    if c.t > 1.9: c.pop(UI.badge_p("TEST", 260, 64, "gold"), 600, 1080, 1.9, key="ts", rot=-8)
def b_countdown(c):
    c.f.alpha_composite(env("E2")); shadow(c.f, 540, 1400, 520, 40, 80); c.put(UI.phone_countdown_p(clock(c.T)), 280, 690, key="ph")
    c.pop(UI.badge_p("ONLY 3 LEFT"), 470, 520, 1.3, key="b3", rot=-7); c.pop(UI.badge_p("RUSH!", 300, 56, "gold"), 120, 880, 2.6, key="rush", rot=8)
def _notepad(c, shown, extra=None, extra_p=0.0, cross_p=0.0, scale=1.0, x=520, y=640):
    img = UI.notepad_p(["Winter coat", "Mom's gift", "Batteries"], shown, extra=extra, extra_p=extra_p, cross_p=cross_p); shadow(c.f, x + 210 * scale, y + 620 * scale, 380 * scale, 30, 60); c.put(img, x, y, key="np", scale=scale)
def b_rule1(c):
    e2 = env("E2"); c.f.alpha_composite(e2); ren(c, "ren_clipboard_tick", 5.4, 300, 1800, 1330, behind_table=1); table_front(c, e2)
    _notepad(c, clamp((c.t - 0.5) / 1.6) * 3, x=520, y=650); c.pop(UI.tag_p("RULE 1"), 560, 520, 0.2, key="r1")
def b_not_listed(c):
    e2 = env("E2"); c.f.alpha_composite(e2); _notepad(c, 3, "Smart watch", clamp(c.t / 0.55), clamp((c.t - 0.6) / 0.6), 1.3, 270, 470)
def b_rule2(c):
    e2 = env("E2"); c.f.alpha_composite(e2); ren(c, "ren_point_down_right", 1.0, 300, 1800, 1330, behind_table=1); table_front(c, e2)
    shadow(c.f, 700, 1400, 400, 30, 60); c.put(UI.calc_p("30% off", "?", 440, 640), 480, 700, key="cl"); c.pop(UI.tag_p("RULE 2"), 560, 520, 0.15, key="r2")
def b_math(c):
    c.f.alpha_composite(env("E2")); shadow(c.f, 540, 1400, 520, 36, 80); done = c.t > 1.2
    c.put(UI.calc_p("$100 x 0.70", "= $70" if done else "", 520, 760), 280, 520, key="cl")
    st = clamp((c.t - 1.7) / 0.4); c.put(UI.pricetag_p("$100" if c.t < 2.2 else "$70", c.t < 2.2, st), 380, 1280 if False else 1300 - 0, key="pt", scale=0.75)
def b_savings(c):
    c.f.alpha_composite(env("E3")); ren(c, "ren_shrug", 1.12, **REN); c.slide(UI.sign_p("Only savings if you needed it", 420, "gold", 52), 500, 600, 0.5, key="sv", dx=60, dy=0)
def b_rule3(c):
    e2 = env("E2"); c.f.alpha_composite(e2); hg = prop("P2"); s = 760 / hg.height; im = hg.resize((int(hg.width * s), 760), Image.LANCZOS)
    rot = 180 * ease((c.t - 0.7) / 0.9); im = im.rotate(rot, Image.BICUBIC, expand=True); shadow(c.f, 260, 1470, 260, 36, 80); c.f.alpha_composite(im, (260 - im.width // 2, 1480 - im.height))
    c.put(UI.cart_phone_p("24h"), 500, 700, key="cart"); c.pop(UI.tag_p("RULE 3"), 540, 560, 0.15, key="r3")
def b_tomorrow(c):
    c.f.alpha_composite(env("E4")); ren(c, "ren_nod_yes", 1.12, **REN); c.slide(UI.sign_p("Still want it tomorrow?", 420, "cream", 52), 500, 560, 0.2, key="tm", dx=60, dy=0)
    if c.t > 1.2: c.pop(UI.badge_p("Buy it", 300, 60, "gold"), 560, 900, 1.2, key="buy")
def b_cta(c):
    c.f.alpha_composite(env("E4")); ren(c, "ren_thumbs_up", 4.9, **REN); pg = prop("P1"); s = 300 / pg.height; im = pg.resize((int(pg.width * s), 300), Image.LANCZOS); shadow(c.f, 740, 1380, 280, 30, 70); c.f.alpha_composite(im, (740 - im.width // 2, 1380 - im.height))
    c.slide(UI.sign_p("Money Leak Audit Workbook: see the description", 420, "gold", 48), 500, 560, 0.2, key="cta", dx=60, dy=0)
BEAT = {"hook": b_hook, "countdown": b_countdown, "rule-one": b_rule1, "not-listed": b_not_listed, "rule-two": b_rule2, "the-math": b_math, "savings": b_savings, "rule-three": b_rule3, "tomorrow": b_tomorrow, "cta": b_cta}

class Short:
    def __init__(self, spec, rec, proto_end=0): self.spec, self.rec, self.proto_end = spec, rec, proto_end; self.beats = spec["beats"]; self.total = spec["frames"] / FPS
    def beat_at(self, k): return next(b for b in self.beats if b["start_frame"] <= k < b["end_frame"])
    def frame(self, k):
        b = self.beat_at(k); t = (k - b["start_frame"]) / FPS; d = (b["end_frame"] - b["start_frame"]) / FPS; T_ = k / FPS
        c = Ctx(b["id"], t, d, T_, self.rec, Image.new("RGBA", (W, H))); BEAT[b["id"]](c)
        if T_ < 3.0: c.pill("Educational only. Illustrative example.", 90, 1490, 36, role="disclaimer", alpha=min(clamp(T_ / 0.4), clamp((3.0 - T_) / 0.4)))
        end = self.proto_end / FPS if self.proto_end else self.total
        if T_ >= end - 2.3: c.pill(DISCLAIMER, 100, 1490, 32, role="disclaimer", alpha=clamp((T_ - (end - 2.3)) / 0.25))
        return c.f, b

def build_audio(frames, out_wav):
    raw = HERE / "voice" / "narration.wav"
    p = subprocess.run(["ffmpeg", "-nostats", "-i", str(raw), "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr; i0 = float(p[p.rindex("I:") + 2:].split()[0])
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af", f"volume={-16 - i0:.2f}dB,alimiter=limit=0.8:level=false,aresample=48000,apad", "-t", f"{frames / FPS:.4f}", str(out_wav)], check=True)
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
