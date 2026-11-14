"""Black Friday long-form: FULL film (all 8 script sections, FTC line cut), delivered 1280x720 (rendered at 1920x1080 and scaled once), 24 fps.
  project/.tools/venv/bin/python production/black-friday-5min/bf_full.py --plan | --stills DIR | --out DIR --jobs 4
Reuses the approved pilot's machinery (bf_pilot: sage plate, Ren clips via pilot_ren.RenClip in mouth-closed windows at the approved position, stills, entrance animations). Shots start at the first narrated word of
their phrase (Whisper medium.en alignment of voice/S1..S8.wav joined as generated; voice/words_full.json). Ren: genuine library clips only. All text and figures are drawn in code (bf_ui.py)."""
import argparse, difflib, json, re, subprocess, sys
from pathlib import Path
import numpy as np, soundfile as sf
from PIL import Image
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]; sys.path.insert(0, str(HERE))
import bf_pilot as BP, bf_ui as B, pilot_ui as U
from bf_pilot import W, H, FPS, CAP, Ctx, Rec, sage, still, ren_draw, build_audio as _unused, VOICE, A, TAIL, norm, SP
clamp, ease = U.clamp, U.ease
BP.STILL.update({"S7c3": A / "stills_batch2/candidates_space/S7_budget_note_c3_space.png", "S2c2": A / "stills_batch2/candidates/S2_compare_coats_c2.png", "S3c1": A / "stills_batch2/candidates/S3_checkout_c1.png",
    "S4a": A / "stills_batch2/candidates_space/S4a_laptop_night_tempted_c2_space.png", "S4b2": A / "stills_batch2/candidates_space/S4b2_laptop_closed_hands_c2_space.png", "S5c3": A / "stills_batch2/candidates_space/S5_phone_cart_c3_space.png",
    "S6c2": A / "stills_batch2/candidates_space/S6_dead_earbuds_c2_space.png", "C1": A / "stills/11_C1_calculator.png", "C2": A / "stills/12_C2_price_history.png", "W2": A / "stills/14_W2_morning_kitchen.png", "W3": A / "stills/15_W3_old_pan.png",
    "T1": A / "stills/17_T1_sofa_bags.png", "E1": A / "stills/18_E1_phone_transfer.png", "E2": A / "stills/19_E2_piggy_jar.png", "P3": A / "stills/10_P3_cart_items.png", "P2": A / "stills/09_P2_phone_ping.png"})
