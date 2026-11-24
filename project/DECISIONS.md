# Ren Video Production & Decision Log

## Production fixes — 24 November 2026 (code alignment and asset promotion; not a new owner decision)

Recorded from the production audit the owner asked to progress on 24 November 2026
(recommendations 1–3). This section records evidence and code alignment only; it does
not record any new owner approval, and nothing here is merged until the owner reviews
the pull request.

- **Qwen x-vector setting — cliplib code was wrong; the rules were right.** The v3
  rules (`REN_LONGFORM_BASELINE.md`, `REN_VIDEO_RULES.md`) state
  `use_xvector_only=True`. Every approved episode voice script already follows them:
  `videos/free_money/gen_voice.py`, `videos/three_bills/gen_voice.py` and
  `videos/unclaimed_401k/gen_voice.py` all build the prompt with
  `x_vector_only_mode=True` and `ref_text=None`, and `videos/three_bills/tb_qa.py`
  (check 12a) asserts `x_vector_only_mode=True` in the episode's voice script.
  `videos/free_money/REPORT.md` had already flagged that the earlier cliplib wrappers
  used `False`. The generic wrappers in `project/cliplib/` (`qwen_voice.py`,
  `qwen_local_voice.py`, `local_voice.py`, dating from 26–27 October 2026, before the
  v3 rules) were the only code still using `False`; they have been aligned to `True`
  (`ref_text=None` locally) in the production-fixes pull request. The sentence in the
  27 October 2026 prototype update below describing cloning "from
  `Audio/ren_reference.wav` plus its exact transcript" describes those earlier
  wrappers and is superseded for voice-prompt construction by the x-vector-only
  standard in `REN_LONGFORM_BASELINE.md`. No voice was synthesised for this fix; the
  owner's standing ear check at the next pilot still applies.
- **Coffee prototype v3 promoted by pull request.** `project/prototypes/coffee-minute-v3/`
  existed only on branch `codex/ren-approved-v3` although `REN_VIDEO_RULES.md` says it
  is published there. Its 110 files have been copied byte-for-byte into the
  production-fixes pull request (all file sizes match the source branch, and the four
  artwork PNGs restored from the base64 chunks match the SHA-256 hashes in
  `artwork/manifest.json` and `validation-approved-baseline.json`). The prototype's
  own README says "Do not merge into main without Jon's instruction" — merging the
  pull request is therefore the owner's decision.
- **Approved-asset registry created.** `project/assets/APPROVED_ASSET_REGISTRY.md`
  (with a JSON version) records what the repository actually proves for Ren, Alex
  and Maya. In particular: Alex has approved episodic prototype artwork only and no
  reusable character asset; Maya's Three Bills poses are not in Git, were recorded
  as approved only second-hand ("per pack record"), and are not the same design as
  the 401(k) episode's Maya — her identity is not locked. No approval is claimed in
  the registry beyond what the cited source documents state.

## Current long-form baseline — 8 November 2026

The owner approved the overall visual and storytelling direction of the 401(k)
video as the new long-form baseline. Read `REN_LONGFORM_BASELINE.md`,
`REN_VIDEO_RULES.md` and `REN_LONGFORM_CHECKLIST.md` for new long-form work.
The white-background, static-bust and Kokoro decisions recorded below are
historical and apply only to legacy work where explicitly required. Do not apply
their automatic Shorts, thumbnail or merge steps to a new long-form request.

## Current prototype update — 27 October 2026

Owner requested the newer hybrid style and voice reference integration. For animation prototypes,
use `cliplib/render_hybrid.py` and `cliplib/README.md`: real Ren clip animation, office backgrounds,
story stills capped at 2.5s, count-up graphics capped at 3.5s, frequent returns to Ren. Qwen Base
clones the voice from `Audio/ren_reference.wav` plus its exact transcript; hosted and local wrappers
are available. No separate voice training is required. No automatic fallback voice or long idle holds.
This overrides the older white-only/static-bust/Kokoro decisions below for the prototype route.
The bundled office and story portrait are placeholders pending approved office/Alex assets.


