"""Gate 2 pilot: S1 + S2 of "I Said No to Free Money for 3 Years" (1280x720, 24 fps, v3 rules).

  project/.tools/venv/bin/python videos/free_money/fm_pilot.py --stills            # one still per shot, no video
  project/.tools/venv/bin/python videos/free_money/fm_pilot.py --out /output       # render (local only, never committed)

Shot timing comes from the Whisper word times of the real narration (voice/words_S1.json, words_S2.json):
each shot starts when its first narrated word starts, so graphics sync with the voice. The narration is joined
exactly as generated (no speed change, stretching or padding). Reuses the approved matted Ren stills, the library
clips (decoded at native 1280x720 by build_pilot.RenShot), the approved plates/props/characters, and draws all
text, numbers, cards and diagrams in code (Fredoka, navy / sage / cream).
"""
import argparse, json, math, re, subprocess, sys
from pathlib import Path
import difflib
import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "videos" / "postponing_life"))
import build_pilot as bp  # noqa: E402  (RenShot: native-resolution clip frames + background removal)
import render_shots as rs  # noqa: E402
import plan_data as pd  # noqa: E402

W, H, FPS = 1280, 720, 24
NAVY, SAGE, CREAM, GREEN, MUTED = (19, 35, 63), (127, 160, 138), (251, 246, 234), (30, 158, 90), (122, 132, 150)
LIBD = ROOT / "library"
VOICE = HERE / "voice"
ease = bp.ease
font = bp.font
EDU = "Educational content only, not financial advice"


def lerp(a, b, x):
    return a + (b - a) * x


def layer():
    return Image.new("RGBA", (W, H), (255, 255, 255, 0))


# ------------------------------------------------------------------ assets
class Assets:
    def __init__(self):
        sup = LIBD / "supporting_assets"
        self.plate = {k: Image.open(sup / "backgrounds" / f).convert("RGB") for k, f in
                      (("PORCH", "Porch_background_16x9.png"), ("OFFICE", "Office_background_16x9.png"), ("LOT", "Office_parking_lot_car_16x9.png"))}
        self.blur = {}
        for k, im in self.plate.items():
            b = im.resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(11))
            self.blur[k] = Image.blend(b, Image.new("RGB", (W, H), CREAM), 0.28)
        self.dev = self._trim(Image.open(sup / "characters" / "Dev_pay_stub.png").convert("RGBA"))
        full = Image.open(sup / "characters" / "Dev_pay_stub.png").convert("RGBA")
        self.dev_full = full                                    # untrimmed, for the stub close-ups (coordinates are in this image)
        self.folder = Image.open(sup / "props" / "HR_folder_page6_prop.png").convert("RGBA")
        self.ren = {k: self._trim(Image.open(HERE / "matted" / f"{n}.png").convert("RGBA")) for k, n in
                    (("R1", "Ren_1_neutral"), ("R2", "Ren_2_hand_on_chest_talking"), ("R3", "Ren_3_thinking_bust"), ("R4", "Ren_4_pointing"),
                     ("FT", "Ren_extra_thinking_full_body"), ("FP", "Ren_full_body_presenting"), ("FS", "Ren_full_body_standing"), ("FW", "Ren_full_body_waving"))}
        self.lib = rs.load_library()
        pad = 1400
        self.dev_pad = Image.new("RGBA", (full.width + 2 * pad, full.height + 2 * pad), (0, 0, 0, 0))
        self.dev_pad.paste(full, (pad, pad))
        self.pad = pad

    @staticmethod
    def _trim(im):
        a = np.array(im)[..., 3]
        ys, xs = np.where(a > 20)
        return im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))


def camera(img, cx, cy, z):
    """16:9 crop of a plate around (cx, cy) at zoom z (1 = whole plate), resized to the frame."""
    iw, ih = img.size
    cw, ch = iw / z, ih / z
    x0, y0 = min(max(cx - cw / 2, 0), iw - cw), min(max(cy - ch / 2, 0), ih - ch)
    return img.resize((W, H), Image.LANCZOS, box=(x0, y0, x0 + cw, y0 + ch)).convert("RGBA")


def view(img, anchor, dst, scale, pad=0):
    """Frame-sized view of `img` (optionally padded by `pad`) with src point `anchor` shown at `dst` at `scale`."""
    ax, ay = anchor[0] + pad, anchor[1] + pad
    box = (ax - dst[0] / scale, ay - dst[1] / scale, ax + (W - dst[0]) / scale, ay + (H - dst[1]) / scale)
    return img.resize((W, H), Image.LANCZOS, box=box)