R = lambda clip, mir=False: (clip, mir)
# (section, index into shot_plan.P[section], kind, source, card)  -- sections 1-2 are the approved pilot's shots
FULL = list(BP.PL) + [
 (3, 0, "R", R("ren_clipboard_tick"), "rule1"), (3, 1, "S", "S7c3", None), (3, 2, "R", R("ren_point_right"), "coat"), (3, 3, "S", "S2c2", None), (3, 4, "R", R("ren_present_palm_left", True), "twotags"), (3, 5, "G", None, "charger_tag"),
 (3, 6, "G", None, "charger_tag2"), (3, 7, "R", R("ren_point_down_right"), "sum"), (3, 8, "S", "S3c1", None), (3, 9, "G", None, "ticks3"), (3, 10, "R", R("ren_idle_calm"), "working"),
 (4, 0, "S", "S4a", None), (4, 1, "G", None, "clock"), (4, 2, "G", None, "only3"), (4, 3, "S", "P3", "cartcount"), (4, 4, "G", None, "fryer"), (4, 5, "R", R("ren_hold_phone"), "earbuds"), (4, 6, "G", None, "bundle"), (4, 7, "G", None, "announce"),
 (4, 8, "G", None, "saved107"), (4, 9, "S", "S5c3", None), (4, 10, "S", "P2", "email"), (4, 11, "R", R("ren_thinking"), "jolt"), (4, 12, "S", "S4a", None), (4, 13, "R", R("ren_point_right"), "icons"),
 (4, 16, "R", R("ren_idle_listen"), "saved_q"), (4, 17, "R", R("ren_present_palm_left", True), "spent183"),
 (5, 0, "G", None, "rule2"), (5, 1, "S", "C1", None), (5, 2, "G", None, "smaller"), (5, 3, "G", None, "eq"), (5, 4, "R", R("ren_point_right"), "t341"), (5, 5, "G", None, "bar"), (5, 6, "R", R("ren_thinking"), "rule3"), (5, 7, "R", R("ren_hold_phone"), "was150"),
 (5, 8, "S", "C2", None), (5, 9, "R", R("ren_point_right"), "hist"), (5, 10, "G", None, "hist105"), (5, 11, "R", R("ren_shake_no"), "real"), (5, 12, "G", None, "fine"), (5, 13, "R", R("ren_shrug"), "sticker"),
 (6, 0, "R", R("ren_point_right"), "rule4"), (6, 1, "G", None, "bought3"), (6, 2, "G", None, "cart3"), (6, 3, "S", "S4b2", None), (6, 4, "S", "W2", None), (6, 5, "G", None, "question"), (6, 6, "R", R("ren_thinking"), "need"), (6, 7, "G", None, "i_fryer"),
 (6, 8, "S", "W3", None), (6, 9, "G", None, "i_fryer_x"), (6, 10, "G", None, "i_bundle"), (6, 11, "G", None, "i_bundle_q"), (6, 12, "G", None, "i_earbuds"), (6, 13, "S", "S6c2", None), (6, 14, "G", None, "i_earbuds_ok"),
 (6, 15, "G", None, "two_go"), (6, 16, "R", R("ren_nod_yes"), "waiting"), (6, 17, "R", R("ren_present_palm_left", True), "moon"), (6, 18, "R", R("ren_point_down_right"), "room_bar"), (6, 19, "G", None, "onpurpose"),
 (7, 0, "R", R("ren_present_palm_left", True), "tally0"), (7, 1, "G", None, "tally1"), (7, 2, "G", None, "tally1b"), (7, 3, "R", R("ren_point_right"), "rulesA"), (7, 4, "G", None, "tally2"), (7, 5, "G", None, "tally2b"),
 (7, 6, "R", R("ren_idle_calm"), "under37"), (7, 7, "G", None, "less"), (7, 8, "R", R("ren_shrug"), "extra"), (7, 9, "S", "T1", None), (7, 10, "G", None, "prize"), (7, 11, "R", R("ren_thinking"), "room"), (7, 12, "R", R("ren_nod_yes"), "treat"),
 (8, 0, "R", R("ren_point_right"), "rule5"), (8, 1, "S", "E1", None), (8, 2, "S", "E2", None), (8, 3, "R", R("ren_idle_calm"), "recap3"), (8, 4, "G", None, "recap5"), (8, 5, "R", R("ren_thumbs_up"), "endcard"), (8, 6, "G", None, "endcard2")]
