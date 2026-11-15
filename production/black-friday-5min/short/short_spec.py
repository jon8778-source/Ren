"""The ~33 s Short (revision 2) from the Black Friday long video: beats, asset bindings, manifest (production.json), short_spec.json and ASSET_REQUIREMENTS.md, generated from one place.
  project/.tools/venv/bin/python production/black-friday-5min/short/short_spec.py
Each beat starts at the first spoken word of its phrase (short_cues.json). Only the first 360 frames (15 s) are rendered until the owner approves the prototype."""
import hashlib, json, re
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[2]; FPS = 24; DISCLAIMER = "Educational content only, not financial advice."
# id, kind, composition, phrase, action, motion purpose, assets
B = [
 ("hook-saved", "story_still", "alex-leaves-shop-107", "He saved one hundred and seven dollars on", "Alex walks out of the shop with two bags (slow push); a green 'Saved $107' chip slides in; opening educational chip", "Open on the claim", ["s1c2"]),
 ("hook-checkout", "story_still", "alex-checkout-face", "Black Friday", "Alex at the checkout counter, placing a coat, a gift and a charger box (crop on Alex)", "Cut to the spending", ["s3c1"]),
 ("hook-spent", "story_still", "alex-checkout-items-spent-more", "but spent more money!", "Closer crop of the checkout items; a red 'Spent MORE' card lands", "Land the twist", ["s3c1"]),
 ("website", "presenter", "ren-left-website", "Then Alex opens a shop's website.", "Ren holds a phone; a 'Shop website' card", "Rewind to the story", ["ren_phone", "sage"]),
 ("clock", "graphic", "countdown-clock", "A countdown clock is ticking.", "A navy countdown clock counts down in code", "Show the pressure tactic", ["sage"]),
 ("badge", "graphic", "only-3-left", "A badge says only three left.", "A red ONLY 3 LEFT badge pops", "Show the scarcity tactic", ["sage"]),
 ("announces", "presenter", "ren-left-saved-107", "The website cheerfully announces that Alex has saved one hundred and seven dollars.", "Ren points at the store's '$107 saved' card", "The store's claim", ["ren_point", "sage"]),
 ("thing", "story_still", "alex-compares-coats", "And here's the thing.", "Alex compares two coats in the shop (slow push)", "Cut to Alex shopping as the claim turns", ["s2c2"]),
 ("not-saved", "presenter", "ren-left-struck-107", "Alex hasn't saved one hundred and seven dollars.", "Ren listens; the '$107 saved' figure is struck through", "Contradict the claim", ["ren_listen", "sage"]),
 ("spend-183", "graphic", "parts-183", "Alex is about to spend one hundred and eighty-three.", "The three items $48 + $105 + $30 add to $183", "Show the real cost", ["sage"]),
 ("rule-4", "presenter", "ren-left-rule4", "Rule four: let it sit for twenty-four hours.", "Ren points down-right; RULE 4 tag", "Rule four", ["ren_point_down", "sage"]),
 ("sleep", "graphic", "moon-to-sun", "It just means the answer has to survive a night's sleep.", "A moon becomes a sun: 'Still want it tomorrow?'", "The 24-hour idea", ["sage"]),
 ("tally-a", "story_still", "alex-relaxed-37-under", "That's thirty-seven under budget,", "Approved art of Alex at ease in the kitchen; a '$37 under budget' card", "The calm result", ["home"]),
 ("tally-b", "presenter", "ren-left-78-less", "and seventy-eight dollars less than the impulse cart.", "Ren presents (mirrored palm); the '$78 less' card", "The gap", ["ren_present", "sage"]),
 ("closing", "presenter", "ren-left-full-video", "Watch the full Black Friday video to see all five rules.", "Ren points at a 'Watch the full video' card; the exact disclaimer holds for the last two seconds", "Prompt to watch the full video", ["ren_point", "sage"]),
]
def lib(n): return f"assets/ren_library/{n}.mp4"
EV_VIDEO = "Used in the owner-approved long video ('Approved', 14 Nov 2026, SHA-256 eef4d914...)"
EV_NEW = "Owner approved the narration of this revision ('Approved, proceed with existing stills', 15 Nov 2026); two new lines (hook, closing) synthesised with the approved Qwen clone, the rest cut from the approved long-video audio"
ASSETS = [
 ("script", "script", "production/black-friday-5min/short/REVISION_PLAN.md", "Revision 2 narration, approved by the owner ('Approved, proceed with existing stills', 15 Nov 2026); the long film's script was approved 14 Nov 2026"),
 ("audio", "audio", "production/black-friday-5min/short/short_audio_raw.wav", EV_NEW),
 ("renderer", "renderer", "production/black-friday-5min/short/render_short.py", "Portrait adapter under the Shorts launcher; reuses the long film's Ren matting and the Three Bills Short layout code"),
 ("cards", "configuration", "production/black-friday-5min/short/bf_short_ui.py", "Portrait card builders (code-drawn text and figures from data/assumptions.csv); hashed so a card change invalidates the approval"),
 ("configuration", "configuration", "production/black-friday-5min/short/short_spec.json", "Generated from short_spec.py: beats and timings tied to short_cues.json"),
 ("ren_phone", "character", lib("ren_hold_phone"), "Approved animated Ren library clip; " + EV_VIDEO), ("ren_point", "character", lib("ren_point_right"), "Approved animated Ren library clip; " + EV_VIDEO),
 ("ren_present", "character", lib("ren_present_palm_left"), "Approved animated Ren library clip (mirrored); " + EV_VIDEO), ("ren_listen", "character", lib("ren_idle_listen"), "Approved animated Ren library clip; " + EV_VIDEO),
 ("ren_point_down", "character", lib("ren_point_down_right"), "Approved animated Ren library clip; " + EV_VIDEO),
 ("sage", "environment", "videos/unclaimed_401k/art/plates/SAGE_4k.png", "Ren's approved sage home office (REN_VIDEO_RULES.md), used in the approved long video"),
 ("s1c2", "environment", "production/black-friday-5min/assets/stills_batch2/candidates/S1_shop_entrance_c2.png", "Alex shop-exit candidate (FLUX.2-dev from the approved Alex art), used in the owner-approved long video; no separate art approval; 1920x1088, enlarged about 1.8x for a portrait crop"),
 ("s2c2", "environment", "production/black-friday-5min/assets/stills_batch2/candidates/S2_compare_coats_c2.png", "Alex compares-coats candidate, used in the owner-approved long video; no separate art approval; 1920x1088, enlarged about 1.8x"),
 ("s3c1", "environment", "production/black-friday-5min/assets/stills_batch2/candidates/S3_checkout_c1.png", "Alex checkout candidate, used in the owner-approved long video; no separate art approval; 1920x1088, enlarged about 1.8x (two crops)"),
 ("home", "environment", "production/black-friday-5min/assets/approved_alex/alex-home.png", "Approved coffee-v3 art 'Alex pours French press coffee' (SHA-256 5ff172ba...), restored from codex/ren-approved-v3; 1672x941, enlarged about 2x"),
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
    man = {"schema_version": 1, "title": "Ren | Black Friday: the sale that tests you: ~33 s Short, revision 2 (derived from the long video)", "width": 1080, "height": 1920, "fps": FPS, "frames": nf, "full_bleed": True, "permanent_border": False, "asset_report": "ASSET_REQUIREMENTS.md",
           "layout_evidence": "layout.json", "prototype": "prototype.mp4", "prototype_report": "prototype.qa.json",
           "assets": [dict(id=i, kind=k, path=str(Path("../../..") / p), sha256=sha(p) if (ROOT / p).exists() else "MISSING", status="approved", approval_evidence=e) for i, k, p, e in ASSETS], "scenes": scenes}
    groups, cur = [], []
    for w in words:
        cur.append(w)
    man["audio_cues"] = [dict(start=words[0]["start"], end=words[-1]["end"], text=" ".join(w["word"] for w in words))]
    (HERE / "production.json").write_text(json.dumps(man, indent=1, ensure_ascii=False))
    L = ["# Asset requirements report: ~1-minute Short from \"Black Friday: the sale that tests you\"", "", "Prepared before rendering (Shorts rules, asset-first checkpoint). **Status: prototype (first 15 s) only; the complete Short is not rendered until the owner approves the prototype.**", "",
         "## Narration", f"- {cues['duration']:.2f} s, {len(words)} words, cut from the approved long-video narration by `short_audio.py`: {len(cues['sentences']) - 2} excerpts of whole script sentences from the approved long-video audio, plus two NEW lines (the owner's hook and a closing prompt to watch the full video) synthesised with the approved Qwen clone after the owner approved the wording.",
         "- No new synthesis, speed change, stretching or inserted silence; each excerpt starts 0.05 s before its first word and keeps up to 0.22 s of the original audio after the last (never past the next word). **The joins between the excerpts and the two new lines are tighter than in the long video: listen to each** (I cannot hear audio). The figure 107 repeats by design.", "",
         "## Inventory (hashes in `production.json`)", "", "| Id | Kind | Path | SHA-256 (first 12) | Provenance |", "|---|---|---|---|---|"]
    for i, k, p, e in ASSETS: L.append(f"| {i} | {k} | `{p}` | {sha(p)[:12] if (ROOT / p).exists() else 'MISSING'} | {e} |")
    L += ["", "## Scenes", "", "| Scene | Frames | Seconds | Composition | Action | Assets |", "|---|---|---|---|---|---|"]
    for s in scenes: L.append(f"| {s['id']} | {s['start_frame']}-{s['end_frame']} | {(s['end_frame'] - s['start_frame']) / FPS:.2f} | {s['composition']} | {s['action']} | {', '.join(s['assets'])} |")
    L += ["", "Drawn in code (never generated art): every number, card, clock, badge, bar and the disclaimers.", "", "## Missing items and risks", "",
          "1. **No portrait-native art.** The sage office plate is a 4K landscape and is cropped to 9:16 (about 1.85x), as in the Three Bills Short; the three API stills (1920x1088) are enlarged about 1.8x and the approved coffee art (1672x941) about 2x for portrait crops, so they are softer than the landscape film. **Brief for portrait-native Alex shopping art, if wanted:** \"Alex browsing a clothes rack, holding a price tag, queueing with bags, carrying bags out of a shop: same character, hair, sage overshirt, white sneakers and flat 2D style as the approved coffee art, vertical 9:16 at 1080x1920 or larger, blank signs and tags\" (not generated: the Hugging Face API credits ran out).",
          "2. **Alex cutaways are limited to the existing sharp stills**: shop exit, checkout (two crops), compares coats, and the approved kitchen art (5 of 15 beats). The other stills would enlarge 2.5-3.3x in portrait and are not used. S1 c2, S2 c2 and S3 c1 were used in the owner-approved long film but never approved as separate art.",
          "3. Ren is in 6 of 15 beats (2-3.5 s each) and never shares a frame with Alex (Alex exists only as stills). Ren's mouth windows come from the long film's frame scan (closed); Ren stands at the Three Bills Short's approved portrait position beside the chair.",
          "4. No captions are planned (not required); say if you want word-by-word captions."]
    (HERE / "ASSET_REQUIREMENTS.md").write_text("\n".join(L) + "\n"); print(len(scenes), "beats,", nf, "frames,", cues["duration"], "s")
    for s in scenes: d = (s["end_frame"] - s["start_frame"]) / FPS; print(f"  {s['id']:14s} {s['start_frame'] / FPS:6.2f}-{s['end_frame'] / FPS:6.2f} {d:4.2f}s {s['kind']:11s}{'  (justified)' if s.get('timing_justification') else ''}")
if __name__ == "__main__": main()
