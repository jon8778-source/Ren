"""Build the 15-second vertical short "My Job Offered Free Money. I Said No." (1080x1920, 30 fps).

  project/.tools/venv/bin/python videos/job_match_short/build_short.py [--out videos/job_match_short/renders]

Reuses: the approved Ren clip library (via videos/postponing_life/build_pilot.RenShot, which plans each
shot with the library's neutral-frame rules and cuts Ren out of his near-white backdrop), the Fredoka
font, and Ren's Qwen3-TTS cloned voice (voice/L1..L6.wav from gen_voice.py). Everything else on screen
(keys, folder, chip, ghost jar, phone UI, badges, captions, disclaimer) is drawn here in code.
The background is pure white (255,255,255) in every frame.
"""
import argparse
import json
import math
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "postponing_life"))
import build_pilot as bp  # noqa: E402
import render_shots as rs  # noqa: E402

W, H, FPS = 1080, 1920, 30
SRC_FPS = 24
NAVY, GREEN, RED, MUTED = (19, 35, 63), (30, 158, 90), (214, 48, 49), (122, 132, 150)
SAFE_TOP, SAFE_BOTTOM, RIGHT_CLEAR = 150, 1500, 130
REN_SCALE, FEET_Y, REN_CX = 1.45, 1235, 330      # Ren ~960px tall, feet at y=1235, body centred at x=330
SRC_FEET, SRC_BODY_X = 698, 600
DISCLAIMER = "Example only, not financial advice. Based on a $44k salary."
VOICE = HERE / "voice"
GAP, LEAD, HOLD_END, XF = 0.14, 0.12, 0.5, 0.25
font = bp.font
ease = bp.ease


def rgba(c, a=255):
    return (*c, a)


def pulse(t, t0, dur=0.5, amp=0.22):
    """One bump of scale 1 -> 1+amp -> 1 starting at t0."""
    x = (t - t0) / dur
    return 1 + amp * math.sin(math.pi * x) if 0 <= x <= 1 else 1.0


def pop(t, t0, dur=0.28):
    """Overshoot pop-in scale, 0 before t0."""
    x = (t - t0) / dur
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    return ease(x) * (1 + 0.18 * math.sin(math.pi * x))


# --------------------------------------------------------------------------- narration timeline
def narration():
    info = json.loads((VOICE / "lines.json").read_text())
    words = json.loads((VOICE / "word_times.json").read_text())
    L, t = {}, LEAD
    for lid in info:
        d = sf.info(VOICE / f"{lid}.wav").duration
        L[lid] = {"start": t, "end": t + d, "text": info[lid]["text"]}
        t += d + GAP
    return L, words


# --------------------------------------------------------------------------- Ren
class Ren:
    """One library clip placed on the vertical canvas; frame(t) -> RGBA layer, hand(t) -> hand position."""

    def __init__(self, lib, clip, seconds, mirror=False, end_on=None, hand_region=None):
        self.shot = bp.RenShot(lib, clip, seconds, mirror=mirror, end_on=end_on)
        print(clip, self.shot.note, flush=True)
        self.n = len(self.shot.frames)
        self.hand_region = hand_region
        self.hands = [self._hand(i) for i in range(self.n)] if hand_region else None

    def _hand(self, i):
        x0, y0, x1, y1 = self.hand_region
        fr = self.shot.frames[i]
        r, g, b, a = (fr[y0:y1, x0:x1, c].astype(int) for c in range(4))
        skin = (a > 128) & (r > 190) & (r - b > 40) & (r > g) & (g > b)
        ys, xs = np.nonzero(skin)
        if len(xs) < 30:
            return None
        return x0 + xs.mean(), y0 + ys.mean()

    def frame(self, t):
        i = min(max(int(t * SRC_FPS), 0), self.n - 1)
        big = Image.fromarray(self.shot.frames[i], "RGBA").resize((round(1280 * REN_SCALE), round(720 * REN_SCALE)), Image.LANCZOS)
        shift = self.shot.shifts[i] / 1.5          # RenShot's per-clip x offset, in 1280-wide clip pixels
        ox = round(REN_CX - SRC_BODY_X * REN_SCALE + (shift + 293) * REN_SCALE)   # shift = -293 + library x_offset
        oy = round(FEET_Y - SRC_FEET * REN_SCALE)
        out = layer()
        cx0, cy0 = max(0, -ox), max(0, -oy)
        crop = big.crop((cx0, cy0, min(big.width, W - ox), min(big.height, H - oy)))
        out.paste(crop, (max(ox, 0), max(oy, 0)))
        return out

    def hand(self, t):
        if not self.hands:
            return None
        i = min(max(int(t * SRC_FPS), 0), self.n - 1)
        h = self.hands[i] or next((x for x in self.hands[i:] + self.hands[:i][::-1] if x), None)
        if h is None:
            return None
        shift = self.shot.shifts[i] / 1.5
        return (REN_CX - SRC_BODY_X * REN_SCALE + (h[0] + shift + 293) * REN_SCALE, FEET_Y - (SRC_FEET - h[1]) * REN_SCALE)


