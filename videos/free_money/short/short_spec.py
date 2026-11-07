"""The 1-minute Short: beats (scenes), asset bindings, manifest and asset-requirements report, all generated from one place.

  project/.tools/venv/bin/python videos/free_money/short/short_spec.py        # rewrites production.json, short_spec.json, ASSET_REQUIREMENTS.md

Beats are tied to the narration cues (short_cues.json). Each is 2-4 s unless it carries a timing_justification (v3 Shorts rules).
Only the first 360 frames (15 s) are rendered until the owner approves the prototype.
"""
import hashlib, json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
FPS = 24
TOTAL_S = 57.5
DISCLAIMER = "Educational content only, not financial advice."

# id, start s, end s, kind, composition, narration, action, motion_purpose, assets, fullscreen environment, justification
B = [
 ("stub-hook", 0.00, 3.90, "action", "stub-closeup-plan-panel", "I was 28 when Dev held up my pay stub and asked me one question.",
  "Dev's pay stub fills the frame; the match line glows and a panel shows one employer's example plan: You 2%, Employer 2%, the limit ghosted at 4%",
  "Show the overlooked employer benefit in the first seconds, without sound", ["dev", "porch"], False, ""),
 ("porch-question", 3.90, 6.73, "action", "porch-two-shot", "\"Who's keeping the difference?\" Then he pointed at one line,",
  "Ren and Dev stand on the porch; the question appears; slow push toward Dev and the stub",
  "Establish the conflict between the two people", ["ren_fs", "dev", "porch"], True, ""),
 ("stub-line", 6.73, 9.71, "action", "stub-line-closeup", "and my stomach dropped. For three years,",
  "The glowing 'Employer match: 2%' line pulses, then darkens and sinks",
  "Show the consequence of the moment of discovery", ["dev", "porch"], False, ""),
 ("three-years", 9.71, 11.37, "presenter", "bust-with-three-stubs", "I'd been turning down free money.",
  "Ren thinks while three pay stubs, each with the same 2% match, stack in above him",
  "Show the same decision repeated each year", ["ren_r3", "office"], False,
  "Ends exactly on the sentence boundary where the page peels into age 25; three stubs need about 1.6 s"),
 ("office-age25", 11.37, 13.88, "action", "office-standing-age25", "Twenty-five. First real job.",
  "Ren stands by the desk and laptop; a single 'Age 25' label appears", "Establish the change in time and place", ["ren_fs", "office"], True, ""),
 ("salary-card", 13.88, 16.79, "presenter", "bust-salary-card", "Forty-four thousand a year, and I felt like I'd made it.",
  "Ren, hand on chest; one salary card '$44,000 salary' appears on the word", "Introduce the one salary figure at the moment it is spoken",
  ["ren_r2", "office"], False, ""),
 ("lot-lease", 16.79, 19.56, "action", "parking-lot-standing", "So I did what felt right and leased a brand-new car,",
  "Ren stands in the parking lot beside the car; slow push", "Change of location: the lease", ["ren_fs", "lot"], True, ""),
 ("phone-489", 19.56, 21.90, "graphic", "phone-lease-closeup", "four hundred and eighty-nine dollars a month.",
  "A phone slides up showing 'Car lease' and $489 per month", "Show the figure at the moment it is spoken, on the story's own phone", ["office"], False, ""),
 ("folder-page6", 21.90, 24.50, "action", "folder-page6-closeup", "Somewhere on page six it said the company would match every dollar I put into my retirement plan,",
  "The HR folder slides in; the camera pushes to the PAGE 6 tab", "Reveal where the match was written", ["folder", "office"], False, ""),
 ("match-coins", 24.50, 27.18, "graphic", "you-and-employer-coins", "match every dollar I put into my retirement plan,",
  "One employee coin is matched by one employer coin, then stacks grow equally", "Explain dollar-for-dollar matching", ["office"], False, ""),
 ("match-strip", 27.18, 28.78, "graphic", "folder-match-strip", "up to four percent of my salary.",
  "The 'We match 100%' strip lights up on the folder page; 'up to 4%' appears", "Show the limit of this one employer's match", ["folder"], False,
  "Single clause of narration (1.6 s); the strip needs to be readable and the next beat starts on the next clause"),
 ("picked-two", 28.78, 31.86, "graphic", "benefits-screen-two-percent", "I picked two percent, because two sounded responsible,",
  "The contribution slider moves to 2%; the dashed 'up to 4%' appears", "Show the decision against the limit", ["office"], False, ""),
 ("lease-urgent", 31.86, 34.41, "graphic", "phone-lease-urgent", "and the lease sounded urgent.",
  "A 'Payment due' banner drops onto the lease phone", "Show why the lease won", ["office"], False, ""),
 ("jars-two", 34.41, 36.83, "graphic", "two-jars", "I put in two, so they put in two. The other two percent?",
  "You and Employer jars fill to 2%; a dashed ghost level rises above the employer's", "Show the unpaid half of the match", ["office"], False, ""),
 ("never-paid", 36.83, 40.17, "graphic", "ghost-jar-never-paid", "It wasn't saved for later. It just never got paid.",
  "The ghost level is labelled 'Never paid'", "Say what happened to the other 2%", ["office"], False, ""),
 ("missed-880", 40.17, 43.08, "graphic", "ledger-880", "That was eight hundred and eighty dollars the first year.",
  "A ledger shows Age 25, $44,000 and 'Missed match: $880'", "Show the first year's cost", ["office"], False, ""),
 ("toggle-app", 43.08, 46.86, "action", "phone-app-toggle", "I went home, opened the app on my phone, and changed two to four.",
  "The retirement app slides in at 2% and the toggle moves to 4%", "Show the fix and how simple it is", ["office"], False, ""),
 ("ninety-seconds", 46.86, 49.05, "graphic", "ninety-seconds-badge", "It took ninety seconds. Ninety seconds,",
  "A '90 seconds' badge pops on the phone", "Show how little time it took", ["office"], False, ""),
 ("three-years-late", 49.05, 51.65, "presenter", "bust-three-years-late", "three years late. You don't have to max it out.",
  "Ren, rueful, with a '3 years late' tag", "Land the regret, then the reassurance", ["ren_r1", "office"], False, ""),
 ("free-part", 51.65, 53.66, "presenter", "bust-free-part", "You just don't want to skip the free part.",
  "Ren, hand on chest, with the line as a card", "State the takeaway", ["ren_r2", "office"], False, ""),
 ("collect-owed", 53.66, 57.50, "presenter", "office-standing-collect", "Before you cut a single thing, collect what you're already owed.",
  "Ren presents toward the desk; 'Collect what you're owed' card; the disclaimer holds for the last two seconds", "Close with the call to action and the disclaimer",
  ["ren_fp", "office"], True, "Holds 0.84 s past the last word so the exact end disclaimer is readable for 2 s"),
]

