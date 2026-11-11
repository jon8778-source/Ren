"""Shot builders for the Three Bills full episode (after the approved pilot). Every builder is fn(c) with c = tb_render.Ctx (local time c.t, shot length c.d, frame c.f, text-box list c.B).
Maya is the approved four-pose cut-out (static artwork: pose cross-fades, camera pushes, close-ups); objects and graphics are animated in code; Ren is a genuine library clip."""
import math, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / "unclaimed_401k")); sys.path.insert(0, str(HERE.parents[1] / "project" / "cliplib"))
import tb_render as TR, tb_ui as T, tb_ui2 as T2, pilot_ui as U, render_pilot as RP
from tb_render import Cam, plate, veil, maya, put_prop, prop, evening, W, H, ease, clamp
from ren_stage import paste_smooth

CLOSEUP = set()          # shot ids whose feet are out of frame on purpose (checked by QA: head in frame, scale correct)
GRADE = {"eve": (40, 50, 110, 56), "morn": (255, 222, 150, 34), "sun": (255, 150, 90, 46)}
def grade(c, g):
    if g: c.f.alpha_composite(Image.new("RGBA", c.f.size, GRADE[g]))
PLX = {"LOT": (480, 800), "PORCH": (580, 800), "OFFICE": (760, 820)}

def ms(pl, z0, z1, cx, cy, poses, g=None, extra=None, mx=None, my=None, closeup=False):
    """Maya on an approved plate. Camera pushes z0 -> z1 over the shot; extra(c, r) draws overlays (r = Maya's frame box)."""
    def fn(c):
        cam = Cam(z0 + (z1 - z0) * ease(c.t / max(c.d, 1e-6)), cx, cy); c.f.alpha_composite(plate(pl, cam))
        x, y = (mx if mx is not None else PLX[pl][0]), (my if my is not None else PLX[pl][1]); r = maya(c.f, cam, pl, poses, c.t, x, y, c.B); grade(c, g)
        if extra: RP.REC["poses"].append("overlay"); extra(c, r)       # every extra is an animated overlay (slide-in, tick, drip, spin, glow ...): counted as motion, not as a pose
    fn.closeup = closeup
    return fn
def chip(text, x, y, t0=0.3, w=560, tone="cream", px=56): return lambda c, r=None: c.slide(T.chip_card(text, w, tone, px), x, y, t0, frm=40)
def sign(text, x, y, t0=0.3, w=900, tone="sage", px=60): return lambda c, r=None: c.slide(T2.sign(text, w, tone, px), x, y, t0, frm=40)
def cross(text, x, y, t0=0.4, w=620, dur=0.7): return lambda c, r=None: c.slide(T2.cross_chip(text, clamp((c.t - t0 - 0.3) / dur), w), x, y, t0, frm=40)
def both(*fs): return lambda c, r=None: [f(c, r) for f in fs]
def bubble(text, x, y, t0=0.3, w=760): return lambda c, r=None: c.slide(T.bubble(text, w), x, y, t0, frm=30)

def table_bg(c, plate_name="OFFICE", grade_=None):
    f = c.f; f.alpha_composite(veil(plate_name)); d = ImageDraw.Draw(f); d.rectangle((0, 690, W, H), fill=(178, 124, 88, 255)); d.line((0, 690, W, 690), fill=(*U.NAVY, 255), width=6)
    for x in range(-100, W + 200, 260): d.line((x, 700, x - 60, H), fill=(160, 110, 78, 255), width=3)
    grade(c, grade_)
def veil_bg(plate_name="OFFICE", g=None):
    def fn(c): c.f.alpha_composite(veil(plate_name)); grade(c, g)
    return fn
def phone(c, img, x, y, t0=0.15, dur=0.4, scale=1.0):
    p = ease((c.t - t0) / dur); im = img.im if scale == 1 else img.im.resize((int(img.im.width * scale), int(img.im.height * scale)), Image.LANCZOS)
    U.put(c.f, im, x, y + int(220 * (1 - p)), alpha=min(1, p * 1.6), boxes=c.B if p > 0.99 else None, texts=[(a * scale, b * scale, cc * scale, e * scale, s, px * scale) for (a, b, cc, e, s, px) in img.texts])

def graphic(fn_draw, bg=None):
    def fn(c):
        if bg: bg(c)
        fn_draw(c)
    return fn

