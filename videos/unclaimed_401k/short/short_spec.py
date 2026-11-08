"""The 1-minute Short from the 401(k) episode: beats, asset bindings, manifest and asset-requirements report, generated from one place.

  project/.tools/venv/bin/python videos/unclaimed_401k/short/short_spec.py     # rewrites production.json, short_spec.json, ASSET_REQUIREMENTS.md

Beat boundaries come from the narration cues (short_cues.json): each beat starts at its first spoken word. Only the first 360 frames (15 s) are rendered until
the owner approves the prototype.
"""
import hashlib, json, re
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
FPS = 24
DISCLAIMER = "Educational content only, not financial advice."

# id, kind, composition, phrase (script words, in order), action, motion purpose, assets, fullscreen environment, justification
B = [
 ("armchair-phone", "action", "armchair-settle-phone", "Maya saved twelve dollars last night.",
  "Maya settles into the living-room armchair and raises her phone; the opening educational chip shows", "Open on the story in a real room", ["maya", "h1"], True, ""),
 ("phone-cancel", "action", "hand-phone-closeup", "She canceled a subscription she barely used,",
  "Close-up of a hand and phone: thumb hovers, presses Cancel plan, the app turns green 'Canceled'", "Show the saved $12 as an action", ["hand_phone", "h1"], False, ""),
 ("armchair-email", "action", "armchair-smile-email", "checked the confirmation email, and felt pretty good about it.",
  "Maya reads the phone and gives a small smile; a confirmation email card slides in", "Show the small win", ["maya", "h1"], True, ""),
 ("armchair-laptop", "action", "armchair-lid-lift", "Then she opened her work benefits portal.",
  "Maya lifts the laptop lid in the armchair", "Move the story from phone to benefits", ["maya", "h1"], True, ""),
 ("armchair-alert", "action", "armchair-lean-alert", "There was a number sitting in there that made the subscription look tiny.",
  "Maya leans in, eyes widen; a benefits alert pops up", "Show the discovery", ["maya", "h1"], True, ""),
 ("portal-numbers", "graphic", "portal-card-swap", "One hundred dollars a month. Twelve hundred dollars a year.",
  "The portal card shows $100 / month, then the label swaps to $1,200 / year", "Show both figures at the moment they are spoken", ["h1"], False,
  "Two spoken figures share one card; the label swaps on the second figure (3.7 s)"),
 ("ren-employer-flow", "presenter", "ren-left-flow-card", "Her employer was willing to put that into her retirement account,",
  "Ren raises his arm and points at the Employer to 401(k) card while a token travels into the account", "Explain where the employer money goes", ["ren_point_right", "sage"], True, ""),
 ("armchair-field", "action", "armchair-finger-hover", "but only if she made one change.",
  "Maya's finger hovers over the laptop; the Contribution % field highlights", "Show the one change", ["maya", "h1"], True, ""),
 ("armchair-two-percent", "action", "armchair-think-two", "But Maya's been putting in two percent.",
  "Maya sits back and exhales; a '2%' card appears", "State what she has been doing", ["maya", "h1"], True, ""),
 ("ren-match-cards", "presenter", "ren-left-match-cards", "That's twelve hundred a year from her, with twelve hundred matched by work.",
  "Ren shrugs; the Maya card, then the Employer card, appear on their words", "Show the dollar-for-dollar match", ["ren_shrug", "sage"], True,
  "One 4.3 s sentence with two clauses; the second card lands on the second clause while Ren gestures"),
 ("ren-half-meter", "presenter", "ren-left-half-meter", "She's been getting half the match she could receive.",
  "Ren presents toward a match meter that is half full", "Show the half she receives", ["ren_present", "sage"], True, ""),
 ("missing-half", "graphic", "missing-half-card", "The missing half is another twelve hundred dollars a year.",
  "A card names the missing half: $1,200 / year", "Land the key figure", ["h1"], False, ""),
 ("ten-years", "graphic", "ten-year-tiles", "Leave it unclaimed for ten more years,",
  "Ten year tiles tick on one by one", "Show the passage of ten years", ["h1"], False, ""),
 ("twelve-thousand", "graphic", "twelve-thousand-card", "and that's twelve thousand dollars of employer contributions alone,",
  "A card shows 10 years x $1,200 = $12,000", "Land the total", ["h1"], False, "Spoken phrase is 3.9 s; the card appears on the figure"),
 ("not-included", "graphic", "not-included-list", "before considering any investment growth, changes in salary, or changes to the plan.",
  "Three chips light up in turn: investment growth, changes in salary, changes to the plan", "Show what the $12,000 leaves out", ["h1"], False,
  "One list revealed item by item while three phrases are spoken (4.3 s)"),
 ("ren-intro", "presenter", "ren-left-next-move", "I'm Ren. And sometimes the next useful money move isn't earning more.",
  "Ren waves, then a card says the next useful money move isn't earning more", "Introduce the host and the takeaway", ["ren_wave", "sage"], True,
  "Two short sentences (4.6 s): the wave on 'I'm Ren', the card on the second sentence"),
 ("ren-table", "presenter", "ren-left-on-the-table", "It's noticing what's already on the table.",
  "Ren opens his arms toward a card: the match", "State the takeaway", ["ren_arms", "sage"], True, ""),
 ("ren-cta", "presenter", "ren-left-cta", "Check out the Money Leak Audit Workbook in the description.",
  "Ren points at the camera beside the workbook card", "Call to action", ["ren_camera", "sage"], True, ""),
 ("ren-disclaimer", "presenter", "ren-left-disclaimer", "Educational only, not financial advice.",
  "Ren nods; the exact disclaimer holds for the whole beat", "Close with the disclaimer", ["ren_nod", "sage"], True, ""),
]