ASSETS = [  # id, kind, path (repo-relative), approval evidence
 ("script", "script", "scripts/Ren_Free_Money_Script.md", "Owner supplied the script 7 Nov 2026; narration used word for word; Gate 3 'rough cut approved'"),
 ("audio", "audio", "videos/free_money/short/short_audio_raw.wav", "Cut from the approved long-form narration (voice/S1-S7.wav), no resynthesis; owner approved the long video narration at Gate 3 ('rough cut approved') and 'Approved, great' on the final"),
 ("renderer", "renderer", "videos/free_money/short/fm_short.py", "Adapter under the Shorts launcher; reuses the approved ren_stage placement (owner request 7 Nov 2026)"),
 ("configuration", "configuration", "videos/free_money/short/short_spec.json", "Generated from short_spec.py: beats and timings tied to short_cues.json"),
 ("ren_r1", "character", "videos/free_money/matted/Ren_1_neutral.png", "Approved Ren still (library/ren_approved/Ren_1_neutral.jpg), matted; owner 'style lock approved' 7 Nov 2026"),
 ("ren_r2", "character", "videos/free_money/matted/Ren_2_hand_on_chest_talking.png", "Approved Ren still, matted; 'style lock approved'"),
 ("ren_r3", "character", "videos/free_money/matted/Ren_3_thinking_bust.png", "Approved Ren still, matted; 'style lock approved'"),
 ("ren_fs", "character", "videos/free_money/matted/Ren_full_body_standing.png", "Approved Ren still, matted; 'style lock approved'"),
 ("ren_fp", "character", "videos/free_money/matted/Ren_full_body_presenting.png", "Approved Ren still, matted; 'style lock approved'"),
 ("dev", "character", "library/supporting_assets/characters/Dev_pay_stub.png", "Supporting character from the owner's asset pack; style option (b) accepted at 'style lock approved'"),
 ("porch", "environment", "library/supporting_assets/backgrounds/Porch_background_16x9.png", "Owner's asset pack plate; 'style lock approved'"),
 ("office", "environment", "library/supporting_assets/backgrounds/Office_background_16x9.png", "Owner's asset pack plate; 'style lock approved'"),
 ("lot", "environment", "library/supporting_assets/backgrounds/Office_parking_lot_car_16x9.png", "Owner's asset pack plate; 'style lock approved'"),
 ("folder", "prop", "library/supporting_assets/props/HR_folder_page6_prop.png", "Owner's asset pack prop; baked-in text accepted for this video at 'style lock approved'"),
 ("typography", "font", "project/remotion/public/fonts/fredoka-latin-700-normal.woff2", "Fredoka, the established house typeface"),
]


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def f(t):
    return round(t * FPS)