# --------------------------------------------------------------------------- coded graphics
def layer():
    return Image.new("RGBA", (W, H), (255, 255, 255, 0))


def shadow(d_img, box, r, alpha=38):
    sh = Image.new("RGBA", d_img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((box[0] + 4, box[1] + 10, box[2] + 4, box[3] + 10), r, fill=(*NAVY, alpha))
    d_img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)))


def scaled(img, centre, s, alpha=1.0, rot=0.0):
    """Scale/rotate a full-canvas RGBA layer about `centre` (returns a new full-canvas layer)."""
    if s <= 0 or alpha <= 0:
        return layer()
    cx, cy = centre
    out = img
    if rot:
        out = out.rotate(rot, resample=Image.BICUBIC, center=(cx, cy))
    if abs(s - 1) > 1e-3:
        w, h = out.size
        out = out.transform((w, h), Image.AFFINE, (1 / s, 0, cx - cx / s, 0, 1 / s, cy - cy / s), Image.BICUBIC)
    if alpha < 1:
        out.putalpha(out.getchannel("A").point(lambda v: int(v * alpha)))
    return out


def sparkle(cx, cy, r, a=1.0):
    img = layer()
    d = ImageDraw.Draw(img)
    c = (255, 255, 255, int(255 * a))
    edge = (255, 196, 40, int(255 * a))
    pts = [(cx, cy - r), (cx + r * .22, cy - r * .22), (cx + r, cy), (cx + r * .22, cy + r * .22),
           (cx, cy + r), (cx - r * .22, cy + r * .22), (cx - r, cy), (cx - r * .22, cy - r * .22)]
    d.polygon(pts, fill=edge)
    s2 = [(cx + (x - cx) * .55, cy + (y - cy) * .55) for x, y in pts]
    d.polygon(s2, fill=c)
    return img


def keys_layer(cx, cy, swing=0.0):
    """Car-key fob and a ring, hanging from a hand at (cx, cy)."""
    img = layer()
    d = ImageDraw.Draw(img)
    d.ellipse((cx - 22, cy - 6, cx + 22, cy + 38), outline=(120, 128, 140), width=6)      # ring
    # key blade
    d.rounded_rectangle((cx - 40, cy + 40, cx - 14, cy + 112), 8, fill=(196, 202, 212), outline=(120, 128, 140), width=3)
    d.rectangle((cx - 28, cy + 92, cx - 14, cy + 99), fill=(120, 128, 140))
    # fob: navy body with gold highlight
    d.rounded_rectangle((cx - 2, cy + 34, cx + 56, cy + 128), 22, fill=NAVY, outline=(255, 196, 40), width=4)
    d.ellipse((cx + 14, cy + 58, cx + 40, cy + 84), fill=(255, 196, 40))
    d.arc((cx + 6, cy + 42, cx + 48, cy + 116), 200, 280, fill=(255, 255, 255), width=4)  # shine
    return img.rotate(swing, resample=Image.BICUBIC, center=(cx, cy))


def age_tag(x, y):
    img = layer()
    d = ImageDraw.Draw(img)
    f = font(54, 700)
    t = "Age 25"
    b = d.textbbox((0, 0), t, font=f)
    w = b[2] - b[0] + 56
    box = (x, y, x + w, y + 92)
    shadow(img, box, 46)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle(box, 46, fill=(255, 255, 255), outline=NAVY, width=5)
    d.text((x + 28 - b[0], y + 14 - b[1] * 0 - 2), t, font=f, fill=NAVY)
    return img