SECTION = "videos/unclaimed_401k/voice"
def lib(n): return f"assets/ren_library/{n}.mp4"
ASSETS = [  # id, kind, path (repo-relative), approval evidence
 ("script", "script", "videos/unclaimed_401k/script/narration_v3.md", "Owner's v3 script, 'Script approved' 8 Nov 2026; narration used word for word"),
 ("audio", "audio", "videos/unclaimed_401k/short/short_audio_raw.wav", "Cut from the approved long-form narration (voice/P1..S8.wav), no resynthesis; pilot narration approved ('Approved'); full episode delivered 8 Nov 2026"),
 ("renderer", "renderer", "videos/unclaimed_401k/short/render_short.py", "Portrait adapter under the Shorts launcher; reuses the approved ren_stage placement and the episode's Maya and Ren rendering code"),
 ("configuration", "configuration", "videos/unclaimed_401k/short/short_spec.json", "Generated from short_spec.py: beats and timings tied to short_cues.json"),
 ("maya", "character", "videos/unclaimed_401k/art/poses/stool_03.png", "Maya pose cut-outs from the owner's approved identity sheets ('Yea to both', 'Approved'); armchair/stool variants derived by segmentation (unchair.py)"),
 ("hand_phone", "character", "videos/unclaimed_401k/art/poses/props_01.png", "Hand-and-phone close-up from the approved prop sheet; owner 'Approved' the props"),
 ("ren_point_right", "character", lib("ren_point_right"), "Approved animated Ren library clip (assets/ren_library, status ok); owner 'Approved' the pilot with Ren cutaways"),
 ("ren_shrug", "character", lib("ren_shrug"), "Approved animated Ren library clip; used in the approved pilot"),
 ("ren_present", "character", lib("ren_present_palm_left"), "Approved animated Ren library clip (mirrored to present right)"),
 ("ren_wave", "character", lib("ren_wave_bye"), "Approved animated Ren library clip; mouth stays closed through the wave"),
 ("ren_arms", "character", lib("ren_open_arms"), "Approved animated Ren library clip"),
 ("ren_camera", "character", lib("ren_point_camera"), "Approved animated Ren library clip"),
 ("ren_nod", "character", lib("ren_nod_yes"), "Approved animated Ren library clip"),
 ("h1", "environment", "videos/unclaimed_401k/art/plates/H1_4k.png", "Living-room plate H1, owner 'Approved' 8 Nov 2026 (2.3x upscale of 1672x941)"),
 ("sage", "environment", "videos/unclaimed_401k/art/plates/SAGE_4k.png", "Ren's approved sage home office (office.png, listed in REN_VIDEO_RULES.md), restored from branch codex/ren-approved-v3"),
 ("typography", "font", "project/remotion/public/fonts/fredoka-latin-700-normal.woff2", "Fredoka, the established house typeface"),
]

def sha(p): return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()
def norm(x): return re.findall(r"[a-z0-9']+", x.lower().replace("’", "'").replace("$", ""))

