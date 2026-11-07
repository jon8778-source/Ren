"""Portrait renderer adapter for the 1-minute Short (1080x1920, 24 fps, H.264/AAC), run under project/pipeline/shorts_standards.py.

  python project/pipeline/shorts_standards.py run --manifest videos/free_money/short/production.json --stage prototype \\
      --output videos/free_money/short/prototype.mp4 -- project/.tools/venv/bin/python videos/free_money/short/fm_short.py --output videos/free_money/short/prototype.mp4

Honours REN_SHORTS_STAGE (prototype | full) and REN_SHORTS_MAX_FRAMES, renders only that interval, and writes layout.json: the
measured final-canvas bounds of every piece of text actually drawn (from the font, not guessed).

Native portrait composition: environment art fills the canvas; text sits in the safe rectangle x 72-900, y 180-1560; text at least
42 px (disclaimer 30 px). Ren and Dev are placed with project/cliplib/ren_stage.py (scale from plate perspective, contact shadow,
sub-pixel motion). The narration is cut from the approved long-form audio (short_audio.py); no music.
"""
import argparse, json, math, os, subprocess, sys
from pathlib import Path
import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "project" / "cliplib"))
import ren_stage as rs  # noqa: E402

W, H, FPS = 1080, 1920, 24
SAFE = (72, 180, 900, 1560)
NAVY, SAGE, CREAM, GREEN, MUTED, RED, GOLD = (19, 35, 63), (127, 160, 138), (251, 246, 234), (30, 158, 90), (122, 132, 150), (196, 70, 60), (255, 196, 40)
DISCLAIMER = "Educational content only, not financial advice."
FONTS = ROOT / "project" / "remotion" / "public" / "fonts"
LIB = ROOT / "library"
MATTED = HERE.parent / "matted"


def font(px, weight=700):
    return ImageFont.truetype(str(FONTS / f"fredoka-latin-{weight}-normal.woff2"), int(px))


def ease(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def lerp(a, b, x):
    return a + (b - a) * x


def fade(t, start, dur=0.3):
    return ease((t - start) / dur)


def layer():
    return Image.new("RGBA", (W, H), (0, 0, 0, 0))


# ------------------------------------------------------------------ assets
def trim(im):
    a = np.array(im)[..., 3]
    ys, xs = np.where(a > 20)
    return im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))


class Assets:
    def __init__(self):
        sup = LIB / "supporting_assets"
        self.plate = {k: Image.open(sup / "backgrounds" / n).convert("RGB") for k, n in
                      (("PORCH", "Porch_background_16x9.png"), ("OFFICE", "Office_background_16x9.png"), ("LOT", "Office_parking_lot_car_16x9.png"))}
        dev = Image.open(sup / "characters" / "Dev_pay_stub.png").convert("RGBA")
        self.dev = trim(dev)
        pad = 1600
        self.dev_pad = Image.new("RGBA", (dev.width + 2 * pad, dev.height + 2 * pad), (0, 0, 0, 0))
        self.dev_pad.paste(dev, (pad, pad))
        self.pad = pad
        self.ren = {k: trim(Image.open(MATTED / f"{n}.png").convert("RGBA")) for k, n in
                    (("R1", "Ren_1_neutral"), ("R2", "Ren_2_hand_on_chest_talking"), ("R3", "Ren_3_thinking_bust"), ("FS", "Ren_full_body_standing"), ("FP", "Ren_full_body_presenting"))}
        self.folder = Image.open(sup / "props" / "HR_folder_page6_prop.png").convert("RGBA")


class PCam:
    """A 9:16 window onto a landscape plate: centre (cx, cy) in plate pixels, zoom z (1 = the full plate height)."""
    def __init__(self, img, cx, cy, z):
        iw, ih = img.size
        self.img, self.ch = img, ih / z
        self.cw = self.ch * 9 / 16
        self.x0 = min(max(cx - self.cw / 2, 0), iw - self.cw)
        self.y0 = min(max(cy - self.ch / 2, 0), ih - self.ch)
        self.k = H / self.ch

    def render(self):
        return self.img.resize((W, H), Image.LANCZOS, box=(self.x0, self.y0, self.x0 + self.cw, self.y0 + self.ch)).convert("RGBA")

    def pt(self, x, y):
        return ((x - self.x0) * self.k, (y - self.y0) * self.k)