def main():
    cues = json.loads((HERE / "short_cues.json").read_text())
    spec = {"fps": FPS, "frames": f(TOTAL_S), "disclaimer": DISCLAIMER, "narration_s": cues["duration"], "beats": []}
    scenes, cursor = [], 0
    for i, (sid, a, b, kind, comp, narr, action, purpose, assets, full, just) in enumerate(B):
        fa, fb = (0 if i == 0 else f(a)), (f(TOTAL_S) if i == len(B) - 1 else f(b))
        assert fa == cursor and fb > fa, sid
        cursor = fb
        spec["beats"].append(dict(id=sid, start_frame=fa, end_frame=fb, kind=kind, composition=comp, narration=narr))
        s = dict(id=sid, start_frame=fa, end_frame=fb, kind=kind, composition=comp, action=action, motion_purpose=purpose, assets=assets,
                 animations=[sid + "-motion"], environment_fullscreen=full)
        if just:
            s["timing_justification"] = just
        scenes.append(s)
    (HERE / "short_spec.json").write_text(json.dumps(spec, indent=1))
    manifest = {"schema_version": 1, "title": "I Said No to Free Money for 3 Years: 1-minute Short (derived from the long video)", "width": 1080, "height": 1920, "fps": FPS,
                "frames": f(TOTAL_S), "full_bleed": True, "permanent_border": False, "asset_report": "ASSET_REQUIREMENTS.md", "layout_evidence": "layout.json",
                "prototype": "prototype.mp4", "prototype_report": "prototype.qa.json",
                "assets": [dict(id=i, kind=k, path=p, sha256=sha(p) if (ROOT / p).exists() else "MISSING", status="approved", approval_evidence=e) for i, k, p, e in ASSETS],
                "scenes": scenes}
    manifest["assets"] = [dict(a, path=str(Path("../../..") / a["path"])) for a in manifest["assets"]]
    # audio cues: one per sentence-ish group, from the real cue map
    words, groups, cur = cues["words"], [], []
    for w in words:
        cur.append(w)
        if w["word"][-1] in '.?!"”':
            groups.append(dict(start=cur[0]["start"], end=cur[-1]["end"], text=" ".join(x["word"] for x in cur))); cur = []
    if cur:
        groups.append(dict(start=cur[0]["start"], end=cur[-1]["end"], text=" ".join(x["word"] for x in cur)))
    manifest["audio_cues"] = groups
    (HERE / "production.json").write_text(json.dumps(manifest, indent=1, ensure_ascii=False))
    # asset requirements report
    L = ["# Asset requirements report: 1-minute Short from \"I Said No to Free Money for 3 Years\"", "",
         "Prepared before rendering, under the v3 Shorts rules (asset-first checkpoint). **Status: prototype (first 15 s) only; the complete Short is not rendered until the owner approves the prototype.**", "",
         "## Narration", f"- {cues['duration']:.2f} s, {len(cues['words'])} words, cut from the approved long-form narration (`videos/free_money/voice/S1..S7.wav`) by `short_audio.py`: whole sentences, script order, wording unchanged.",
         "- No new synthesis, speed change, stretching or inserted silence. Excerpts start 0.05 s before the first word and keep up to 0.22 s of the original audio after the last word; they are joined exactly as cut.",
         "- Joins between non-adjacent sentences are therefore tighter than in the long video: **listen to every join** (owner ear check; I cannot hear audio).", "",
         "## Inventory (all approved, hashes in `production.json`)", "", "| Id | Kind | Path | SHA-256 (first 12) | Provenance |", "|---|---|---|---|---|"]
    for i, k, p, e in ASSETS:
        L.append(f"| {i} | {k} | `{p}` | {sha(p)[:12] if (ROOT / p).exists() else 'MISSING'} | {e} |")
    L += ["", "## Scenes", "", "| Scene | Frames | Seconds | Composition | Action | Assets |", "|---|---|---|---|---|---|"]
    for s in scenes:
        L.append(f"| {s['id']} | {s['start_frame']}-{s['end_frame']} | {(s['end_frame'] - s['start_frame']) / FPS:.2f} | {s['composition']} | {s['action']} | {', '.join(s['assets'])} |")
    L += ["", "Drawn in code (never generated artwork): every number, label, card, jar, coin, phone screen, toggle, badge, ledger and the disclaimer.", "",
          "## Missing items and risks", "",
          "1. **No portrait-native plates.** The approved office, porch and parking-lot plates are 1672x941 landscape. A 9:16 crop is 529x941 plate pixels shown at 1080x1920, a 2.04x enlargement. The art is flat and soft, so this may look slightly soft; I will judge it on the prototype at full size. **Brief, only if the owner finds it too soft:** \"Extend the approved [office / porch / parking lot] plate to a vertical 9:16 full-bleed image at 1080x1920 or larger. Preserve the exact room, furniture, colours, lighting and flat 2D linework of the attached approved plate. Background only: no people, text, labels or borders.\" Reference: the exact plate file named above. New plate approval required.",
          "2. **Ren is standing, not seated** (no seated pose exists); he is placed with the shared ren_stage scale and grounding rules.",
          "3. **Supporting character** Dev has one pose; the stub close-ups are enlarged about 3x from a 160 px stub and will be soft: the glowing line is drawn in code and stays sharp.",
          "4. **HR folder text** is baked into the supplied art (accepted for this video only at the style lock).",
          "5. No captions are planned (not required by the rules); say if you want word-by-word captions."]
    (HERE / "ASSET_REQUIREMENTS.md").write_text("\n".join(L) + "\n")
    print(len(scenes), "scenes,", f(TOTAL_S), "frames,", cues["duration"], "s narration")
    for s in scenes:
        d = (s["end_frame"] - s["start_frame"]) / FPS
        flag = "" if 2 <= d <= 4 else ("  (justified)" if s.get("timing_justification") else "  <== OUTSIDE 2-4 s")
        print(f"  {s['id']:18s} {d:4.2f}s {s['kind']:9s}{flag}")


if __name__ == "__main__":
    main()