def folder_layer(x, y, hl):
    """HR folder with 'Match up to 4%'; `hl` 0..1 highlights 4% in green."""
    img = layer()
    w, h = 470, 360
    shadow(img, (x, y, x + w, y + h), 28)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((x, y - 46, x + 190, y + 30), 22, fill=(233, 190, 90))              # tab
    d.rounded_rectangle((x, y, x + w, y + h), 28, fill=(244, 205, 108), outline=(207, 160, 60), width=4)
    d.text((x + 22, y - 36), "HR", font=font(44, 700), fill=NAVY)
    lines = [("Match", 62), ("up to", 62)]
    d.text((x + 36, y + 56), "Match up to", font=font(64, 700), fill=NAVY)
    col = tuple(int(NAVY[i] + (GREEN[i] - NAVY[i]) * hl) for i in range(3))
    f = font(128, 700)
    t = "4%"
    b = d.textbbox((0, 0), t, font=f)
    if hl > 0.01:
        d.rounded_rectangle((x + 30, y + 150, x + 30 + (b[2] - b[0]) + 40, y + 150 + 150), 30,
                            fill=(255, 255, 255, int(235 * hl)))
    d.text((x + 50 - b[0], y + 142 - b[1] * 0), t, font=f, fill=col)
    return img


def chip_layer(x, y, label="2%", sub="I put in"):
    img = layer()
    d = ImageDraw.Draw(img)
    f = font(112, 700)
    b = d.textbbox((0, 0), label, font=f)
    w, h = b[2] - b[0] + 90, 168
    shadow(img, (x, y, x + w, y + h), 84)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((x, y, x + w, y + h), 84, fill=(255, 255, 255), outline=NAVY, width=6)
    d.text((x + 45 - b[0], y + 18 - b[1] * 0), label, font=f, fill=NAVY)
    d.text((x + 8, y - 54), sub, font=font(42, 600), fill=MUTED)
    return img


def jar_layer(cx, cy, fill, pulse_s, ink_a=1.0):
    """Translucent 'ghost jar' of coins; fill 1 = full, 0 = empty. Label '-$880/yr' in red."""
    img = layer()
    d = ImageDraw.Draw(img)
    jw, jh = 300, 400
    x0, y0 = cx - jw // 2, cy - jh // 2
    glass = (150, 175, 205)
    d.rounded_rectangle((x0, y0, x0 + jw, y0 + jh), 54, fill=(190, 210, 235, 70), outline=(*glass, 190), width=6)
    d.rounded_rectangle((x0 + 30, y0 - 34, x0 + jw - 30, y0 + 8), 14, fill=(*glass, 200))          # lid
    level = y0 + jh - 14 - fill * (jh - 40)
    if fill > 0.02:
        m = Image.new("L", img.size, 0)
        ImageDraw.Draw(m).rounded_rectangle((x0 + 8, y0 + 8, x0 + jw - 8, y0 + jh - 8), 48, fill=255)
        coins = layer()
        cd = ImageDraw.Draw(coins)
        cd.rectangle((x0, level, x0 + jw, y0 + jh), fill=(255, 205, 70, 120))
        n = int(fill * 12)
        for k in range(n):
            ccx = x0 + 60 + (k % 3) * 90
            ccy = y0 + jh - 50 - (k // 3) * 60
            if ccy > level + 12:
                cd.ellipse((ccx - 34, ccy - 22, ccx + 34, ccy + 22), fill=(255, 196, 40, 170), outline=(214, 150, 20, 200), width=4)
        coins.putalpha(Image.fromarray(np.minimum(np.array(coins.getchannel("A")), np.array(m))))
        img.alpha_composite(coins)
    d = ImageDraw.Draw(img)
    f = font(int(66 * pulse_s), 700)
    t = "-$880/yr"
    b = d.textbbox((0, 0), t, font=f)
    tw = b[2] - b[0]
    ty = y0 + jh + 26
    d.text((cx - tw / 2 - b[0], ty), t, font=f, fill=(*RED, int(255 * ink_a)))
    return img


def phone_layer(x, y, toggle, badge_s):
    """Coded phone with a settings screen: 'Contribution' toggle sliding 2% -> 4% (toggle 0..1)."""
    img = layer()
    w, h = 400, 740
    shadow(img, (x, y, x + w, y + h), 56)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((x, y, x + w, y + h), 56, fill=(24, 30, 44))
    sx0, sy0, sx1, sy1 = x + 16, y + 18, x + w - 16, y + h - 18
    d.rounded_rectangle((sx0, sy0, sx1, sy1), 42, fill=(255, 255, 255))
    d.rounded_rectangle((x + w / 2 - 50, y + 26, x + w / 2 + 50, y + 44), 9, fill=(24, 30, 44))
    d.text((sx0 + 28, sy0 + 62), "Settings", font=font(44, 700), fill=NAVY)
    d.text((sx0 + 28, sy0 + 130), "401(k) match", font=font(34, 600), fill=MUTED)
    # contribution card
    cy0 = sy0 + 190
    d.rounded_rectangle((sx0 + 20, cy0, sx1 - 20, cy0 + 270), 28, fill=(240, 244, 250))
    d.text((sx0 + 44, cy0 + 22), "My contribution", font=font(32, 600), fill=NAVY)
    v = ease(toggle)
    pct = "4%" if v > 0.5 else "2%"
    col = tuple(int(NAVY[i] + (GREEN[i] - NAVY[i]) * v) for i in range(3))
    f = font(104, 700)
    d.text((sx0 + 44, cy0 + 66), pct, font=f, fill=col)
    # toggle track
    tx0, ty0, tw_, th_ = sx0 + 44, cy0 + 196, 268, 48
    track = tuple(int(200 + (GREEN[i] - 200) * v) for i in range(3))
    d.rounded_rectangle((tx0, ty0, tx0 + tw_, ty0 + th_), 24, fill=track)
    kx = tx0 + 24 + v * (tw_ - 48)
    d.ellipse((kx - 21, ty0 + 3, kx + 21, ty0 + th_ - 3), fill=(255, 255, 255), outline=(150, 156, 170), width=2)
    d.text((tx0, ty0 + 56), "2%", font=font(28, 600), fill=MUTED)
    d.text((tx0 + tw_ - 40, ty0 + 56), "4%", font=font(28, 600), fill=MUTED)
    # employer match line
    d.text((sx0 + 44, cy0 + 300), "Full match", font=font(32, 600), fill=MUTED)
    if v > 0.98:
        d.text((sx0 + 44, cy0 + 344), "unlocked", font=font(52, 700), fill=GREEN)
    return img


def badge_layer(cx, cy, s):
    img = layer()
    d = ImageDraw.Draw(img)
    r = 128
    d.ellipse((cx - r + 5, cy - r + 11, cx + r + 5, cy + r + 11), fill=(*NAVY, 40))
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=GREEN)
    d.text((cx, cy - 34), "90", font=font(124, 700), fill=(255, 255, 255), anchor="mm")
    d.text((cx, cy + 62), "seconds", font=font(54, 700), fill=(255, 255, 255), anchor="mm")
    return scaled(img, (cx, cy), s)


