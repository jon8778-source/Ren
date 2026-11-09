"""Three Bills in 30 Days: the full episode (approved pilot + scenes after it). 1920x1080, 24 fps.

  project/.tools/venv/bin/python videos/three_bills/tb_full.py --plan                 # shot table with timing + cap check
  project/.tools/venv/bin/python videos/three_bills/tb_full.py --stills OUT_DIR       # one still per new shot
  project/.tools/venv/bin/python videos/three_bills/tb_full.py --out OUT_DIR --jobs 4 # render (local only)

The pilot shots (S01-S17) are rendered by the SAME builders as the approved pilot (tb_render.FN); the narration is H + L (uncut) + D1..D7, joined exactly as generated.
"""
import argparse, difflib, json, math, re, subprocess, sys, time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import numpy as np, soundfile as sf
from PIL import Image
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / "unclaimed_401k")); sys.path.insert(0, str(ROOT / "project" / "cliplib"))
import tb_render as TR, tb_shots as SH, tb_ui as T, tb_ui2 as T2, pilot_ui as U, render_pilot as RP
from tb_shots import ms, chip, sign, cross, both, bubble, ren, graphic, phone, veil_bg, table_bg, day, estimate_invoice
W, H, FPS = TR.W, TR.H, 24
clamp = U.clamp
VOICE = TR.VOICE; DSEC = [f"D{i}" for i in range(1, 8)]; SECS = ["H", "L"] + DSEC
TM = dict(TR.TM); FAKE = [s for s in SECS if s not in TM or not (VOICE / f"{s}.wav").exists() or not (VOICE / f"words_{s}.json").exists()]
_paras = [" ".join(p.split()) for p in (HERE / "script" / "VOICE_SCRIPT.txt").read_text().strip().split("\n\n")]
_RANGES = {"H": (0, 4), "L": (5, 9), "D1": (10, 16), "D2": (17, 22), "D3": (23, 27), "D4": (28, 34), "D5": (35, 39), "D6": (40, 44), "D7": (45, 48)}
for s_ in FAKE:
    a_, b_ = _RANGES[s_]; t_ = " ".join(_paras[a_:b_ + 1]); TM[s_] = {"duration": 0.36 * len(t_.split()) + 0.3, "text": t_}
CA, GR, RN, ST = "CHARACTER_ACTION", "GRAPHIC", "REN_ANIMATED", "STORY_STILL"
P, LT, OF = "PORCH", "LOT", "OFFICE"
# Ren clips: (clip, start second in the clip, mirror)
R_TH = ("ren_thinking", 1.5, False); R_OA = ("ren_open_arms", 1.5, False); R_PL = ("ren_present_palm_left", 1.3, True); R_NY = ("ren_nod_yes", 1.3, False); R_SH = ("ren_shrug", 1.3, False)
R_PU = ("ren_point_up", 1.3, False); R_PR = ("ren_point_right", 1.3, False); R_NO = ("ren_shake_no", 1.5, False); R_HP = ("ren_hold_phone", 1.5, False); R_EX = ("ren_explain_hands", 10.0, False); R_PC = ("ren_point_camera", 1.3, False)
def R(clip, panel, y=None): return ren(*clip, panel, y)
def sg(text, tone="sage", w=900, px=60): return lambda c: T2.sign(text, w, tone, px)
def ch(text, w=560, tone="cream", px=56): return lambda c: T.chip_card(text, w, tone, px)
def pp(txt, c=None): return txt