def paste(frame, im, x, y):
    """alpha_composite with clipping."""
    x, y = int(round(x)), int(round(y))
    x0, y0 = max(0, -x), max(0, -y)
    x1, y1 = min(im.width, W - x), min(im.height, H - y)
    if x1 <= x0 or y1 <= y0:
        return
    frame.alpha_composite(im.crop((x0, y0, x1, y1)), (max(x, 0), max(y, 0)))


def shadow(frame, cx, y, w, alpha=70):
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse((cx - w / 2, y - 12, cx + w / 2, y + 14), fill=(19, 35, 63, alpha))
    frame.alpha_composite(sh.filter(ImageFilter.GaussianBlur(9)))


class Boxes:
    """Layout registry: text/graphics boxes and Ren's box per rendered frame, for the layout check."""
    def __init__(self):
        self.text, self.ren, self.face = [], None, None


# ------------------------------------------------------------------ placing Ren
def ren_still(frame, A, key, cx, bottom, h, boxes, push=0.0):
    im = A.ren[key]
    h = h * (1 + 0.07 * push)
    w = round(im.width * h / im.height)
    r = im.resize((w, round(h)), Image.LANCZOS)
    x, y = cx - w / 2, bottom - h
    paste(frame, r, x, y)
    boxes.ren = (x, y, x + w, y + h)
    boxes.face = (x + w * 0.22, y, x + w * 0.78, y + h * (0.42 if key in ("R1", "R2", "R3", "R4") else 0.18))
    return boxes.ren


class ClipRen:
    """A library clip (native 1280x720 frames, background removed) placed on the 1280x720 frame.
    Plays the real footage from `start` seconds for `seconds` with no idle filler and no automatic hold, cutting on the action."""
    S, CX, FEET = 0.92, 880, 705

    def __init__(self, A, clip, start, seconds):
        entry = A.lib[clip + ".mp4"]
        n = int(math.ceil(seconds * FPS))
        raw = subprocess.check_output(["ffmpeg", "-v", "error", "-ss", f"{start:.3f}", "-i", str(rs.LIB / entry["file"]), "-frames:v", str(n),
                                       "-vf", "fps=24,format=rgb24", "-f", "rawvideo", "-"])
        rgb = np.frombuffer(raw, np.uint8).reshape(-1, 720, 1280, 3)
        self.frames = [bp.cut_out(f) for f in rgb]
        self.n = len(self.frames)
        self.off = entry["x_offset_px"]
        self.note = f"{clip} {start:.2f}s +{self.n / FPS:.2f}s native 1280x720, no idle filler"
        assert self.n >= n - 1, (clip, self.n, n)

    def draw(self, frame, t, boxes):
        i = min(max(int(t * FPS), 0), self.n - 1)
        big = Image.fromarray(self.frames[i], "RGBA").resize((round(1280 * self.S), round(720 * self.S)), Image.LANCZOS)
        ox = round(self.CX - 600 * self.S + self.off * self.S)
        oy = round(self.FEET - 698 * self.S)
        shadow(frame, self.CX, self.FEET, 300)
        paste(frame, big, ox, oy)
        a = np.array(big)[..., 3]
        ys, xs = np.where(a > 128)
        boxes.ren = (ox + xs.min(), oy + ys.min(), ox + xs.max(), oy + ys.max())
        boxes.face = (boxes.ren[0] + 0.3 * (boxes.ren[2] - boxes.ren[0]), boxes.ren[1], boxes.ren[0] + 0.7 * (boxes.ren[2] - boxes.ren[0]), boxes.ren[1] + 0.2 * (boxes.ren[3] - boxes.ren[1]))