def blurred(cam, amount=16):
    b = cam.render().convert("RGB").resize((W // 6, H // 6), Image.LANCZOS).filter(ImageFilter.GaussianBlur(amount / 6)).resize((W, H), Image.BICUBIC)
    return Image.blend(b, Image.new("RGB", (W, H), CREAM), 0.25).convert("RGBA")


def push(t, d, a, b):
    return lerp(a, b, min(max(t / d, 0), 1))


# ------------------------------------------------------------------ measured text
class Recorder:
    """Records the actual final-canvas bounds of every text drawn, per scene (union over frames, so motion extrema are covered)."""
    def __init__(self):
        self.items = {}

    def note(self, sid, key, bbox, px, role, text, t):
        k = (sid, key)
        it = self.items.get(k)
        if it is None:
            self.items[k] = dict(text=text, bbox=[float(v) for v in bbox], font_px=float(px), role=role, start=t)
        else:
            b = it["bbox"]
            it["bbox"] = [min(b[0], bbox[0]), min(b[1], bbox[1]), max(b[2], bbox[2]), max(b[3], bbox[3])]
            it["start"] = min(it["start"], t)
            it["font_px"] = min(it["font_px"], float(px))


class Ctx:
    """What a scene builder gets: local time t, duration d, scene id, the recorder and the absolute time of the frame."""
    def __init__(self, sid, t, d, T, rec):
        self.sid, self.t, self.d, self.T, self.rec = sid, t, d, T, rec

    def text(self, f, key, xy, text, px, weight=700, fill=NAVY, anchor="la", role="text", alpha=1.0, eff_px=None):
        """Draw text onto frame `f` and record its measured bounds. `eff_px` = on-screen size when the text is perspective-warped."""
        if alpha <= 0.001:
            return None
        lay = layer()
        d = ImageDraw.Draw(lay)
        fnt = font(px, weight)
        d.text(xy, text, font=fnt, fill=(*fill, 255), anchor=anchor)
        box = d.textbbox(xy, text, font=fnt, anchor=anchor)
        if alpha < 1:
            lay.putalpha(lay.getchannel("A").point(lambda v: int(v * alpha)))
        f.alpha_composite(lay)
        self.rec.note(self.sid, key, box, eff_px or px, role, text, self.T)
        return box

    def note_box(self, key, box, px, text, role="text"):
        self.rec.note(self.sid, key, box, px, role, text, self.T)


def card(f, box, alpha=1.0, r=36):
    x0, y0, x1, y1 = box
    lay = layer()
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle((x0 + 6, y0 + 12, x1 + 6, y1 + 12), r, fill=(19, 35, 63, 55))
    d.rounded_rectangle((x0, y0, x1, y1), r, fill=(*CREAM, 255), outline=(*SAGE, 255), width=6)
    if alpha < 1:
        lay.putalpha(lay.getchannel("A").point(lambda v: int(v * alpha)))
    f.alpha_composite(lay)


def dashed(d, box, col, width=5, dash=18, gap=11):
    x0, y0, x1, y1 = box
    x = x0
    while x < x1:
        d.line((x, y0, min(x + dash, x1), y0), fill=col, width=width); d.line((x, y1, min(x + dash, x1), y1), fill=col, width=width); x += dash + gap
    y = y0
    while y < y1:
        d.line((x0, y, x0, min(y + dash, y1)), fill=col, width=width); d.line((x1, y, x1, min(y + dash, y1)), fill=col, width=width); y += dash + gap


def warp_to(src, quad, size=(W, H)):
    """Warp an RGBA image onto the 4-point quad (TL, TR, BR, BL) in canvas coordinates."""
    w, h = src.size
    s = [(0, 0), (w, 0), (w, h), (0, h)]
    A = []
    for (x, y), (u, v) in zip(quad, s):
        A += [[x, y, 1, 0, 0, 0, -u * x, -u * y], [0, 0, 0, x, y, 1, -v * x, -v * y]]
    coeff = np.linalg.solve(np.array(A, float), np.array([c for p in s for c in p], float))
    return src.transform(size, Image.PERSPECTIVE, tuple(coeff), Image.BICUBIC)


STUB = [(710, 254), (823, 271), (796, 412), (666, 401)]       # pay stub corners in Dev_pay_stub.png (TL, TR, BR, BL)


def stub_point(u, v):
    tl, tr, br, bl = STUB
    top = (lerp(tl[0], tr[0], u), lerp(tl[1], tr[1], u))
    bot = (lerp(bl[0], br[0], u), lerp(bl[1], br[1], u))
    return (lerp(top[0], bot[0], v), lerp(top[1], bot[1], v))


def dev_view(A, anchor, dst, scale):
    """Dev's image with plate point `anchor` shown at canvas point `dst` at `scale` (a full-canvas RGBA layer)."""
    ax, ay = anchor[0] + A.pad, anchor[1] + A.pad
    box = (ax - dst[0] / scale, ay - dst[1] / scale, ax + (W - dst[0]) / scale, ay + (H - dst[1]) / scale)
    return A.dev_pad.resize((W, H), Image.LANCZOS, box=box)


# ------------------------------------------------------------------ the scenes
class Short:
    def __init__(self, spec, rec):
        self.A = Assets()
        self.spec, self.rec = spec, rec
        self.beats = spec["beats"]
        self.total = spec["frames"]
        self.build = {b["id"]: getattr(self, "s_" + b["id"].replace("-", "_"), None) for b in self.beats}
        self.proto = os.environ.get("REN_SHORTS_STAGE", "prototype") == "prototype"      # the prototype shows the exact end disclaimer in its last 2 s

    # ---- helpers
    def disclaimer(self, c, f, start, end, sid_end):
        """The exact educational disclaimer (32 px) on its own light pill, inside the safe area, shown between absolute start and end."""
        if start <= c.T < end:
            fnt = font(32, 600)
            tw = ImageDraw.Draw(layer()).textlength(DISCLAIMER, font=fnt)
            lay = layer()
            ImageDraw.Draw(lay).rounded_rectangle((72, 1488, 72 + tw + 48, 1548), 30, fill=(*CREAM, 235))
            f.alpha_composite(lay)
            c.text(f, "disclaimer", (96, 1518), DISCLAIMER, 32, 600, NAVY, "lm", role="disclaimer")

    def glow_line(self, c, f, anchor, dst, scale, text, pulse, glow, key):
        quad = []
        for u, v in ((0.04, 0.48), (0.97, 0.48), (0.97, 0.64), (0.04, 0.64)):
            px, py = stub_point(u, v)
            quad.append(((px - anchor[0]) * scale + dst[0], (py - anchor[1]) * scale + dst[1]))
        sw, sh = 330, 76                      # same aspect as the stub's line, so the text is not distorted by the warp
        s = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
        d = ImageDraw.Draw(s)
        d.rounded_rectangle((0, 0, sw - 1, sh - 1), 16, fill=(255, 236, 150, 245), outline=(*GREEN, 255), width=5)
        fnt = font(56, 700)
        b = d.textbbox((0, 0), text, font=fnt)
        d.text(((sw - (b[2] - b[0])) / 2 - b[0], (sh - (b[3] - b[1])) / 2 - b[1]), text, font=fnt, fill=(*NAVY, 255))
        cx, cy = sum(p[0] for p in quad) / 4, sum(p[1] for p in quad) / 4
        quad = [(cx + (x - cx) * pulse, cy + (y - cy) * pulse) for x, y in quad]
        if glow > 0:
            g = layer()
            ImageDraw.Draw(g).polygon(quad, fill=(255, 226, 90, int(190 * glow)))
            f.alpha_composite(g.filter(ImageFilter.GaussianBlur(26)))
        f.alpha_composite(warp_to(s, quad))
        qw = max(p[0] for p in quad) - min(p[0] for p in quad)
        c.note_box(key, (min(p[0] for p in quad), min(p[1] for p in quad), max(p[0] for p in quad), max(p[1] for p in quad)), 56 * qw / sw, text)

    def bust(self, c, f, key, h=1180, cx=540, push_=0.0):
        im = self.A.ren[key]
        h = h * (1 + 0.05 * push_)
        w = im.width * h / im.height
        rs.paste_smooth(f, im, cx - w / 2, H + 6 - h, w, h)
        return (cx - w / 2, H + 6 - h, cx + w / 2, H + 6)

    def stub_bg(self, A, c, z0, z1, dst, sc0, sc1):
        cam = PCam(A.plate["PORCH"], 1000, 470, 1.0)
        f = blurred(cam, 20)
        sc = push(c.t, c.d, sc0, sc1)
        f.alpha_composite(dev_view(A, (745, 335), dst, sc))
        return f, sc

    # ---- B1: stub close-up with the example plan
    def s_stub_hook(self, c):
        A = self.A
        dst = (560, push(c.t, c.d, 520, 470))
        f, sc = self.stub_bg(A, c, 3.0, 3.2, dst, 3.0, 3.2)
        self.glow_line(c, f, (745, 335), dst, sc, "Match: 2%", 1.0, 0.8, "stub-line")
        ca = fade(c.t, 0.55, 0.3)
        x0, y0, x1, y1 = 72, 980, 900, 1440
        card(f, (x0, y0, x1, y1), ca)
        if ca > 0:
            c.text(f, "panel-title", (x0 + 36, y0 + 28), "One employer's plan (example)", 42, 600, MUTED, "la", alpha=ca)
            tx0, tw = x0 + 300, 480
            grow = ease((c.t - 0.9) / 0.6)
            for label, col, y in (("You", NAVY, y0 + 150), ("Employer", SAGE, y0 + 285)):
                c.text(f, "lab-" + label, (x0 + 36, y + 31), label, 46, 700, NAVY, "lm", alpha=ca)
                lay = layer()
                d = ImageDraw.Draw(lay)
                d.rounded_rectangle((tx0, y, tx0 + tw, y + 62), 16, fill=(231, 236, 232, 255))
                if grow > 0.02:
                    d.rounded_rectangle((tx0, y, tx0 + tw * 0.5 * grow, y + 62), 16, fill=(*col, 255))
                lay.putalpha(lay.getchannel("A").point(lambda v: int(v * ca)))
                f.alpha_composite(lay)
                if grow > 0.9:
                    c.text(f, "pct-" + label, (tx0 + tw * 0.25, y + 31), "2%", 44, 700, (255, 255, 255), "mm")
            ga = fade(c.t, 2.0, 0.4)
            if ga > 0:
                lay = layer()
                d = ImageDraw.Draw(lay)
                dashed(d, (tx0 + tw * 0.5 + 6, y0 + 285, tx0 + tw, y0 + 347), (*GREEN, 255))
                lay.putalpha(lay.getchannel("A").point(lambda v: int(v * ga)))
                f.alpha_composite(lay)
                c.text(f, "limit", (tx0 + tw * 0.75 + 3, y0 + 316), "up to 4%", 42, 700, GREEN, "mm", alpha=ga)
        self.disclaimer(c, f, 0.3, 2.6, None)
        return f

    # ---- B2: the question on the porch
    def s_porch_question(self, c):
        A = self.A
        cam = PCam(A.plate["PORCH"], push(c.t, c.d, 915, 930), 500, push(c.t, c.d, 1.0, 1.03))
        f = cam.render()
        rs.stand(f, cam, "PORCH", A.dev, 1045, 672, None, is_ren=False)      # standing back at the door: heads fall below the text band
        rs.stand(f, cam, "PORCH", A.ren["FS"], 790, 672, None)
        a = fade(c.T, 4.0, 0.3)
        if a > 0:
            card(f, (72, 196, 900, 316), a)
            c.text(f, "quote", (486, 256), "“Who's keeping the difference?”", 50, 700, NAVY, "mm", alpha=a)
        return f

    # ---- B3: the line, sinking
    def s_stub_line(self, c):
        A = self.A
        dst = (560, push(c.t, c.d, 560, 600))
        f, sc = self.stub_bg(A, c, 3.4, 3.6, dst, 3.4, 3.6)
        drop = ease((c.T - 7.2) / 0.5)                       # "my stomach dropped": the line darkens and sinks
        pulse = 1.0 + 0.07 * math.sin(math.pi * min(1, max(0, (c.t - 0.2) / 0.5))) - 0.05 * drop
        self.glow_line(c, f, (745, 335), dst, sc, "Match: 2%", pulse, 1.0 * (1 - 0.8 * drop), "stub-line")
        return f

    # ---- B4: three years
    def s_three_years(self, c):
        A = self.A
        cam = PCam(A.plate["OFFICE"], 900, 470, 1.0)
        f = blurred(cam, 10)
        for k in range(3):
            x0 = 72 + k * 284
            a = fade(c.t, 0.05 + 0.3 * k, 0.25)
            if a <= 0:
                continue
            lay = layer()
            d = ImageDraw.Draw(lay)
            d.rounded_rectangle((x0 + 6, 236, x0 + 266, 556), 22, fill=(19, 35, 63, 55))
            d.rounded_rectangle((x0, 224, x0 + 260, 544), 22, fill=(*CREAM, 255), outline=(*NAVY, 255), width=5)
            d.rectangle((x0 + 5, 229, x0 + 255, 268), fill=(*NAVY, 255))
            for j, yy in enumerate((300, 340)):
                d.rounded_rectangle((x0 + 26, yy, x0 + 234 - 26 * j, yy + 20), 8, fill=(200, 208, 220, 255))
            d.rounded_rectangle((x0 + 16, 392, x0 + 244, 470), 14, fill=(255, 236, 150, 255), outline=(*GREEN, 255), width=4)
            lay.putalpha(lay.getchannel("A").point(lambda v: int(v * a)))
            f.alpha_composite(lay)
            c.text(f, f"stub-{k}", (x0 + 130, 431), "match 2%", 42, 700, NAVY, "mm", alpha=a)
            c.text(f, f"year-{k}", (x0 + 130, 592), f"Year {k + 1}", 44, 700, NAVY, "mm", alpha=a)
        self.bust(c, f, "R3", push_=c.t / c.d)
        return f

    # ---- B5: age 25 at the desk
    def s_office_age25(self, c):
        A = self.A
        cam = PCam(A.plate["OFFICE"], 540, 470, push(c.t, c.d, 1.0, 1.04))
        f = cam.render()
        rs.stand(f, cam, "OFFICE", A.ren["FS"], 700, 890, None)
        a = fade(c.t, 0.1, 0.3)
        if a > 0:
            lay = layer()
            d = ImageDraw.Draw(lay)
            d.rounded_rectangle((72, 236, 380, 340), 52, fill=(*NAVY, 255))
            lay.putalpha(lay.getchannel("A").point(lambda v: int(v * a)))
            f.alpha_composite(lay)
            c.text(f, "age", (226, 288), "Age 25", 60, 700, (255, 255, 255), "mm", alpha=a)
        if self.proto:
            self.disclaimer(c, f, 13.0, 15.0, None)
        return f

    # ---- B6: salary
    def s_salary_card(self, c):
        A = self.A
        cam = PCam(A.plate["OFFICE"], 940, 470, 1.0)
        f = cam.render()
        self.bust(c, f, "R2", push_=c.t / c.d)
        a = fade(c.t, 0.05, 0.3)
        if a > 0:
            card(f, (72, 236, 900, 470), a)
            c.text(f, "salary", (486, 353), "$44,000 salary", 78, 700, GREEN, "mm", alpha=a)
        if self.proto:
            self.disclaimer(c, f, 13.0, 15.0, None)
        return f

    # ---- frames
    def frame(self, T):
        T = min(T, self.total / FPS - 1 / FPS)
        b = next(b for b in self.beats if b["start_frame"] <= round(T * FPS) + 0 < b["end_frame"])
        d = (b["end_frame"] - b["start_frame"]) / FPS
        c = Ctx(b["id"], T - b["start_frame"] / FPS, d, T, self.rec)
        fn = self.build[b["id"]]
        if fn is None:
            raise NotImplementedError(f"scene '{b['id']}' is not built yet: the complete Short is rendered only after prototype approval")
        return fn(c).convert("RGB"), b


# ------------------------------------------------------------------ audio + encode
def build_audio(frames, out_wav):
    """Gain the cut narration to -16 LUFS (gain + limiter only), then trim or pad nothing: it is cut to the video length."""
    a, sr = sf.read(HERE / "short_audio_raw.wav", dtype="float32")
    raw = out_wav.with_suffix(".raw.wav")
    sf.write(raw, a, sr)
    p = subprocess.run(["ffmpeg", "-nostats", "-i", str(raw), "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
    i0 = float(p[p.rindex("I:") + 2:].split()[0])
    dur = frames / FPS
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af", f"volume={-16 - i0:.2f}dB,alimiter=limit=0.8:level=false,aresample=48000",
                    "-t", f"{dur:.4f}", str(out_wav)], check=True)
    raw.unlink()


def merge_layout(parts, spec, frames, path):
    scenes = {b["id"]: [] for b in spec["beats"] if b["start_frame"] < frames}
    merged = {}
    for p in parts:
        for it in json.loads(Path(p).read_text()):
            k = (it["scene"], it["key"])
            if k not in merged:
                merged[k] = it
            else:
                m, b = merged[k], it["bbox"]
                m["bbox"] = [min(m["bbox"][0], b[0]), min(m["bbox"][1], b[1]), max(m["bbox"][2], b[2]), max(m["bbox"][3], b[3])]
                m["start"] = min(m["start"], it["start"]); m["end"] = max(m["end"], it["end"]); m["font_px"] = min(m["font_px"], it["font_px"])
    for (sid, key), it in merged.items():
        scenes[sid].append(dict(text=it["text"], bbox=[round(v, 1) for v in it["bbox"]], font_px=round(it["font_px"], 1), role=it["role"],
                                start=round(it["start"], 4), end=round(it["end"], 4)))
    Path(path).write_text(json.dumps({"scenes": scenes}, indent=2) + "\n")


def item_end(spec, sid, frames):
    b = next(b for b in spec["beats"] if b["id"] == sid)
    return min(b["end_frame"], frames) / FPS


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--range", type=int, nargs=2)
    ap.add_argument("--seg", type=int, default=0)
    ap.add_argument("--stills", type=float, nargs="*", help="write stills at these seconds next to --output and exit")
    args = ap.parse_args()
    spec = json.loads((HERE / "short_spec.json").read_text())
    stage = os.environ.get("REN_SHORTS_STAGE", "prototype")
    frames = int(os.environ.get("REN_SHORTS_MAX_FRAMES", 360 if stage == "prototype" else spec["frames"]))
    frames = min(frames, spec["frames"])
    out = args.output
    layout_path = out.parent / "layout.json"
    if args.stills is not None:
        rec = Recorder()
        S = Short(spec, rec)
        for t in args.stills:
            S.frame(t)[0].save(out.parent / f"still_{t:05.2f}.png")
        return
    if args.range is None:
        build_audio(frames, out.with_suffix(".audio.wav"))
        jobs = max(1, args.jobs)
        bounds = [round(frames * k / jobs) for k in range(jobs + 1)]
        procs = [subprocess.Popen([sys.executable, str(Path(__file__)), "--output", str(out), "--range", str(bounds[k]), str(bounds[k + 1]), "--seg", str(k)], env=dict(os.environ))
                 for k in range(jobs)]
        for pr in procs:
            if pr.wait() != 0:
                raise SystemExit("a render segment failed")
        lst = out.parent / "segments.txt"
        lst.write_text("".join(f"file '{out.parent / f'{out.stem}_seg{k}.mp4'}'\n" for k in range(jobs)))
        silent = out.with_suffix(".video.mp4")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(silent)], check=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(silent), "-i", str(out.with_suffix(".audio.wav")), "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac",
                        "-b:a", "192k", "-ar", "48000", "-t", f"{frames / FPS:.4f}", "-movflags", "+faststart", str(out)], check=True)
        parts = []
        for k in range(jobs):
            parts.append(out.parent / f"{out.stem}_seg{k}.layout.json")
        merge_layout(parts, spec, frames, layout_path)
        # end of every text interval = the end of its scene (or of the prototype)
        lay = json.loads(layout_path.read_text())
        for sid, items in lay["scenes"].items():
            for it in items:
                it["end"] = round(item_end(spec, sid, frames), 4)
                if it["role"] == "disclaimer":
                    it["end"] = round(min(it["end"], 15.0 if frames <= 360 else it["end"]), 4)
        layout_path.write_text(json.dumps(lay, indent=2) + "\n")
        for k in range(jobs):
            for suffix in (".mp4", ".layout.json"):
                (out.parent / f"{out.stem}_seg{k}{suffix}").unlink()
        for p in (lst, silent, out.with_suffix(".audio.wav")):
            p.unlink()
        print("rendered", frames, "frames ->", out)
        return
    rec = Recorder()
    S = Short(spec, rec)
    a0, a1 = args.range
    seg = out.parent / f"{out.stem}_seg{args.seg}.mp4"
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264",
                            "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", str(seg)], stdin=subprocess.PIPE)
    for k in range(a0, a1):
        f, b = S.frame(k / FPS)
        enc.stdin.write(np.asarray(f, np.uint8).tobytes())
        if (k - a0) % 60 == 0:
            print(f"frame {k}/{a1}", flush=True)
    enc.stdin.close()
    enc.wait()
    items = [dict(scene=sid, key=key, **{kk: vv for kk, vv in it.items()}, end=0.0) for (sid, key), it in rec.items.items()]
    (out.parent / f"{out.stem}_seg{args.seg}.layout.json").write_text(json.dumps(items))


if __name__ == "__main__":
    main()