FULL = [
 ("F01", CA, "The hardest part wasn't the repair itself.", ms(P, 1.5, 1.6, 640, 380, [(0, "worried")], extra=cross("The repair", 1200, 220), closeup=True)),
 ("F02", GR, "It was watching one surprise turn into a chain of other decisions.", SH.dominoes_scene),
 ("F03", CA, "She never wanted that feeling again.", ms(P, 1.08, 1.16, 620, 560, [(0, "worried"), (1.2, "neutral")])),
 ("F04", CA, "Maya didn't suddenly double her salary.", ms(OF, 1.4, 1.5, 880, 600, [(0, "neutral")], extra=cross("Double salary", 1250, 230))),
 ("F05", CA, "She didn't discover a perfect side hustle.", ms(OF, 1.5, 1.4, 900, 600, [(0, "neutral"), (1.0, "surprised")], extra=cross("Perfect side hustle", 1170, 230, 0.4, 700))),
 ("F06", CA, "And she definitely didn't stop enjoying her life for a year.", ms(P, 1.1, 1.18, 700, 560, [(0, "relief")], g="sun", extra=SH.cups_ov)),
 ("F07", GR, "Once the card was paid off,", SH.paid_off),
 ("F08", GR, "she opened a separate savings account", SH.new_account),
 ("F09", GR, "and set up an automatic transfer of fifty dollars every week.", SH.auto_transfer),
 ("F10", RN, "Fifty dollars a week, for fifty-two weeks,", R(R_HP, sg("$50 a week for 52 weeks", "cream", 860, 56))),
 ("F11", GR, "gave her two thousand six hundred dollars.", SH.equation_full),
 ("F12", CA, "No miracle return.", ms(P, 1.12, 1.2, 600, 560, [(0, "neutral")], extra=cross("Miracle return", 1200, 260, 0.2, 700, 0.5))),
 ("F13", GR, "Just money deliberately left untouched.", SH.envelope_fill),
 ("F14", CA, "She still went out with friends.", ms(P, 1.12, 1.2, 700, 560, [(0, "relief")], g="sun", extra=SH.cups_ov)),
 ("F15", CA, "She still took a weekend trip she'd planned.", ms(LT, 1.25, 1.35, 700, 560, [(0, "relief")], g="morn", extra=SH.suitcase_ov)),
 ("F16", RN, "This account had one job:", R(R_PR, sg("One job", "gold", 560, 80))),
 ("F17", CA, "be available when life did something expensive and uninvited.", ms(P, 1.1, 1.18, 620, 560, [(0, "neutral")], extra=SH.falling_props)),
 ("F18", GR, "When the balance reached that first target,", SH.target_reached),
 ("F19", GR, "she paused the transfers.", SH.paused),
 ("F20", CA, "And then, one Tuesday, life tested it.", ms(LT, 1.25, 1.3, 700, 560, [(0, "neutral")], g="morn", extra=chip("Tuesday", 1350, 220, 0.3, 480, "cream", 64))),
 ("F21", GR, "Day three.", day(3)),
 ("F22", CA, "Maya turned the key.", ms(LT, 1.25, 1.35, 860, 560, [(0, "neutral")], extra=SH.key_turn)),
 ("F23", CA, "The engine complained, then nothing.", ms(LT, 1.3, 1.45, 900, 560, [(0, "surprised")], extra=SH.smoke)),
 ("F24", GR, "The repair shop's estimate was seven hundred and sixty dollars.", estimate_invoice("Repair estimate", T.A["car_bill"], "Car repair")),
 ("F25", CA, "Her old instinct arrived immediately:", ms(LT, 1.35, 1.3, 560, 520, [(0, "worried")])),
 ("F26", CA, "How am I going to pay for this?", ms(LT, 1.3, 1.4, 600, 520, [(0, "worried")], extra=bubble("How am I going to pay for this?", 1000, 200, 0.2, 860))),
 ("F27", RN, "But this time, she had an answer. The money was already there.", R(R_NY, sg("The money was already there", "gold", 880, 56))),
 ("F28", GR, "She paid for the repair from savings,", phone_card := SH.phone_card(SH.new_bal(T.A["fund_start"], T.A["fund_after_car"], "Car repair", T.A["car_bill"]))),
 ("F29", CA, "got the car back, and drove to work the next morning.", ms(OF, 1.3, 1.4, 900, 600, [(0, "worried"), (0.8, "relief")], g="morn", extra=chip("Next morning", 1230, 230, 0.4, 560, "cream", 58))),
 ("F30", RN, "Her emergency balance dropped from two thousand six hundred dollars", R(R_OA, lambda c: T2.fund_bar((T.A["fund_start"], T.A["fund_after_car"]), clamp(c.t / max(c.d, 1e-6)), 860, 560))),
 ("F31", GR, "to one thousand eight hundred and forty.", SH.graphic(lambda c: c.slide(T2.sign(T.usd(T.A["fund_after_car"]), 760, "sage", 130), 580, 400, 0.15, frm=0), SH.veil_bg())),
 ("F32", CA, "It stung.", ms(LT, 1.3, 1.36, 600, 520, [(0, "worried")])),
 ("F33", CA, "But the problem ended where it began: with the car.", ms(LT, 1.25, 1.3, 760, 560, [(0, "relief")], extra=chip("Car fixed", 1300, 220, 0.5, 480, "sage", 60))),
 ("F34", CA, "Day sixteen.", ms(LT, 1.3, 1.34, 620, 540, [(0, "worried")], extra=lambda c, r=None: c.slide(T2.day_card(16), 1180, 200, 0.2, frm=60))),
 ("F35", GR, "Toothache. Appointment.", SH.tooth_appt),
 ("F36", GR, "A three-hundred-and-ninety-dollar bill after insurance.", estimate_invoice("Dental bill", T.A["dental_bill"], "After insurance")),
 ("F37", CA, "Maya sat in the parking lot with the invoice on her phone.", ms(LT, 1.25, 1.3, 760, 560, [(0, "worried")], extra=SH.pay_phone)),
 ("F38", GR, "She looked at the savings account, tapped transfer,", SH.phone_card(SH.tapped)),
 ("F39", GR, "and stared at the new balance: one thousand four hundred and fifty dollars.", SH.phone_card(SH.new_bal(T.A["fund_after_car"], T.A["fund_after_dental"], "Dental bill", T.A["dental_bill"], 0.5))),
 ("F40", CA, "She felt the same little punch of anxiety.", ms(LT, 1.32, 1.4, 560, 520, [(0, "surprised"), (0.9, "worried")])),
 ("F41", RN, "But there was no missed rent payment to rearrange.", R(R_NO, lambda c: T2.cross_chip("Missed rent", clamp((c.t - 0.6) / 0.7), 640))),
 ("F42", RN, "No new card balance she had to carry just to cover the bill.", R(R_SH, lambda c: T2.cross_chip("New card balance", clamp((c.t - 0.8) / 0.7), 760))),
 ("F43", CA, "Two surprises. Both paid. She kept moving.", ms(P, 1.1, 1.18, 600, 560, [(0, "relief")], extra=SH.tiles_ov(["Car", "Dental"], [0.6, 1.5], 1330, 230))),
 ("F44", GR, "Day twenty-seven.", day(27)),
 ("F45", ST, "Water appeared", SH.kitchen(TR.BOX_A, TR.BOX_B)),
 ("F46", ST, "beneath the kitchen sink.", SH.kitchen(TR.BOX_B, TR.BOX_C)),
 ("F47", ST, "Not a dramatic flood.", SH.kitchen(SH.BOX_D, TR.BOX_B, True, False, SH.cross("Flood", 1100, 120, 0.2, 560, 0.7))),
 ("F48", CA, "Just enough to make ignoring it a terrible idea.", ms(P, 1.5, 1.6, 640, 380, [(0, "surprised")], extra=cross("Ignore it", 1200, 220), closeup=True)),
 ("F49", GR, "The emergency plumbing repair was one thousand and fifty dollars.", estimate_invoice("Plumbing repair", T.A["plumber_bill"], "Emergency")),
 ("F50", CA, "Maya actually laughed when she heard the number.", ms(P, 1.5, 1.6, 660, 380, [(0, "surprised"), (0.8, "relief")], extra=chip(T.usd(T.A["plumber_bill"]), 1260, 200, 0.2, 440, "gold", 80), closeup=True)),
 ("F51", CA, "Not because it was funny. Because, seriously, again?", ms(P, 1.4, 1.5, 640, 380, [(0, "relief"), (1.4, "surprised")], extra=bubble("Again?", 1180, 220, 1.6, 420), closeup=True)),
 ("F52", GR, "She checked the fund. There was enough.", SH.enough),
 ("F53", GR, "She booked the repair and paid it.", SH.phone_card(SH.new_bal(T.A["fund_after_dental"], T.A["fund_final"], "Plumbing repair", T.A["plumber_bill"], 0.7))),
 ("F54", RN, "Three bills in thirty days. Two thousand two hundred dollars gone.", R(R_PL, lambda c: T.equation_card())),
 ("F55", GR, "Four hundred dollars left.", SH.tank(T.A["fund_after_dental"], T.A["fund_final"], "Left")),
 ("F56", CA, "That evening, Maya opened her savings app.", ms(LT, 1.25, 1.32, 700, 560, [(0, "worried")], g="eve", extra=lambda c, r=None: SH._glow_or(c, r))),
 ("F57", GR, "The number looked small.", SH.shrink_phone),
 ("F58", CA, "I've gone backwards, she thought.", ms(P, 1.5, 1.6, 640, 380, [(0, "worried")], g="eve", extra=bubble("I've gone backwards", 1100, 260, 0.3, 700), closeup=True)),
 ("F59", CA, "From the outside, it looked like a month", ms(P, 1.08, 1.14, 620, 560, [(0, "worried")], g="eve", extra=chip("From the outside", 1250, 220, 0.3, 560, "cream", 56))),
 ("F60", GR, "where she'd lost almost everything she'd saved.", SH.tank(T.A["fund_start"], T.A["fund_final"], "Looks like")),
 ("F61", RN, "But look at what she kept.", R(R_PU, sg("What she kept", "gold", 640, 80))),
 ("F62", CA, "She kept her car working.", ms(LT, 1.25, 1.32, 700, 560, [(0, "relief")], extra=lambda c, r=None: SH.key_turn(c, r))),
 ("F63", GR, "She got dental care when she needed it.", SH.tooth_ok),
 ("F64", ST, "She stopped the leak before it got worse.", SH.kitchen(TR.BOX_B, TR.BOX_C, False, True)),
 ("F65", CA, "And she didn't have to turn three urgent problems into three new debts.", ms(P, 1.1, 1.18, 600, 560, [(0, "relief")], extra=SH.tiles_ov(["Car", "Dental", "Pipe"], [0.8, 1.9, 3.0], 1300, 170))),
 ("F66", RN, "Now, savings cannot prevent every hardship.", R(R_OA, sg("Savings can't prevent every hardship", "cream", 860, 52))),
 ("F67", CA, "Four hundred dollars would not be enough for a long stretch without a paycheck.", ms(P, 1.1, 1.16, 600, 560, [(0, "neutral")], extra=SH.compare)),
 ("F68", CA, "And plenty of people simply don't have fifty dollars spare every week.", ms(OF, 1.4, 1.5, 880, 600, [(0, "neutral")], extra=sign("Not everyone has $50 spare", 1130, 260, 0.4, 760, "cream", 54))),
 ("F69", CA, "But this is the part we rarely celebrate.", ms(P, 1.1, 1.2, 620, 560, [(0, "neutral"), (1.4, "relief")], g="sun")),
 ("F70", RN, "An emergency fund is supposed to get smaller when there's an emergency.", R(R_SH, lambda c: T2.fund_bar((T.A["fund_start"], T.A["fund_final"]), clamp(c.t / max(c.d, 1e-6)), 860, 560, "Emergency happens"))),
 ("F71", CA, "Using it isn't failure.", ms(P, 1.5, 1.6, 640, 380, [(0, "relief")], extra=cross("Failure", 1250, 220, 0.2, 520, 0.6), closeup=True)),
 ("F72", GR, "That's literally the job it was hired to do.", SH.graphic(lambda c: [c.slide(T2.sign("Job: pay for emergencies", 1000, "gold", 70), 460, 330, 0.15, frm=0), c.put(T2.tiles(["Done"], [clamp((c.t - 1.0) / 0.4)], 360), 780, 620) if c.t > 0.9 else None], SH.veil_bg())),
 ("F73", CA, "The old Maya saw an unexpected bill and lost her options.", ms(P, 1.12, 1.2, 600, 560, [(0, "worried")], g="eve", extra=cross("Options", 1280, 240, 0.4, 480, 0.8))),
 ("F74", CA, "This Maya could choose what to do next.", ms(P, 1.12, 1.2, 600, 560, [(0, "worried"), (0.5, "relief")], extra=sign("Her choice", 1230, 240, 0.8, 520, "sage", 70))),
 ("F75", RN, "So what can you take from her month?", R(R_PL, sg("Build your own buffer", "gold", 820, 64))),
 ("F76", CA, "First, start with a realistic first target.", ms(OF, 1.4, 1.5, 880, 600, [(0, "neutral")], extra=sign("1  A realistic first target", 1100, 250, 0.4, 780, "sage", 52))),
 ("F77", CA, "Not somebody else's magic number.", ms(OF, 1.5, 1.4, 900, 600, [(0, "surprised")], extra=cross("Magic number", 1200, 250, 0.3, 640, 0.6))),
 ("F78", CA, "Think about the unexpected expense that would cause the most trouble for you right now.", ms(P, 1.1, 1.16, 640, 560, [(0, "neutral")], extra=SH.three_props_pick)),
 ("F79", RN, "Even a small buffer can change the choices you have.", R(R_TH, sg("A small buffer, more choices", "cream", 840, 54))),
 ("F80", CA, "Second, move a manageable amount automatically into a separate, easy-to-access savings account.", ms(OF, 1.35, 1.45, 880, 600, [(0, "neutral")], extra=SH.two_acc)),
 ("F81", GR, "Five dollars, twenty dollars, fifty dollars:", SH.amounts),
 ("F82", CA, "the right amount is the one your budget can actually sustain without creating overdraft fees.", ms(P, 1.1, 1.18, 620, 560, [(0, "relief")], extra=both(sign("Sustainable", 1200, 200, 0.3, 560, "sage", 64), cross("Overdraft fees", 1160, 420, 1.4, 640, 0.7)))),
 ("F83", RN, "Third, don't call every predictable bill an emergency.", R(R_PR, sg("3  Not every bill is an emergency", "cream", 860, 52))),
 ("F84", CA, "Annual insurance, holiday gifts, and routine car maintenance need their own plan.", ms(OF, 1.35, 1.45, 880, 600, [(0, "neutral")], extra=SH.envelopes_three)),
 ("F85", CA, "The emergency fund is for the things you couldn't reasonably schedule.", ms(LT, 1.25, 1.32, 700, 560, [(0, "neutral"), (1.5, "surprised")], extra=sign("Unscheduled", 1330, 240, 0.4, 520, "gold", 64))),
 ("F86", CA, "And fourth, when you use it, refill it as circumstances allow.", ms(OF, 1.35, 1.42, 880, 600, [(0, "relief")], extra=SH.refill)),
 ("F87", CA, "Maya's next step isn't shame.", ms(P, 1.5, 1.6, 640, 380, [(0, "relief")], extra=cross("Shame", 1250, 220, 0.3, 480, 0.6), closeup=True)),
 ("F88", RN, "It's restarting that transfer.", R(R_NY, lambda c: T2.phone_ui([("title", "Automatic transfer"), ("big", T.usd(T.A["weekly_transfer"])), ("toggle", "Automatic", True, clamp((c.t - 0.5) / 0.4))], 440, 620))),
 ("F89", CA, "Maya still wants a bigger emergency cushion,", ms(P, 1.1, 1.18, 620, 560, [(0, "neutral")], g="sun", extra=SH.cushion)),
 ("F90", CA, "eventually enough to help with a loss of income as well as repairs.", ms(P, 1.18, 1.1, 700, 560, [(0, "neutral"), (1.5, "relief")], g="sun", extra=SH.tiles_ov(["Repairs", "Loss of income"], [0.8, 1.8], 1300, 220))),
 ("F91", RN, "But she doesn't have to pretend she made no progress", R(R_OA, sg("Smaller balance, real progress", "gold", 860, 54))),
 ("F92", CA, "just because the account looks smaller today.", ms(P, 1.1, 1.16, 620, 560, [(0, "relief")], g="sun")),
 ("F93", CA, "She built something worth more than an impressive number on a screen:", ms(P, 1.5, 1.6, 660, 380, [(0, "relief")], g="sun", closeup=True)),
 ("F94", GR, "room to respond.", SH.graphic(lambda c: c.slide(T2.sign("Room to respond", 1100, "gold", 110), 410, 360, 0.15, frm=0), SH.veil_bg("PORCH", "sun"))),
 ("F95", CA, "That is a kind of financial freedom.", ms(P, 1.1, 1.2, 600, 560, [(0, "relief")], g="sun")),
 ("F96", CA, "Not a life where nothing goes wrong.", ms(P, 1.12, 1.18, 640, 560, [(0, "neutral")], g="sun")),
 ("F97", CA, "A life where one bad month doesn't have to take the next six with it.", ms(P, 1.12, 1.2, 640, 560, [(0, "neutral"), (1.5, "relief")], g="sun", extra=tiles_months if False else SH.tiles_ov(["One bad month", "Next six: still open"], [0.8, 2.0], 1230, 220))),
 ("F98", RN, "What bill would have shaken you a year ago, but feels more manageable today?", R(R_PC, sg("Which bill feels more manageable today?", "cream", 880, 52))),
 ("F99", RN, "I'd love to hear it in the comments.", R(R_NY, sg("Tell me in the comments", "gold", 780, 64))),
]
for i, f_ in enumerate(FULL):
    if getattr(f_[3], "closeup", False): SH.CLOSEUP.add(f_[0])