# ------------------------------------------------------------------ text, cards
def pill(frame, text, x, y, px=26, weight=700, fill=CREAM, colour=NAVY, alpha=1.0, boxes=None, outline=None, pad=(26, 14)):
    if alpha <= 0:
        return
    d0 = ImageDraw.Draw(layer())
    f = font(px, weight)
    b = d0.textbbox((0, 0), text, font=f)
    w, h = b[2] - b[0] + 2 * pad[0], b[3] - b[1] + 2 * pad[1]
    lay = layer()
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle((x + 3, y + 6, x + w + 3, y + h + 6), h // 2, fill=(19, 35, 63, 45))
    d.rounded_rectangle((x, y, x + w, y + h), h // 2, fill=(*fill, 255), outline=(*NAVY, 255) if outline else None, width=3)
    d.text((x + pad[0] - b[0], y + pad[1] - b[1]), text, font=f, fill=colour)
    if alpha < 1:
        lay.putalpha(lay.getchannel("A").point(lambda v: int(v * alpha)))
    frame.alpha_composite(lay)
    if boxes is not None:
        boxes.text.append((x, y, x + w, y + h, text))
    return (x, y, x + w, y + h)


def edu_tag(frame, t_abs, total, boxes):
    """Small low-key disclaimer lower-third at the start and at the end (not a banner)."""
    a = 1.0
    if t_abs < 5.0:
        a = min(bp.fade(t_abs, 0.4, 0.4), 1 - bp.fade(t_abs, 4.4, 0.5))
    elif t_abs > total - 4.0:
        a = bp.fade(t_abs, total - 3.8, 0.4)
    else:
        return
    pill(frame, EDU, 36, 664, px=19, weight=500, fill=CREAM, colour=NAVY, alpha=0.9 * max(a, 0), boxes=boxes, pad=(18, 8))


def info_card(frame, rows, t, boxes, cx=640, cy=330, appear=0.1):
    """The S2 card. rows = [(segments, row_start_time)]; segments = [(text, colour)]. Earlier rows are static."""
    f = font(52, 700)
    d0 = ImageDraw.Draw(layer())
    widths = [sum(d0.textlength(s, font=f) for s, _ in seg) for seg, _ in rows]
    cw = max(widths) + 90
    rh = 90
    ch = rh * len(rows) + 60
    x0, y0 = cx - cw / 2, cy - ch / 2
    lay = layer()
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle((x0 + 5, y0 + 10, x0 + cw + 5, y0 + ch + 10), 34, fill=(19, 35, 63, 55))
    d.rounded_rectangle((x0, y0, x0 + cw, y0 + ch), 34, fill=(*CREAM, 255), outline=(*SAGE, 255), width=5)
    if len(rows) == 1:                              # a new card fades in together with its first row
        ca = bp.fade(t, 0.0, 0.2)
        lay.putalpha(lay.getchannel("A").point(lambda v: int(v * ca)))
    frame.alpha_composite(lay)
    boxes.text.append((x0, y0, x0 + cw, y0 + ch, "card"))
    for i, (seg, ts) in enumerate(rows):
        a = bp.fade(t, ts, 0.3)
        if a <= 0:
            continue
        row = layer()
        rd = ImageDraw.Draw(row)
        x = x0 + 45
        y = y0 + 30 + i * rh + (1 - a) * 18
        for s, col in seg:
            rd.text((x, y), s, font=f, fill=col)
            x += rd.textlength(s, font=f)
        if a < 1:
            row.putalpha(row.getchannel("A").point(lambda v: int(v * a)))
        frame.alpha_composite(row)


def warp(src, quad):
    """Warp an RGBA image onto the 4-point quad (TL, TR, BR, BL) in frame coordinates."""
    w, h = src.size
    dst = quad
    s = [(0, 0), (w, 0), (w, h), (0, h)]
    A = []
    for (x, y), (u, v) in zip(dst, s):
        A += [[x, y, 1, 0, 0, 0, -u * x, -u * y], [0, 0, 0, x, y, 1, -v * x, -v * y]]
    coeff = np.linalg.solve(np.array(A, float), np.array([c for p in s for c in p], float))
    return src.transform((W, H), Image.PERSPECTIVE, tuple(coeff), Image.BICUBIC)


STUB = [(710, 254), (823, 271), (796, 412), (666, 401)]       # pay stub corners in Dev_pay_stub.png (TL, TR, BR, BL)


def stub_point(u, v):
    tl, tr, br, bl = STUB
    top = (lerp(tl[0], tr[0], u), lerp(tl[1], tr[1], u))
    bot = (lerp(bl[0], br[0], u), lerp(bl[1], br[1], u))
    return (lerp(top[0], bot[0], v), lerp(top[1], bot[1], v))


def glow_line(frame, A, anchor, dst, scale, text, pulse, glow, boxes):
    """Code-built glowing line drawn on the stub in the Dev close-up (warped onto the stub's own perspective)."""
    u0, u1, v0, v1 = 0.04, 0.97, 0.48, 0.64
    quad = []
    for u, v in ((u0, v0), (u1, v0), (u1, v1), (u0, v1)):
        px, py = stub_point(u, v)
        quad.append(((px - anchor[0]) * scale + dst[0], (py - anchor[1]) * scale + dst[1]))
    sw, sh = 520, 74
    s = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    d = ImageDraw.Draw(s)
    d.rounded_rectangle((0, 0, sw - 1, sh - 1), 16, fill=(255, 236, 150, 245), outline=(*GREEN, 255), width=5)
    f = font(46, 700)
    b = d.textbbox((0, 0), text, font=f)
    d.text(((sw - (b[2] - b[0])) / 2 - b[0], (sh - (b[3] - b[1])) / 2 - b[1]), text, font=f, fill=NAVY)
    cx = sum(p[0] for p in quad) / 4
    cy = sum(p[1] for p in quad) / 4
    quad = [(cx + (x - cx) * pulse, cy + (y - cy) * pulse) for x, y in quad]
    wl = warp(s, quad)
    if glow > 0:
        g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(g).polygon(quad, fill=(255, 226, 90, int(190 * glow)))
        frame.alpha_composite(g.filter(ImageFilter.GaussianBlur(22)))
    frame.alpha_composite(wl)
    boxes.text.append((min(p[0] for p in quad), min(p[1] for p in quad), max(p[0] for p in quad), max(p[1] for p in quad), text))


def flip(out_img, in_img, p):
    """Page peel: the outgoing page is revealed less and less from the right (never squeezed, so Ren keeps his proportions);
    a cream flap with a soft shadow curls over the fold and the incoming scene shows beneath."""
    p = min(max(p, 0), 1)
    base = in_img.copy()
    wpage = int(W * (1 - ease(p)))
    flap = int(min(W - wpage, 0.2 * W * math.sin(math.pi * p) ** 0.7))
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle((wpage, 0, min(W, wpage + flap + 70), H), fill=(19, 35, 63, int(110 * math.sin(math.pi * p))))
    base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(18)))
    if wpage > 0:
        base.alpha_composite(out_img.crop((0, 0, wpage, H)), (0, 0))
    if flap > 2:
        fl = Image.new("RGBA", (flap, H), (0, 0, 0, 0))
        fd = ImageDraw.Draw(fl)
        for x in range(flap):                       # the back of the page, lighter toward the free edge
            k = x / flap
            fd.line((x, 0, x, H), fill=(int(lerp(236, 251, k)), int(lerp(228, 246, k)), int(lerp(208, 234, k)), 255))
        base.alpha_composite(fl, (wpage, 0))
    return base


