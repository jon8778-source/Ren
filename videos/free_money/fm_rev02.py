"""Pilot revision 2: S1 + S2 of "I Said No to Free Money for 3 Years" with character actions, story-driven cuts and
graphics integrated into the scene (1280x720, 24 fps, v3 rules). Same narration as the pilot: same WAVs, same word
timings, no re-synthesis.

  project/.tools/venv/bin/python videos/free_money/fm_rev02.py --stills --out /tmp/claude-0/rev02_stills
  project/.tools/venv/bin/python videos/free_money/fm_rev02.py --out /output          # local only, never committed

Approved artwork only (matted Ren stills, Dev, folder prop, office / porch / parking-lot plates, library clip
ren_hold_phone). Everything else (phone screens, laptop screen, cards, coins, tags) is drawn in code.
Shot caps (v3): Ren 5.5 s, story still 2.5 s, graphic 3.5 s; every shot with Ren on screen is a Ren shot.
"""
import argparse, json, math, subprocess, sys
from pathlib import Path
import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fm_pilot as fp  # noqa: E402  (assets, timeline from the real narration, helpers)
from fm_pilot import (W, H, FPS, NAVY, SAGE, CREAM, GREEN, MUTED, ease, lerp, layer, paste, shadow, font, pill, warp, flip, Boxes,
                      layout_problems, lufs, edu_tag, bp, rs, VOICE)

RED = (196, 70, 60)
CAPS = {"ren": 5.5, "story": 2.5, "graphic": 3.5}


# ------------------------------------------------------------------ camera over a plate (all elements are drawn at final resolution)
class Cam:
    def __init__(self, img, cx, cy, z):
        iw, ih = img.size
        self.img, self.cw, self.ch = img, iw / z, ih / z
        self.x0 = min(max(cx - self.cw / 2, 0), iw - self.cw)
        self.y0 = min(max(cy - self.ch / 2, 0), ih - self.ch)
        self.k = W / self.cw

    def render(self):
        return self.img.resize((W, H), Image.LANCZOS, box=(self.x0, self.y0, self.x0 + self.cw, self.y0 + self.ch)).convert("RGBA")

    def pt(self, x, y):
        return ((x - self.x0) * self.k, (y - self.y0) * self.k)

    def place(self, frame, im, x, bottom, h_plate):
        h = h_plate * self.k
        w = im.width * h / im.height
        r = im.resize((max(1, round(w)), max(1, round(h))), Image.LANCZOS)
        sx, sy = self.pt(x, bottom)
        paste(frame, r, sx - w / 2, sy - h)
        return (sx - w / 2, sy - h, sx + w / 2, sy)

    def occlude(self, frame, plate_crop, polygon):
        """Redraw the plate over `frame` inside `polygon` (plate coordinates): things drawn before it end up behind it."""
        m = Image.new("L", (W, H), 0)
        ImageDraw.Draw(m).polygon([self.pt(*p) for p in polygon], fill=255)
        m = m.filter(ImageFilter.GaussianBlur(0.8))
        frame.paste(plate_crop, (0, 0), m)


def push(t, d, a, b):
    return lerp(a, b, min(max(t / d, 0), 1))


# desk top + laptop in Office_background (plate px): Ren sits behind these
DESK_POLY = [(0, 598), (214, 596), (218, 500), (326, 497), (413, 597), (498, 572), (502, 582), (282, 658), (0, 664)]
LAPTOP_SCREEN = [(221, 506), (323, 499), (410, 594), (252, 606)]


# ------------------------------------------------------------------ small code-built pieces
def car_icon(d, x, y, s, col=NAVY, wheel=CREAM):
    d.rounded_rectangle((x, y + 0.42 * s, x + s, y + 0.8 * s), 0.16 * s, fill=col)
    d.polygon([(x + 0.2 * s, y + 0.42 * s), (x + 0.32 * s, y + 0.12 * s), (x + 0.7 * s, y + 0.12 * s), (x + 0.84 * s, y + 0.42 * s)], fill=col)
    for cx in (x + 0.25 * s, x + 0.75 * s):
        d.ellipse((cx - 0.13 * s, y + 0.68 * s, cx + 0.13 * s, y + 0.94 * s), fill=col, outline=wheel, width=max(2, int(s * 0.03)))