# ---------------- timeline --------------------------------------------------------------------------------------------------------------------
def aligned(sec):
    text = TM[sec]["text"].split()
    if sec in FAKE: return [(0.36 * i, 0.36 * i + 0.3) for i in range(len(text))]
    words = json.loads((VOICE / f"words_{sec}.json").read_text())
    def toks(s): return [t for t in re.findall(r"[a-z0-9']+", s.lower().replace("’", "'").replace("-", " ").replace(",", "").replace("$", " $ ")) if t != "and"]
    st, sidx = [], []
    for i, w in enumerate(text):
        for t in toks(w) or ["."]: st.append(t); sidx.append(i)
    wt, widx = [], []
    for j, w in enumerate(words):
        for t in toks(w["word"]) or ["."]: wt.append(t); widx.append(j)
    sm = difflib.SequenceMatcher(None, st, wt, autojunk=False); start = [None] * len(text); end = [None] * len(text)
    for blk in sm.get_matching_blocks():
        for k in range(blk.size):
            i, j = sidx[blk.a + k], widx[blk.b + k]
            if start[i] is None: start[i] = words[j]["start"]
            end[i] = words[j]["end"]
    known = [i for i, v in enumerate(start) if v is not None]
    for i in range(len(text)):
        if start[i] is None:
            lo = max([k for k in known if k < i], default=None); hi = min([k for k in known if k > i], default=None)
            a = end[lo] if lo is not None else 0.0; b = start[hi] if hi is not None else words[-1]["end"]; n_lo = lo if lo is not None else -1; n_hi = hi if hi is not None else len(text); frac = (i - n_lo) / (n_hi - n_lo)
            start[i] = a + (b - a) * (frac - 0.5 / (n_hi - n_lo)); end[i] = a + (b - a) * frac
    return list(zip(start, end))