# ------------------------------------------------------------------ timeline from the real narration
def aligned_word_times(sid):
    """Per script word (whitespace-split): (start, end) seconds in the scene audio, from Whisper words by sequence alignment."""
    words = json.loads((VOICE / f"words_{sid}.json").read_text())
    text = pd.scene_text()[sid].split()

    def toks(s):
        s = s.lower().replace("’", "'").replace("-", " ").replace(",", "").replace("$", " $ ")
        return [t for t in re.findall(r"[a-z0-9']+", s) if t != "and"]

    st, sidx = [], []
    for i, w in enumerate(text):
        for t in toks(w) or ["·"]:
            st.append(t); sidx.append(i)
    wt, widx = [], []
    for j, w in enumerate(words):
        for t in toks(w["word"]) or ["·"]:
            wt.append(t); widx.append(j)
    sm = difflib.SequenceMatcher(None, st, wt, autojunk=False)
    start = [None] * len(text)
    end = [None] * len(text)
    for blk in sm.get_matching_blocks():
        for k in range(blk.size):
            i, j = sidx[blk.a + k], widx[blk.b + k]
            if start[i] is None:
                start[i] = words[j]["start"]
            end[i] = words[j]["end"]
    # interpolate script words that had no match
    known = [i for i, v in enumerate(start) if v is not None]
    for i in range(len(text)):
        if start[i] is None:
            lo = max([k for k in known if k < i], default=None)
            hi = min([k for k in known if k > i], default=None)
            a = end[lo] if lo is not None else 0.0
            b = start[hi] if hi is not None else words[-1]["end"]
            n_lo = lo if lo is not None else -1
            n_hi = hi if hi is not None else len(text)
            frac = (i - n_lo) / (n_hi - n_lo)
            start[i] = a + (b - a) * (frac - 0.5 / (n_hi - n_lo))
            end[i] = a + (b - a) * frac
    return list(zip(start, end))


