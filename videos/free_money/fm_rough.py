"""Gate 3 rough cut: S1-S7 of "I Said No to Free Money for 3 Years" (1280x720, 24 fps, v3 rules, draft quality).

  project/.tools/venv/bin/python videos/free_money/fm_rough.py --stills --out /tmp/claude-0/rough     # one still per shot
  project/.tools/venv/bin/python videos/free_money/fm_rough.py --out /output                        # local only, never committed

S1 and S2 are the approved rev03.1 shots (inherited unchanged from fm_rev031.Rev). S3-S7 follow the approved plan
(plan_data.py phrases; shots group phrases so no shot exceeds its v3 cap at the REAL narration timing). Everything on screen
other than the approved art is drawn in code. The narration is joined exactly as generated (no stretching, no padding).
Shot lookup is half-open [start, end) (the rev03.1 fix).
"""
import argparse, json, math, subprocess, sys
from pathlib import Path
import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fm_pilot as fp  # noqa: E402
import fm_rev031 as r3  # noqa: E402
import plan_data as pd  # noqa: E402
from fm_pilot import W, H, FPS, NAVY, SAGE, CREAM, GREEN, MUTED, ease, lerp, layer, paste, shadow, font, pill, flip, Boxes, layout_problems, lufs, bp, VOICE
from fm_rev031 import (Cam, push, zoom_frame, card_fit, card_bg, dashed_rect, car_icon, coin, stack, screen_small, PhoneClip, Rev, RED, CAPS, ROWS,
                       LAPTOP_SCREEN)

import os
SCENES = os.environ.get("FM_SCENES", "S1 S2 S3 S4 S5 S6 S7").split()      # review aid: limit to scenes whose narration exists
GOLD = (255, 196, 40)

# (scene, first phrase, last phrase, type, name)  -- S1/S2 exactly as approved in rev03.1
SPEC = [
    ("S1", 0, 1, "graphic", "stub_hook"), ("S1", 2, 2, "ren", "porch_two_shot"), ("S1", 3, 3, "ren", "quote"), ("S1", 4, 4, "ren", "didnt_know"),
    ("S1", 5, 6, "graphic", "stub_line"), ("S1", 7, 7, "ren", "three_years"), ("S1", 8, 9, "ren", "impress"), ("S1", 10, 10, "ren", "take_you_back"),
    ("S2", 0, 1, "ren", "desk_salary"), ("S2", 2, 2, "ren", "made_it"), ("S2", 3, 4, "ren", "phone_lease"), ("S2", 5, 5, "graphic", "phone_489"),
    ("S2", 6, 6, "ren", "not_needed"), ("S2", 7, 8, "ren", "parking_lot"), ("S2", 9, 10, "ren", "folder_on_desk"), ("S2", 11, 11, "story", "page_six"),
    ("S2", 12, 12, "graphic", "match_strip"), ("S2", 13, 13, "graphic", "laptop_401k"), ("S2", 14, 14, "ren", "reaction_card"),
    ("S2", 15, 15, "ren", "never_page_six"), ("S2", 16, 17, "ren", "picked_two"), ("S2", 18, 18, "graphic", "lease_urgent"),
    # ---- S3: the quiet years (jars)
    ("S3", 0, 0, "ren", "s3_intro"), ("S3", 1, 1, "graphic", "s3_you4"), ("S3", 2, 2, "graphic", "s3_comp4"), ("S3", 3, 3, "graphic", "s3_you2"),
    ("S3", 4, 4, "graphic", "s3_comp2"), ("S3", 5, 5, "graphic", "s3_other2"), ("S3", 6, 6, "ren", "s3_notsaved"), ("S3", 7, 7, "graphic", "s3_neverpaid"),
    ("S3", 8, 8, "graphic", "s3_880"), ("S3", 9, 9, "graphic", "s3_raises_a"), ("S3", 10, 10, "graphic", "s3_raises_b"), ("S3", 11, 11, "ren", "s3_same2"),
    ("S3", 12, 12, "graphic", "s3_ghosts"), ("S3", 13, 13, "graphic", "s3_total"), ("S3", 14, 15, "ren", "s3_lease_pride"),
    ("S3", 16, 16, "graphic", "s3_489"), ("S3", 17, 17, "graphic", "s3_77"), ("S3", 18, 18, "ren", "s3_successful"),
    # ---- S4: back on the porch
    ("S4", 0, 0, "ren", "s4_porch"), ("S4", 1, 1, "story", "s4_dev"), ("S4", 2, 2, "graphic", "s4_q1"), ("S4", 3, 3, "graphic", "s4_q2"),
    ("S4", 4, 4, "story", "s4_folder"), ("S4", 5, 5, "graphic", "s4_q3"), ("S4", 6, 6, "story", "s4_line2"), ("S4", 7, 7, "story", "s4_line4"),
    ("S4", 8, 8, "ren", "s4_diff"), ("S4", 9, 9, "graphic", "s4_keeps"), ("S4", 10, 11, "ren", "s4_notevil"), ("S4", 12, 13, "graphic", "s4_unclaimed"),
    ("S4", 14, 14, "graphic", "s4_phone_in"), ("S4", 15, 15, "graphic", "s4_toggle"), ("S4", 16, 16, "graphic", "s4_90s"), ("S4", 17, 17, "ren", "s4_late"),
    # ---- S5: the sting, then the twist
    ("S5", 0, 0, "ren", "s5_maths"), ("S5", 1, 1, "graphic", "s5_2760"), ("S5", 2, 2, "graphic", "s5_invested"), ("S5", 3, 3, "graphic", "s5_seven"),
    ("S5", 4, 4, "graphic", "s5_hypo"), ("S5", 5, 5, "graphic", "s5_thirty"), ("S5", 6, 6, "graphic", "s5_21k"), ("S5", 7, 7, "ren", "s5_cost"),
    ("S5", 8, 9, "ren", "s5_twist"), ("S5", 10, 10, "ren", "s5_fixed"), ("S5", 11, 12, "graphic", "s5_takehome"), ("S5", 13, 13, "graphic", "s5_pretax"),
    ("S5", 14, 15, "ren", "s5_never_missed"), ("S5", 16, 16, "graphic", "s5_32"), ("S5", 17, 17, "story", "s5_carwash_a"), ("S5", 18, 18, "story", "s5_carwash_b"),
    ("S5", 19, 19, "story", "s5_carwash_c"),
    # ---- S6: what I check now
    ("S6", 0, 0, "story", "s6_today"), ("S6", 1, 1, "story", "s6_older"), ("S6", 2, 3, "ren", "s6_100k"), ("S6", 4, 4, "graphic", "s6_more"), ("S6", 5, 5, "story", "s6_priya_in"),
    ("S6", 6, 6, "graphic", "s6_priya_200"), ("S6", 7, 7, "story", "s6_priya_hike"), ("S6", 8, 8, "story", "s6_priya_pack"), ("S6", 9, 9, "graphic", "s6_priya_max"),
    ("S6", 10, 10, "story", "s6_gary_in"), ("S6", 11, 11, "graphic", "s6_gary_boat"), ("S6", 12, 12, "ren", "s6_everyone_a"), ("S6", 13, 13, "ren", "s6_everyone_b"), ("S6", 14, 14, "ren", "s6_first_money"),
    ("S6", 15, 16, "ren", "s6_check_now"), ("S6", 17, 17, "graphic", "s6_c1"), ("S6", 18, 18, "ren", "s6_plan_docs"), ("S6", 19, 19, "graphic", "s6_c2"),
    ("S6", 20, 21, "graphic", "s6_vest_bar"), ("S6", 22, 22, "graphic", "s6_vest_open"), ("S6", 23, 23, "graphic", "s6_c3"), ("S6", 24, 24, "graphic", "s6_lim_a"),
    ("S6", 25, 25, "graphic", "s6_lim_b"), ("S6", 26, 26, "graphic", "s6_lim_c"), ("S6", 27, 27, "ren", "s6_irs"), ("S6", 28, 28, "ren", "s6_check_official"),
    ("S6", 29, 30, "ren", "s6_dont_max"),
    # ---- S7: handoff and close
    ("S7", 0, 1, "ren", "s7_goback"), ("S7", 2, 2, "story", "s7_hand"), ("S7", 3, 3, "story", "s7_page6"), ("S7", 4, 4, "ren", "s7_before_cut"),
    ("S7", 5, 5, "ren", "s7_owed"), ("S7", 6, 6, "graphic", "s7_list_a"), ("S7", 7, 7, "graphic", "s7_list_b"), ("S7", 8, 8, "ren", "s7_25"),
    ("S7", 9, 9, "ren", "s7_richer_a"), ("S7", 10, 10, "ren", "s7_richer_b"), ("S7", 11, 11, "ren", "s7_next_week"), ("S7", 12, 12, "ren", "s7_wave"),
]
SPEC = [x for x in SPEC if x[0] in SCENES]
PEEL_AT = [n for n in ("desk_salary", "s6_today") if n in [x[4] for x in SPEC]]            # time changes: the page peel (age 25; eight years later)