def build():
    offs, o = {}, 0.0
    for s in SECS: offs[s] = o; o += TM[s]["duration"]
    total = o; text = {s: TM[s]["text"].split() for s in SECS}; al = {s: aligned(s) for s in SECS}
    allw = [(s, i) for s in SECS for i in range(len(text[s]))]; spec = [(sid, typ, ph) for sid, typ, ph in TR.SPEC] + [(sid, typ, ph) for sid, typ, ph, _ in FULL]; pos = 0; shots = []
    for sid, typ, phrase in spec:
        ph = phrase.split(); seg = allw[pos:pos + len(ph)]; got = [text[s][i] for s, i in seg]; assert got == ph, (sid, got, ph); pos += len(ph); s0, i0 = seg[0]
        shots.append(dict(id=sid, type=typ, phrase=phrase, a=0.0 if not shots else offs[s0] + al[s0][i0][0]))
    assert pos == len(allw), (pos, len(allw))
    for k, s in enumerate(shots):
        s["b"] = shots[k + 1]["a"] if k + 1 < len(shots) else total; s["fa"] = 0 if k == 0 else round(s["a"] * FPS); s["fb"] = round(s["b"] * FPS) if k + 1 < len(shots) else int(math.ceil(total * FPS - 1e-6))
    for k, s in enumerate(shots[:-1]): assert shots[k + 1]["fa"] == s["fb"]
    return shots, total, offs