Repo jon8778-source/Ren; work on branch ccr-a31871f7-ihoco0 (PR #2 → main). Workflow: CLAUDE.md + project/README.md. Setup: `cd project && ./setup.sh`.

## 1. Core aesthetics & style
- Ren (glasses, dark hair, navy jacket) narrates everything; characters never speak.
- Solid plain white background, edge to edge; no gradients, patterns, scenery or office.
- Font Fredoka 500/600/700 only. Colours: ink #13233F, red #E23D3D (cost), green #1E9E5A (save), gold #F5B82E/#C98A0B, muted #7A8496, line #E3E7EE. No new colours.
- Flat 2D cartoon busts; all lettering/prices/numbers drawn in code, never AI lettering.
- No shaking: no talking bob, sway or breathing. Only entrance slide + small pop on pose change. Slow pan/zoom every scene; new visual every 5-7 s.
- Voice: Kokoro-82M, am_michael 0.5 + am_eric 0.5, speed 0.93 (~165 wpm), matched to the owner's "Bank Fee" reference. No music.
- Tone: warm, upbeat storytelling (scenarios, character comparisons); original, never copied.

## 2. Structural formats
- Long video: 16:9 1920x1080, ~5-6 min (~770-940 words). Character in left/right third, cards on the other side. Captions 50px, max 2 lines, above bottom 12% (y<950), long sentences split at a pause. Text ≥40px.
- Shorts: 9:16 1080x1920, ~30 s, 2 per episode, cut from the long video's lines and voice (shorts.json → pipeline/shorts.py → config.vertical.json). Nothing in bottom 420px or under right-hand buttons.
- Thumbnails: 1280x720, 3 options. Chosen: $1,200 ep = C ("WHO COPES BETTER?" low vs high income); $2M ep = A (big number + regretful face + "AND HE NEVER WENT"); $1,000 bonus ep = A ("WHO'S HAPPIER?" Max vs Lena + envelope).
- Pattern: hook with biggest number → meet characters → per-character segment (life, event, outcome, habit) → twist + takeaways → soft CTA.
- Disclaimer "Educational only, not financial advice" on screen at start and end, and in description.
- CTA: "Check out the Money Leak Audit Workbook in the description." Never "free" in video. $2M ep: no workbook mention (owner). Descriptions keep [WORKBOOK LINK].
- Money graphics tagged "Example figures"; conceptual charts "Illustrative".

## 3. Key decisions (chronological)
1. First 9:16 Remotion short "monthly vs yearly" ($9.99→$119.88); Ren art, voice, number spoken in hook.
2. More animation added; later rejected shaking/bobbing and office/walking for long form.
3. "Ahead by 30" (HyperFrames, 9:16, 49 s, office): one-off, not the main format.
4. Long-form pipeline: assumptions.csv → calc.py (+claims.txt) → script.md (numbers as spoken, tagged) → scenes.json → Remotion → qc.py.
5. "The Same $1,200 Surprise" (5:45; Sam, Nina, Claire, Marcus, Richard). Cut from 10 to 6 min. "FREE" removed from workbook graphic.
6. "The Man Who Died With $2 Million" (4:42), owner's script word for word except: "ahead of a lot of people" → "off to a strong start"; "decades later" → "nearly two decades into retirement". EBRI line verified by owner, kept. Thumbnail A + 2 shorts (Frank "next year", Bea life fund).
7. "Two Neighbors, Same $1,000 Bonus" (4:12; new cast Max and Lena at 30 and one year later, locked from the owner's sheets).
   Owner's script, except: all research claims and [VERIFY] lines removed (owner), "hedonic adaptation" line cut,
   US phrasing ("goes to", "booked three months ahead"), and the standing workbook CTA instead of "free 50/30/20 workbook".
   Bonus envelope as the recurring prop. Thumbnail A ("WHO'S HAPPIER?"). Shorts: Max (things fade) and Lena (three-way split).
8. Cut-out puppet rig test (15 s 9:16 walk-in, boots, point, thumbs up): owner found too many errors. Moved to the
   branch lab/animated-ren (never merged into main), which is the test environment for an animated Ren. Not used in episodes. Standing rules unchanged: locked busts, no walking,
   bob, sway or breathing, solid white background.
9. "The $3,000 Trip vs $51,000 at 70" (3:54): owner's brief asked for the puppet rig, music, Poppins and "free" CTA;
   owner chose the locked busts, Ren's voice and the standing rules, and the shorter length. Changes: "Lots of people..."
   and "money tends to go up..." softened; standing CTA. Die With Zero attributions and the 7% assumption verified by the
   owner. $3,000 x 1.07^42 = $51,432.77, shown as $51,433. Owner's backpack/skis/sandcastle icons in project/assets/icons;
   EXPIRES stamp drawn in code. Thumbnail Option 1 (layout j). Shorts: trip vs invest, time buckets.
10. Rejected/avoided: invented stats, unsourced "most/many people" claims, typed numbers on screen, inconsistent character art (Yara 45/70 regenerated from Yara 25), 3-line captions, content in YouTube controls area, shaking, music, coloured backgrounds.

## 4. Active rules for next videos
- "New episode: <topic>" → follow CLAUDE.md. Gates: plan/questions → script OK (before voice) → 60-s pilot → "APPROVED" → full video + QC report → thumbnail choice → 2 shorts.
- Every figure in assumptions.csv; calc.py MATHS OK; every story claim in claims.txt. Real stats need sources.json status "verified" by owner, or cut. Never invent sources.
- Locked cast in project/characters (hashes in manifest.json): Ren(8), Sam/Nina/Claire/Marcus/Richard(5), Frank/Yara/Bea at 25/45/70 (4 each), Max/Lena at 30 and 31 (4 each).
- New art: 4-expression sheets (neutral, happy, worried, +1); make age 25 first, use as reference for older ages. Split with pipeline/split_sheet.py, check on magenta, lock in manifest.
- QC must be OVERALL PASS; fix causes, never loosen checks. Check frames from every scene and fix overlaps before sending.
- Claude can't hear audio: owner checks pronunciation and pace.
- Commit and push after each stage; keep the branch merged with main.