def trim(im):
    a = np.array(im)[..., 3]
    ys, xs = np.where(a > 20)
    return im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))


def jar(f, cx, base, w, h, pct, col, label, ghost_to=None, sub=None, a=1.0, big=4.0, show=True):
    """A jar holding `pct` of `big` percent, with an optional dashed ghost level up to ghost_to."""
    lay = layer()
    d = ImageDraw.Draw(lay)
    x0, y0 = cx - w / 2, base - h
    d.rounded_rectangle((x0 + 4, y0 + 8, x0 + w + 4, base + 8), 34, fill=(19, 35, 63, 45))
    d.rounded_rectangle((x0, y0, x0 + w, base), 34, fill=(246, 249, 252, 255), outline=(*NAVY, 255), width=6)
    if pct > 0.02:
        top = base - 8 - (h - 16) * pct / big
        m = Image.new("L", (W, H), 0)
        ImageDraw.Draw(m).rounded_rectangle((x0 + 7, y0 + 7, x0 + w - 7, base - 7), 28, fill=255)
        fl = layer()
        ImageDraw.Draw(fl).rectangle((x0, top, x0 + w, base), fill=(*col, 255))
        fl.putalpha(Image.fromarray(np.minimum(np.array(fl.getchannel("A")), np.array(m))))
        lay.alpha_composite(fl)
        d = ImageDraw.Draw(lay)
        if show and h * pct / big > 60:
            d.text((cx, (top + base) / 2), f"{pct:.0f}%" if abs(pct - round(pct)) < 0.05 else f"{pct:.1f}%", font=font(46, 700), fill=(255, 255, 255, 255), anchor="mm")
    if ghost_to is not None and ghost_to > pct + 0.1:
        gt = base - 8 - (h - 16) * ghost_to / big
        gb = base - 8 - (h - 16) * pct / big
        dashed_rect(d, (x0 + 12, gt, x0 + w - 12, gb), (*GREEN, 255), width=4)
        fs = 30
        while d.textlength("never paid", font=font(fs, 700)) > w - 26 and fs > 18:
            fs -= 2
        d.text((cx, (gt + gb) / 2), "never paid", font=font(fs, 700), fill=(*GREEN, 255), anchor="mm")
    d.text((cx, base + 40), label, font=font(36, 700), fill=(*NAVY, 255), anchor="mm")
    if sub:
        d.text((cx, base + 82), sub, font=font(28, 600), fill=(*MUTED, 255), anchor="mm")
    if a < 1:
        lay.putalpha(lay.getchannel("A").point(lambda v: int(v * a)))
    f.alpha_composite(lay)