SHOTS, TOTAL, OFFS = build()
NFR = int(math.ceil(TOTAL * FPS - 1e-6)); FN = dict(TR.FN); FN.update({sid: fn for sid, _, _, fn in FULL})
CAP = {"CHARACTER_ACTION": 5.5, "REN_ANIMATED": 5.5, "STORY_STILL": 2.5, "GRAPHIC": 3.5}
TR.TOTAL = TOTAL        # the pilot module's closing disclaimer logic uses TOTAL

def frame_at(i):
    s = next(x for x in SHOTS if x["fa"] <= i < x["fb"]); t = (i - s["fa"]) / FPS; d = (s["fb"] - s["fa"]) / FPS; B = RP.Boxes()
    f = Image.new("RGBA", (W, H)); RP.REC["poses"] = []; RP.REC["maya"] = None; RP.REC["tip"] = None; c = TR.Ctx(s["id"], t, d, i / FPS, f, B)
    FN[s["id"]](c); B.poses = list(RP.REC["poses"]); B.maya = RP.REC["maya"]; T_ = i / FPS
    dw = TR.ImageDraw.Draw(Image.new("RGBA", (4, 4))).textbbox((0, 0), TR.DISC, font=U.font(32, 500)); wpx = dw[2] - dw[0] + 44
    if T_ < 3.0: U.pill(f, TR.DISC, 1860 - wpx, 48, px=32, weight=500, alpha=min(U.clamp(T_ / 0.4), U.clamp((3.0 - T_) / 0.4)), boxes=B, pad=(22, 10))
    elif T_ > TOTAL - 2.6: U.pill(f, TR.DISC, 1860 - wpx, 980, px=32, weight=500, alpha=U.clamp((T_ - (TOTAL - 2.6)) / 0.3), boxes=B, pad=(22, 10))
    return f, s, B