def timeline():
    """List of shots with absolute start/end (s), from the real audio; plus total length and scene offsets."""
    shots, off, offs = [], 0.0, {}
    for sid in ("S1", "S2"):
        dur = sf.info(VOICE / f"{sid}.wav").duration
        wt = aligned_word_times(sid)
        k = 0
        rows = []
        for ph, typ, assets, ren, text, motion in pd.S[sid]:
            n = len(ph.split())
            rows.append((ph, typ, assets, ren, text, motion, wt[k][0], wt[k + n - 1][1]))
            k += n
        for i, r in enumerate(rows):
            start = 0.0 if i == 0 else r[6]
            end = dur if i == len(rows) - 1 else rows[i + 1][6]
            shots.append(dict(scene=sid, phrase=r[0], type=r[1], assets=r[2], ren=r[3], start=off + start, end=off + end, word_start=off + r[6], word_end=off + r[7]))
        offs[sid] = off
        off += dur
    q = lambda x: round(x * FPS) / FPS
    for k, sh in enumerate(shots):
        sh["start"], sh["end"] = q(sh["start"]), q(sh["end"])
    caps = {"ren": 5.5, "story": 2.5, "graphic": 3.5}
    for k, sh in enumerate(shots[:-1]):          # a cut that lands a frame or two over a cap is pulled in (<0.1 s from the voice)
        over = (sh["end"] - sh["start"]) - caps[sh["type"]]
        if 0 < over < 0.1:
            sh["end"] = shots[k + 1]["start"] = sh["start"] + caps[sh["type"]]
    return shots, off, offs