def story_card(x0, y0):
    """Bold 'Story / Friday' headline card (top-left at x0, y0) with a 'Part 2' teaser tag on its corner."""
    img = layer()
    d = ImageDraw.Draw(img)
    f = font(106, 700)
    wmax = max(d.textlength("Story", font=f), d.textlength("Friday", font=f))
    pad = 40
    box = (x0, y0, x0 + wmax + 2 * pad, y0 + 2 * 128 + 2 * pad - 24)
    shadow(img, box, 40)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle(box, 40, fill=NAVY)
    d.text((box[0] + pad, box[1] + pad - 14), "Story", font=f, fill=(255, 255, 255))
    d.text((box[0] + pad, box[1] + pad + 112), "Friday", font=f, fill=(255, 255, 255))
    tag = (box[0] + 18, box[1] - 62, box[0] + 18 + 180, box[1] + 6)
    d.rounded_rectangle(tag, 34, fill=GREEN)
    d.text(((tag[0] + tag[2]) / 2, (tag[1] + tag[3]) / 2), "Part 2", font=font(42, 700), fill=(255, 255, 255), anchor="mm")
    return img


def disclaimer_layer():
    img = layer()
    d = ImageDraw.Draw(img)
    f = font(26, 500)
    d.text((W / 2, 1752), DISCLAIMER, font=f, fill=(176, 182, 194), anchor="mm")
    return img