V = B.V; usd = B.usd; NAVY, GREEN, RED = U.NAVY, U.GREEN, U.RED
def cards(c):
    t, d, T_ = c.t, c.d, c.T; q = lambda a, b: clamp((t - a) / b)
    return {"rule1": lambda: B.rule_chip(1, "Write the list", 960), "coat": lambda: B.tag_single("Winter coat", 120), "twotags": lambda: B.two_tags(("Coat", 120, int(V["coat"])), ("Gift", 60, int(V["gift"]))),
     "charger_tag": lambda: B.tag_single("Phone charger", 25), "charger_tag2": lambda: B.price_tag("Phone charger", 25, int(V["charger"]), q(0.4, 0.5)), "sum": lambda: B.sum_card(int(V["list_sale"]), int(_f("coat_full") + _f("gift_full") + _f("charger_full"))),
     "ticks3": lambda: B.ticks_card(["Coat", "Gift", "Charger"], 1 + int(t / max(d, 1e-6) * 3)), "working": lambda: B.tick_chip("Sales can work for you", 940),
     "clock": lambda: B.clock_card(3 * 3600 - 1 - int(T_)), "only3": lambda: B.badge_red("ONLY 3 LEFT"), "cartcount": lambda: B.counter_card(3 + min(3, int(t / 0.5))), "fryer": lambda: B.price_tag("Air fryer", 80, int(V["airfryer"]), q(0.5, 0.6)),
     "earbuds": lambda: B.price_tag("Earbuds", 150, int(V["earbuds"]), q(0.5, 0.6)), "bundle": lambda: B.price_tag("Mystery bundle", 60, int(V["bundle"]), q(0.5, 0.6)), "announce": lambda: B.banner("You saved!"),
     "saved107": lambda: B.parts_card("Store says you saved", [("Air fryer", 32), ("Earbuds", 45), ("Bundle", 30)], 107, GREEN), "email": lambda: B.email_card("Sale ends at midnight"), "jolt": lambda: B.chip("Get it before it's gone", 900, "gold", 62),
     "icons": lambda: B.mini_icons(), "saved_q": lambda: B.parts_card("Really saved?", [("Air fryer", 32), ("Earbuds", 45), ("Bundle", 30)], 107, RED, 900, q(0.5, 0.7)),
     "spent183": lambda: B.parts_card("About to spend", [("Air fryer", 48), ("Earbuds", 105), ("Bundle", 30)], 183, RED), "rule2": lambda: B.rule_chip(2, "Do the math", 960), "smaller": lambda: B.chip("A smaller bill, still a bill", 1000, "cream", 68),
     "eq": lambda: B.equation_card(int(V["list_sale"]), int(V["impulse"]), int(V["all_in"])), "t341": lambda: B.total_card("Alex is at", usd(V["all_in"]), RED, 720), "bar": lambda: B.budget_bar(int(V["all_in"]), 300, 1000, q(0.2, 1.2)),
     "rule3": lambda: B.rule_chip(3, "Check the usual price", 960), "was150": lambda: B.tag_single("Earbuds were", 150), "hist": lambda: B.history_card(150, 115, 105, q(0.3, 1.5)), "hist105": lambda: B.history_card(150, 115, 105, 1.0),
     "real": lambda: B.real_card(10, 45), "fine": lambda: B.tick_chip("Fine, if Alex truly needs them", 1000), "sticker": lambda: B.chip("Not the bargain the sticker shouted", 1000, "cream", 56),
     "rule4": lambda: B.rule_chip(4, "Wait 24 hours", 960), "bought3": lambda: B.ticks_card(["Coat", "Gift", "Charger"]), "cart3": lambda: B.cart_items(["Air fryer", "Earbuds", "Bundle"], [0, 0, 0]), "question": lambda: B.chip("One question each", 900, "gold", 72),
     "need": lambda: B.chip("Need it, or did the timer?", 1000, "sage", 62), "i_fryer": lambda: B.item_card("Air fryer", 0), "i_fryer_x": lambda: B.item_card("Air fryer", 2 if t > 0.5 else 0), "i_bundle": lambda: B.item_card("Mystery bundle", 0, 900),
     "i_bundle_q": lambda: B.item_card("Mystery bundle", 3, 900), "i_earbuds": lambda: B.item_card("Earbuds", 0), "i_earbuds_ok": lambda: B.item_card("Earbuds", 1), "two_go": lambda: B.cart_items(["Air fryer", "Earbuds", "Bundle"], [2, 1, 2]),
     "waiting": lambda: B.chip("Waiting isn't saying no", 900, "sage", 62), "moon": lambda: B.moon_sun(q(0.4, 1.5)), "room_bar": lambda: B.budget_bar(int(V["rule_path"]), 300, 1000, 1.0) if False else B.total_card("Room in the budget", usd(300 - V["rule_path"]), GREEN, 800),
     "onpurpose": lambda: B.badge_red("On purpose") if False else B.chip("A purchase made on purpose", 1000, "gold", 66), "tally0": lambda: B.chip("The final tally", 760, "gold", 72), "tally1": lambda: B.tally_card(0 if False else 1) if False else B.total_card("Impulse Alex", usd(V["all_in"]), RED, 760),
     "tally1b": lambda: B.total_card("Over budget by", usd(V["all_in"] - 300), RED, 800), "rulesA": lambda: B.total_card("The list", usd(V["list_sale"]), NAVY, 760), "tally2": lambda: B.parts_card("Rule-following Alex", [("List", int(V["list_sale"])), ("Earbuds", int(V["earbuds"])), ("", 0)], int(V["rule_path"]), GREEN) if False else B.equation_card(int(V["list_sale"]), int(V["earbuds"]), int(V["rule_path"])),
     "tally2b": lambda: B.total_card("Rule-following Alex", usd(V["rule_path"]), GREEN, 900), "under37": lambda: B.total_card("Under budget by", usd(300 - V["rule_path"]), GREEN, 800), "less": lambda: B.less_card(), "extra": lambda: B.chip("Still bought something extra", 1000, "cream", 62),
     "prize": lambda: B.chip("Not a prize for being boring", 1000, "cream", 62), "room": lambda: B.envelope_card(), "treat": lambda: B.treat_card(), "rule5": lambda: B.transfer_card(q(0.4, 1.2)), "recap3": lambda: B.recap_card(1 + min(2, int(t / max(d, 1e-6) * 3))),
     "recap5": lambda: B.recap_card(5), "endcard": lambda: B.end_card(900), "endcard2": lambda: B.end_card(1000)}