# ------------------------------------------------------------------ the 30 shots
class Pilot:
    def __init__(self):
        self.A = Assets()
        self.shots, self.audio_len, self.offs = timeline()
        for i, s in enumerate(self.shots):
            s["i"] = i + 1
        self.total = self.audio_len + 0.6          # short visual hold on the last frame after the last word
        self.shots[-1]["end"] = self.total
        A = self.A
        self.clips = {}
        for s in self.shots:
            if s["assets"].startswith("CLIP:"):
                name = {"NOD": "ren_nod_yes", "SNO": "ren_shake_no", "THK": "ren_thinking"}[s["assets"][5:]]
                self.clips[s["i"]] = ClipRen(A, name, 1.3, s["end"] - s["start"] + 0.1)
                print(s["i"], self.clips[s["i"]].note, flush=True)
        self.builders = self._builders()

    # --- helpers
    def ren_bg(self, t, d, z0=1.0, z1=1.04):
        return camera(self.A.plate["OFFICE"], 836, 470, lerp(z0, z1, t / d))

    def bust(self, key, t, d, boxes, cx=880):
        f = self.ren_bg(t, d)
        shadow(f, cx, H, 10, 0)
        ren_still(f, self.A, key, cx, H + 4, 640, boxes, push=t / d)
        return f

    def full(self, key, t, d, boxes, bgimg=None, cx=880, feet=700, h=590):
        f = bgimg if bgimg is not None else self.ren_bg(t, d)
        shadow(f, cx, feet, 280)
        ren_still(f, self.A, key, cx, feet, h, boxes, push=t / d * 0.4)
        return f

    def _builders(self):
        A = self.A
        B = {}
        cl = self.clips

        def porch_wide(t, d, b):
            return camera(A.plate["PORCH"], 1050, 470, lerp(1.0, 1.14, t / d))
        B[1] = porch_wide

        def two_shot(t, d, b):
            f = camera(A.plate["PORCH"], 836, 470, 1.0)
            dx = lerp(-260, 470, ease(t / 0.5))
            h = 590
            shadow(f, dx, 690, 280); shadow(f, 880, 690, 280)
            dv = A.dev.resize((round(A.dev.width * h / A.dev.height), h), Image.LANCZOS)
            paste(f, dv, dx - dv.width / 2, 690 - h)
            ren_still(f, A, "FS", 880, 690, h, b, push=0)
            return f
        B[2] = two_shot

        def dev_close(t, d, b):
            f = camera(A.plate["PORCH"], 900, 470, 1.25)
            hh = lerp(1050, 1110, t / d)
            dv = A.dev.resize((round(A.dev.width * hh / A.dev.height), round(hh)), Image.LANCZOS)
            x, y = 640 - dv.width / 2 + 90, 30
            paste(f, dv, x, y)
            b.face = (x + dv.width * 0.3, y, x + dv.width * 0.7, y + hh * 0.2)
            b.ren = None
            return f
        B[3] = dev_close

        B[4] = lambda t, d, b: self._quote(t, d, b)
        B[5] = lambda t, d, b: self.bust("R1", t, d, b)

        def stub_view(scale0, scale1, dst, glow_text=None, glow=0.0, pulse_t=None):
            def fn(t, d, b):
                sc = lerp(scale0, scale1, t / d)
                f = A.blur["PORCH"].convert("RGBA")
                anchor = (745, 335)
                f.alpha_composite(view(A.dev_pad, anchor, dst, sc, A.pad))
                if glow_text:
                    pulse = 1.0 + (0.07 * math.sin(math.pi * min(1, max(0, (t - pulse_t) / 0.5))) if pulse_t is not None else 0)
                    glow_line(f, A, anchor, dst, sc, glow_text, pulse, glow * (0.6 + 0.4 * math.sin(t * 6)), b)
                return f
            return fn
        B[6] = stub_view(1.9, 2.05, (600, 170))
        B[7] = stub_view(2.45, 2.6, (600, 205), "Employer match: 2%", 1.0, 0.25)
        B[8] = lambda t, d, b: self._clip(8, t, d, b)
        B[9] = lambda t, d, b: self.bust("R3", t, d, b)
        B[10] = lambda t, d, b: self.bust("R2", t, d, b)
        B[11] = lambda t, d, b: self.full("FP", t, d, b)

        # ---- S2
        def s2_1(t, d, b):
            f = self.full("FS", t, d, b, cx=860)
            pill(f, "Age 25", 60, 110, px=44, fill=NAVY, colour=(255, 255, 255), alpha=bp.fade(t, 0.15, 0.3), boxes=b, pad=(30, 12))
            return f
        B[12] = s2_1

        def card_shot(nrows, bg):
            def fn(t, d, b):
                f = A.blur[bg].convert("RGBA")
                rows = [([("Age 25: ", NAVY), ("$44,000 salary", GREEN)], 0.05),
                        ([("Lease: ", NAVY), ("$489/month", (196, 70, 60))], 0.05),
                        ([("Page 6: We match ", NAVY), ("100%", GREEN), (" up to ", NAVY), ("4%", GREEN)], 0.05)][:nrows]
                rows = [(seg, ts if k == nrows - 1 else -1) for k, (seg, ts) in enumerate(rows)]
                info_card(f, rows, t, b, cy=340)
                return f
            return fn
        B[13] = card_shot(1, "OFFICE")
        B[14] = lambda t, d, b: self._clip(14, t, d, b)
        B[15] = lambda t, d, b: self.bust("R3", t, d, b)
        B[16] = lambda t, d, b: camera(A.plate["LOT"], 1250, 560, lerp(1.0, 1.25, t / d))
        B[17] = card_shot(2, "LOT")
        B[18] = lambda t, d, b: self._clip(18, t, d, b)

        def lot_ren(t, d, b):
            f = camera(A.plate["LOT"], 836, 470, 1.0)
            shadow(f, 330, 690, 260)
            ren_still(f, A, "FS", 330, 690, 560, b, push=t / d * 0.3)
            return f
        B[19] = lot_ren
        B[20] = lambda t, d, b: self._clip(20, t, d, b)

        def day_one(t, d, b):
            f = self.ren_bg(t, d, 1.0, 1.06)
            pill(f, "Day one", 60, 110, px=44, fill=SAGE, colour=(255, 255, 255), alpha=bp.fade(t, 0.1, 0.3), boxes=b, pad=(30, 12))
            return f
        B[21] = day_one

        def folder_slide(t, d, b):
            f = A.blur["OFFICE"].convert("RGBA")
            w = 880
            fo = A.folder.resize((w, round(A.folder.height * w / A.folder.width)), Image.LANCZOS)
            x = lerp(1500, 640 - w / 2, ease(t / 0.45))
            sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(sh).rounded_rectangle((x + 20, 360 - fo.height / 2 + 28, x + w - 10, 360 + fo.height / 2 + 24), 40, fill=(19, 35, 63, 70))
            f.alpha_composite(sh.filter(ImageFilter.GaussianBlur(16)))
            paste(f, fo, x, 360 - fo.height / 2)
            return f
        B[22] = folder_slide

        def folder_crop(cx, cy, w0, w1):
            def fn(t, d, b):
                f = A.blur["OFFICE"].convert("RGBA")
                w = lerp(w0, w1, t / d)
                h = w * 9 / 16
                ax = min(max(cx, w / 2 + 1), A.folder.width - w / 2 - 1)        # keep the crop inside the prop
                ay = min(max(cy, h / 2 + 1), A.folder.height - h / 2 - 1)
                f.alpha_composite(view(A.folder, (ax, ay), (640, 360), W / w))
                return f
            return fn
        B[23] = folder_crop(1180, 210, 760, 620)           # PAGE 6 tab
        B[24] = self._match_diagram
        B[25] = folder_crop(1000, 455, 580, 500)            # piggy-bank panel
        B[26] = card_shot(3, "OFFICE")
        B[27] = lambda t, d, b: self.bust("R1", t, d, b)
        B[28] = self._chip
        B[29] = lambda t, d, b: self._clip(29, t, d, b)
        B[30] = lambda t, d, b: camera(A.plate["LOT"], 1150, 540, lerp(1.2, 1.0, t / d))
        return B

    def _quote(self, t, d, b):
        f = self.bust("R4", t, d, b)
        a = bp.fade(t, 0.15, 0.35)
        bp.text_card(f, [("“Who's keeping", 50, 700, NAVY), ("the difference?”", 50, 700, NAVY)], 70, 210, "la", pad=34, alpha=a)
        b.text.append((70, 210, 470, 400, "quote"))
        return f

    def _clip(self, idx, t, d, b):
        f = self.ren_bg(t, d, 1.0, 1.03)
        self.clips[idx].draw(f, t, b)
        return f

    def _match_diagram(self, t, d, b):
        f = self.A.blur["OFFICE"].convert("RGBA")
        lay = layer()
        dr = ImageDraw.Draw(lay)
        cw, chh = 940, 300
        x0, y0 = 170, 210
        dr.rounded_rectangle((x0 + 5, y0 + 10, x0 + cw + 5, y0 + chh + 10), 34, fill=(19, 35, 63, 55))
        dr.rounded_rectangle((x0, y0, x0 + cw, y0 + chh), 34, fill=(*CREAM, 255), outline=(*SAGE, 255), width=5)
        ca = bp.fade(t, 0.0, 0.2)
        lay.putalpha(lay.getchannel("A").point(lambda v: int(v * ca)))
        f.alpha_composite(lay)
        b.text.append((x0, y0, x0 + cw, y0 + chh, "diagram"))
        for k, (label, cx, ts) in enumerate((("You  $1", 400, 0.05), ("Company  $1", 880, 0.7))):
            a = bp.fade(t, ts, 0.3)
            if a <= 0:
                continue
            s = 1 + 0.12 * math.sin(math.pi * min(1, max(0, (t - ts) / 0.3)))
            c = layer()
            cd = ImageDraw.Draw(c)
            r = int(70 * s)
            col = (255, 196, 40) if k == 0 else (*SAGE,)
            cd.ellipse((cx - r, 300 - r, cx + r, 300 + r), fill=(*col, 255), outline=(*NAVY, 255), width=5)
            cd.text((cx, 300), "$", font=font(int(84 * s), 700), fill=NAVY, anchor="mm")
            cd.text((cx, 420), label, font=font(46, 700), fill=NAVY, anchor="mm")
            c.putalpha(c.getchannel("A").point(lambda v: int(v * a)))
            f.alpha_composite(c)
        a = bp.fade(t, 0.45, 0.3)
        if a > 0:
            ar = layer()
            ad = ImageDraw.Draw(ar)
            ad.line((500, 300, 760, 300), fill=(*NAVY, 255), width=9)
            ad.polygon([(790, 300), (755, 275), (755, 325)], fill=(*NAVY, 255))
            ar.putalpha(ar.getchannel("A").point(lambda v: int(v * a)))
            f.alpha_composite(ar)
        return f

    def _chip(self, t, d, b):
        f = self.A.blur["OFFICE"].convert("RGBA")
        lay = layer()
        dr = ImageDraw.Draw(lay)
        s = bp.ease(min(1, t / 0.3)) * (1 + 0.1 * math.sin(math.pi * min(1, t / 0.4)))
        # ghost 4%
        dr.rounded_rectangle((690, 270, 940, 440), 85, outline=(*MUTED, 200), width=6)
        dr.text((815, 355), "4%", font=font(110, 700), fill=(*MUTED, 200), anchor="mm")
        dr.text((815, 245), "the full match", font=font(34, 600), fill=(*MUTED, 255), anchor="mm")
        f.alpha_composite(lay)
        chip = layer()
        cd = ImageDraw.Draw(chip)
        cd.rounded_rectangle((330, 255, 620, 455), 100, fill=(*NAVY, 255))
        cd.text((475, 355), "2%", font=font(140, 700), fill=(255, 255, 255), anchor="mm")
        cd.text((475, 230), "what I picked", font=font(34, 600), fill=(*NAVY, 255), anchor="mm")
        chip = chip.transform((W, H), Image.AFFINE, (1 / max(s, 0.01), 0, 475 - 475 / max(s, 0.01), 0, 1 / max(s, 0.01), 355 - 355 / max(s, 0.01)), Image.BICUBIC)
        if s > 0.06:
            f.alpha_composite(chip)
        b.text.append((330, 230, 940, 455, "chip"))
        return f

    # --- frames
    def frame_at(self, T):
        T = min(T, self.total - 1 / FPS)
        sh = next(s for s in self.shots if s["start"] <= T < s["end"] + 1e-9) if T < self.total else self.shots[-1]
        boxes = Boxes()
        f = self.builders[sh["i"]](T - sh["start"], sh["end"] - sh["start"], boxes)
        f = f.convert("RGBA")
        # page flip S1 -> S2 over the last 0.7 s of S1
        b1 = self.offs["S2"]
        if b1 - 0.7 <= T < b1:
            first = self.shots[11]
            boxes2 = Boxes()
            inc = self.builders[first["i"]](0.0, first["end"] - first["start"], boxes2).convert("RGBA")
            f = flip(f, inc, (T - (b1 - 0.7)) / 0.7)
        edu_tag(f, T, self.total, boxes)
        return f.convert("RGB"), boxes, sh