def audio():
    parts = []
    for k in SECS: a, sr = sf.read(VOICE / f"{k}.wav", dtype="float32"); parts.append(a)
    return np.concatenate(parts), sr

def render_range(args):
    lo, hi, out = args
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "15", "-pix_fmt", "yuv420p", "-g", "48", str(out)], stdin=subprocess.PIPE)
    for i in range(lo, hi): f, _, _ = frame_at(i); p.stdin.write(f.convert("RGB").tobytes())
    p.stdin.close(); assert p.wait() == 0; return str(out)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--plan", action="store_true"); ap.add_argument("--stills"); ap.add_argument("--only", nargs="*"); ap.add_argument("--out"); ap.add_argument("--jobs", type=int, default=4); ap.add_argument("--name", default="episode"); a = ap.parse_args()
    if a.plan:
        for s in SHOTS: print(f"{s['id']:4s} {s['type'][:6]:6s} {s['a']:7.2f}-{s['b']:7.2f} {s['b'] - s['a']:4.1f}s {s['phrase'][:78]}")
        bad = [(s["id"], round(s["b"] - s["a"], 2), s["type"]) for s in SHOTS if s["b"] - s["a"] > CAP[s["type"]] + 1e-6]; print(f"total {TOTAL:.1f}s = {TOTAL / 60:.2f} min = {NFR} frames; fake timing for {FAKE}; over cap: {bad}"); return
    if a.stills:
        o = Path(a.stills); o.mkdir(parents=True, exist_ok=True)
        for s in SHOTS:
            if a.only and s["id"] not in a.only: continue
            if not a.only and s["id"] in TR.FN and s["id"] <= "S17": continue
            for tag, fr in (("a", 0.3), ("b", 0.75)): i = int(s["fa"] + (s["fb"] - s["fa"] - 1) * fr); frame_at(i)[0].convert("RGB").save(o / f"{s['id']}_{tag}.png")
        print("stills ->", o); return
    assert not FAKE, f"no real narration for {FAKE}"
    o = Path(a.out).resolve(); o.mkdir(parents=True, exist_ok=True); n = a.jobs; edges = [round(NFR * k / n) for k in range(n + 1)]; t0 = time.monotonic()
    with ProcessPoolExecutor(n) as ex: futs = [ex.submit(render_range, (edges[k], edges[k + 1], o / f"_seg{k}.mp4")) for k in range(n)]; segs = [f.result() for f in futs]
    lst = o / "_segs.txt"; lst.write_text("".join(f"file '{s}'\n" for s in segs)); au, sr = audio(); wav = o / f"{a.name}_audio.wav"; sf.write(wav, au, sr); mp4 = o / f"{a.name}.mp4"
    subprocess.check_call(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-i", str(wav), "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-af", "apad,volume=-0.3dB", "-shortest", "-movflags", "+faststart", str(mp4)])
    for s in segs: Path(s).unlink()
    lst.unlink(); rep = dict(video=mp4.name, frames=NFR, fps=FPS, size=[W, H], audio_s=len(au) / sr, shots=[dict(id=s["id"], type=s["type"], phrase=s["phrase"], start=s["fa"] / FPS, end=s["fb"] / FPS, fa=s["fa"], fb=s["fb"]) for s in SHOTS], render_s=round(time.monotonic() - t0))
    (o / f"{a.name}_report.json").write_text(json.dumps(rep, indent=1)); print("done", mp4, rep["render_s"], "s")

if __name__ == "__main__":
    main()