def screen_small(w, h, kind="lease"):
    """A lit phone / laptop screen at small size (colour blocks only; the readable version is the close-up)."""
    im = Image.new("RGBA", (w, h), (*CREAM, 255))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w, h * 0.16), fill=NAVY)
    if kind == "lease":
        car_icon(d, w * 0.2, h * 0.28, w * 0.6, NAVY)
        d.rounded_rectangle((w * 0.18, h * 0.66, w * 0.82, h * 0.78), 3, fill=GREEN)
        d.rounded_rectangle((w * 0.18, h * 0.82, w * 0.62, h * 0.9), 3, fill=SAGE)
    else:
        for k in range(4):
            d.rounded_rectangle((w * 0.1, h * (0.26 + 0.17 * k), w * (0.9 - 0.12 * k), h * (0.34 + 0.17 * k)), 3, fill=(SAGE if k % 2 == 0 else (200, 214, 206)))
    return im


def coin(d, cx, cy, r, col, label="$"):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(*col, 255), outline=(*NAVY, 255), width=max(3, r // 9))
    d.text((cx, cy), label, font=font(int(r * 1.25), 700), fill=NAVY, anchor="mm")


def stack(d, cx, base_y, n, col, r=34, step=26):
    for k in range(n):
        y = base_y - k * step
        d.ellipse((cx - r, y - r * 0.55, cx + r, y + r * 0.55), fill=(*col, 255), outline=(*NAVY, 255), width=4)


def card_fit(frame, rows, t, boxes, x0, cy, max_w=600, base_px=44):
    """Right-hand card whose rows fit max_w; rows = [(segments, start_time)]; start_time < 0 = already there."""
    px = base_px
    d0 = ImageDraw.Draw(layer())
    while True:
        f = font(px, 700)
        widths = [sum(d0.textlength(s, font=f) for s, _ in seg) for seg, _ in rows]
        if max(widths) + 70 <= max_w or px <= 28:
            break
        px -= 2
    rh = int(px * 1.75)
    cw, ch = max(widths) + 70, rh * len(rows) + 44
    y0 = cy - ch / 2
    lay = layer()
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle((x0 + 5, y0 + 9, x0 + cw + 5, y0 + ch + 9), 30, fill=(19, 35, 63, 55))
    d.rounded_rectangle((x0, y0, x0 + cw, y0 + ch), 30, fill=(*CREAM, 255), outline=(*SAGE, 255), width=5)
    new_first = rows[0][1] >= 0
    if new_first:
        a = bp.fade(t, rows[0][1] - 0.05, 0.2)
        lay.putalpha(lay.getchannel("A").point(lambda v: int(v * a)))
    frame.alpha_composite(lay)
    boxes.text.append((x0, y0, x0 + cw, y0 + ch, "card"))
    for i, (seg, ts) in enumerate(rows):
        a = 1.0 if ts < 0 else bp.fade(t, ts, 0.3)
        if a <= 0:
            continue
        row = layer()
        rd = ImageDraw.Draw(row)
        x, y = x0 + 35, y0 + 22 + i * rh + (1 - a) * 14
        for s, col in seg:
            rd.text((x, y), s, font=f, fill=col)
            x += rd.textlength(s, font=f)
        if a < 1:
            row.putalpha(row.getchannel("A").point(lambda v: int(v * a)))
        frame.alpha_composite(row)


ROWS = [([("Age 25: ", NAVY), ("$44,000 salary", GREEN)], 0.1),
        ([("Lease: ", NAVY), ("$489/month", RED)], 0.1),
        ([("Page 6: We match ", NAVY), ("100%", GREEN), (" up to ", NAVY), ("4%", GREEN)], 0.1)]


# ------------------------------------------------------------------ phone clip (library: ren_hold_phone) with a code-built screen
class PhoneClip:
    S, CX, FEET = 0.92, 330, 705

    def __init__(self, A, start, seconds):
        entry = A.lib["ren_hold_phone.mp4"]
        n = int(math.ceil(seconds * FPS))
        raw = subprocess.check_output(["ffmpeg", "-v", "error", "-ss", f"{start:.3f}", "-i", str(rs.LIB / entry["file"]), "-frames:v", str(n),
                                       "-vf", "fps=24,format=rgb24", "-f", "rawvideo", "-"])
        rgb = np.frombuffer(raw, np.uint8).reshape(-1, 720, 1280, 3)
        self.off = entry["x_offset_px"]
        self.frames, self.holes = [], []
        for f in rgb:
            rgba = bp.cut_out(f)
            hole = self._screen(rgba)
            self.frames.append(rgba)
            self.holes.append(hole)
        self.n = n

    @staticmethod
    def _screen(rgba):
        """The phone screen = the enclosed transparent pocket (cut out as 'background' because it is white)."""
        a = rgba[..., 3] < 128
        lab, k = ndimage.label(a)
        if not k:
            return None
        best = None
        for i in range(1, k + 1):
            m = lab == i
            ys, xs = np.nonzero(m)
            if m[0, :].any() or m[-1, :].any() or m[:, 0].any() or m[:, -1].any():
                continue
            if 600 < len(xs) < 9000 and (ys.max() - ys.min()) > 1.2 * (xs.max() - xs.min()):
                best = (xs.min(), ys.min(), xs.max(), ys.max(), m)
        return best

    def draw(self, frame, t, boxes, ui):
        i = min(max(int(t * FPS), 0), self.n - 1)
        S = self.S
        ox = round(self.CX - 600 * S + self.off * S)
        oy = round(self.FEET - 698 * S)
        rgba = self.frames[i].copy()
        hole = self.holes[i]
        if hole is not None:                                   # paint the lit UI into the screen pocket, then Ren over it
            x0, y0, x1, y1, m = hole
            w, h = x1 - x0 + 1, y1 - y0 + 1
            scr = ui.resize((w, h), Image.LANCZOS)
            mask = Image.fromarray((m[y0:y1 + 1, x0:x1 + 1] * 255).astype(np.uint8))
            lay = np.zeros_like(rgba)
            tmp = Image.fromarray(lay)
            tmp.paste(scr, (x0, y0), mask.filter(ImageFilter.MaxFilter(3)))
            under = np.array(tmp)
            rgba = np.where((rgba[..., 3:4] < 128) & (under[..., 3:4] > 0), under, rgba)
        big = Image.fromarray(rgba, "RGBA").resize((round(1280 * S), round(720 * S)), Image.LANCZOS)
        shadow(frame, self.CX, self.FEET, 300)
        paste(frame, big, ox, oy)
        a = np.array(big)[..., 3]
        ys, xs = np.where(a > 128)
        boxes.ren = (ox + xs.min(), oy + ys.min(), ox + xs.max(), oy + ys.max())
        boxes.face = (boxes.ren[0] + 0.3 * (boxes.ren[2] - boxes.ren[0]), boxes.ren[1], boxes.ren[0] + 0.7 * (boxes.ren[2] - boxes.ren[0]), boxes.ren[1] + 0.2 * (boxes.ren[3] - boxes.ren[1]))


# ------------------------------------------------------------------ the revised film
class Rev:
    def __init__(self):
        self.A = fp.Assets()
        base, self.audio_len, self.offs = fp.timeline()
        self.total = self.audio_len + 0.6
        self.ph = base                                   # per-phrase timings from the real narration (22 + ... phrases)
        self.ph[-1]["end"] = self.total
        S1 = [s for s in base if s["scene"] == "S1"]
        S2 = [s for s in base if s["scene"] == "S2"]
        self.p = lambda sc, i: (S1 if sc == 1 else S2)[i]
        spec = [  # (scene, first phrase, last phrase, type, name)
            (1, 0, 1, "ren", "porch_two_shot"), (1, 2, 2, "story", "dev_close"), (1, 3, 3, "ren", "quote"), (1, 4, 4, "ren", "didnt_know"),
            (1, 5, 6, "graphic", "stub_line"), (1, 7, 7, "ren", "three_years"), (1, 8, 9, "ren", "impress"), (1, 10, 10, "ren", "take_you_back"),
            (2, 0, 1, "ren", "desk_salary"), (2, 2, 2, "ren", "made_it"), (2, 3, 4, "ren", "phone_lease"), (2, 5, 5, "graphic", "phone_489"),
            (2, 6, 6, "ren", "not_needed"), (2, 7, 8, "ren", "parking_lot"), (2, 9, 10, "ren", "folder_on_desk"), (2, 11, 11, "story", "page_six"),
            (2, 12, 12, "graphic", "match_strip"), (2, 13, 13, "graphic", "laptop_401k"), (2, 14, 14, "ren", "reaction_card"),
            (2, 15, 15, "ren", "never_page_six"), (2, 16, 17, "ren", "picked_two"), (2, 18, 18, "graphic", "lease_urgent")]
        self.shots = []
        for k, (sc, a, b, typ, name) in enumerate(spec):
            first, last = self.p(sc, a), self.p(sc, b)
            self.shots.append(dict(i=k + 1, scene=f"S{sc}", type=typ, name=name, start=first["start"], end=last["end"],
                                   phrase=" ".join(self.p(sc, j)["phrase"] for j in range(a, b + 1))))
        self.shots[0]["start"] = 0.0
        self.shots[-1]["end"] = self.total
        for k in range(len(self.shots) - 1):
            self.shots[k]["end"] = self.shots[k + 1]["start"]
        # frame-snap the cuts
        q = lambda x: round(x * FPS) / FPS
        for s in self.shots:
            s["start"], s["end"] = q(s["start"]), q(s["end"])
        for k, s in enumerate(self.shots[:-1]):
            over = (s["end"] - s["start"]) - CAPS[s["type"]]
            if 0 < over < 0.12:
                s["end"] = self.shots[k + 1]["start"] = s["start"] + CAPS[s["type"]]
        self.by = {s["name"]: s for s in self.shots}
        pc = self.by["phone_lease"]
        self.phone = PhoneClip(self.A, 1.5, pc["end"] - pc["start"] + 0.1)
        self.build = {s["name"]: getattr(self, "s_" + s["name"]) for s in self.shots}

    # ---- helpers
    def office(self, cx, cy, z):
        return Cam(self.A.plate["OFFICE"], cx, cy, z)

    def presenter(self, key, t, d, boxes, cx_ren=320, cam=None, h=580):
        cam = cam or self.office(720, 430, push(t, d, 1.25, 1.3))
        f = cam.render()
        shadow(f, cx_ren, H, 10, 0)
        fp.ren_still(f, self.A, key, cx_ren, H + 4, h, boxes, push=t / d)
        return f

    def at_desk(self, key, t, d, boxes, z0=1.25, z1=1.34, cx=470, cy=430):
        """Ren behind the plate's own desk and laptop: the desk is redrawn over his lower body so he reads as seated at it."""
        cam = self.office(cx, cy, push(t, d, z0, z1))
        f = cam.render()
        crop = f.copy()
        im = self.A.ren[key]
        hp, xr, yb = 430, 275, 602
        boxes.ren = cam.place(f, im, xr, yb, hp)
        boxes.face = (boxes.ren[0] + 0.2 * (boxes.ren[2] - boxes.ren[0]), boxes.ren[1], boxes.ren[2] - 0.2 * (boxes.ren[2] - boxes.ren[0]), boxes.ren[1] + 0.45 * (boxes.ren[3] - boxes.ren[1]))
        cam.occlude(f, crop, DESK_POLY)
        return f, cam

    # ---- S1
    def s_porch_two_shot(self, t, d, b):
        A = self.A
        cam = Cam(A.plate["PORCH"], push(t, d, 836, 960), push(t, d, 470, 440), push(t, d, 1.0, 1.22))
        f = cam.render()
        for x in (560, 1090):
            sx, sy = cam.pt(x, 880)
            shadow(f, sx, sy, 330 * cam.k)
        cam.place(f, A.dev, 1090, 880, 790)
        r = cam.place(f, A.ren["FS"], 560, 880, 790)
        b.ren, b.face = r, (r[0] + (r[2] - r[0]) * 0.3, r[1], r[0] + (r[2] - r[0]) * 0.7, r[1] + (r[3] - r[1]) * 0.18)
        return f

    def s_dev_close(self, t, d, b):
        A = self.A
        cam = Cam(A.plate["PORCH"], push(t, d, 1120, 1160), 330, push(t, d, 1.55, 1.75))
        f = cam.render()
        cam.place(f, A.dev, 1090, 880, 790)
        return f

    def s_quote(self, t, d, b):
        f = self.presenter("R4", t, d, b)
        a = bp.fade(t, 0.12, 0.3)
        bp.text_card(f, [("“Who's keeping", 46, 700, NAVY), ("the difference?”", 46, 700, NAVY)], 620, 230, "la", pad=32, alpha=a)
        b.text.append((620, 230, 1030, 410, "quote"))
        return f

    def s_didnt_know(self, t, d, b):
        return self.presenter("R1" if t < d * 0.45 else "R3", t, d, b)

    def s_stub_line(self, t, d, b):
        A = self.A
        sc = push(t, d, 2.3, 2.6)
        f = A.blur["PORCH"].convert("RGBA")
        anchor, dst = (745, 335), (620, push(t, d, 190, 250))
        f.alpha_composite(fp.view(A.dev_pad, anchor, dst, sc, A.pad))
        t_drop = self.p(1, 6)["start"] - self.by["stub_line"]["start"]
        pulse = 1.0 + 0.09 * math.sin(math.pi * min(1, max(0, (t - 0.2) / 0.5)))
        if t > t_drop:                                          # "my stomach dropped": the line darkens and sinks
            pulse = 1.0 - 0.04 * ease((t - t_drop) / 0.4)
        fp.glow_line(f, A, anchor, dst, sc, "Employer match: 2%", pulse, 1.0 * (1 - 0.7 * ease((t - t_drop) / 0.5)), b)
        return f

    def s_three_years(self, t, d, b):
        f = self.presenter("R3", t, d, b)
        lay = layer()
        dr = ImageDraw.Draw(lay)
        for k in range(3):
            cx = 690 + k * 150
            a = bp.fade(t, 0.15 + 0.55 * k, 0.3)
            if a <= 0:
                continue
            c = layer()
            cd = ImageDraw.Draw(c)
            cd.ellipse((cx - 56, 300 - 56, cx + 56, 300 + 56), outline=(*MUTED, 255), width=6)
            cd.text((cx, 300), "$", font=font(68, 700), fill=(*MUTED, 255), anchor="mm")
            cd.text((cx, 392), f"Year {k + 1}", font=font(36, 600), fill=(*NAVY, 255), anchor="mm")
            c.putalpha(c.getchannel("A").point(lambda v: int(v * a)))
            f.alpha_composite(c)
        b.text.append((620, 230, 1090, 420, "years"))
        return f

    def s_impress(self, t, d, b):
        return self.presenter("R3" if t < d * 0.3 else "R2", t, d, b)

    def s_take_you_back(self, t, d, b):
        cam = self.office(836, 470, push(t, d, 1.0, 1.06))
        f = cam.render()
        shadow(f, 880, 700, 280)
        fp.ren_still(f, self.A, "FP", 880, 700, 590, b, push=0)
        return f

    # ---- S2
    def s_desk_salary(self, t, d, b):
        f, cam = self.at_desk("R1", t, d, b)
        sc = Image.new("RGBA", (1, 1))
        # the laptop screen lights up with the payroll screen when "Forty-four thousand" is said
        a = bp.fade(t, 0.5, 0.35)
        if a > 0:
            ui = screen_small(200, 120, "doc")
            ui.putalpha(ui.getchannel("A").point(lambda v: int(v * a)))
            quad = [cam.pt(*p) for p in LAPTOP_SCREEN]
            lay = warp(ui, quad)
            f.alpha_composite(lay)
        pill(f, "Age 25", 700, 190, px=44, fill=NAVY, colour=(255, 255, 255), alpha=bp.fade(t, 0.1, 0.3), boxes=b, pad=(30, 12))
        card_fit(f, [(ROWS[0][0], 0.9)], t, b, 700, 330)
        return f

    def s_made_it(self, t, d, b):
        f = self.presenter("R2", t, d, b)
        card_fit(f, [([("Age 25: ", NAVY), ("$44,000 salary", GREEN)], -1)], t, b, 620, 330, max_w=520)
        return f

    def s_phone_lease(self, t, d, b):
        cam = self.office(720, 430, push(t, d, 1.25, 1.3))
        f = cam.render()
        ui = screen_small(60, 100, "lease")
        self.phone.draw(f, t, b, ui)
        return f

    def _phone_big(self, t, d, b, urgent):
        f = self.A.blur["OFFICE"].convert("RGBA")
        cx, top, ph, pw = 640, 40, 650, 340
        lay = layer()
        dr = ImageDraw.Draw(lay)
        dr.rounded_rectangle((cx - pw / 2 + 6, top + 12, cx + pw / 2 + 6, top + ph + 12), 52, fill=(19, 35, 63, 60))
        dr.rounded_rectangle((cx - pw / 2, top, cx + pw / 2, top + ph), 52, fill=(24, 30, 44, 255))
        sx0, sy0, sx1, sy1 = cx - pw / 2 + 14, top + 16, cx + pw / 2 - 14, top + ph - 16
        dr.rounded_rectangle((sx0, sy0, sx1, sy1), 40, fill=(*CREAM, 255))
        dr.rounded_rectangle((cx - 44, top + 24, cx + 44, top + 40), 8, fill=(24, 30, 44, 255))
        dr.text((sx0 + 28, sy0 + 58), "Car lease", font=font(36, 700), fill=NAVY)
        car_icon(dr, sx0 + 28, sy0 + 108, 90, NAVY)
        dr.text((sx0 + 28, sy0 + 214), "Brand-new car", font=font(26, 600), fill=NAVY)
        dr.text((sx0 + 28, sy0 + 272), "Monthly payment", font=font(28, 600), fill=MUTED)
        a = bp.fade(t, 0.05, 0.3)
        txt = layer()
        td = ImageDraw.Draw(txt)
        td.text((sx0 + 28, sy0 + 306), "$489", font=font(112, 700), fill=RED if urgent else NAVY)
        td.text((sx0 + 32, sy0 + 434), "per month", font=font(34, 600), fill=NAVY)
        txt.putalpha(txt.getchannel("A").point(lambda v: int(v * a)))
        f.alpha_composite(lay)
        f.alpha_composite(txt)
        dr3 = ImageDraw.Draw(f)
        dr3.rounded_rectangle((sx0 + 28, sy1 - 96, sx1 - 28, sy1 - 34), 31, fill=(*NAVY, 255))
        dr3.text(((sx0 + sx1) / 2, sy1 - 65), "Review lease", font=font(30, 700), fill=(255, 255, 255), anchor="mm")
        dr2 = ImageDraw.Draw(f)
        if urgent:
            e = ease((t - 0.15) / 0.3)
            by = lerp(-120, sy0 + 12, e)
            ban = layer()
            bd = ImageDraw.Draw(ban)
            bd.rounded_rectangle((sx0 + 12, by, sx1 - 12, by + 104), 26, fill=(*RED, 255))
            bd.text((sx0 + 36, by + 14), "Payment due", font=font(30, 700), fill=(255, 255, 255))
            bd.text((sx0 + 36, by + 56), "Lease: $489", font=font(34, 700), fill=(255, 255, 255))
            f.alpha_composite(ban)
        b.text.append((cx - pw / 2, top, cx + pw / 2, top + ph, "phone"))
        return f

    def s_phone_489(self, t, d, b):
        return self._phone_big(t, d, b, False)

    def s_not_needed(self, t, d, b):
        return self.presenter("R3", t, d, b)

    def s_parking_lot(self, t, d, b):
        A = self.A
        cam = Cam(A.plate["LOT"], push(t, d, 836, 990), push(t, d, 470, 520), push(t, d, 1.0, 1.18))
        f = cam.render()
        sx, sy = cam.pt(330, 905)
        shadow(f, sx, sy, 300 * cam.k)
        r = cam.place(f, A.ren["FS"], 330, 905, 760)
        b.ren, b.face = r, (r[0] + (r[2] - r[0]) * 0.3, r[1], r[0] + (r[2] - r[0]) * 0.7, r[1] + (r[3] - r[1]) * 0.18)
        return f

    def s_folder_on_desk(self, t, d, b):
        f, cam = self.at_desk("R1", t, d, b, z0=1.3, z1=1.36, cx=430, cy=450)
        A = self.A
        e = ease(t / 0.55)
        dx = lerp(-300, 0, e)
        quad_plate = [(60 + dx, 624), (215 + dx, 612), (238 + dx, 648), (72 + dx, 662)]
        fo = A.folder
        scr = [cam.pt(*p) for p in quad_plate]
        flat = warp(fo.resize((600, 450), Image.LANCZOS), scr)
        f.alpha_composite(flat)
        return f

    def s_page_six(self, t, d, b):
        A = self.A
        f = A.blur["OFFICE"].convert("RGBA")
        w = push(t, d, 780, 640)
        h = w * 9 / 16
        ax, ay = min(max(1180, w / 2 + 1), A.folder.width - w / 2 - 1), min(max(215, h / 2 + 1), A.folder.height - h / 2 - 1)
        f.alpha_composite(fp.view(A.folder, (ax, ay), (640, 360), W / w))
        return f

    def s_match_strip(self, t, d, b):
        A = self.A
        f = A.blur["OFFICE"].convert("RGBA")
        w = push(t, d, 700, 640)
        h = w * 9 / 16
        cx, cy = 1030, 590
        ax, ay = min(max(cx, w / 2 + 1), A.folder.width - w / 2 - 1), min(max(cy, h / 2 + 1), A.folder.height - h / 2 - 1)
        f.alpha_composite(fp.view(A.folder, (ax, ay), (640, 360), W / w))
        a = bp.fade(t, 0.25, 0.3)
        if a > 0:
            lay = layer()
            dr = ImageDraw.Draw(lay)
            x0, y0, x1, y1 = 330, 418, 1180, 528
            dr.rounded_rectangle((x0, y0, x1, y1), 24, fill=(255, 236, 150, 245), outline=(*GREEN, 255), width=6)
            ft = font(60, 700)
            segs = [("We match ", NAVY), ("100%", GREEN)]
            wtot = sum(dr.textlength(s, font=ft) for s, _ in segs)
            x = (x0 + x1) / 2 - wtot / 2
            for s, col in segs:
                dr.text((x, (y0 + y1) / 2), s, font=ft, fill=col, anchor="lm")
                x += dr.textlength(s, font=ft)
            lay.putalpha(lay.getchannel("A").point(lambda v: int(v * a)))
            glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(glow).rounded_rectangle((x0, y0, x1, y1), 24, fill=(255, 226, 90, int(150 * a)))
            f.alpha_composite(glow.filter(ImageFilter.GaussianBlur(20)))
            f.alpha_composite(lay)
            b.text.append((x0, y0, x1, y1, "match strip"))
        return f

    def s_laptop_401k(self, t, d, b):
        f = Image.new("RGBA", (W, H), (*CREAM, 255))
        lay = layer()
        dr = ImageDraw.Draw(lay)
        dr.rounded_rectangle((70, 40, 1210, 650), 34, fill=(24, 30, 44, 255))
        dr.rounded_rectangle((92, 62, 1188, 628), 20, fill=(*CREAM, 255))
        dr.rectangle((92, 62, 1188, 132), fill=(*NAVY, 255))
        dr.text((130, 97), "401(k) enrollment", font=font(40, 700), fill=(255, 255, 255), anchor="lm")
        dr.text((640, 190), "Every dollar you put in is matched", font=font(40, 600), fill=(*NAVY, 255), anchor="mm")
        n = int(min(6, max(0, (t - 0.25) / 0.2)))
        stack(dr, 400, 540, n, (255, 196, 40), r=52, step=38)
        stack(dr, 880, 540, max(0, min(6, int((t - 0.45) / 0.2))), SAGE, r=52, step=38)
        dr.text((640, 380), "=", font=font(120, 700), fill=(*MUTED, 255), anchor="mm")
        dr.text((400, 600), "You", font=font(34, 700), fill=NAVY, anchor="mm")
        dr.text((880, 600), "Company", font=font(34, 700), fill=NAVY, anchor="mm")
        f.alpha_composite(lay)
        b.text.append((70, 40, 1210, 650, "laptop"))
        return f

    def s_reaction_card(self, t, d, b):
        f = self.presenter("R3" if t < d * 0.4 else "R2", t, d, b)
        rows = [(ROWS[0][0], -1), (ROWS[1][0], -1), ([("Page 6:", NAVY)], 0.12),
                ([("We match ", NAVY), ("100%", GREEN), (" up to ", NAVY), ("4%", GREEN)], 0.3)]
        card_fit(f, rows, t, b, 620, 340, max_w=540, base_px=40)
        return f

    def s_never_page_six(self, t, d, b):
        f = self.presenter("R1", t, d, b)
        a = bp.fade(t, 0.1, 0.3)
        lay = layer()
        dr = ImageDraw.Draw(lay)
        dr.rounded_rectangle((700, 300, 960, 380), 40, fill=(*SAGE, 170))
        dr.text((830, 340), "Page 6", font=font(48, 700), fill=(255, 255, 255, 255), anchor="mm")
        dr.text((830, 420), "never read", font=font(34, 600), fill=(*MUTED, 255), anchor="mm")
        lay.putalpha(lay.getchannel("A").point(lambda v: int(v * a)))
        f.alpha_composite(lay)
        b.text.append((700, 300, 960, 440, "page6 tag"))
        return f

    def s_picked_two(self, t, d, b):
        f = self.presenter("R2", t, d, b)
        s = ease(min(1, t / 0.3)) * (1 + 0.1 * math.sin(math.pi * min(1, t / 0.4)))
        lay = layer()
        dr = ImageDraw.Draw(lay)
        dr.rounded_rectangle((890, 300, 1100, 440), 70, outline=(*MUTED, 200), width=6)
        dr.text((995, 372), "4%", font=font(80, 700), fill=(*MUTED, 200), anchor="mm")
        dr.text((995, 270), "the full match", font=font(30, 600), fill=(*MUTED, 255), anchor="mm")
        f.alpha_composite(lay)
        chip = layer()
        cd = ImageDraw.Draw(chip)
        cd.rounded_rectangle((640, 295, 840, 445), 75, fill=(*NAVY, 255))
        cd.text((740, 370), "2%", font=font(100, 700), fill=(255, 255, 255), anchor="mm")
        cd.text((740, 265), "what I picked", font=font(30, 600), fill=(*NAVY, 255), anchor="mm")
        ss = max(s, 0.01)
        chip = chip.transform((W, H), Image.AFFINE, (1 / ss, 0, 740 - 740 / ss, 0, 1 / ss, 370 - 370 / ss), Image.BICUBIC)
        if s > 0.06:
            f.alpha_composite(chip)
        b.text.append((630, 255, 1110, 450, "chip"))
        return f

    def s_lease_urgent(self, t, d, b):
        return self._phone_big(t, d, b, True)

    def edu(self, f, T, boxes):
        """Small disclaimer tag at the start and end, bottom-right so it never sits on Ren."""
        if T < 5.0:
            a = min(bp.fade(T, 0.4, 0.4), 1 - bp.fade(T, 4.4, 0.5))
        elif T > self.total - 4.0:
            a = bp.fade(T, self.total - 3.8, 0.4)
        else:
            return
        fnt = font(19, 500)
        w = ImageDraw.Draw(layer()).textlength(fp.EDU, font=fnt) + 36
        pill(f, fp.EDU, W - 36 - w, 668, px=19, weight=500, fill=CREAM, colour=NAVY, alpha=0.92 * max(a, 0), boxes=boxes, pad=(18, 8))

    # ---- frames
    def frame_at(self, T):
        T = min(T, self.total - 1 / FPS)
        sh = next((s for s in self.shots if s["start"] <= T < s["end"] + 1e-9), self.shots[-1])
        boxes = Boxes()
        f = self.build[sh["name"]](T - sh["start"], sh["end"] - sh["start"], boxes).convert("RGBA")
        b1 = self.by["desk_salary"]["start"]
        if b1 - 0.7 <= T < b1:                            # time change: the page peels away into the age-25 office
            nxt = self.by["desk_salary"]
            bx = Boxes()
            inc = self.build["desk_salary"](0.0, nxt["end"] - nxt["start"], bx).convert("RGBA")
            f = flip(f, inc, (T - (b1 - 0.7)) / 0.7)
        self.edu(f, T, boxes)
        return f.convert("RGB"), boxes, sh


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(HERE / "renders"))
    ap.add_argument("--stills", action="store_true")
    ap.add_argument("--name", default="free_money_S1_S2_pilot_rev02")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    R = Rev()
    over = [(s["i"], s["name"], s["type"], round(s["end"] - s["start"], 2)) for s in R.shots if s["end"] - s["start"] > CAPS[s["type"]]]
    print(f"{len(R.shots)} shots, total {R.total:.2f}s | over cap: {over or 'none'}", flush=True)
    print([(s["i"], s["name"], round(s["end"] - s["start"], 2)) for s in R.shots], flush=True)
    if args.stills:
        d = out / "stills"
        d.mkdir(exist_ok=True)
        probs = []
        for s in R.shots:
            for tag, frac in (("a", 0.1), ("b", 0.5), ("c", 0.9)):
                T = s["start"] + (s["end"] - s["start"]) * frac
                f, boxes, sh = R.frame_at(T)
                f.save(d / f"shot{s['i']:02d}{tag}.png")
                if tag == "b":
                    probs += layout_problems(boxes, sh)
        print("layout problems:", probs or "none")
        return
    sr = 24000
    a1, r1 = sf.read(VOICE / "S1.wav", dtype="float32")
    a2, r2 = sf.read(VOICE / "S2.wav", dtype="float32")
    assert r1 == r2 == sr
    track = np.concatenate([a1, a2, np.zeros(int(0.6 * sr), np.float32)])
    raw = out / "rev02_voice_raw.wav"
    sf.write(raw, track, sr)
    i0, _ = lufs(raw)
    wav = out / "rev02_voice.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af", f"volume={-16 - i0:.2f}dB,alimiter=limit=0.8:level=false,aresample=48000", str(wav)], check=True)
    video = out / f"{args.name}_video.mp4"
    n = int(round(R.total * FPS))
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(video)], stdin=subprocess.PIPE)
    probs = []
    for k in range(n):
        f, boxes, sh = R.frame_at(k / FPS)
        if k % 6 == 0:
            probs += layout_problems(boxes, sh)
        enc.stdin.write(np.asarray(f, np.uint8).tobytes())
        if k % 120 == 0:
            print(f"frame {k}/{n}", flush=True)
    enc.stdin.close()
    enc.wait()
    final = out / f"{args.name}.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-i", str(wav), "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-ar", "48000", "-t", f"{R.total:.3f}", "-movflags", "+faststart", str(final)], check=True)
    video.unlink()
    I, pk = lufs(final)
    rep = {"frames": n, "duration_s": round(R.total, 3), "narration_s": round(R.audio_len, 3), "lufs": I, "true_peak_dbtp": pk, "layout_problems": probs, "over_cap": over,
           "shots": [{k: (round(v, 3) if isinstance(v, float) else v) for k, v in s.items()} for s in R.shots]}
    (out / f"{args.name}_report.json").write_text(json.dumps(rep, indent=1, ensure_ascii=False))
    print(json.dumps({k: rep[k] for k in ("frames", "duration_s", "lufs", "true_peak_dbtp", "layout_problems", "over_cap")}))


if __name__ == "__main__":
    main()