def _f(k): return B._a[k]
FIGS = re.compile(r"\$")
def shot_times_full():
    """(start, end) per shot from the aligned narration (never uniform in a render)."""
    ph = [norm(SP.P[s][i][2]) for s, i, *_ in FULL]; flat = [w for p in ph for w in p]; n = len(flat); Wd = json.loads((VOICE / "words_full.json").read_text())
    hyp = [(norm(x["w"]) or [""])[0] for x in Wd]; sm = difflib.SequenceMatcher(None, flat, hyp, autojunk=False); idx = {}
    for a, b, k in sm.get_matching_blocks():
        for j in range(k): idx[a + j] = b + j
    known = sorted(idx); tm = {}
    for i in range(n):
        if i in idx: tm[i] = Wd[idx[i]]["s"]
        else:
            lo = max([k for k in known if k < i], default=None); hi = min([k for k in known if k > i], default=None)
            tm[i] = Wd[idx[lo]]["e"] + 0.05 * (i - lo) if lo is not None else (Wd[idx[hi]]["s"] - 0.05 * (hi - i) if hi is not None else 0.0)
    starts, c = [], 0
    for p in ph: starts.append(0.0 if c == 0 else max(0.0, tm[c] - 0.04)); c += len(p)
    dur = sum(len(sf.read(VOICE / f"S{k}.wav", dtype="float32")[0]) for k in range(1, 9)) / 24000.0 + TAIL; ends = starts[1:] + [dur]; return list(zip(starts, ends)), sm.ratio()
def narration():
    parts = [sf.read(VOICE / f"S{k}.wav", dtype="float32") for k in range(1, 9)]; assert len({p[1] for p in parts}) == 1; return np.concatenate([p[0] for p in parts]), parts[0][1]
def build_shots():
    times, ratio = shot_times_full(); out = []
    for k, ((s, i, kind, src, card), (a, b)) in enumerate(zip(FULL, times)):
        out.append(dict(n=k + 1, id=f"F{k + 1:03d}", kind=kind, src=src, card=card, start=round(a * FPS), end=round(b * FPS), phrase=SP.P[s][i][2], section=s))
    return out, ratio
END_PILL = "Educational only, not financial advice."
def draw_shot(c, sh, figs):
    kind = sh["kind"]; name = sh["card"]
    if kind == "R":
        c.f.alpha_composite(sage()); ren_draw(c, *sh["src"]); img = cards(c)[name](); c.slide(img); figs.append(img)
    elif kind == "S":
        c.f.alpha_composite(still(sh["src"], c.t / max(c.d, 1e-6)))
        if name: img = cards(c)[name](); c.slide(img, y=120); figs.append(img)
    else:
        c.f.alpha_composite(sage(9, True)); img = cards(c)[name](); figs.append(img)
        c.pop(img, 960, 540, 0.12, 0.4, big=1.2 if img.im.width > 900 else 1.35)
def frame_at(shots, k, rec, total):
    sh = next(x for x in shots if x["start"] <= k < x["end"]); t = (k - sh["start"]) / FPS; d = (sh["end"] - sh["start"]) / FPS; T_ = k / FPS
    c = Ctx(sh["id"], t, d, T_, Image.new("RGBA", (W, H)), rec); figs = []; draw_shot(c, sh, figs)
    if T_ < 4.0: c.pill(BP.DISC, 60, 985, 38, alpha=min(clamp(T_ / 0.4), clamp((4.0 - T_) / 0.4)))
    elif T_ > total / FPS - 2.6: c.pill(END_PILL, 60, 985, 38, alpha=clamp((T_ - (total / FPS - 2.6)) / 0.3))
    if any("$" in tx[4] for im in figs for tx in im.texts) and not (T_ < 4.0 and False): c.pill("Example figures", W - 60, 985, 38, anchor="r")
    return c.f, sh
