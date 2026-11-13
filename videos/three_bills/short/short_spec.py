"""The 1-minute Short from the Three Bills episode: beats, asset bindings, manifest and asset-requirements report, generated from one place.

  project/.tools/venv/bin/python videos/three_bills/short/short_spec.py      # rewrites production.json, short_spec.json, ASSET_REQUIREMENTS.md

Each beat starts at the first spoken word of its phrase (short_cues.json). Only the first 360 frames (15 s) are rendered until the owner approves the prototype.
"""
import hashlib, json, re
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[2]; FPS = 24
DISCLAIMER = "Educational content only, not financial advice."
# id, kind, composition, phrase, action, motion purpose, assets, fullscreen environment
B = [
 ("ren-hook", "presenter", "ren-left-title-card", "Three bills. Thirty days.", "Ren (genuine clip, presenting) beside a '3 bills / 30 days' card; the opening educational chip shows", "Introduce the host and the premise", ["ren_present", "sage"], True),
 ("car-breakdown", "action", "lot-maya-car-key", "First, Maya's car broke down.", "Maya surprised beside the car; the car key spins and stops", "Show bill one as an action", ["maya", "lot"], True),
 ("dental-invoice", "graphic", "invoice-urgent", "Then came an urgent dental bill.", "An urgent $390 invoice drops onto the table and the URGENT stamp lands", "Show bill two as an object", ["lot"], False),
 ("porch-worse", "action", "porch-maya-worried", "And just when she thought the month couldn't get worse,", "Maya on the porch, worried with her phone; slow push", "Build the tension before the third bill", ["maya", "porch"], True),
 ("kitchen-leak", "story_still", "sink-leak-portrait", "a pipe leaked beneath her kitchen sink.", "The sink-leak illustration (pipe, sink, bucket) with an animated drip and ripple", "Show bill three", ["kitchen"], True),
 ("ren-total", "presenter", "ren-left-equation", "The total? Two thousand two hundred dollars.", "Ren shrugs; the three bills and their total appear in a column", "State the total once", ["ren_shrug", "sage"], True),
 ("savings-app", "action", "office-maya-phone-balance", "But when Maya opened her savings app afterward, she didn't feel proud.", "Maya at her desk looks worried at her phone; a savings card shows $2,600 falling to $400", "Show the emotional low", ["maya", "office"], True),
 ("gone-backwards", "action", "porch-maya-closeup-bubble", "She saw how much her balance had fallen and thought, I've gone backwards.", "Close-up of Maya at dusk; a thought bubble appears", "Land the hook's worry", ["maya", "porch"], True),
 ("ren-why", "presenter", "ren-left-not-backwards", "Here's why she hadn't.", "Ren points; a 'Not backwards' chip appears", "Turn the story from worry to explanation", ["ren_point", "sage"], True),
 ("card-paid-off", "action", "porch-maya-paid-off", "Once the card was paid off, she opened a separate savings account", "Maya relieved on the porch; a 'Paid off' stamp lands on a credit card", "Show the fresh start", ["maya", "porch"], True),
 ("auto-transfer", "graphic", "phone-auto-transfer", "and set up an automatic transfer of fifty dollars every week.", "A phone shows the $50 automatic transfer; the toggle switches on", "Show the one habit", ["office"], False),
 ("ren-fifty-two", "presenter", "ren-left-fund-equation", "Fifty dollars a week, for fifty-two weeks, gave her two thousand six hundred dollars.", "Ren opens his arms toward the finished sum $50 x 52 = $2,600", "Show the fund and its source", ["ren_open", "sage"], True),
 ("money-was-there", "action", "lot-maya-answer", "But this time, she had an answer. The money was already there.", "Maya relieved beside the car; 'The money was already there' card", "Pay off the hook", ["maya", "lot"], True),
 ("three-bills-gone", "action", "office-maya-fund-tank", "Three bills in thirty days. Two thousand two hundred dollars gone.", "Maya at her desk; the fund tank drains from $2,600", "Show the cost of the month", ["maya", "office"], True),
 ("four-hundred", "graphic", "phone-400-left", "Four hundred dollars left.", "The savings phone shows $400 left", "Land the remaining balance", ["office"], False),
 ("ren-smaller", "presenter", "ren-left-fund-smaller", "An emergency fund is supposed to get smaller when there's an emergency.", "Ren nods; the fund tank drops from $2,600 to $400", "State the idea", ["ren_nod", "sage"], True),
 ("using-it", "action", "porch-maya-failure-struck", "Using it isn't failure.", "Close-up of Maya, relieved; 'Failure' is struck through", "Reframe the spend", ["maya", "porch"], True),
 ("its-the-job", "action", "lot-maya-the-job", "That's literally the job it was hired to do.", "Maya in the morning light; 'Its job: pay for emergencies' card", "Land the takeaway", ["maya", "lot"], True),
 ("ren-question", "presenter", "ren-left-question", "What bill would have shaken you a year ago, but feels more manageable today?", "Ren thinks; the question card appears", "Ask the audience", ["ren_think", "sage"], True),
 ("closing", "action", "porch-maya-sunset-close", "I'd love to hear it in the comments.", "Maya at sunset on the porch; the exact disclaimer holds for the last two seconds", "Close with the call to comment and the disclaimer", ["maya", "porch"], True),
]
def lib(n): return f"assets/ren_library/{n}.mp4"
ASSETS = [
 ("script", "script", "videos/three_bills/script/SCRIPT.md", "Owner's v2 script, 'Script approved' 9 Nov 2026 (SHA-256 14801320...); the full episode was approved ('Approved, good work Claude')"),
 ("audio", "audio", "videos/three_bills/short/short_audio_raw.wav", "Cut from the approved full-episode narration (voice/H, L, D1-D7), no resynthesis"),
 ("renderer", "renderer", "videos/three_bills/short/render_short.py", "Portrait adapter under the Shorts launcher; reuses the approved ren_stage placement and the episode's Maya and Ren rendering code"),
 ("configuration", "configuration", "videos/three_bills/short/short_spec.json", "Generated from short_spec.py: beats and timings tied to short_cues.json"),
 ("maya", "character", "videos/three_bills/art/cast/maya_01_neutral.png", "Owner-approved four-pose Maya sheet ('Maya images approved', 9 Nov 2026; hashes in the pack manifest)"),
 ("ren_present", "character", lib("ren_present_palm_left"), "Approved animated Ren library clip (mirrored); approved in the full episode"),
 ("ren_shrug", "character", lib("ren_shrug"), "Approved animated Ren library clip; approved in the full episode"),
 ("ren_point", "character", lib("ren_point_right"), "Approved animated Ren library clip; approved in the full episode"),
 ("ren_open", "character", lib("ren_open_arms"), "Approved animated Ren library clip; approved in the full episode"),
 ("ren_nod", "character", lib("ren_nod_yes"), "Approved animated Ren library clip; approved in the full episode"),
 ("ren_think", "character", lib("ren_thinking"), "Approved animated Ren library clip; approved in the full episode"),
 ("lot", "environment", "library/supporting_assets/backgrounds/Office_parking_lot_car_16x9.png", "Approved plate (Free Money pack; used in the approved episode); 1672x941 landscape, enlarged about 2x for portrait"),
 ("porch", "environment", "library/supporting_assets/backgrounds/Porch_background_16x9.png", "Approved plate (used in the approved episode)"),
 ("office", "environment", "library/supporting_assets/backgrounds/Office_background_16x9.png", "Approved plate (used in the approved episode)"),
 ("sage", "environment", "videos/unclaimed_401k/art/plates/SAGE_4k.png", "Ren's approved sage home office (REN_VIDEO_RULES.md), restored from codex/ren-approved-v3"),
 ("kitchen", "environment", "videos/three_bills/art/plates/kitchen_leak_ref.png", "Sink-leak illustration supplied by the owner (9 Nov 2026); only the pipe/sink/bucket area is used; approved in the full episode ('Approved')"),
 ("typography", "font", "project/remotion/public/fonts/fredoka-latin-700-normal.woff2", "Fredoka, the established house typeface"),
]
def sha(p): return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()
def norm(x): return re.findall(r"[a-z0-9']+", x.lower().replace("’", "'").replace("$", ""))
def main():
    cues = json.loads((HERE / "short_cues.json").read_text()); words = cues["words"]; nf = int(round(cues["duration"] * FPS)); pos, starts = 0, []
    for b in B:
        ph = norm(b[3]); acc = []; k = pos
        while len(acc) < len(ph): acc += norm(words[k]["word"]); k += 1
        assert acc == ph, (b[0], acc, ph); starts.append(0.0 if pos == 0 else words[pos]["start"]); pos = k
    assert pos == len(words), (pos, len(words))
    frames = [0 if i == 0 else round(s * FPS) for i, s in enumerate(starts)] + [nf]; spec = {"fps": FPS, "frames": nf, "disclaimer": DISCLAIMER, "narration_s": cues["duration"], "beats": []}; scenes = []
    for i, (sid, kind, comp, phrase, action, purpose, assets, full) in enumerate(B):
        fa, fb = frames[i], frames[i + 1]; assert fb > fa, sid; d = (fb - fa) / FPS; lim = {"presenter": 5.5, "graphic": 3.5, "story_still": 2.5}.get(kind, 4)
        spec["beats"].append(dict(id=sid, start_frame=fa, end_frame=fb, kind=kind, composition=comp, narration=phrase))
        s = dict(id=sid, start_frame=fa, end_frame=fb, kind=kind, composition=comp, action=action, motion_purpose=purpose, assets=assets, animations=[sid + "-motion"], environment_fullscreen=full)
        if d < 2 or d > 4.0: s["timing_justification"] = f"Beat length {d:.1f} s follows the spoken phrase boundaries; the visual change lands on its words"
        scenes.append(s)
    (HERE / "short_spec.json").write_text(json.dumps(spec, indent=1))
    manifest = {"schema_version": 1, "title": "Ren | Three Bills in 30 Days: 1-minute Short (derived from the long video)", "width": 1080, "height": 1920, "fps": FPS, "frames": nf, "full_bleed": True, "permanent_border": False,
                "asset_report": "ASSET_REQUIREMENTS.md", "layout_evidence": "layout.json", "prototype": "prototype.mp4", "prototype_report": "prototype.qa.json",
                "assets": [dict(id=i, kind=k, path=str(Path("../../..") / p), sha256=sha(p) if (ROOT / p).exists() else "MISSING", status="approved", approval_evidence=e) for i, k, p, e in ASSETS], "scenes": scenes}
    groups, cur = [], []
    for w in words:
        cur.append(w)
        if w["word"][-1] in '.?!"”': groups.append(dict(start=cur[0]["start"], end=cur[-1]["end"], text=" ".join(x["word"] for x in cur))); cur = []
    if cur: groups.append(dict(start=cur[0]["start"], end=cur[-1]["end"], text=" ".join(x["word"] for x in cur)))
    manifest["audio_cues"] = groups; (HERE / "production.json").write_text(json.dumps(manifest, indent=1, ensure_ascii=False))
    L = ["# Asset requirements report: 1-minute Short from \"Three Bills in 30 Days\"", "", "Prepared before rendering (v3 Shorts rules, asset-first checkpoint). **Status: prototype (first 15 s) only; the complete Short is not rendered until the owner approves the prototype.**", "",
         "## Narration", f"- {cues['duration']:.2f} s, {len(words)} words, cut from the approved full-episode narration by `short_audio.py` (excerpts: H s1-7 and s10-12, D1 s5-6, D2 s6-7, D4 s12-14, D5 s9-11, D7 s7-8): whole sentences, script order, wording unchanged.",
         "- No new synthesis, speed change, stretching or inserted silence; excerpts start 0.05 s before the first word and keep up to 0.22 s of the original audio after the last. **The six joins between non-adjacent excerpts are tighter than in the full episode: listen to each** (I cannot hear audio).", "",
         "## Inventory (hashes in `production.json`)", "", "| Id | Kind | Path | SHA-256 (first 12) | Provenance |", "|---|---|---|---|---|"]
    for i, k, p, e in ASSETS: L.append(f"| {i} | {k} | `{p}` | {sha(p)[:12] if (ROOT / p).exists() else 'MISSING'} | {e} |")
    L += ["", "## Scenes", "", "| Scene | Frames | Seconds | Composition | Action | Assets |", "|---|---|---|---|---|---|"]
    for s in scenes: L.append(f"| {s['id']} | {s['start_frame']}-{s['end_frame']} | {(s['end_frame'] - s['start_frame']) / FPS:.2f} | {s['composition']} | {s['action']} | {', '.join(s['assets'])} |")
    L += ["", "Drawn in code (never generated art): every number, card, phone, tank, invoice, credit card, stamp and the disclaimers.", "", "## Missing items and risks", "",
          "1. **No portrait-native plates.** The approved plates are landscape 1672x941; a 9:16 crop is about 529x941 plate pixels at 1080x1920 (2.04x enlargement), so backgrounds are soft. **Brief, only if the owner finds it too soft:** \"Extend the approved [parking lot / porch / office] plate to a vertical 9:16 full-bleed image at 1080x1920 or larger. Preserve the exact scene, colours, lighting and flat 2D linework of the attached approved plate. Background only: no people, text or borders.\" New plate approval required.",
          "2. **Maya is static cut-out art (four poses)**: pose cross-fades, camera pushes and moving props; no walking or reaching. Ren is genuine library animation.",
          "3. The sink-leak image is enlarged about 2x for portrait and cropped to the pipe/sink/bucket area (the figure in the image is outside every crop).",
          "4. Ren is life-size on the plate, so in portrait he fills the left of the frame and cards sit in the narrow right column.", "5. No captions are planned (not required by the rules); say if you want word-by-word captions."]
    (HERE / "ASSET_REQUIREMENTS.md").write_text("\n".join(L) + "\n"); print(len(scenes), "beats,", nf, "frames,", cues["duration"], "s")
    for s in scenes:
        d = (s["end_frame"] - s["start_frame"]) / FPS; print(f"  {s['id']:18s} {s['start_frame'] / FPS:6.2f}-{s['end_frame'] / FPS:6.2f} {d:4.2f}s {s['kind']:11s}{'  (justified)' if s.get('timing_justification') else ''}")
if __name__ == "__main__": main()