# ---------------- Ren -----------------------------------------------------------------------------------------------------------------------
def ren(clip, start, mirror, panel, y=None, px=None):
    """Ren genuine clip on the left of his sage office; panel(c) -> Img (slides in on the right)."""
    def fn(c):
        TR.REN[c.sid] = (clip, start, mirror); f = plate("SAGE", Cam()); c.f.alpha_composite(f); rc = TR.ren_clip(c); bx, i = rc.draw(c.f, c.t); c.B.ren, c.B.ren_i = bx, i
        img = panel(c); x = 1860 - img.im.width; yy = int(max(60, 520 - img.im.height / 2)) if y is None else y
        RP.slide_in(c.f, img, x, yy, c.t, 0.25, dur=0.45, frm=0, B=c.B)
    return fn

# ---------------- object / graphic scenes -------------------------------------------------------------------------------------------------
def dom(p0, p1):
    """Dominoes scene covering progress p0 -> p1 of the tipping chain over the shot."""
    def fn(c):
        table_bg(c, "PORCH"); p = p0 + (p1 - p0) * clamp((c.t - 0.1) / max(c.d - 0.3, 0.4)); img = T2.dominoes(p); sc = 1.35
        im = img.im.resize((int(img.im.width * sc), int(img.im.height * sc)), Image.LANCZOS); c.f.alpha_composite(im, (150, 150)); c.B.extend([(150 + a * sc, 150 + b * sc, 150 + cc * sc, 150 + e * sc, s_, px * sc) for (a, b, cc, e, s_, px) in img.texts])
    return fn
dominoes_scene = dom(0.0, 1.0)
def amount_big(text, tone="gold"):
    def fn(c): veil_bg()(c); k = max(0.3, U.back(c.t / 0.3)); img = T2.sign(text, 900, tone, 150); im = img.im.resize((int(img.im.width * k), int(img.im.height * k)), Image.LANCZOS); x0, y0 = 960 - im.width / 2, 540 - im.height / 2; c.f.alpha_composite(im, (int(x0), int(y0))); c.B.extend([(x0 + a * k, y0 + b * k, x0 + cc * k, y0 + e * k, s_, px * k) for (a, b, cc, e, s_, px) in img.texts] if k > 0.97 else [])
    return fn
def two_big(c):
    veil_bg()(c); c.put(T2.two_accounts(c.t, 1100, 560), 410, 260)