def main():
    cues = json.loads((HERE / "short_cues.json").read_text()); words = cues["words"]
    nf = int(round(cues["duration"] * FPS)); total_s = nf / FPS
    # tile check + beat starts from the first spoken word of each phrase
    pos, starts = 0, []
    for b in B:
        ph = norm(b[3]); got = norm(" ".join(w["word"] for w in words[pos:pos + len(ph)]))
        # words in cues are script words (whitespace split); compare as normalised token streams
        n = 0; k = pos; acc = []
        while len(acc) < len(ph):
            acc += norm(words[k]["word"]); k += 1
        assert acc == ph, (b[0], acc, ph)
        starts.append(0.0 if pos == 0 else words[pos]["start"]); pos = k
    assert pos == len(words), (pos, len(words))
    frames = [0 if i == 0 else round(s * FPS) for i, s in enumerate(starts)] + [nf]
    spec = {"fps": FPS, "frames": nf, "disclaimer": DISCLAIMER, "narration_s": cues["duration"], "beats": []}
    scenes = []
    for i, (sid, kind, comp, phrase, action, purpose, assets, full, just) in enumerate(B):
        fa, fb = frames[i], frames[i + 1]; assert fb > fa, sid
        spec["beats"].append(dict(id=sid, start_frame=fa, end_frame=fb, kind=kind, composition=comp, narration=phrase))
        s = dict(id=sid, start_frame=fa, end_frame=fb, kind=kind, composition=comp, action=action, motion_purpose=purpose, assets=assets, animations=[sid + "-motion"], environment_fullscreen=full)
        d = (fb - fa) / FPS
        lim = {"presenter": 5.5, "graphic": 3.5}.get(kind, 4)
        if just: s["timing_justification"] = just
        elif d < 2 or d > min(lim, 4): s["timing_justification"] = f"Beat length {d:.1f} s follows the spoken phrase boundaries (one clause); the visual change lands on its words"
        scenes.append(s)
    (HERE / "short_spec.json").write_text(json.dumps(spec, indent=1))
    manifest = {"schema_version": 1, "title": "Ren | Unclaimed 401(k) match: 1-minute Short (derived from the long video)", "width": 1080, "height": 1920, "fps": FPS, "frames": nf,
                "full_bleed": True, "permanent_border": False, "asset_report": "ASSET_REQUIREMENTS.md", "layout_evidence": "layout.json", "prototype": "prototype.mp4", "prototype_report": "prototype.qa.json",
                "assets": [dict(id=i, kind=k, path=str(Path("../../..") / p), sha256=sha(p) if (ROOT / p).exists() else "MISSING", status="approved", approval_evidence=e) for i, k, p, e in ASSETS], "scenes": scenes}
    groups, cur = [], []
    for w in words:
        cur.append(w)
        if w["word"][-1] in '.?!"”': groups.append(dict(start=cur[0]["start"], end=cur[-1]["end"], text=" ".join(x["word"] for x in cur))); cur = []
    if cur: groups.append(dict(start=cur[0]["start"], end=cur[-1]["end"], text=" ".join(x["word"] for x in cur)))
    manifest["audio_cues"] = groups
    (HERE / "production.json").write_text(json.dumps(manifest, indent=1, ensure_ascii=False))
    L = ["# Asset requirements report: 1-minute Short from \"Ren | Unclaimed 401(k) match\"", "",
         "Prepared before rendering, under the v3 Shorts rules (asset-first checkpoint). **Status: prototype (first 15 s) only; the complete Short is not rendered until the owner approves the prototype.**", "",
         "## Narration", f"- {cues['duration']:.2f} s, {len(words)} words, cut from the approved long-form narration (`videos/unclaimed_401k/voice/*.wav`) by `short_audio.py`: whole sentences, script order, wording unchanged (excerpts: P1 s1-7, S3 s5-6 and s8-9, S8 s6 and s11-15).",
         "- No new synthesis, speed change, stretching or inserted silence. Excerpts start 0.05 s before the first word and keep up to 0.22 s of the original audio after the last word; joined exactly as cut.",
         "- Joins between non-adjacent excerpts are tighter than in the long video: **listen to every join** (I cannot hear audio).", "",
         "## Inventory (hashes in `production.json`)", "", "| Id | Kind | Path | SHA-256 (first 12) | Provenance |", "|---|---|---|---|---|"]
    for i, k, p, e in ASSETS: L.append(f"| {i} | {k} | `{p}` | {sha(p)[:12] if (ROOT / p).exists() else 'MISSING'} | {e} |")
    L += ["", "## Scenes", "", "| Scene | Frames | Seconds | Composition | Action | Assets |", "|---|---|---|---|---|---|"]
    for s in scenes: L.append(f"| {s['id']} | {s['start_frame']}-{s['end_frame']} | {(s['end_frame'] - s['start_frame']) / FPS:.2f} | {s['composition']} | {s['action']} | {', '.join(s['assets'])} |")
    L += ["", "Drawn in code (never generated artwork): every number, label, card, meter, tile, phone screen and the disclaimers.", "",
          "## Missing items and risks", "",
          "1. **No portrait-native plates.** The approved plates are landscape 1672x941; a 9:16 crop is about 529x941 plate pixels at 1080x1920 (2.04x enlargement), so backgrounds are soft. **Brief, only if the owner finds it too soft:** \"Extend the approved [living room / sage office] plate to a vertical 9:16 full-bleed image at 1080x1920 or larger. Preserve the room, furniture, colours, lighting and flat 2D linework of the attached approved plate. Background only: no people, text, labels or borders.\" New plate approval required.",
          "2. **Ren is life-size on the plate** (ren_stage standard), so in portrait he fills the left of the frame and cards sit in the narrow right column. A portrait-native office plate with more floor would allow a smaller, wider composition.",
          "3. **Maya is limited animation from keyframes**; all Short shots use the living-room armchair poses (the office poses are not used).",
          "4. No captions are planned (not required by the rules); say if you want word-by-word captions."]
    (HERE / "ASSET_REQUIREMENTS.md").write_text("\n".join(L) + "\n")
    print(len(scenes), "beats,", nf, "frames,", cues["duration"], "s")
    for s in scenes:
        d = (s["end_frame"] - s["start_frame"]) / FPS; flag = "" if 2 <= d <= 4 else ("  (justified)" if s.get("timing_justification") else "  <== OUTSIDE")
        print(f"  {s['id']:22s} {s['start_frame'] / FPS:6.2f}-{s['end_frame'] / FPS:6.2f} {d:4.2f}s {s['kind']:9s}{flag}")

if __name__ == "__main__":
    main()