# --------------------------------------------------------------------------- captions
def caption_tokens(L, words):
    """[(display_word, start_s, end_s, line_id)] using whisper word times; display forms follow the script."""
    disp = {
        "L1": ["At", "25,", "my", "job", "matched", "up", "to", "4%."],
        "L2": ["I", "put", "in", "2,", "because", "my", "car", "lease", "felt", "urgent."],
        "L3": ["That's", "about", "$880", "a", "year", "of", "free", "money,", "gone."],
        "L4": ["Check", "your", "match", "tonight."],
        "L5": ["It", "takes", "90", "seconds."],
        "L6": ["Story", "Friday."],
    }
    # how many spoken words each display token covers (so whisper's word list maps onto it)
    span = {}   # whisper writes numerals, so every display token is exactly one whisper word
    out = []
    for lid, toks in disp.items():
        ws = words[lid]
        base = L[lid]["start"]
        sp = span.get(lid, [1] * len(toks))
        k = 0
        for tok, n in zip(toks, sp):
            seg = ws[k:k + n] if k < len(ws) else ws[-1:]
            if not seg:
                seg = ws[-1:]
            out.append((tok, base + seg[0]["start"], base + seg[-1]["end"], lid))
            k += n
    return out


def caption_layer(t, toks):
    """Word-by-word: the words of the current phrase (up to 3) appear as they are spoken, the live word in green."""
    live = None
    for i, (_, s, e, _) in enumerate(toks):
        if s - 0.02 <= t:
            live = i
    img = layer()
    if live is None:
        return img
    tok = toks[live]
    if t > tok[2] + 0.45 and live == len(toks) - 1 and False:
        return img
    # phrase = consecutive tokens in the same line, grouped in threes
    same = [i for i, x in enumerate(toks) if x[3] == tok[3]]
    pos = same.index(live)
    gstart = same[(pos // 3) * 3]
    group = [i for i in same if gstart <= i < gstart + 3 and i <= live]
    d = ImageDraw.Draw(img)
    full = [i for i in same if gstart <= i < gstart + 3]
    px, spc = 104, 26
    while True:   # shrink the phrase until it fits inside the safe width (right 130px kept clear)
        f = font(px, 700)
        if sum(d.textlength(toks[i][0], font=f) for i in full) + spc * (len(full) - 1) <= W - 60 - RIGHT_CLEAR - 60:
            break
        px -= 4
    fw = [d.textlength(toks[i][0], font=f) for i in full]
    ftotal = sum(fw) + spc * (len(fw) - 1)
    x = (W - RIGHT_CLEAR - ftotal) / 2 + 0
    y = 1330
    for i, w_ in zip(full, fw):
        if i <= live:
            col = GREEN if i == live else NAVY
            sc = pop(t, toks[i][1], 0.14) if i == live else 1.0
            s = 1 + 0.12 * (1 - min(1, max(0, (t - toks[i][1]) / 0.16))) if i == live else 1.0
            word = Image.new("RGBA", (int(w_ + 40), 150), (255, 255, 255, 0))
            ImageDraw.Draw(word).text((20, 20), toks[i][0], font=f, fill=col, stroke_width=0)
            if s != 1:
                nw = word.resize((int(word.width * s), int(word.height * s)), Image.LANCZOS)
                img.alpha_composite(nw, (int(x - 20 - (nw.width - word.width) / 2), int(y - 20 - (nw.height - word.height) / 2)))
            else:
                img.alpha_composite(word, (int(x - 20), int(y - 20)))
        x += w_ + spc
    return img




# --------------------------------------------------------------------------- scene composition
def word_time(L, words, lid, spoken, nth=0):
    """Absolute start time of the nth whisper word in line `lid` whose text starts with `spoken`."""
    hits = [w for w in words[lid] if w["word"].lower().strip(",.?!'\"").startswith(spoken)]
    return L[lid]["start"] + hits[nth]["start"]


class Short:
    def __init__(self):
        self.L, self.words = narration()
        L, words = self.L, self.words
        self.toks = caption_tokens(L, words)
        w1 = words["L1"]
        my_t = L["L1"]["start"] + next(x["start"] for x in w1 if x["word"].lower().strip(",.") == "my") - 0.06
        self.b = [0.0, my_t, L["L2"]["start"] - 0.04, L["L3"]["end"] + 0.3, L["L5"]["end"] + 0.15]
        self.total = L["L6"]["end"] + HOLD_END
        self.b.append(self.total)
        lib = rs.load_library()
        spans = [self.b[i + 1] - self.b[i] + XF + 0.3 for i in range(5)]
        hand = (440, 330, 600, 480)
        self.ren = [
            Ren(lib, "ren_idle_calm", spans[0], hand_region=hand),
            Ren(lib, "ren_idle_calm", spans[1], hand_region=hand),
            Ren(lib, "ren_point_down_right", spans[2], hand_region=hand),
            Ren(lib, "ren_point_right", spans[3]),
            Ren(lib, "ren_wave_hello", spans[4], end_on=1.55 + spans[4]),   # start with the hand already rising
        ]
        T = lambda lid, w, n=0: word_time(L, words, lid, w, n)
        self.t_four = T("L1", "4")
        self.t_two = T("L2", "two") if any(x["word"].lower().startswith("two") for x in words["L2"]) else L["L2"]["start"] + 0.5
        self.t_880 = T("L3", "$880")
        self.t_gone = T("L3", "gone")
        self.t_match = T("L4", "match")
        self.t_ninety = T("L5", "90")
        self.disc = disclaimer_layer()
        self.hand_cache = {}

    # ---- the five scenes (return an RGBA layer, no caption/disclaimer)
    def scene(self, k, t):
        a = self.b[k]
        lt = max(0.0, t - a)
        base = layer()
        ren = self.ren[k]
        if k in (0, 1, 2):
            base.alpha_composite(ren.frame(lt))
            h = ren.hand(lt)
            swing = 0.0
            if h:
                if k == 2:
                    swing = 9 * math.sin((t - a) * 14)            # rushed: keys jiggle faster
                else:
                    swing = 3.5 * math.sin((t - a) * 3.2)
                base.alpha_composite(scaled(keys_layer(h[0], h[1] - 22, swing), (h[0], h[1] - 22), 1.5))
                tw = t * 5.5
                for dx, dy, ph, r in ((34, 66, 0.0, 26), (-2, 120, 2.1, 20), (58, 100, 4.0, 16)):
                    a_ = max(0.0, math.sin(tw + ph)) ** 2
                    if a_ > 0.02:
                        base.alpha_composite(sparkle(h[0] + dx * 1.5, h[1] - 22 + dy * 1.5, r * 1.3 * (0.5 + 0.5 * a_), a_))
        if k == 0:
            base.alpha_composite(scaled(age_tag(500, 330), (610, 376), pop(lt, 0.1)))
        elif k == 1:
            x = 505 + 520 * (1 - ease(lt / 0.32))
            hl = ease((t - self.t_four) / 0.25)
            fs = 0.85 * (1 + 0.06 * math.sin(math.pi * min(1, max(0, (t - self.t_four) / 0.4))) if t > self.t_four else 1)
            base.alpha_composite(scaled(folder_layer(int(x), 660, hl), (int(x) + 235, 840), fs))
        elif k == 2:
            base.alpha_composite(scaled(chip_layer(690, 880), (810, 964), pop(t, self.t_two - 0.05)))
            if t > self.L["L3"]["start"] - 0.05:
                fade_in = ease((t - self.L["L3"]["start"] + 0.05) / 0.35)
                drain = ease((t - self.t_gone) / (self.b[3] - self.t_gone))
                ps = pulse(t, self.t_880, 0.55, 0.28)
                jar = jar_layer(775, 430, 1 - drain, ps, 1 - 0.8 * drain)
                base.alpha_composite(scaled(jar, (775, 430), 1.0, fade_in * (1 - 0.85 * drain), rot=0))
        elif k == 3:
            tog = ease((t - self.t_match) / 0.45)
            ph = scaled(phone_layer(560, 500, tog, 0), (770, 870), 0.88)
            base.alpha_composite(ph)
            base.alpha_composite(ren.frame(lt))
            bs = pop(t, self.t_ninety - 0.05, 0.3)
            if bs > 0:
                base.alpha_composite(badge_layer(815, 385, bs * 0.9))
        elif k == 4:
            base.alpha_composite(ren.frame(lt))
            base.alpha_composite(scaled(story_card(550, 580), (740, 700), pop(lt, 0.08, 0.3)))
        return base

    def frame(self, t):
        t = min(t, self.total - HOLD_END)       # hold the final frame for the last 0.5 s
        tt = t
        # which scene(s)? slide transition centred on each boundary
        k = max(i for i in range(5) if tt >= self.b[i] - XF / 2) if tt >= self.b[0] else 0
        canvas = Image.new("RGBA", (W, H), (255, 255, 255, 255))
        nxt = k + 1
        if nxt < 5 and tt > self.b[nxt] - XF / 2:
            e = ease((tt - (self.b[nxt] - XF / 2)) / XF)
            canvas.alpha_composite(shift_x(self.scene(k, tt), -int(W * e)))
            canvas.alpha_composite(shift_x(self.scene(nxt, tt), int(W * (1 - e))))
        else:
            canvas.alpha_composite(self.scene(k, tt))
        canvas.alpha_composite(caption_layer(tt, self.toks))
        canvas.alpha_composite(self.disc)
        return canvas.convert("RGB")


def shift_x(img, dx):
    out = layer()
    if dx == 0:
        return img
    if abs(dx) >= W:
        return out
    if dx > 0:
        out.paste(img.crop((0, 0, W - dx, H)), (dx, 0))
    else:
        out.paste(img.crop((-dx, 0, W, H)), (0, 0))
    return out


# --------------------------------------------------------------------------- audio, encode
def build_audio(sh, path):
    sr = 24000
    n = int(math.ceil(sh.total * sr)) + sr
    track = np.zeros(n, np.float32)
    for lid, v in sh.L.items():
        a, r = sf.read(VOICE / f"{lid}.wav", dtype="float32")
        if a.ndim > 1:
            a = a.mean(1)
        assert r == sr, r
        s = int(v["start"] * sr)
        track[s:s + len(a)] += a
    sf.write(path, track[:int(sh.total * sr)], sr)


def lufs(path):
    p = subprocess.run(["ffmpeg", "-nostats", "-i", str(path), "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    i = p.rindex("I:")
    return float(p[i + 2:].split()[0]), float(p[p.rindex("Peak:") + 5:].split()[0])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(HERE / "renders"))
    ap.add_argument("--name", default="job_match_short")
    ap.add_argument("--stills", action="store_true", help="only write one still per scene, no video")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    sh = Short()
    print("scene bounds", [round(x, 2) for x in sh.b], "total", round(sh.total, 2), flush=True)
    assert sh.total <= 15.0, sh.total
    if args.stills:
        mids = [(sh.b[i] + sh.b[i + 1]) / 2 for i in range(5)]
        mids[2] = sh.t_880 + 0.3          # jar and red label visible
        mids[3] = sh.t_ninety + 0.5
        mids[4] = sh.b[4] + 0.9
        for i, t in enumerate(mids):
            sh.frame(t).save(out / f"still_{i + 1}.png")
        sh.frame(sh.t_two + 0.5).save(out / "still_3b.png")
        sh.frame(sh.t_match + 0.15).save(out / "still_4b.png")
        return
    raw_wav = out / "voice_raw.wav"
    build_audio(sh, raw_wav)
    wav = out / "voice_norm.wav"
    I0, _ = lufs(raw_wav)                      # measure, then apply an exact gain to -16 LUFS (loudnorm is unreliable on 14 s)
    gain = -16.0 - I0
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw_wav), "-af",
                    f"highpass=f=70,volume={gain:.2f}dB,alimiter=limit=0.7:level=false,aresample=48000", str(wav)], check=True)
    video = out / f"{args.name}_video.mp4"
    n = int(round(sh.total * FPS))
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "17",
                            "-vf", "scale=in_range=full:out_range=tv,format=yuv420p",
                            "-color_range", "tv", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
                            "-movflags", "+faststart", str(video)], stdin=subprocess.PIPE)
    for i in range(n):
        enc.stdin.write(np.asarray(sh.frame(i / FPS), np.uint8).tobytes())
        if i % 60 == 0:
            print(f"frame {i}/{n}", flush=True)
    enc.stdin.close()
    enc.wait()
    final = out / f"{args.name}.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-i", str(wav), "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest", "-t", f"{sh.total:.3f}",
                    "-movflags", "+faststart", str(final)], check=True)
    I, peak = lufs(final)
    rep = {"runtime_s": round(sh.total, 3), "fps": FPS, "size": [W, H], "loudness_lufs": I, "true_peak_dbtp": peak,
           "scenes": [{"scene": i + 1, "start": round(sh.b[i], 2), "end": round(sh.b[i + 1], 2),
                       "ren_clip": sh.ren[i].shot.used} for i in range(5)],
           "lines": {k: {kk: (round(vv, 2) if isinstance(vv, float) else vv) for kk, vv in v.items()} for k, v in sh.L.items()}}
    (out / f"{args.name}_report.json").write_text(json.dumps(rep, indent=1))
    print(json.dumps({k: rep[k] for k in ("runtime_s", "loudness_lufs", "true_peak_dbtp")}))


if __name__ == "__main__":
    main()