def paid_off(c):
    table_bg(c); cc_ = T.credit_card(620); f = c.f; x, y = 640, 250
    f.alpha_composite(cc_.im, (x, y)); [c.B.append((x + a, y + b, x + cc, y + e, s, px)) for (a, b, cc, e, s, px) in cc_.texts]
    p = 1 - ease((c.t - 0.3) / 1.1); d = ImageDraw.Draw(f); d.rounded_rectangle((x, y + 360, x + 620, y + 420), 22, fill=(235, 236, 240, 255), outline=(*U.NAVY, 255), width=4)
    if p > 0.01: d.rounded_rectangle((x + 4, y + 364, x + 4 + int(612 * p), y + 416), 18, fill=(*U.RED, 255))
    if c.t > 1.5:
        k = U.back((c.t - 1.5) / 0.3); s_ = max(0.05, k); im = T.chip_card("Paid off", 360, "gold", 64).im; im2 = Image.new("RGBA", im.size, (0, 0, 0, 0)); dd = ImageDraw.Draw(im2); U.rrect(dd, (0, 0, im.width - 1, im.height - 1), 40, (*U.GREEN, 255), (*U.NAVY, 255), 5); dd.text((im.width // 2, im.height // 2), "Paid off", font=U.font(70, 700), fill=U.CREAM, anchor="mm")
        im2 = im2.resize((int(im2.width * s_), int(im2.height * s_)), Image.LANCZOS).rotate(-8, Image.BICUBIC, expand=True); f.alpha_composite(im2, (int(1000 - im2.width / 2 + 120), int(300 - im2.height / 2)))
        if k > 0.97: c.B.append((1120 - 90, 300 - 40, 1120 + 90, 300 + 40, "Paid off", 70))
def new_account(c):
    veil_bg()(c); phone(c, T2.phone_ui([("title", "New account"), ("big", "$0"), ("row", "Savings", "Separate")]), 700, 70)
def auto_transfer(c):
    veil_bg()(c); on = clamp((c.t - 1.0) / 0.35); phone(c, T2.phone_ui([("title", "Automatic transfer"), ("big", T.usd(T.A["weekly_transfer"])), ("row", "Every", "week"), ("toggle", "Automatic", True, on)]), 700, 70)
def equation_full(c):
    veil_bg()(c); img = T2.sign(f"{T.usd(T.A['weekly_transfer'])} x {T.A['contribution_weeks']} weeks = {T.usd(T.A['fund_start'])}", 1300, "gold", 90); c.slide(img, 310, 400, 0.15, frm=0)
def envelope_fill(c):
    veil_bg()(c); n = min(3, int(c.t / 0.6)); TR.envelope(c.f, 960, 640, 520, n, 1.0); c.slide(T.chip_card("Left untouched", 560, "sage", 60), 680, 150, 0.2, frm=0)
def target_reached(c):
    veil_bg()(c); p = ease(c.t / max(c.d, 1e-6)); phone(c, T2.phone_ui([("title", "Savings"), ("big", T.usd(T.A["fund_start"])), ("bar", p, T.GREEN if hasattr(T, "GREEN") else U.GREEN, "First target"), ("check", "Target reached")]), 700, 70)
def paused(c):
    veil_bg()(c); q = 1 - clamp((c.t - 0.7) / 0.35); phone(c, T2.phone_ui([("title", "Automatic transfer"), ("big", T.usd(T.A["weekly_transfer"])), ("toggle", "Automatic", True, q), ("row", "Status", "Paused", U.MUTED)]), 700, 70)
def day(n):
    def fn(c):
        veil_bg()(c); k = 0.7 + 0.3 * ease(c.t / 0.5); img = T2.day_card(n); sc = 1.5 * k; im = img.im.resize((int(img.im.width * sc), int(img.im.height * sc)), Image.LANCZOS)
        x0, y0 = 960 - im.width / 2, 540 - im.height / 2; c.f.alpha_composite(im, (int(x0), int(y0)))
        if k > 1.0 or c.t > 0.4: c.B.extend([(x0 + a * sc, y0 + b * sc, x0 + cc * sc, y0 + e * sc, s_, px * sc) for (a, b, cc, e, s_, px) in img.texts])
    return fn
def estimate_invoice(title, amount, note):
    def fn(c):
        table_bg(c); inv = T.invoice(title, amount, False, 520, 680, note); q = clamp(c.t / 0.4); y = -700 + (150 + 700) * q * q
        if c.t > 0.4: y = 150 - 24 * math.sin(clamp((c.t - 0.4) / 0.22) * math.pi)
        c.f.alpha_composite(inv.im.rotate(-4, Image.BICUBIC, expand=True), (700, int(y)))
        if y > 60: [c.B.append((720 + a, y + b + 10, 720 + cc, y + e + 10, s, px)) for (a, b, cc, e, s, px) in inv.texts]
    return fn
def tooth_appt(c):
    veil_bg()(c); c.put(T2.tooth(c.t, "pain", 520), 330, 280, rec=False); c.slide(T.calendar_card("Appointment", "Dentist", w=620), 1000, 330, 0.5, frm=60)
def tooth_ok(c):
    veil_bg()(c); c.put(T2.tooth(clamp((c.t - 0.3) / 0.5), "ok", 520), 700, 280, rec=False); c.slide(T.chip_card("Dental care", 480, "cream", 56), 720, 150, 0.2, frm=0)
def phone_card(elems_fn, x=700, y=70, bg=None):
    def fn(c):
        (bg or veil_bg())(c); phone(c, elems_fn(c), x, y)
    return fn
def tapped(c): return T2.phone_ui([("title", "Savings"), ("big", T.usd(T.A["fund_after_car"])), ("row", "Dental bill", T.usd(T.A["dental_bill"]), U.RED), ("toggle", "Transfer", True, clamp((c.t - 0.9) / 0.3))])
def new_bal(a, b, label, amt, flip=0.9):
    def elems(c): return T2.phone_ui([("title", "Savings"), ("big", T.usd(b) if c.t >= flip else T.usd(a), U.RED if (b == T.A["fund_final"] and c.t >= flip) else U.NAVY), ("row", label, "-" + T.usd(amt), U.RED) if c.t >= flip else ("gap", 120)])
    return elems
def enough(c):
    veil_bg()(c); phone(c, T2.phone_ui([("title", "Savings"), ("big", T.usd(T.A["fund_after_dental"])), ("bar", clamp((c.t - 0.3) / 0.6) * T.A["plumber_bill"] / T.A["fund_after_dental"], U.SAGE, "Plumbing " + T.usd(T.A["plumber_bill"])), ("check", "Enough")]), 700, 70)
def shrink_phone(c):
    veil_bg("OFFICE", "eve")(c); s = 1.0 - 0.28 * ease(c.t / max(c.d, 1e-6)); img = T2.phone_ui([("title", "Savings"), ("big", T.usd(T.A["fund_final"]))]); im = img.im.resize((int(img.im.width * s), int(img.im.height * s)), Image.LANCZOS)
    x0, y0 = 960 - im.width / 2, 540 - im.height / 2; c.f.alpha_composite(im, (int(x0), int(y0))); c.B.extend([(x0 + a * s, y0 + b * s, x0 + cc * s, y0 + e * s, s_, px * s) for (a, b, cc, e, s_, px) in img.texts])
def tank(a, b, title="Emergency fund"):
    def fn(c): veil_bg("OFFICE", "eve" if title == "Looks like" else None)(c); c.put(T2.fund_bar((a, b), clamp(c.t / max(c.d - 0.4, 0.5)), 860, 560, title), 530, 260)
    return fn
def kitchen(box_a, box_b, drip=True, tick=False, chip_=None):
    def fn(c):
        f, m, s = TR.kit_view(TR._lerp_box(box_a, box_b, ease(c.t / max(c.d, 1e-6)))); c.f.alpha_composite(f)
        if drip: TR.kit_drip(c.f, m, s, c.t)
        if tick:
            k = U.back((c.t - 0.5) / 0.35); r = 110 * max(0.1, k); d = ImageDraw.Draw(c.f); d.ellipse((1500 - r, 260 - r, 1500 + r, 260 + r), fill=(*U.GREEN, 255), outline=(*U.NAVY, 255), width=6); U.check(d, 1500, 262, 0.5 * r, U.CREAM, 18, p=clamp((c.t - 0.6) / 0.4))
        if chip_: chip_(c)
    return fn
BOX_D = (780, 440, 1672, 941); BOX_E = (780, 560, 1672, 941 - 0)
def compare(c, r=None): c.slide(T2.compare_card(clamp((c.t - 0.5) / 2.5)), 880, 300, 0.2, frm=50)
def pay_phone(c, r=None): phone(c, T2.phone_ui([("title", "Invoice"), ("big", T.usd(T.A["dental_bill"])), ("row", "Dental bill", "Due"), ("toggle", "Pay", True, clamp((c.t - 1.5) / 0.4))]), 1250, 60, 0.3, scale=0.92)
def tiles_ov(items, t0s, x=1250, y=160): return lambda c, r=None: c.slide(T2.tiles(items, [clamp((c.t - t) / 0.4) for t in t0s]), x, y, 0.2, frm=50)
def two_acc(c, r=None): c.slide(T2.two_accounts(c.t), 880, 300, 0.2, frm=60)
def amounts(c):
    veil_bg()(c)
    for i, lab in enumerate(("$5", "$20", "$50")): c.slide(T.chip_card(lab, 380, "sage" if i == 2 else "cream", 84), 330 + 440 * i, 400, 0.25 + 0.6 * i, frm=60)
def refill(c, r=None): phone(c, T2.phone_ui([("title", "Savings"), ("big", T.usd(T.A["fund_final"])), ("toggle", "Automatic", True, clamp((c.t - 0.3) / 0.35)), ("bar", clamp((c.t - 0.8) / 2.5) * 0.7 + 0.15, U.SAGE, "Refilling")]), 1180, 70, 0.2, scale=0.8)
def cups_ov(c, r=None):
    d = ImageDraw.Draw(c.f); d.ellipse((1140, 700, 1620, 760), fill=(*U.CREAM, 255), outline=(*U.NAVY, 255), width=5); d.rectangle((1360, 760, 1400, 900), fill=(*U.NAVY, 255)); d.ellipse((1290, 890, 1470, 930), fill=(*U.NAVY, 255))
    for k, x in enumerate((1190, 1400)):
        p = ease((c.t - 0.2 - 0.3 * k) / 0.4); im = T2.cup(200, 200, c.t); c.f.alpha_composite(im, (int(x + (0.0 if k == 0 else 0) + (60 if k == 0 else -60) * (1 - p) * 0), int(530 - 70 * (1 - p))))
def suitcase_ov(c, r=None):
    p = ease((c.t - 0.2) / 0.5); im = T2.suitcase(); c.f.alpha_composite(im, (int(1350 + 300 * (1 - p)), 640)); c.slide(T.chip_card("Weekend trip", 480, "cream", 56), 1220, 440, 0.7, frm=40)
def falling_props(c, r=None):
    for k, (nm, x) in enumerate((("car_key", 1180), ("blank_invoice", 1420), ("leaking_pipe", 1660))):
        t0 = 0.3 + 0.7 * k; q = clamp((c.t - t0) / 0.45)
        if c.t < t0: continue
        y = -150 + (640 + 150) * q * q
        if q >= 1: y = 640 - 30 * math.sin(clamp((c.t - t0 - 0.45) / 0.2) * math.pi)
        if nm == "leaking_pipe": im = TR.pipe_crop(); h = 200; w = im.width * h / im.height; c.f.alpha_composite(im.resize((int(w), h), Image.LANCZOS), (int(x - w / 2), int(y)))
        else: put_prop(c.f, nm, x, y + 90, 180 if nm == "blank_invoice" else 120)
    if c.t > 2.6: c.slide(T.chip_card("Available", 420, "sage", 60), 1300, 380, 2.6, frm=0)
def smoke(c, r=None):
    for k in range(6):
        ph = ((c.t * 0.9) + k / 6) % 1.0; x = 1290 + 25 * math.sin(k * 2 + c.t * 3); y = 560 - 260 * ph; rad = 30 + 70 * ph; lay = Image.new("RGBA", c.f.size, (0, 0, 0, 0)); ImageDraw.Draw(lay).ellipse((x - rad, y - rad, x + rad, y + rad), fill=(235, 236, 240, int(210 * (1 - ph)))); c.f.alpha_composite(lay)
def key_turn(c, r=None):
    ang = 70 * ease((c.t - 0.2) / 1.1); put_prop(c.f, "car_key", 1500, 420, 300, rot=-ang + 20)
def friends_tiles(c, r=None): pass
def three_props_pick(c, r=None):
    for k, nm in enumerate(("car_key", "blank_invoice", "leaking_pipe")):
        x = 1150 + 250 * k; hl = 1 if (int(c.t / 1.0) % 3 == 1 and k == 1) else 0
        d = ImageDraw.Draw(c.f); d.rounded_rectangle((x - 110, 300, x + 110, 560), 30, fill=(*U.CREAM, 255), outline=(*(U.GOLD if hl else U.NAVY), 255), width=8 if hl else 4)
        if nm == "leaking_pipe": im = TR.pipe_crop(); w = im.width * 150 / im.height; c.f.alpha_composite(im.resize((int(w), 150), Image.LANCZOS), (int(x - w / 2), 360))
        else: put_prop(c.f, nm, x, 430, 190 if nm == "blank_invoice" else 120)
def envelopes_three(c, r=None):
    for k, lab in enumerate(("Insurance", "Gifts", "Maintenance")):
        t0 = 0.3 + 0.9 * k; c.slide(T.chip_card(lab, 460, "cream", 52), 1250, 170 + 190 * k, t0, frm=60)
        if c.t > t0 + 0.5:
            d = ImageDraw.Draw(c.f); U.check(d, 1760, 245 + 190 * k, 36, U.GREEN, 13, p=clamp((c.t - t0 - 0.5) / 0.4))
def cushion(c, r=None):
    p = clamp((c.t - 0.4) / max(c.d - 0.8, 0.5)); x, y, w, h = 1250, 700, 480, 70; d = ImageDraw.Draw(c.f); d.rounded_rectangle((x, y, x + w, y + h), 24, fill=(235, 236, 240, 255), outline=(*U.NAVY, 255), width=5)
    d.rounded_rectangle((x + 5, y + 5, x + 5 + int((w - 10) * (0.2 + 0.5 * p)), y + h - 5), 20, fill=(*U.SAGE, 255)); c.slide(T.chip_card("Bigger cushion", 500, "sage", 54), x - 10, y - 160, 0.3, frm=0)

def _glow_or(c, r):
    """Pulsing phone light on Maya (moving overlay)."""
    if r is None: return
    RP.REC["poses"].append("glow_overlay"); cx, cy = (r[0] + r[2]) / 2, r[1] + (r[3] - r[1]) * 0.33; a = 0.5 + 0.5 * math.sin(c.t * 2.4); lay = Image.new("RGBA", c.f.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for r_, al in ((260, 18), (170, 26), (90, 34)): d.ellipse((cx - r_, cy - r_, cx + r_, cy + r_), fill=(190, 215, 245, int(al * (0.6 + 0.4 * a))))
    c.f.alpha_composite(lay)