def layout_problems(boxes, sh):
    out = []
    for (x0, y0, x1, y1, name) in boxes.text:
        if name == EDU:
            continue
        if x0 < 20 or y0 < 20 or x1 > W - 20 or y1 > H - 20:
            out.append(f"shot {sh['i']}: '{name}' outside the safe area ({x0:.0f},{y0:.0f},{x1:.0f},{y1:.0f})")
        for r, label in ((boxes.face, "face"), (boxes.ren, "Ren")):
            if r and name not in ("diagram",) and not (x1 < r[0] or x0 > r[2] or y1 < r[1] or y0 > r[3]):
                out.append(f"shot {sh['i']}: '{name}' overlaps {label}")
    return out


def lufs(path):
    p = subprocess.run(["ffmpeg", "-nostats", "-i", str(path), "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
    i = p.rindex("I:")
    return float(p[i + 2:].split()[0]), float(p[p.rindex("Peak:") + 5:].split()[0])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(HERE / "renders"))
    ap.add_argument("--stills", action="store_true")
    ap.add_argument("--name", default="free_money_S1_S2_pilot")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    P = Pilot()
    print(f"{len(P.shots)} shots, total {P.total:.2f}s ({P.audio_len:.2f}s narration)", flush=True)
    caps = {"ren": 5.5, "story": 2.5, "graphic": 3.5}
    over = [(s["i"], s["type"], round(s["end"] - s["start"], 2)) for s in P.shots if s["end"] - s["start"] > caps[s["type"]]]
    print("shots over the v3 cap:", over or "none", flush=True)
    if args.stills:
        d = out / "stills"
        d.mkdir(exist_ok=True)
        probs = []
        for s in P.shots:
            for tag, frac in (("a", 0.12), ("b", 0.5), ("c", 0.92)):
                T = s["start"] + (s["end"] - s["start"]) * frac
                f, boxes, sh = P.frame_at(T)
                f.save(d / f"shot{s['i']:02d}{tag}.png")
                if tag == "b":
                    probs += layout_problems(boxes, sh)
        print("layout problems:", probs or "none")
        return
    # audio: S1 then S2 exactly as generated, then silence for the hold; gain to -16 LUFS, limited
    sr = 24000
    a1, r1 = sf.read(VOICE / "S1.wav", dtype="float32")
    a2, r2 = sf.read(VOICE / "S2.wav", dtype="float32")
    assert r1 == r2 == sr
    track = np.concatenate([a1, a2, np.zeros(int(0.6 * sr), np.float32)])
    raw = out / "pilot_voice_raw.wav"
    sf.write(raw, track, sr)
    i0, _ = lufs(raw)
    wav = out / "pilot_voice.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af", f"volume={-16 - i0:.2f}dB,alimiter=limit=0.8:level=false,aresample=48000", str(wav)], check=True)
    video = out / f"{args.name}_video.mp4"
    n = int(round(P.total * FPS))
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(video)], stdin=subprocess.PIPE)
    probs = []
    for k in range(n):
        f, boxes, sh = P.frame_at(k / FPS)
        if k % 6 == 0:
            probs += layout_problems(boxes, sh)
        enc.stdin.write(np.asarray(f, np.uint8).tobytes())
        if k % 120 == 0:
            print(f"frame {k}/{n}", flush=True)
    enc.stdin.close()
    enc.wait()
    final = out / f"{args.name}.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-i", str(wav), "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-ar", "48000", "-t", f"{P.total:.3f}", "-movflags", "+faststart", str(final)], check=True)
    I, pk = lufs(final)
    rep = {"frames": n, "duration_s": round(P.total, 3), "narration_s": round(P.audio_len, 3), "lufs": I, "true_peak_dbtp": pk, "layout_problems": probs, "over_cap": over,
           "shots": [{k: (round(v, 3) if isinstance(v, float) else v) for k, v in s.items()} for s in P.shots]}
    (out / f"{args.name}_report.json").write_text(json.dumps(rep, indent=1, ensure_ascii=False))
    print(json.dumps({k: rep[k] for k in ("frames", "duration_s", "lufs", "true_peak_dbtp", "layout_problems", "over_cap")}))


if __name__ == "__main__":
    main()
