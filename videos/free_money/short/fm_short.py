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

    # ---- B3: the line, sinking (a tight crop on the line; the camera sinks with it on "dropped")
    def s_stub_line(self, c):
        A = self.A
        drop = ease((c.T - 7.2) / 0.55)                       # "my stomach dropped": the line darkens and sinks, the camera follows
        sc = push(c.t, c.d, 4.3, 4.7)
        dst = (500, lerp(430, 790, drop))
        cam = PCam(A.plate["PORCH"], 1000, 470, 1.0)
        f = blurred(cam, 20)
        f.alpha_composite(dev_view(A, (745, 335), dst, sc))
        dark = layer()
        ImageDraw.Draw(dark).rectangle((0, 0, W, H), fill=(19, 35, 63, int(95 * drop)))
        f.alpha_composite(dark)
        pulse = 1.0 + 0.06 * math.sin(math.pi * min(1, max(0, (c.t - 0.2) / 0.5))) - 0.05 * drop
        self.glow_line(c, f, (745, 335), dst, sc, "Match: 2%", pulse, 1.0 * (1 - 0.75 * drop), "stub-line")
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


    # ================= beats 7-21 (rendered only after prototype approval) =================
    def scaled(self, lay, s, alpha=1.0, centre=(486, 840)):
        """Pop a full-canvas layer about `centre`: scale s (<=1 keeps text inside its measured bounds) and alpha."""
        if s != 1.0:
            cx, cy = centre
            lay = lay.transform((W, H), Image.AFFINE, (1 / s, 0, cx - cx / s, 0, 1 / s, cy - cy / s), Image.BICUBIC)
        if alpha < 1:
            lay.putalpha(lay.getchannel("A").point(lambda v: int(v * alpha)))
        return lay

    def phone(self, c, tag, draw_screen, s=1.0, alpha=1.0):
        """A big portrait phone (x 166-806, y 250-1430) drawn in code; `draw_screen(lay, box)` fills the screen and records its text."""
        lay = layer()
        d = ImageDraw.Draw(lay)
        cx, top, pw, ph = 486, 250, 640, 1180
        d.rounded_rectangle((cx - pw / 2 + 8, top + 14, cx + pw / 2 + 8, top + ph + 14), 76, fill=(19, 35, 63, 60))
        d.rounded_rectangle((cx - pw / 2, top, cx + pw / 2, top + ph), 76, fill=(24, 30, 44, 255))
        box = (cx - pw / 2 + 20, top + 22, cx + pw / 2 - 20, top + ph - 22)
        d.rounded_rectangle(box, 58, fill=(*CREAM, 255))
        d.rounded_rectangle((cx - 60, top + 34, cx + 60, top + 58), 12, fill=(24, 30, 44, 255))
        draw_screen(lay, box)
        return self.scaled(lay, s, alpha)

    def car_icon(self, d, x, y, w):
        d.rounded_rectangle((x, y + 0.42 * w, x + w, y + 0.8 * w), 0.16 * w, fill=NAVY)
        d.polygon([(x + 0.2 * w, y + 0.42 * w), (x + 0.32 * w, y + 0.12 * w), (x + 0.7 * w, y + 0.12 * w), (x + 0.84 * w, y + 0.42 * w)], fill=NAVY)
        for cx_ in (x + 0.25 * w, x + 0.75 * w):
            d.ellipse((cx_ - 0.13 * w, y + 0.68 * w, cx_ + 0.13 * w, y + 0.94 * w), fill=NAVY, outline=CREAM, width=4)

    def lease_screen(self, c, urgent):
        def draw(lay, box):
            x0, y0, x1, y1 = box
            d = ImageDraw.Draw(lay)
            c.text(lay, "lease-title", (x0 + 44, y0 + 70), "Car lease", 56, 700, NAVY, "lm")
            self.car_icon(d, x0 + 44, y0 + 150, 230)
            c.text(lay, "lease-brand", (x0 + 44, y0 + 420), "Brand-new car", 44, 600, NAVY, "lm")
            c.text(lay, "lease-monthly", (x0 + 44, y0 + 540), "Monthly payment", 44, 600, MUTED, "lm")
            c.text(lay, "lease-489", (x0 + 40, y0 + 690), "$489", 190, 700, RED if urgent else NAVY, "lm")
            c.text(lay, "lease-permonth", (x0 + 44, y0 + 835), "per month", 52, 600, NAVY, "lm")
            d.rounded_rectangle((x0 + 44, y1 - 190, x1 - 44, y1 - 80), 55, fill=(*NAVY, 255))
            c.text(lay, "lease-button", ((x0 + x1) / 2, y1 - 135), "Review lease", 50, 700, (255, 255, 255), "mm")
            if urgent:
                e = fade(c.t, 0.15, 0.3)
                d2 = ImageDraw.Draw(lay)
                d2.rounded_rectangle((x0 + 20, y0 + 20, x1 - 20, y0 + 170), 34, fill=(*RED, int(255 * e)))
                c.text(lay, "due-1", (x0 + 70, y0 + 66), "Payment due", 50, 700, (255, 255, 255), "lm", alpha=e)
                c.text(lay, "due-2", (x0 + 70, y0 + 124), "Lease: $489", 54, 700, (255, 255, 255), "lm", alpha=e)
        return draw

    def office_blur(self, z=1.0, cx=900):
        return blurred(PCam(self.A.plate["OFFICE"], cx, 470, z), 14)

    # ---- B7: the lease, in the parking lot
    def s_lot_lease(self, c):
        A = self.A
        cam = PCam(A.plate["LOT"], push(c.t, c.d, 760, 790), 470, push(c.t, c.d, 1.0, 1.05))
        f = cam.render()
        rs.stand(f, cam, "LOT", A.ren["FS"], 650, 870, None)
        return f

    # ---- B8: $489 on the phone
    def s_phone_489(self, c):
        f = self.office_blur()
        e = fade(c.t, 0.0, 0.3)
        f.alpha_composite(self.phone(c, "p", self.lease_screen(c, False), s=lerp(0.92, 1.0, e), alpha=e))
        return f

    # ---- B9: the folder, page six (a portrait crop of the folder prop)
    def folder_crop(self, c, wwin, cy=543, dx=0):
        A = self.A
        bg = self.office_blur()
        wwin = min(wwin, 1086 * 9 / 16 - 0.01)
        h = wwin * 16 / 9
        x0 = min(max(1142 - wwin / 2, 0), 1448 - wwin)
        y0 = min(max(cy - h / 2, 0), 1086 - h)
        crop = A.folder.resize((W, H), Image.LANCZOS, box=(x0, y0, x0 + wwin, y0 + h))
        if dx:
            lay = layer()
            lay.paste(crop, (int(dx), 0))
            crop = lay
        bg.alpha_composite(crop)
        return bg, (x0, y0, wwin / W)

    def s_folder_page6(self, c):
        f, _ = self.folder_crop(c, push(c.t, c.d, 611, 570), dx=lerp(W, 0, ease(c.t / 0.45)))
        return f

    # ---- B10: dollar for dollar
    def s_match_coins(self, c):
        f = self.office_blur(cx=700)
        n = int(min(6, max(0, (c.t - 0.35) / 0.28)))                     # both stacks grow together: the "=" is true on every frame
        lay = layer()
        d = ImageDraw.Draw(lay)
        for cx_, col in ((250, GOLD), (722, SAGE)):
            for k in range(n):
                y = 1150 - k * 46
                d.ellipse((cx_ - 130, y - 36, cx_ + 130, y + 36), fill=(*col, 255), outline=(*NAVY, 255), width=6)
        f.alpha_composite(lay)
        c.text(f, "coin-you", (250, 1250), "You", 56, 700, NAVY, "mm")
        c.text(f, "coin-emp", (722, 1250), "Employer", 56, 700, NAVY, "mm")
        if n > 0:
            c.text(f, "equals", (486, 960), "=", 190, 700, MUTED, "mm")
        a = fade(c.t, 0.1, 0.3)
        if a > 0:
            lay = layer()
            ImageDraw.Draw(lay).rounded_rectangle((176, 330, 796, 440), 55, fill=(*CREAM, int(255 * a)), outline=(*SAGE, int(255 * a)), width=5)
            f.alpha_composite(lay)
            c.text(f, "coin-title", (486, 385), "$1 matched by $1", 54, 700, NAVY, "mm", alpha=a)
        return f

    # ---- B11: up to 4%
    def s_match_strip(self, c):
        f, (x0, y0, k) = self.folder_crop(c, 611)
        a = fade(c.t, 0.1, 0.3)
        sx0, sy0, sx1, sy1 = (860 - x0) / k, (621 - y0) / k, (1325 - x0) / k, (682 - y0) / k
        lay = layer()
        d = ImageDraw.Draw(lay)
        glow = layer()
        ImageDraw.Draw(glow).rounded_rectangle((sx0, sy0, sx1, sy1), 30, fill=(255, 226, 90, int(170 * a)))
        f.alpha_composite(glow.filter(ImageFilter.GaussianBlur(24)))
        d.rounded_rectangle((sx0, sy0, sx1, sy1), 30, fill=(255, 236, 150, int(245 * a)), outline=(*GREEN, int(255 * a)), width=7)
        f.alpha_composite(lay)
        c.text(f, "strip", ((sx0 + sx1) / 2 + 20, (sy0 + sy1) / 2), "We match 100%", 56, 700, NAVY, "mm", alpha=a)
        b = fade(c.t, 0.7, 0.3)
        if b > 0:
            lay = layer()
            ImageDraw.Draw(lay).rounded_rectangle((300, sy1 + 40, 760, sy1 + 150), 55, fill=(*GREEN, int(255 * b)))
            f.alpha_composite(lay)
            c.text(f, "up-to-4", (530, sy1 + 95), "up to 4%", 60, 700, (255, 255, 255), "mm", alpha=b)
        return f

    # ---- B12: the 2% decision on a benefits screen
    def s_picked_two(self, c):
        f = self.office_blur(cx=1000)
        a = fade(c.t, 0.05, 0.3)
        card(f, (72, 300, 900, 1240), a)
        if a > 0:
            c.text(f, "bs-title", (486, 400), "Retirement contribution", 52, 700, NAVY, "mm", alpha=a)
            tx0, tx1, ty = 150, 820, 640
            lay = layer()
            d = ImageDraw.Draw(lay)
            d.rounded_rectangle((tx0, ty, tx1, ty + 22), 11, fill=(205, 214, 226, 255))
            kn = ease((c.t - 0.35) / 0.6)
            kx = tx0 + (tx1 - tx0) * (2 / 6) * kn
            d.rounded_rectangle((tx0, ty, kx, ty + 22), 11, fill=(*NAVY, 255))
            for pct in (0, 2, 4, 6):
                x = tx0 + (tx1 - tx0) * pct / 6
                d.line((x, ty - 14, x, ty + 36), fill=(*MUTED, 255), width=4)
            d.ellipse((kx - 26, ty - 14, kx + 26, ty + 38), fill=(255, 255, 255, 255), outline=(*NAVY, 255), width=7)
            ey = 960
            d.rounded_rectangle((tx0, ey, tx0 + (tx1 - tx0) * (2 / 6) * kn, ey + 56), 16, fill=(*SAGE, 255))
            ga = fade(c.t, 1.2, 0.35)
            if ga > 0:
                g = layer()
                dashed(ImageDraw.Draw(g), (tx0 + (tx1 - tx0) * (2 / 6) + 6, ey, tx0 + (tx1 - tx0) * (4 / 6), ey + 56), (*GREEN, 255))
                g.putalpha(g.getchannel("A").point(lambda v: int(v * ga)))
                lay.alpha_composite(g)
            f.alpha_composite(lay)
            for pct in (0, 2, 4, 6):
                c.text(f, f"tick-{pct}", (tx0 + (tx1 - tx0) * pct / 6, ty + 80), f"{pct}%", 44, 600, MUTED, "mm")
            if kn > 0.9:
                c.text(f, "you-2", (kx, ty - 70), "You: 2%", 52, 700, NAVY, "mm")
            c.text(f, "emp-label", (tx0, ey - 56), "Employer match", 46, 600, MUTED, "lm")
            c.text(f, "up-to", (tx0 + (tx1 - tx0) * 0.5, ey + 120), "up to 4%", 50, 700, GREEN, "mm", alpha=ga)
        return f

    # ---- B13: the lease won
    def s_lease_urgent(self, c):
        f = self.office_blur()
        f.alpha_composite(self.phone(c, "p", self.lease_screen(c, True)))
        return f

    # ---- jars (beats 14-15)
    def jar(self, c, f, cx, base, label, pct, col, ghost_to=None, big=4.0, w=300, h=620, show=True):
        lay = layer()
        d = ImageDraw.Draw(lay)
        x0, y0 = cx - w / 2, base - h
        d.rounded_rectangle((x0 + 6, y0 + 12, x0 + w + 6, base + 12), 44, fill=(19, 35, 63, 45))
        d.rounded_rectangle((x0, y0, x0 + w, base), 44, fill=(246, 249, 252, 255), outline=(*NAVY, 255), width=7)
        top = base - 10 - (h - 20) * pct / big
        if pct > 0.02:
            m = Image.new("L", (W, H), 0)
            ImageDraw.Draw(m).rounded_rectangle((x0 + 9, y0 + 9, x0 + w - 9, base - 9), 36, fill=255)
            fl = layer()
            ImageDraw.Draw(fl).rectangle((x0, top, x0 + w, base), fill=(*col, 255))
            fl.putalpha(Image.fromarray(np.minimum(np.array(fl.getchannel("A")), np.array(m))))
            lay.alpha_composite(fl)
        if ghost_to is not None and ghost_to > pct + 0.1:
            gt = base - 10 - (h - 20) * ghost_to / big
            dashed(ImageDraw.Draw(lay), (x0 + 16, gt, x0 + w - 16, top), (*GREEN, 255))
        f.alpha_composite(lay)
        if show and pct >= 1.9 and h * pct / big > 90:
            c.text(f, f"jar-{label}-pct", (cx, (top + base) / 2), "2%", 56, 700, (255, 255, 255), "mm")
        c.text(f, f"jar-{label}", (cx, base + 60), "You (employee)" if label == "you" else "Employer", 46, 700, NAVY, "mm")

    def s_jars_two(self, c):
        f = self.office_blur(cx=700)
        c.text(f, "jars-title", (486, 280), "One employer's plan (example)", 44, 600, MUTED, "mm")
        e = ease((c.t - 0.1) / 1.0)
        self.jar(c, f, 250, 1120, "you", 2 * e, NAVY)
        self.jar(c, f, 722, 1120, "emp", 2 * e, SAGE, ghost_to=2 + 2 * ease((c.t - 1.3) / 0.7))
        a = fade(c.t, 0.05, 0.3)
        if a > 0:
            lay = layer()
            ImageDraw.Draw(lay).rounded_rectangle((176, 350, 796, 460), 55, fill=(*CREAM, int(255 * a)), outline=(*SAGE, int(255 * a)), width=5)
            f.alpha_composite(lay)
            c.text(f, "jars-pill", (486, 405), "$1 matched by $1", 54, 700, NAVY, "mm", alpha=a)
        return f

    def s_never_paid(self, c):
        f = self.office_blur(cx=700)
        c.text(f, "jars-title", (486, 280), "One employer's plan (example)", 44, 600, MUTED, "mm")
        self.jar(c, f, 250, 1120, "you", 2, NAVY)
        self.jar(c, f, 722, 1120, "emp", 2, SAGE, ghost_to=4)
        a = fade(c.t, 0.4, 0.4)
        if a > 0:
            lay = layer()
            ImageDraw.Draw(lay).rounded_rectangle((226, 1290, 746, 1400), 55, fill=(*NAVY, int(255 * a)))
            f.alpha_composite(lay)
            c.text(f, "never-paid", (486, 1345), "Never paid", 62, 700, (255, 255, 255), "mm", alpha=a)
        return f

    # ---- B16: the first year's cost
    def s_missed_880(self, c):
        f = self.office_blur(cx=600)
        card(f, (72, 300, 900, 1180), fade(c.t, 0.0, 0.25))
        c.text(f, "led-age", (122, 392), "Age 25", 58, 700, NAVY, "lm")
        c.text(f, "led-sal", (850, 392), "$44,000", 58, 700, GREEN, "rm")
        lay = layer()
        ImageDraw.Draw(lay).line((122, 450, 850, 450), fill=(*SAGE, 255), width=5)
        f.alpha_composite(lay)
        c.text(f, "led-missed", (122, 540), "Missed match:", 50, 600, MUTED, "lm")
        a = fade(c.t, 0.5, 0.4)
        c.text(f, "led-880", (486, 760), "$880", 200, 700, RED, "mm", alpha=a)
        c.text(f, "led-year", (486, 980), "the first year", 56, 600, NAVY, "mm", alpha=fade(c.t, 0.9, 0.4))
        return f

    # ---- B17 / B18: the retirement app
    def app_screen(self, c, v):
        def draw(lay, box):
            x0, y0, x1, y1 = box
            d = ImageDraw.Draw(lay)
            c.text(lay, "app-title", (x0 + 44, y0 + 80), "401(k)", 58, 700, NAVY, "lm")
            c.text(lay, "app-mine", (x0 + 44, y0 + 200), "My contribution", 46, 600, MUTED, "lm")
            col = tuple(int(NAVY[i] + (GREEN[i] - NAVY[i]) * v) for i in range(3))
            c.text(lay, "app-pct", (x0 + 44, y0 + 460), "4%" if v > 0.5 else "2%", 250, 700, col, "lm")
            tx0, ty, tw, th = x0 + 60, y0 + 760, 440, 100
            track = tuple(int(200 + (GREEN[i] - 200) * v) for i in range(3))
            d.rounded_rectangle((tx0, ty, tx0 + tw, ty + th), 50, fill=(*track, 255))
            kx = tx0 + 50 + v * (tw - 100)
            d.ellipse((kx - 44, ty + 6, kx + 44, ty + th - 6), fill=(255, 255, 255, 255), outline=(150, 156, 170, 255), width=3)
            c.text(lay, "app-2", (tx0 + 20, ty + 160), "2%", 46, 600, MUTED, "lm")
            c.text(lay, "app-4", (tx0 + tw - 20, ty + 160), "4%", 46, 600, MUTED, "rm")
        return draw

    def s_toggle_app(self, c):
        f = self.office_blur()
        e = fade(c.t, 0.0, 0.3)
        v = ease((c.t - 1.9) / 0.6)                                    # "changed two to four"
        f.alpha_composite(self.phone(c, "p", self.app_screen(c, v), s=lerp(0.92, 1.0, e), alpha=e))
        return f

    def s_ninety_seconds(self, c):
        f = self.office_blur()
        f.alpha_composite(self.phone(c, "p", self.app_screen(c, 1.0)))
        s_ = ease(min(1, c.t / 0.3)) * (1 + 0.08 * math.sin(math.pi * min(1, c.t / 0.4)))
        s_ = min(s_, 1.0)
        lay = layer()
        d = ImageDraw.Draw(lay)
        cx_, cy_, r = 702, 400, 138
        d.ellipse((cx_ - r + 8, cy_ - r + 14, cx_ + r + 8, cy_ + r + 14), fill=(19, 35, 63, 50))
        d.ellipse((cx_ - r, cy_ - r, cx_ + r, cy_ + r), fill=(*GREEN, 255))
        c.text(lay, "badge-90", (cx_, cy_ - 28), "90", 120, 700, (255, 255, 255), "mm")
        c.text(lay, "badge-sec", (cx_, cy_ + 62), "seconds", 46, 700, (255, 255, 255), "mm")
        f.alpha_composite(self.scaled(lay, max(s_, 0.02), 1.0, centre=(cx_, cy_)))
        return f

    # ---- B19-B21: closing busts and the call to action
    def s_three_years_late(self, c):
        f = PCam(self.A.plate["OFFICE"], 940, 470, 1.0).render()
        self.bust(c, f, "R1", push_=c.t / c.d)
        a = fade(c.t, 0.1, 0.3)
        if a > 0:
            lay = layer()
            ImageDraw.Draw(lay).rounded_rectangle((200, 236, 772, 372), 68, fill=(*NAVY, int(255 * a)))
            f.alpha_composite(lay)
            c.text(f, "late", (486, 304), "3 years late", 72, 700, (255, 255, 255), "mm", alpha=a)
        return f

    def s_free_part(self, c):
        f = PCam(self.A.plate["OFFICE"], 700, 470, 1.0).render()
        self.bust(c, f, "R2", push_=c.t / c.d)
        a = fade(c.t, 0.1, 0.3)
        card(f, (72, 236, 900, 400), a)
        c.text(f, "free", (486, 318), "Don't skip the free part", 62, 700, GREEN, "mm", alpha=a)
        return f

    def s_collect_owed(self, c):
        A = self.A
        cam = PCam(A.plate["OFFICE"], 540, 470, push(c.t, c.d, 1.0, 1.04))
        f = cam.render()
        rs.stand(f, cam, "OFFICE", A.ren["FP"], 635, 890, None)
        a = fade(c.t, 0.1, 0.3)
        card(f, (72, 220, 900, 470), a)
        c.text(f, "collect-1", (486, 300), "Collect what", 72, 700, NAVY, "mm", alpha=a)
        c.text(f, "collect-2", (486, 396), "you're owed", 72, 700, GREEN, "mm", alpha=a)
        self.disclaimer(c, f, self.total / FPS - 2.0, self.total / FPS + 1, None)      # the exact end disclaimer, continuous for the last 2 s
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
                                start=it["start"], end=it["end"]))
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
    out = args.output.resolve()
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
                it["end"] = item_end(spec, sid, frames)
                if it["role"] == "disclaimer":
                    it["end"] = min(it["end"], 15.0 if frames <= 360 else it["end"])
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