def audio(out_wav, frames):
    a, sr = narration(); raw = out_wav.with_suffix(".raw.wav"); sf.write(raw, a, sr)
    p = subprocess.run(["ffmpeg", "-nostats", "-i", str(raw), "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr; i0 = float(p[p.rindex("I:") + 2:].split()[0])
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af", f"volume={-16 - i0:.2f}dB,alimiter=limit=0.8:level=false,aresample=48000,apad", "-t", f"{frames / FPS:.4f}", str(out_wav)], check=True); raw.unlink()
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--plan", action="store_true"); ap.add_argument("--stills"); ap.add_argument("--out"); ap.add_argument("--jobs", type=int, default=4); ap.add_argument("--range", type=int, nargs=2); ap.add_argument("--seg", type=int, default=0); ap.add_argument("--only", nargs="*"); a = ap.parse_args()
    shots, ratio = build_shots(); total = shots[-1]["end"]
    if a.plan:
        print(f"{len(shots)} shots, {total} frames = {total / FPS:.1f} s, alignment ratio {ratio:.3f}"); ren = [s for s in shots if s["kind"] == "R"]; last = None
        for s in shots:
            d = (s["end"] - s["start"]) / FPS; fl = " OVER CAP" if d > CAP[s["kind"]] + 1e-9 else ""; print(f"{s['id']} s{s['section']} {s['start'] / FPS:6.1f}-{s['end'] / FPS:6.1f} {d:4.2f}s {s['kind']} {s['card'] or s['src']}{fl} | {s['phrase'][:48]}")
        gaps = [round((b["start"] - a_["start"]) / FPS, 1) for a_, b in zip(ren, ren[1:])]; print("Ren shots", len(ren), "gaps", gaps); return
    if a.stills:
        out = Path(a.stills); out.mkdir(parents=True, exist_ok=True); rec = Rec()
        for s in shots:
            if a.only and s["id"] not in a.only: continue
            frame_at(shots, (s["start"] + s["end"]) // 2, rec, total)[0].convert("RGB").save(out / f"{s['id']}.png")
        return
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    if a.range is None:
        audio(out / "audio.wav", total); jobs = a.jobs; bounds = [round(total * k / jobs) for k in range(jobs + 1)]
        procs = [subprocess.Popen([sys.executable, str(Path(__file__)), "--out", str(out), "--range", str(bounds[k]), str(bounds[k + 1]), "--seg", str(k)]) for k in range(jobs)]
        for p in procs:
            if p.wait() != 0: raise SystemExit("a segment failed")
        (out / "segments.txt").write_text("".join(f"file '{out / f'seg{k}.mp4'}'\n" for k in range(jobs))); subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(out / "segments.txt"), "-c", "copy", str(out / "video.mp4")], check=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(out / "video.mp4"), "-i", str(out / "audio.wav"), "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-t", f"{total / FPS:.4f}", "-movflags", "+faststart", str(out / "pilot.mp4")], check=True)
        items, ren = [], []
        for k in range(jobs): r = json.loads((out / f"layout{k}.json").read_text()); items += r["items"]; ren += r["ren"]
        (out / "layout.json").write_text(json.dumps({"items": items, "ren": ren, "shots": [{k: v for k, v in s.items()} for s in shots]}, indent=1)); print("done", total, "frames"); return
    rec = Rec(); a0, a1 = a.range; ren = {}
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-vf", "scale=1280:720:flags=lanczos", "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", str(out / f"seg{a.seg}.mp4")], stdin=subprocess.PIPE)
    for k in range(a0, a1):
        f, sh = frame_at(shots, k, rec, total); enc.stdin.write(np.asarray(f.convert("RGB"), np.uint8).tobytes())
        if rec.ren and rec.ren[1] == k / FPS: ren[k] = rec.ren
        if (k - a0) % 96 == 0: print(f"frame {k}/{a1}", flush=True)
    enc.stdin.close(); enc.wait(); seen = {}
    for it in rec.items: seen[(it[0], it[6])] = it
    (out / f"layout{a.seg}.json").write_text(json.dumps({"items": list(seen.values()), "ren": [[k, *v] for k, v in ren.items()]}))
if __name__ == "__main__": main()
