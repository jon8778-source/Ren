"""The ~1-minute Short from the Black Friday long video: beats, asset bindings, manifest (production.json), short_spec.json and ASSET_REQUIREMENTS.md, generated from one place.
  project/.tools/venv/bin/python production/black-friday-5min/short/short_spec.py
Each beat starts at the first spoken word of its phrase (short_cues.json). Only the first 360 frames (15 s) are rendered until the owner approves the prototype."""
import hashlib, json, re
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[2]; FPS = 24; DISCLAIMER = "Educational content only, not financial advice."
# id, kind, composition, phrase, action, motion purpose, assets
B = [
 ("hook", "presenter", "ren-left-title", "Black Friday has a clever trick.", "Ren waves hello in his office; a 'Black Friday / a test' card slides in; opening educational chip", "Introduce the host and the premise", ["ren_wave", "sage"]),
 ("spend-saving", "story_still", "alex-leaves-shop-tag", "It can make spending feel like saving.", "Alex walks out of the shop with two bags (slow push); a price tag flips 'Spending' to 'Saving'", "Show the trick", ["s1c2"]),
 ("budget", "presenter", "ren-left-budget", "Today, Alex heads into the sales with a three hundred dollar budget", "Ren points at a '$300 budget' card", "State the budget", ["ren_point", "sage"]),
 ("two-plans", "story_still", "alex-pays-plans-card", "and two very different plans.", "Approved art of Alex paying; a Plan A / Plan B card slides up", "Set up the comparison", ["cafe"]),
 ("plan-a", "presenter", "ren-left-341", "One plan ends at three hundred and forty-one dollars.", "Ren presents (mirrored palm); the $341 card appears", "Plan A total", ["ren_present", "sage"]),
 ("plan-b", "graphic", "total-263", "The other ends at two hundred and sixty-three.", "A big $263 card pops over the blurred office", "Plan B total", ["sage"]),
 ("apart", "presenter", "ren-left-78-apart", "Same shop, same sales, seventy-eight dollars apart.", "Ren stands calm; both totals and a '$78 apart' chip", "The gap", ["ren_calm", "sage"]),
 ("website", "presenter", "ren-left-website", "Then Alex opens a shop's website.", "Ren holds a phone; a 'Shop website' card", "Start the pressure story", ["ren_phone", "sage"]),
 ("clock", "graphic", "countdown-clock", "A countdown clock is ticking.", "A navy countdown clock counts down in code", "Show the pressure tactic", ["sage"]),
 ("badge", "graphic", "only-3-left", "A badge says only three left.", "A red ONLY 3 LEFT badge pops", "Show the scarcity tactic", ["sage"]),
 ("saved-107", "presenter", "ren-left-saved-107", "The website cheerfully announces that Alex has saved one hundred and seven dollars.", "Ren points at the store's '$107 saved' card", "The store's claim", ["ren_point", "sage"]),
 ("not-saved", "presenter", "ren-left-struck-107", "And here's the thing. Alex hasn't saved one hundred and seven dollars.", "Ren listens; the '$107 saved' figure is struck through", "Contradict the claim", ["ren_listen", "sage"]),
 ("spend-183", "graphic", "parts-183", "Alex is about to spend one hundred and eighty-three.", "The three items $48 + $105 + $30 add to $183", "Show the real cost", ["sage"]),
 ("rule-2", "presenter", "ren-left-rule2", "Rule two: do the math. A discount isn't a saving.", "Ren thinks; a RULE 2 tag", "Rule two", ["ren_think", "sage"]),
 ("smaller-bill", "graphic", "equation-341", "It's just a smaller bill. Add the list to the cart", "The finished equation $158 + $183 = $341", "Do the math", ["sage"]),
 ("over-341", "presenter", "ren-left-341-total", "and Alex is at three hundred and forty-one dollars,", "Ren points right at 'Alex is at $341'", "The total", ["ren_point", "sage"]),
 ("over-budget", "graphic", "budget-bar", "which is forty-one dollars over budget.", "A budget bar fills past $300; '$41 over' lands", "Show the overspend", ["sage"]),
 ("rule-4", "presenter", "ren-left-rule4", "Rule four: let it sit for twenty-four hours.", "Ren points down-right; RULE 4 tag", "Rule four", ["ren_point_down", "sage"]),
 ("question", "presenter", "ren-left-question", "Do I need this, or did the timer need me to buy it?", "Ren shrugs; a 'Need it, or did the timer?' card", "The question to ask", ["ren_shrug", "sage"]),
 ("sleep", "graphic", "moon-to-sun", "It just means the answer has to survive a night's sleep.", "A moon becomes a sun: 'Still want it tomorrow?'", "The 24-hour idea", ["sage"]),
 ("tally", "presenter", "ren-left-tally", "That's thirty-seven under budget, and seventy-eight dollars less than the impulse cart.", "Ren presents; the '$37 under budget' card changes to '$78 less' on the second figure", "The result", ["ren_present", "sage"]),
 ("cta", "presenter", "ren-left-end-card", "Check out the Money Leak Audit Workbook in the description.", "Ren gives a thumbs up; the workbook card; the exact disclaimer holds for the last two seconds", "Call to action and disclaimer", ["ren_thumbs", "sage"]),
]
def lib(n): return f"assets/ren_library/{n}.mp4"
EV_VIDEO = "Used in the owner-approved long video ('Approved', 14 Nov 2026, SHA-256 eef4d914...)"
ASSETS = [
 ("script", "script", "production/black-friday-5min/script/script.md", "Owner-approved script ('Approved', 14 Nov 2026; FTC line cut); the Short reuses whole sentences of it"),
 ("audio", "audio", "production/black-friday-5min/short/short_audio_raw.wav", "Cut from the approved long-video narration (voice/S1..S8 joined), no resynthesis"),
 ("renderer", "renderer", "production/black-friday-5min/short/render_short.py", "Portrait adapter under the Shorts launcher; reuses the long film's Ren matting and the Three Bills Short layout code"),
 ("cards", "configuration", "production/black-friday-5min/short/bf_short_ui.py", "Portrait card builders (code-drawn text and figures from data/assumptions.csv); hashed so a card change invalidates the approval"),
 ("configuration", "configuration", "production/black-friday-5min/short/short_spec.json", "Generated from short_spec.py: beats and timings tied to short_cues.json"),
 ("ren_wave", "character", lib("ren_wave_hello"), "Approved animated Ren library clip; " + EV_VIDEO), ("ren_point", "character", lib("ren_point_right"), "Approved animated Ren library clip; " + EV_VIDEO),
 ("ren_present", "character", lib("ren_present_palm_left"), "Approved animated Ren library clip (mirrored); " + EV_VIDEO), ("ren_calm", "character", lib("ren_idle_calm"), "Approved animated Ren library clip; " + EV_VIDEO),
 ("ren_phone", "character", lib("ren_hold_phone"), "Approved animated Ren library clip; " + EV_VIDEO), ("ren_listen", "character", lib("ren_idle_listen"), "Approved animated Ren library clip; " + EV_VIDEO),
 ("ren_think", "character", lib("ren_thinking"), "Approved animated Ren library clip; " + EV_VIDEO), ("ren_point_down", "character", lib("ren_point_down_right"), "Approved animated Ren library clip; " + EV_VIDEO),
 ("ren_shrug", "character", lib("ren_shrug"), "Approved animated Ren library clip; " + EV_VIDEO), ("ren_thumbs", "character", lib("ren_thumbs_up"), "Approved animated Ren library clip; " + EV_VIDEO),
 ("sage", "environment", "videos/unclaimed_401k/art/plates/SAGE_4k.png", "Ren's approved sage home office (REN_VIDEO_RULES.md), used in the approved long video"),
 ("s1c2", "environment", "production/black-friday-5min/assets/stills_batch2/candidates/S1_shop_entrance_c2.png", "Alex shop-entrance candidate (FLUX.2-dev from the approved Alex art), used in the owner-approved long video; no separate art approval; 1920x1088, enlarged about 1.8x for a portrait crop"),
 ("cafe", "environment", "production/black-friday-5min/assets/approved_alex/alex-cafe.png", "Approved coffee-v3 art 'Alex taps to pay for coffee' (SHA-256 83d61936...), restored from codex/ren-approved-v3; 1672x941, enlarged about 2x for a portrait crop"),
 ("typography", "font", "project/remotion/public/fonts/fredoka-latin-700-normal.woff2", "Fredoka, the established house typeface"),
]
def sha(p): return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()
def norm(x): return re.findall(r"[a-z0-9']+", x.lower().replace("’", "'").replace("$", ""))
def main():
    cues = json.loads((HERE / "short_cues.json").read_text()); words = cues["words"]; nf = int(round(cues["duration"] * FPS)); pos, starts = 0, []
    for b in B:
        ph = norm(b[3]); acc = []; k = pos
        while len(acc) < len(ph): acc += norm(words[k]["word"]); k += 1
        assert acc == ph, (b[0], acc, ph); starts.append(0.0 if pos == 0 else words[pos]["start"] - 0.04); pos = k
    assert pos == len(words), (pos, len(words))
    frames = [0 if i == 0 else round(s * FPS) for i, s in enumerate(starts)] + [nf]; spec = {"fps": FPS, "frames": nf, "disclaimer": DISCLAIMER, "narration_s": cues["duration"], "beats": []}; scenes = []
    for i, (sid, kind, comp, phrase, action, purpose, assets) in enumerate(B):
        fa, fb = frames[i], frames[i + 1]; assert fb > fa, sid; d = (fb - fa) / FPS
        spec["beats"].append(dict(id=sid, start_frame=fa, end_frame=fb, kind=kind, composition=comp, narration=phrase))
        s = dict(id=sid, start_frame=fa, end_frame=fb, kind=kind, composition=comp, action=action, motion_purpose=purpose, assets=assets, animations=[sid + "-motion"], environment_fullscreen=True)
        if d < 2 or d > 4.0: s["timing_justification"] = f"Beat length {d:.1f} s follows the spoken phrase boundaries; the visual change lands on its words"
        scenes.append(s)
    (HERE / "short_spec.json").write_text(json.dumps(spec, indent=1))
    man = {"schema_version": 1, "title": "Ren | Black Friday: the sale that tests you: ~1-minute Short (derived from the long video)", "width": 1080, "height": 1920, "fps": FPS, "frames": nf, "full_bleed": True, "permanent_border": False, "asset_report": "ASSET_REQUIREMENTS.md",
           "layout_evidence": "layout.json", "prototype": "prototype.mp4", "prototype_report": "prototype.qa.json",
           "assets": [dict(id=i, kind=k, path=str(Path("../../..") / p), sha256=sha(p) if (ROOT / p).exists() else "MISSING", status="approved", approval_evidence=e) for i, k, p, e in ASSETS], "scenes": scenes}
    groups, cur = [], []
    for w in words:
        cur.append(w)
    man["audio_cues"] = [dict(start=words[0]["start"], end=words[-1]["end"], text=" ".join(w["word"] for w in words))]
    (HERE / "production.json").write_text(json.dumps(man, indent=1, ensure_ascii=False))
    L = ["# Asset requirements report: ~1-minute Short from \"Black Friday: the sale that tests you\"", "", "Prepared before rendering (Shorts rules, asset-first checkpoint). **Status: prototype (first 15 s) only; the complete Short is not rendered until the owner approves the prototype.**", "",
         "## Narration", f"- {cues['duration']:.2f} s, {len(words)} words, cut from the approved long-video narration by `short_audio.py`: {len(cues['sentences'])} excerpts of whole script sentences, in script order, wording unchanged.",
         "- No new synthesis, speed change, stretching or inserted silence; each excerpt starts 0.05 s before its first word and keeps up to 0.22 s of the original audio after the last (never past the next word). **The nine joins between non-adjacent excerpts are tighter than in the long video: listen to each** (I cannot hear audio). Two numbers repeat (341, 107) by design.", "",
         "## Inventory (hashes in `production.json`)", "", "| Id | Kind | Path | SHA-256 (first 12) | Provenance |", "|---|---|---|---|---|"]
    for i, k, p, e in ASSETS: L.append(f"| {i} | {k} | `{p}` | {sha(p)[:12] if (ROOT / p).exists() else 'MISSING'} | {e} |")
    L += ["", "## Scenes", "", "| Scene | Frames | Seconds | Composition | Action | Assets |", "|---|---|---|---|---|---|"]
    for s in scenes: L.append(f"| {s['id']} | {s['start_frame']}-{s['end_frame']} | {(s['end_frame'] - s['start_frame']) / FPS:.2f} | {s['composition']} | {s['action']} | {', '.join(s['assets'])} |")
    L += ["", "Drawn in code (never generated art): every number, card, clock, badge, bar and the disclaimers.", "", "## Missing items and risks", "",
          "1. **No portrait-native art.** The sage office plate is a 4K landscape and is cropped to 9:16 (about 1.85x), as in the Three Bills Short; the two Alex stills (1920x1088 and the approved 1672x941) are enlarged about 1.8x and 2x for portrait crops, so they are softer than the landscape film. **Brief, only if you find them too soft:** \"Extend the approved Alex scene art to vertical 9:16 full-bleed images at 1080x1920 or larger, keeping the exact character, colours and flat 2D linework\".",
          "2. **Only two Alex story beats.** The other Alex stills in the long film are 1024x576 (Space) or 1344x768 and would enlarge 2.5-3.3x in portrait, so they are not used. The pressure story is told with Ren and code-drawn clock, badge and figures; 13 of 22 beats are Ren shots (the long film is also about half Ren).",
          "3. Ren and Alex never share a frame (Alex exists only as stills). Ren's mouth windows come from the long film's frame scan (closed); Ren stands at the Three Bills Short's approved portrait position beside the chair.",
          "4. No captions are planned (not required); say if you want word-by-word captions."]
    (HERE / "ASSET_REQUIREMENTS.md").write_text("\n".join(L) + "\n"); print(len(scenes), "beats,", nf, "frames,", cues["duration"], "s")
    for s in scenes: d = (s["end_frame"] - s["start_frame"]) / FPS; print(f"  {s['id']:14s} {s['start_frame'] / FPS:6.2f}-{s['end_frame'] / FPS:6.2f} {d:4.2f}s {s['kind']:11s}{'  (justified)' if s.get('timing_justification') else ''}")
if __name__ == "__main__": main()