class Rough(Rev):
    def __init__(self):
        self.A = fp.Assets()
        sup = Path(self.A.folder.filename).parent.parent if hasattr(self.A.folder, "filename") else None
        lib = HERE.parents[1] / "library" / "supporting_assets" / "characters"
        self.priya = trim(Image.open(lib / "Priya_hiking_style.png").convert("RGBA"))
        self.gary = trim(Image.open(lib / "Uncle_Gary.png").convert("RGBA"))
        # ---- phrase timings from the real narration, scene by scene
        self.phr = {}
        off, self.scene_start = 0.0, {}
        for sid in SCENES:
            dur = sf.info(VOICE / f"{sid}.wav").duration
            wt = fp.aligned_word_times(sid)
            k, rows = 0, []
            for i, (ph, typ, assets, ren, text, motion) in enumerate(pd.S[sid]):
                n = len(ph.split())
                rows.append(dict(phrase=ph, start=off + (0.0 if i == 0 else wt[k][0]), end=off + wt[k + n - 1][1]))
                k += n
            self.phr[sid] = rows
            self.scene_start[sid] = off
            off += dur
        self.audio_len = off
        self.total = off + 0.6
        self.shots = []
        for i, (sid, a, b, typ, name) in enumerate(SPEC):
            rows = self.phr[sid]
            self.shots.append(dict(i=i + 1, scene=sid, type=typ, name=name, start=rows[a]["start"], end=rows[b]["end"], a=a, b=b,
                                   phrase=" ".join(rows[j]["phrase"] for j in range(a, b + 1))))
        for k in range(len(self.shots) - 1):
            self.shots[k]["end"] = self.shots[k + 1]["start"]
        self.shots[-1]["end"] = self.total
        q = lambda x: round(x * FPS) / FPS
        for s in self.shots:
            s["start"], s["end"] = q(s["start"]), q(s["end"])
        for k, s in enumerate(self.shots[:-1]):
            over = (s["end"] - s["start"]) - CAPS[s["type"]]
            if 0 < over < 0.12:
                s["end"] = self.shots[k + 1]["start"] = s["start"] + CAPS[s["type"]]
        self.by = {s["name"]: s for s in self.shots}
        self.p = lambda sc, i: self.phr[f"S{sc}"][i]            # phrase timings, as in the rev03.1 Rev class
        pc = self.by["phone_lease"]
        self.phone = PhoneClip(self.A, 1.5, pc["end"] - pc["start"] + 0.1)
        self.build = {}
        for s in self.shots:
            fn = getattr(self, "s_" + s["name"], None)
            if fn is None:
                raise AttributeError("no builder for " + s["name"])
            self.build[s["name"]] = fn

    # ------------------------------------------------------------ shared S3+ helpers
    def pres(self, key, t, d, b, card=None, swap=None, x_card=620, w_card=540, cy=330, label=None, px=40):
        """Presenter (Ren left) with an optional card on the right. swap = (fraction, key2) switches pose part-way."""
        if swap and t >= d * swap[0]:
            key = swap[1]
        f = self.presenter(key, t, d, b)
        if card:
            card_fit(f, card, t, b, x_card, cy, max_w=w_card, base_px=px)
        if label:
            ImageDraw.Draw(f).text((x_card, cy - 175), label, font=font(30, 600), fill=(*MUTED, 255))
            b.text.append((x_card, cy - 180, x_card + 520, cy - 140, "label"))
        return f

    def blur(self, name="OFFICE"):
        return self.A.blur[name].convert("RGBA")

    def title(self, f, text, y=44):
        ImageDraw.Draw(f).text((W / 2, y), text, font=font(32, 600), fill=(*MUTED, 255), anchor="mm")

    def jars(self, t, d, b, you, comp, ghost=None, tags=(), title="One employer's plan (example)", base=500):
        f = self.blur("OFFICE")
        self.title(f, title)
        e = ease((t - 0.1) / min(0.9, max(0.3, d - 0.3)))
        yv, cv = lerp(you[0], you[1], e), lerp(comp[0], comp[1], e)
        gh = None
        if ghost:
            gh = lerp(ghost[0], ghost[1], e)
        jar(f, 430, base, 190, 330, yv, NAVY, "You (employee)", sub=None, show=(e > 0.97 or you[0] == you[1]))
        jar(f, 850, base, 190, 330, cv, SAGE, "Employer", ghost_to=gh, sub=None, show=(e > 0.97 or comp[0] == comp[1]))
        for tx in tags:
            pill(f, tx, 640 - 110, 98, px=34, fill=CREAM, colour=NAVY, boxes=b, pad=(22, 8))
        b.text.append((300, 150, 1000, 600, "jars"))
        return f

    # ------------------------------------------------------------ S3
    def s_s3_intro(self, t, d, b):
        return self.pres("R4", t, d, b, card=[([("How a match works", NAVY)], 0.15)], label="One employer's plan (example)", cy=345)

    def s_s3_you4(self, t, d, b):
        return self.jars(t, d, b, (0, 4), (0, 0))

    def s_s3_comp4(self, t, d, b):
        return self.jars(t, d, b, (4, 4), (0, 4))

    def s_s3_you2(self, t, d, b):
        return self.jars(t, d, b, (4, 2), (4, 4), tags=("$1 matched by $1",))

    def s_s3_comp2(self, t, d, b):
        return self.jars(t, d, b, (2, 2), (4, 2), tags=("$1 matched by $1",))

    def s_s3_other2(self, t, d, b):
        return self.jars(t, d, b, (2, 2), (2, 2), ghost=(2, 4), tags=("$1 matched by $1",))

    def s_s3_notsaved(self, t, d, b):
        return self.pres("R3", t, d, b, card=[([("Not saved for later", NAVY)], 0.15)], label="The other 2% of salary", cy=345)

    def s_s3_neverpaid(self, t, d, b):
        f = self.jars(t, d, b, (2, 2), (2, 2), ghost=(4, 4), tags=("$1 matched by $1",))
        a = ease((t - 0.1) / 0.5)
        pill(f, "Never paid", 540, 560, px=40, fill=NAVY, colour=(255, 255, 255), alpha=a, boxes=b, pad=(30, 12))
        return f

    def counter(self, f, t, d, b, age, salary, missed, total=None, appear=0.0):
        """Age / salary / missed ledger. missed = list of amounts shown; total drawn only when given (so the sum is always true)."""
        card_bg(f, (270, 130, 1010, 560))
        dr = ImageDraw.Draw(f)
        dr.text((310, 175), f"Age {age}", font=font(44, 700), fill=(*NAVY, 255), anchor="lm")
        dr.text((970, 175), salary, font=font(44, 700), fill=(*GREEN, 255), anchor="rm")
        dr.line((310, 215, 970, 215), fill=(*SAGE, 255), width=3)
        dr.text((310, 262), "Missed match:", font=font(36, 600), fill=(*MUTED, 255), anchor="lm")
        x = 310
        for k, m in enumerate(missed):
            a = 1.0
            txt = m
            tw = dr.textlength(txt, font=font(52, 700))
            dr.text((x, 340), txt, font=font(52, 700), fill=(*RED, 255), anchor="lm")
            x += tw + 34
        if total:
            dr.line((310, 400, 970, 400), fill=(*SAGE, 255), width=3)
            dr.text((310, 460), "3 years = about", font=font(40, 600), fill=(*NAVY, 255), anchor="lm")
            dr.text((970, 460), total, font=font(64, 700), fill=(*RED, 255), anchor="rm")
        b.text.append((270, 130, 1010, 560, "ledger"))
        return f

    def s_s3_880(self, t, d, b):
        f = self.blur("OFFICE")
        f = self.counter(f, t, d, b, 25, "$44,000", ["$880"])
        pill(f, "Year 1", 540, 590, px=32, fill=SAGE, colour=(255, 255, 255), alpha=bp.fade(t, 0.3, 0.3), boxes=b, pad=(24, 8))
        return f

    def s_s3_raises_a(self, t, d, b):
        f = self.blur("OFFICE")
        e = bp.fade(t, d * 0.5, 0.3)
        f = self.counter(f, t, d, b, 25 if e < 0.5 else 26, "$44,000", ["$880"])
        return f

    def s_s3_raises_b(self, t, d, b):
        f = self.blur("OFFICE")
        if t < d * 0.45:
            return self.counter(f, t, d, b, 26, "$46,000", ["$880", "$920"])
        return self.counter(f, t, d, b, 27, "$48,000", ["$880", "$920", "$960"])

    def s_s3_same2(self, t, d, b):
        return self.pres("R1", t, d, b, card=[([("Same 2% every year", NAVY)], 0.15), ([("Missed: ", NAVY), ("$880, $920, $960", RED)], 0.5)], cy=345, px=38)

    def s_s3_ghosts(self, t, d, b):
        f = self.blur("OFFICE")
        self.title(f, "Match never paid")
        for k, (amt, cx) in enumerate((("$880", 300), ("$920", 640), ("$960", 980))):
            a = bp.fade(t, 0.15 + 0.4 * k, 0.3)
            if a > 0:
                jar(f, cx, 450, 150, 250, 2, SAGE, f"Year {k + 1}", ghost_to=4, sub=amt, a=a)
        b.text.append((200, 150, 1100, 560, "ghost jars"))
        return f

    def s_s3_total(self, t, d, b):
        f = self.blur("OFFICE")
        return self.counter(f, t, d, b, 27, "$48,000", ["$880", "$920", "$960"], total="$2,760")

    def s_s3_lease_pride(self, t, d, b):
        return self.pres("R2", t, d, b, card=[([("Lease: ", NAVY), ("$489/month", RED)], 0.15), ([("Paid on time, every month", NAVY)], 0.7)], swap=(0.6, "R1"), cy=345, px=38)

    def s_s3_489(self, t, d, b):
        f = self.blur("OFFICE")
        card_bg(f, (240, 170, 1040, 520), bp.fade(t, 0.05, 0.25))
        dr = ImageDraw.Draw(f)
        car_icon(dr, 300, 230, 150, NAVY)
        dr.text((520, 262), "$489/month", font=font(76, 700), fill=(*RED, 255), anchor="lm")
        dr.text((520, 350), "to look successful", font=font(44, 600), fill=(*NAVY, 255), anchor="lm")
        b.text.append((240, 170, 1040, 520, "lease card"))
        return f

    def s_s3_77(self, t, d, b):
        f = self.blur("OFFICE")
        a = bp.fade(t, 0.1, 0.3)
        jar(f, 360, 500, 190, 330, 2, SAGE, "Never paid", ghost_to=4, a=a)
        card_bg(f, (560, 200, 1060, 440), a)
        dr = ImageDraw.Draw(f)
        dr.text((810, 280), "about $77/month", font=font(52, 700), fill=(*RED, 255), anchor="mm")
        dr.text((810, 350), "skipped, on average", font=font(34, 600), fill=(*NAVY, 255), anchor="mm")
        b.text.append((560, 200, 1060, 440, "77 card"))
        return f

    def s_s3_successful(self, t, d, b):
        f = self.presenter("FP", t, d, b)
        return f

    # ------------------------------------------------------------ S4
    def s_s4_porch(self, t, d, b):
        return self.s_porch_two_shot(t, d, b)

    def s_s4_dev(self, t, d, b):
        A = self.A
        cam = Cam(A.plate["PORCH"], push(t, d, 1120, 1160), 330, push(t, d, 1.55, 1.75))
        f = cam.render()
        cam.place(f, A.dev, 1090, 880, 790)
        return f

    def qcard(self, t, d, b, lines, hot=None):
        f = self.A.blur["PORCH"].convert("RGBA")
        rows = [([(q, GREEN if hot == k else NAVY)], 0.1 if k == len(lines) - 1 else -1) for k, q in enumerate(lines)]
        card_fit(f, rows, t, b, 220, 330, max_w=840, base_px=48)
        return f

    def s_s4_q1(self, t, d, b):
        return self.qcard(t, d, b, ["What does this line mean?"])

    def s_s4_q2(self, t, d, b):
        return self.qcard(t, d, b, ["What does this line mean?", "What would it say if you'd read the folder?"])

    def s_s4_folder(self, t, d, b):
        A = self.A
        f = A.blur["OFFICE"].convert("RGBA")
        w = push(t, d, 780, 640)
        h = w * 9 / 16
        ax, ay = min(max(1180, w / 2 + 1), A.folder.width - w / 2 - 1), min(max(215, h / 2 + 1), A.folder.height - h / 2 - 1)
        f.alpha_composite(fp.view(A.folder, (ax, ay), (640, 360), W / w))
        return f

    def s_s4_q3(self, t, d, b):
        return self.qcard(t, d, b, ["What does this line mean?", "What would it say if you'd read the folder?", "Who's keeping the difference?"], hot=2)

    def stub_text(self, t, d, b, text, drop=False):
        A = self.A
        sc = push(t, d, 2.3, 2.5)
        f = A.blur["PORCH"].convert("RGBA")
        anchor, dst = (745, 335), (620, 215)
        f.alpha_composite(fp.view(A.dev_pad, anchor, dst, sc, A.pad))
        fp.glow_line(f, A, anchor, dst, sc, text, 1.0, 0.9, b)
        return f

    def s_s4_line2(self, t, d, b):
        return self.stub_text(t, d, b, "Employer match: 2%")

    def s_s4_line4(self, t, d, b):
        return self.stub_text(t, d, b, "Employer match: 2%" if t < d * 0.2 else "Employer match: 4%")

    def s_s4_diff(self, t, d, b):
        return self.pres("R4", t, d, b)

    def s_s4_keeps(self, t, d, b):
        f = self.jars(t, d, b, (2, 2), (2, 2), ghost=(4, 4), title="The unpaid 2%")
        pill(f, "The employer keeps it", 400, 570, px=38, fill=NAVY, colour=(255, 255, 255), alpha=bp.fade(t, 0.3, 0.3), boxes=b, pad=(30, 12))
        return f

    def s_s4_notevil(self, t, d, b):
        return self.pres("R1", t, d, b, card=[([("That's how matches work", NAVY)], 0.9)], swap=(0.45, "R3"), cy=345, label="One employer's plan (example)")

    def s_s4_unclaimed(self, t, d, b):
        f = self.blur("OFFICE")
        self.title(f, "If you don't claim it")
        jar(f, 430, 500, 190, 330, 2, NAVY, "You (employee)")
        jar(f, 850, 500, 190, 330, 2, SAGE, "Employer")
        e = ease((t - 0.2) / (d * 0.7))
        gx = lerp(430 + 60, 850 - 60, e)
        gl = layer()
        gd = ImageDraw.Draw(gl)
        dashed_rect(gd, (gx - 70, 150, gx + 70, 240), (*GREEN, 255), width=4)
        gd.text((gx, 195), "unclaimed 2%", font=font(28, 700), fill=(*GREEN, 255), anchor="mm")
        f.alpha_composite(gl)
        pill(f, "Stays with the employer", 400, 570, px=36, fill=CREAM, colour=NAVY, alpha=bp.fade(t, d * 0.55, 0.3), boxes=b, pad=(28, 10))
        b.text.append((300, 140, 1000, 600, "jars"))
        return f

    def s_s4_phone_in(self, t, d, b):
        """He opens the retirement app: the phone slides in showing the 401(k) screen at 2%."""
        f = self.toggle_phone(t, d, b, 0.0)
        dx = int(380 * (1 - ease(t / 0.45)))
        if dx > 0:
            sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            sh.paste(f.crop((0, 0, W - dx, H)), (dx, 0))
            bg = self.blur("OFFICE")
            bg.alpha_composite(sh)
            return bg
        return f

    def toggle_phone(self, t, d, b, v):
        f = self.blur("OFFICE")
        cx, top, ph, pw = 640, 40, 650, 340
        lay = layer()
        dr = ImageDraw.Draw(lay)
        dr.rounded_rectangle((cx - pw / 2 + 6, top + 12, cx + pw / 2 + 6, top + ph + 12), 52, fill=(19, 35, 63, 60))
        dr.rounded_rectangle((cx - pw / 2, top, cx + pw / 2, top + ph), 52, fill=(24, 30, 44, 255))
        sx0, sy0, sx1, sy1 = cx - pw / 2 + 14, top + 16, cx + pw / 2 - 14, top + ph - 16
        dr.rounded_rectangle((sx0, sy0, sx1, sy1), 40, fill=(*CREAM, 255))
        dr.text((sx0 + 28, sy0 + 56), "401(k)", font=font(36, 700), fill=(*NAVY, 255))
        dr.text((sx0 + 28, sy0 + 130), "My contribution", font=font(28, 600), fill=(*MUTED, 255))
        pct = "4%" if v > 0.5 else "2%"
        col = tuple(int(NAVY[i] + (GREEN[i] - NAVY[i]) * v) for i in range(3))
        dr.text((sx0 + 28, sy0 + 160), pct, font=font(120, 700), fill=(*col, 255))
        tx0, ty, tw = sx0 + 32, sy0 + 340, 240
        track = tuple(int(200 + (GREEN[i] - 200) * v) for i in range(3))
        dr.rounded_rectangle((tx0, ty, tx0 + tw, ty + 52), 26, fill=(*track, 255))
        kx = tx0 + 26 + v * (tw - 52)
        dr.ellipse((kx - 23, ty + 3, kx + 23, ty + 49), fill=(255, 255, 255, 255), outline=(150, 156, 170, 255), width=2)
        dr.text((tx0, ty + 78), "2%", font=font(28, 600), fill=(*MUTED, 255))
        dr.text((tx0 + tw - 40, ty + 78), "4%", font=font(28, 600), fill=(*MUTED, 255))
        f.alpha_composite(lay)
        b.text.append((cx - pw / 2, top, cx + pw / 2, top + ph, "phone"))
        return f

    def s_s4_toggle(self, t, d, b):
        return zoom_frame(self.toggle_phone(t, d, b, ease((t - 0.7) / 0.5)), push(t, d, 1.0, 1.05))

    def s_s4_90s(self, t, d, b):
        f = self.toggle_phone(t, d, b, 1.0)
        s = bp.ease(min(1, t / 0.3)) * (1 + 0.1 * math.sin(math.pi * min(1, t / 0.4)))
        lay = layer()
        dr = ImageDraw.Draw(lay)
        cx, cy, r = 960, 330, 120
        dr.ellipse((cx - r + 5, cy - r + 10, cx + r + 5, cy + r + 10), fill=(19, 35, 63, 40))
        dr.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(*GREEN, 255))
        dr.text((cx, cy - 28), "90", font=font(116, 700), fill=(255, 255, 255, 255), anchor="mm")
        dr.text((cx, cy + 62), "seconds", font=font(46, 700), fill=(255, 255, 255, 255), anchor="mm")
        ss = max(s, 0.01)
        lay = lay.transform((W, H), Image.AFFINE, (1 / ss, 0, cx - cx / ss, 0, 1 / ss, cy - cy / ss), Image.BICUBIC)
        if s > 0.06:
            f.alpha_composite(lay)
        b.text.append((cx - r, cy - r, cx + r, cy + r, "badge"))
        return f

    def s_s4_late(self, t, d, b):
        return self.pres("R1", t, d, b)

    # ------------------------------------------------------------ S5
    def timeline_graphic(self, t, d, b, coins, years=None, tag=None, sticker=None, number=True):
        f = self.blur("OFFICE")
        e = ease((t - 0.1) / max(0.4, d - 0.2))
        c0, c1 = coins
        n = lerp(c0, c1, e)
        lay = layer()
        dr = ImageDraw.Draw(lay)
        x0, x1, y = 140, 1140, 470
        dr.line((x0, y, x1, y), fill=(*NAVY, 255), width=6)
        for yr in (0, 10, 20, 30):
            x = x0 + (x1 - x0) * yr / 30
            dr.line((x, y - 14, x, y + 14), fill=(*NAVY, 255), width=5)
            dr.text((x, y + 44), "Now" if yr == 0 else f"Year {yr}", font=font(30, 700), fill=(*NAVY, 255), anchor="mm")
        if years is not None:
            yy = lerp(years[0], years[1], e)
            xm = x0 + (x1 - x0) * yy / 30
            dr.polygon([(xm, y - 18), (xm - 16, y - 46), (xm + 16, y - 46)], fill=(*GREEN, 255))
        for k in range(int(n)):
            cx = x0 + 60 + (k % 14) * 66
            cyv = y - 50 - (k // 14) * 30 - (k % 14) * 6
            dr.ellipse((cx - 28, cyv - 18, cx + 28, cyv + 18), fill=(*GOLD, 255), outline=(*NAVY, 255), width=4)
        f.alpha_composite(lay)
        if number:
            pill(f, "$2,760", 140, 100, px=60, fill=NAVY, colour=(255, 255, 255), boxes=b, pad=(34, 14))
        if tag:
            pill(f, tag, 620, 110, px=36, fill=CREAM, colour=NAVY, alpha=bp.fade(t, 0.15, 0.3), boxes=b, pad=(26, 10))
        if sticker:
            card_bg(f, (140, 195, 1140, 305), bp.fade(t, 0.2, 0.3))
            ImageDraw.Draw(f).multiline_text((640, 250), sticker, font=font(34, 700), fill=(*NAVY, 255), anchor="mm", align="center", spacing=8)
            b.text.append((140, 195, 1140, 305, "sticker"))
        b.text.append((130, 80, 1150, 520, "timeline"))
        return f

    def s_s5_maths(self, t, d, b):
        return self.pres("R3", t, d, b, card=[([("The maths", NAVY)], 0.2)], cy=345)

    def s_s5_2760(self, t, d, b):
        return self.timeline_graphic(t, d, b, (0, 3), years=(0, 0), number=True)

    def s_s5_invested(self, t, d, b):
        return self.timeline_graphic(t, d, b, (3, 6), years=(0, 3))

    def s_s5_seven(self, t, d, b):
        return self.timeline_graphic(t, d, b, (6, 8), years=(3, 6), tag="hypothetical 7%/yr")

    def s_s5_hypo(self, t, d, b):
        return self.timeline_graphic(t, d, b, (8, 11), years=(6, 12), tag="hypothetical 7%/yr", sticker="Not a promise.")

    def s_s5_thirty(self, t, d, b):
        return self.timeline_graphic(t, d, b, (11, 20), years=(12, 30), tag="hypothetical 7%/yr")

    def s_s5_21k(self, t, d, b):
        return self.timeline_graphic(t, d, b, (20, 28), years=(30, 30), sticker="$2,760 at a hypothetical 7%/yr for 30 years\\n= about $21,000. Not a promise.".replace("\\n", "\n"), number=False)

    def s_s5_cost(self, t, d, b):
        return self.presenter("FP", t, d, b)

    def s_s5_twist(self, t, d, b):
        return self.pres("R4", t, d, b, swap=(0.55, "R2"))

    def s_s5_fixed(self, t, d, b):
        return self.pres("R1", t, d, b)

    def s_s5_takehome(self, t, d, b):
        f = self.blur("OFFICE")
        card_bg(f, (240, 150, 1040, 540), bp.fade(t, 0.05, 0.25))
        dr = ImageDraw.Draw(f)
        dr.text((280, 200), "Pay stub", font=font(40, 700), fill=(*NAVY, 255), anchor="lm")
        dr.line((280, 240, 1000, 240), fill=(*SAGE, 255), width=3)
        dr.text((280, 300), "Take-home change", font=font(40, 600), fill=(*MUTED, 255), anchor="lm")
        a = bp.fade(t, d * 0.35, 0.3)
        txt = layer()
        td = ImageDraw.Draw(txt)
        td.text((280, 395), "only about $32", font=font(86, 700), fill=(*RED, 255), anchor="lm")
        td.text((280, 475), "per paycheck (pre-tax)", font=font(40, 600), fill=(*NAVY, 255), anchor="lm")
        txt.putalpha(txt.getchannel("A").point(lambda v: int(v * a)))
        f.alpha_composite(txt)
        b.text.append((240, 150, 1040, 540, "stub card"))
        return f

    def s_s5_pretax(self, t, d, b):
        f = self.blur("OFFICE")
        self.title(f, "Before income tax")
        e = ease((t - 0.2) / (d * 0.6))
        boxes = [("Paycheck", 200, NAVY), ("401(k) contribution", 640, GREEN), ("Income tax", 1080, MUTED)]
        for lab, cx, col in boxes:
            card_bg(f, (cx - 170, 220, cx + 170, 360))
            ImageDraw.Draw(f).text((cx, 290), lab, font=font(34, 700), fill=(*col, 255), anchor="mm")
        ar = layer()
        ad = ImageDraw.Draw(ar)
        for x0, x1 in ((380, 450), (850, 910)):
            xe = lerp(x0, x1, e)
            ad.line((x0, 290, xe, 290), fill=(*NAVY, 255), width=9)
            if e > 0.9:
                ad.polygon([(x1 + 14, 290), (x1 - 14, 268), (x1 - 14, 312)], fill=(*NAVY, 255))
        f.alpha_composite(ar)
        b.text.append((130, 220, 1250, 360, "flow"))
        return f

    def s_s5_never_missed(self, t, d, b):
        return self.pres("R2", t, d, b, swap=(0.5, "R3"))

    def s_s5_32(self, t, d, b):
        f = self.blur("OFFICE")
        a = 1 - ease((t - d * 0.4) / (d * 0.55))
        pill(f, "$32", 520, 130, px=90, fill=CREAM, colour=NAVY, boxes=b, pad=(50, 20))
        for k in range(5):
            cx = 420 + k * 110
            cy = 420 - 8 * k
            lay = layer()
            dr = ImageDraw.Draw(lay)
            dr.ellipse((cx - 38, cy - 38, cx + 38, cy + 38), fill=(*GOLD, 255), outline=(*NAVY, 255), width=5)
            dr.text((cx, cy), "$", font=font(48, 700), fill=(*NAVY, 255), anchor="mm")
            lay.putalpha(lay.getchannel("A").point(lambda v: int(v * max(0, a - 0.12 * k))))
            f.alpha_composite(lay)
        b.text.append((400, 340, 960, 500, "coins"))
        return f

    def lot_cam(self, t, d, cx, cy, z0, z1):
        return Cam(self.A.plate["LOT"], cx, cy, push(t, d, z0, z1))

    def s_s5_carwash_a(self, t, d, b):
        return self.lot_cam(t, d, 1150, 540, 1.1, 1.25).render()

    def s_s5_carwash_b(self, t, d, b):
        return self.lot_cam(t, d, 836, 470, 1.0, 1.05).render()

    def s_s5_carwash_c(self, t, d, b):
        return self.lot_cam(t, d, 1250, 560, 1.4, 1.5).render()

    # ------------------------------------------------------------ S6
    def s_s6_today(self, t, d, b):
        f = self.lot_cam(t, d, 1150, 540, 1.0, 1.12).render()
        pill(f, "8 years later", 60, 70, px=44, fill=NAVY, colour=(255, 255, 255), alpha=bp.fade(t, 0.15, 0.3), boxes=b, pad=(30, 12))
        return f

    def s_s6_older(self, t, d, b):
        return self.lot_cam(t, d, 1250, 560, 1.25, 1.4).render()

    def s_s6_100k(self, t, d, b):
        return self.pres("R2", t, d, b, card=[([("Today: about ", NAVY), ("$100,000/yr", GREEN)], 0.1), ([("Full match, every year", NAVY)], 0.9)], swap=(0.55, "R3"), cy=345, px=38)

    def bars(self, f, t, rows, y0=190):
        """Contribution bars: rows = [(label, match_part, extra_part, color_extra)] as fractions of the bar width."""
        card_bg(f, (180, y0 - 40, 1100, y0 + 100 + 120 * len(rows)))
        dr = ImageDraw.Draw(f)
        e = ease((t - 0.2) / 0.7)
        for k, (label, m, x, name) in enumerate(rows):
            y = y0 + 20 + k * 120
            dr.text((220, y), label, font=font(36, 700), fill=(*NAVY, 255), anchor="lm")
            dr.rounded_rectangle((220, y + 30, 1060, y + 74), 12, fill=(228, 233, 240, 255))
            dr.rounded_rectangle((220, y + 30, 220 + 840 * m * e, y + 74), 12, fill=(*SAGE, 255))
            if x:
                dr.rounded_rectangle((220 + 840 * m, y + 30, 220 + 840 * (m + x * e), y + 74), 12, fill=(*GREEN, 255))
            dr.text((1060, y), name, font=font(30, 600), fill=(*MUTED, 255), anchor="rm")

    def s_s6_more(self, t, d, b):
        f = self.blur("OFFICE")
        self.bars(f, t, [("My contribution", 0.5, 0.35, "full match + more")])
        b.text.append((180, 150, 1100, 440, "bars"))
        return f

    def person(self, who, t, d, b, x_plate=850, z=(1.0, 1.06), crop=None, card=None):
        A = self.A
        img = self.priya if who == "priya" else self.gary
        cam = Cam(A.plate["OFFICE"], 836, 470, push(t, d, *z))
        f = cam.render()
        sx, sy = cam.pt(x_plate, 880)
        shadow(f, sx, sy, 300 * cam.k)
        if crop:
            f = Cam(A.plate["OFFICE"], 836, 470, 1.0).render()
        r = cam.place(f, img, x_plate, 880, 700)
        b.ren, b.face = r, (r[0] + (r[2] - r[0]) * 0.25, r[1], r[0] + (r[2] - r[0]) * 0.75, r[1] + (r[3] - r[1]) * 0.2)
        return f

    def s_s6_priya_in(self, t, d, b):
        return self.person("priya", t, d, b, x_plate=lerp(1250, 850, ease(t / 0.5)))

    def s_s6_priya_200(self, t, d, b):
        f = self.person("priya", t, d, b, x_plate=420, z=(1.15, 1.2))
        card_fit(f, [([("Priya: about ", NAVY), ("$200,000/yr", GREEN)], 0.1)], t, b, 640, 330, max_w=560, base_px=40)
        return f

    def s_s6_priya_hike(self, t, d, b):
        return self.person("priya", t, d, b, x_plate=700, z=(1.0, 1.05))

    def s_s6_priya_pack(self, t, d, b):
        A = self.A
        cam = Cam(A.plate["OFFICE"], 836, 560, push(t, d, 1.5, 1.6))
        f = cam.render()
        cam.place(f, self.priya, 836, 1140, 1050)
        return f

    def s_s6_priya_max(self, t, d, b):
        f = self.person("priya", t, d, b, x_plate=420, z=(1.15, 1.2))
        card_fit(f, [([("Priya maxes out", NAVY)], 0.1), ([("every year", GREEN)], 0.1)], t, b, 640, 330, max_w=520, base_px=44)
        return f

    def s_s6_gary_in(self, t, d, b):
        return self.person("gary", t, d, b, x_plate=lerp(1250, 850, ease(t / 0.5)))

    def s_s6_gary_boat(self, t, d, b):
        f = self.person("gary", t, d, b, x_plate=420, z=(1.15, 1.2))
        card_fit(f, [([("“Sell the boat.”", NAVY)], 0.1), ([("Uncle Gary's retirement plan", MUTED)], 0.1)], t, b, 640, 330, max_w=560, base_px=46)
        return f

    def s_s6_everyone_a(self, t, d, b):
        return self.pres("FP", t, d, b)

    def s_s6_everyone_b(self, t, d, b):
        return self.pres("R1", t, d, b)

    def s_s6_first_money(self, t, d, b):
        return self.pres("R4", t, d, b, card=[([("The first money", NAVY)], 0.15), ([("you're owed", GREEN)], 0.15)], cy=345, px=44)

    def checklist(self, f, t, shown, ticks, x0=620, y0=170, hl=None):
        items = ["Match formula", "Vesting schedule", "Next year's limit"]
        card_bg(f, (x0, y0, x0 + 560, y0 + 360))
        dr = ImageDraw.Draw(f)
        dr.text((x0 + 30, y0 + 40), "What I check now", font=font(34, 700), fill=(*MUTED, 255), anchor="lm")
        for k, it in enumerate(items):
            if k >= shown:
                break
            y = y0 + 120 + k * 80
            dr.rounded_rectangle((x0 + 30, y - 24, x0 + 78, y + 24), 10, outline=(*NAVY, 255), width=5)
            if k < ticks:
                dr.line((x0 + 40, y, x0 + 52, y + 14), fill=(*GREEN, 255), width=8)
                dr.line((x0 + 52, y + 14, x0 + 72, y - 16), fill=(*GREEN, 255), width=8)
            dr.text((x0 + 104, y), f"{k + 1}. {it}", font=font(36, 700 if hl == k else 600), fill=(*(GREEN if hl == k else NAVY), 255), anchor="lm")

    def s_s6_check_now(self, t, d, b):
        f = self.presenter("R3", t, d, b)
        self.checklist(f, t, 0, 0)
        b.text.append((620, 170, 1180, 530, "checklist"))
        return f

    def s_s6_c1(self, t, d, b):
        f = self.blur("OFFICE")
        self.checklist(f, t, 1, 0, x0=360, hl=0)
        b.text.append((360, 170, 920, 530, "checklist"))
        return f

    def s_s6_plan_docs(self, t, d, b):
        f = self.presenter("R1", t, d, b)
        self.checklist(f, t, 1, 1, hl=0)
        pill(f, "In the plan documents", 640, 560, px=32, fill=SAGE, colour=(255, 255, 255), alpha=bp.fade(t, 0.5, 0.3), boxes=b, pad=(24, 10))
        b.text.append((620, 170, 1180, 530, "checklist"))
        return f

    def s_s6_c2(self, t, d, b):
        f = self.blur("OFFICE")
        self.checklist(f, t, 2, 1, x0=360, hl=1)
        b.text.append((360, 170, 920, 530, "checklist"))
        return f

    def vest(self, f, t, d, b, fill, open_=False):
        card_bg(f, (180, 150, 1100, 520))
        dr = ImageDraw.Draw(f)
        dr.text((220, 205), "Vesting schedule (example)", font=font(36, 700), fill=(*NAVY, 255), anchor="lm")
        for k in range(5):
            x = 230 + k * 160
            col = SAGE if k < fill else (228, 233, 240)
            dr.rounded_rectangle((x, 290, x + 140, 360), 14, fill=(*col, 255))
            dr.text((x + 70, 395), f"Year {k + 1}", font=font(28, 600), fill=(*MUTED, 255), anchor="mm")
        lx, ly = 960, 205
        dr.rounded_rectangle((lx - 24, ly - 4, lx + 24, ly + 34), 8, fill=(*(GREEN if open_ else MUTED), 255))
        if open_:
            dr.arc((lx - 18, ly - 38, lx + 18, ly + 2), 180, 360, fill=(*GREEN, 255), width=7)
            dr.line((lx + 18, ly - 20, lx + 18, ly - 6), fill=(*GREEN, 255), width=7)
        else:
            dr.arc((lx - 18, ly - 38, lx + 18, ly + 2), 180, 360, fill=(*MUTED, 255), width=7)
            dr.line((lx - 18, ly - 20, lx - 18, ly - 4), fill=(*MUTED, 255), width=7)
            dr.line((lx + 18, ly - 20, lx + 18, ly - 4), fill=(*MUTED, 255), width=7)
        b.text.append((180, 150, 1100, 520, "vest"))

    def s_s6_vest_bar(self, t, d, b):
        f = self.blur("OFFICE")
        self.vest(f, t, d, b, int(lerp(0, 5, ease((t - 0.3) / (d - 0.5)))))
        return f

    def s_s6_vest_open(self, t, d, b):
        f = self.blur("OFFICE")
        self.vest(f, t, d, b, 5, open_=True)
        pill(f, "Fully yours", 520, 560, px=40, fill=GREEN, colour=(255, 255, 255), alpha=bp.fade(t, 0.3, 0.3), boxes=b, pad=(30, 12))
        return f

    def s_s6_c3(self, t, d, b):
        f = self.blur("OFFICE")
        self.checklist(f, t, 3, 2, x0=360, hl=2)
        b.text.append((360, 170, 920, 530, "checklist"))
        return f

    def limit_card(self, t, d, b, big=False, old=False):
        f = self.blur("OFFICE")
        card_bg(f, (220, 140, 1060, 540))
        dr = ImageDraw.Draw(f)
        dr.text((260, 190), "2027 contribution limit", font=font(40, 700), fill=(*NAVY, 255), anchor="lm")
        dr.text((260, 240), "Milliman projection, not confirmed", font=font(32, 600), fill=(*MUTED, 255), anchor="lm")
        if big:
            dr.text((640, 360), "$25,500", font=font(120, 700), fill=(*GREEN, 255), anchor="mm")
        if old:
            dr.text((640, 465), "up from $24,500", font=font(48, 700), fill=(*NAVY, 255), anchor="mm")
        b.text.append((220, 140, 1060, 540, "limit card"))
        return f

    def s_s6_lim_a(self, t, d, b):
        return self.limit_card(t, d, b)

    def s_s6_lim_b(self, t, d, b):
        return self.limit_card(t, d, b, big=True)

    def s_s6_lim_c(self, t, d, b):
        return self.limit_card(t, d, b, big=True, old=True)

    def s_s6_irs(self, t, d, b):
        f = self.presenter("FT", t, d, b)
        card_fit(f, [([("IRS: not yet confirmed", NAVY)], 0.2), ([("(as of end of October)", MUTED)], 0.2)], t, b, 620, 330, max_w=540, base_px=38)
        return f

    def s_s6_check_official(self, t, d, b):
        return self.pres("R4", t, d, b, card=[([("Check the official number", NAVY)], 0.15)], cy=345, px=40)

    def s_s6_dont_max(self, t, d, b):
        return self.pres("R3", t, d, b, card=[([("You don't have to max it out", NAVY)], 0.1), ([("Just don't skip the free part", GREEN)], 0.5)], swap=(0.5, "R2"), cy=345, px=38)

    # ------------------------------------------------------------ S7
    def s_s7_goback(self, t, d, b):
        return self.pres("R3", t, d, b, swap=(0.5, "R1"))

    def s_s7_hand(self, t, d, b):
        f, cam = self.at_desk("FP", t, d, b, z0=1.35, z1=1.4)
        e = ease(t / (d * 0.8))
        x = lerp(120, 380, e)
        quad = [(x, 624), (x + 122, 614), (x + 140, 646), (x + 12, 660)]
        f.alpha_composite(fp.warp(self.A.folder.resize((600, 450), Image.LANCZOS), [cam.pt(*p) for p in quad]))
        return f

    def s_s7_page6(self, t, d, b):
        return self.s_s4_folder(t, d, b)

    def s_s7_before_cut(self, t, d, b):
        return self.pres("R4", t, d, b)

    def s_s7_owed(self, t, d, b):
        return self.pres("R1", t, d, b, card=[([("Collect what you're owed", NAVY)], 0.2)], cy=345, px=40)

    def owed_list(self, t, d, b, n):
        f = self.blur("OFFICE")
        card_bg(f, (240, 150, 1040, 520))
        dr = ImageDraw.Draw(f)
        dr.text((280, 200), "Collect first", font=font(38, 700), fill=(*MUTED, 255), anchor="lm")
        for k, it in enumerate(("The match", "The HSA money", "The stuff in the folder")):
            if k >= n:
                break
            a = bp.fade(t, 0.1 if k == n - 1 else -1, 0.25)
            y = 285 + k * 78
            lay = layer()
            ld = ImageDraw.Draw(lay)
            ld.line((290, y, 306, y + 18), fill=(*GREEN, 255), width=9)
            ld.line((306, y + 18, 336, y - 22), fill=(*GREEN, 255), width=9)
            ld.text((372, y), it, font=font(46, 700), fill=(*NAVY, 255), anchor="lm")
            lay.putalpha(lay.getchannel("A").point(lambda v: int(v * a)))
            f.alpha_composite(lay)
        b.text.append((240, 150, 1040, 520, "owed"))
        return f

    def s_s7_list_a(self, t, d, b):
        return self.owed_list(t, d, b, 2)

    def s_s7_list_b(self, t, d, b):
        return self.owed_list(t, d, b, 3)

    def s_s7_25(self, t, d, b):
        f, cam = self.at_desk("FS", t, d, b, z0=1.35, z1=1.4)
        pill(f, "Age 25", 800, 150, px=44, fill=NAVY, colour=(255, 255, 255), alpha=bp.fade(t, 0.1, 0.3), boxes=b, pad=(30, 12))
        return f

    def s_s7_richer_a(self, t, d, b):
        return self.pres("R2", t, d, b)

    def s_s7_richer_b(self, t, d, b):
        return self.pres("R1", t, d, b)

    def s_s7_next_week(self, t, d, b):
        return self.pres("FP", t, d, b, card=[([("Next week:", NAVY)], 0.15), ([("the month three bills", GREEN)], 0.4), ([("hit me at once", GREEN)], 0.4)], cy=345, px=40)

    def s_s7_wave(self, t, d, b):
        return self.presenter("FW", t, d, b)

    # ------------------------------------------------------------ frames
    def shot_at(self, T):
        T = T + 1e-6
        for sh in self.shots:
            if sh["start"] <= T < sh["end"]:
                return sh
        return self.shots[-1]

    def frame_at(self, T):
        T = min(T, self.total - 1 / FPS)
        sh = self.shot_at(T)
        boxes = Boxes()
        f = self.build[sh["name"]](T - sh["start"], sh["end"] - sh["start"], boxes).convert("RGBA")
        for name in PEEL_AT:
            nxt = self.by[name]
            b1 = nxt["start"]
            if b1 - 0.7 <= T < b1:
                bx = Boxes()
                inc = self.build[name](0.0, nxt["end"] - nxt["start"], bx).convert("RGBA")
                f = flip(f, inc, (T - (b1 - 0.7)) / 0.7)
        self.edu(f, T, boxes)
        return f.convert("RGB"), boxes, sh


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(HERE / "renders"))
    ap.add_argument("--stills", action="store_true")
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--draft", action="store_true", help="CRF 23 faster encode")
    ap.add_argument("--jobs", type=int, default=1)
    ap.add_argument("--range", type=int, nargs=2)
    ap.add_argument("--seg", type=int, default=0)
    ap.add_argument("--name", default="free_money_S1_S7_rough_cut")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    R = Rough()
    over = [(s["i"], s["name"], s["type"], round(s["end"] - s["start"], 2)) for s in R.shots if s["end"] - s["start"] > CAPS[s["type"]] + 1e-6]
    print(f"{len(R.shots)} shots, total {R.total:.2f}s ({R.audio_len:.2f}s narration) | over cap: {over or 'none'}", flush=True)
    if over:
        for o in over:
            print("  OVER", o, flush=True)
    if args.stills:
        d = out / "stills"
        d.mkdir(exist_ok=True)
        probs = []
        for s in R.shots:
            if args.only and s["name"] not in args.only and not any(s["scene"] == o for o in args.only):
                continue
            for tag, frac in (("a", 0.1), ("b", 0.5), ("c", 0.9)):
                T = s["start"] + (s["end"] - s["start"]) * frac
                f, boxes, sh = R.frame_at(T)
                f.save(d / f"shot{s['i']:03d}{tag}.png")
                if tag == "b":
                    probs += layout_problems(boxes, sh)
        print("layout problems:", probs or "none")
        return
    wav = out / "rough_voice.wav"
    if args.range is None:
        sr = 24000
        parts = []
        for sid in SCENES:
            a, r = sf.read(VOICE / f"{sid}.wav", dtype="float32")
            assert r == sr
            parts.append(a)
        track = np.concatenate(parts + [np.zeros(int(0.6 * sr), np.float32)])
        raw = out / "rough_voice_raw.wav"
        sf.write(raw, track, sr)
        i0, _ = lufs(raw)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af", f"volume={-16 - i0:.2f}dB,alimiter=limit=0.8:level=false,aresample=48000", str(wav)], check=True)
    video = out / f"{args.name}_video.mp4"
    n = int(round(R.total * FPS))
    crf = "23" if args.draft else "18"
    jobs = max(1, args.jobs)
    if jobs > 1 and args.range is None:                      # render in parallel segments, then stitch (frames are independent)
        bounds = [round(n * k / jobs) for k in range(jobs + 1)]
        procs = []
        for k in range(jobs):
            cmd = [sys.executable, str(Path(__file__)), "--out", str(out), "--name", args.name, "--range", str(bounds[k]), str(bounds[k + 1]), "--seg", str(k)]
            if args.draft:
                cmd.append("--draft")
            procs.append(subprocess.Popen(cmd, env={**os.environ}))
        for pr in procs:
            if pr.wait() != 0:
                raise SystemExit("a render segment failed")
        lst = out / "segments.txt"
        lst.write_text("".join(f"file '{out / f'{args.name}_seg{k}.mp4'}'\n" for k in range(jobs)))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(video)], check=True)
        probs = []
        for k in range(jobs):
            probs += json.loads((out / f"{args.name}_seg{k}.json").read_text())
            (out / f"{args.name}_seg{k}.mp4").unlink()
            (out / f"{args.name}_seg{k}.json").unlink()
        lst.unlink()
    else:
        a0, a1 = (0, n) if args.range is None else args.range
        target = video if args.range is None else out / f"{args.name}_seg{args.seg}.mp4"
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                                "-c:v", "libx264", "-preset", "medium", "-crf", crf, "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(target)], stdin=subprocess.PIPE)
        probs = []
        for k in range(a0, a1):
            f, boxes, sh = R.frame_at(k / FPS)
            if k % 6 == 0:
                probs += layout_problems(boxes, sh)
            enc.stdin.write(np.asarray(f, np.uint8).tobytes())
            if (k - a0) % 240 == 0:
                print(f"frame {k}/{a1}", flush=True)
        enc.stdin.close()
        enc.wait()
        if args.range is not None:
            (out / f"{args.name}_seg{args.seg}.json").write_text(json.dumps(probs))
            return
    final = out / f"{args.name}.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-i", str(wav), "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-ar", "48000", "-t", f"{R.total:.3f}", "-movflags", "+faststart", str(final)], check=True)
    video.unlink()
    I, pk = lufs(final)
    peels = [R.by[nm]["start"] for nm in PEEL_AT]
    rep = {"frames": n, "duration_s": round(R.total, 3), "narration_s": round(R.audio_len, 3), "lufs": I, "true_peak_dbtp": pk, "layout_problems": probs, "over_cap": over,
           "peel_starts": peels, "scenes": SCENES,
           "shots": [{k: (round(v, 3) if isinstance(v, float) else v) for k, v in s.items()} for s in R.shots]}
    (out / f"{args.name}_report.json").write_text(json.dumps(rep, indent=1, ensure_ascii=False))
    print(json.dumps({k: rep[k] for k in ("frames", "duration_s", "lufs", "true_peak_dbtp", "layout_problems", "over_cap")}))


if __name__ == "__main__":
    main()
