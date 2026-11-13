# Three Bills pilot: revision 1 report (for owner approval; the full episode is not started)

File (local, not in git): `/output/three_bills_rev3/ren_three_bills_pilot_rev3_57s.mp4`, 1920x1080, 24 fps, 56.83 s, 1364 frames (identical length and narration to the first pilot).
Owner direction: conditional approval of style, Ren animation and storytelling; one focused visual revision. Branch `video/three-bills-30-days`.

## What changed (only 14 of 24 shots; 9 shots are untouched)
| Shot | Time | Was | Now |
|---|---|---|---|
| S05a/b | 10.0-12.4 | pipe prop on a blurred backdrop, a small drip | **Revision 3: uses your supplied sink-leak illustration** (`art/plates/kitchen_leak_ref.png`, SHA-256 29cb65b8...). **S05a** (0.7 s) full-width crop of the pipe, drip and bucket with a slow push; **S05b** (1.6 s) pull-back that reveals the sink above the pipe. A code-drawn drop falls into the bucket and a ripple expands over the static artwork. Both are classed STORY STILL (caps 2.5 s) and labelled so. Only the area right of x = 780 is used: **the woman in the image is not the approved Maya (bun, denim shirt, wristband) and is cropped out of every frame**; I did not use or redraw her. (Revision 2's coded cabinet and puddle were replaced and no longer appear.) |
| S07a/b | 14.9-19.4 | porch, Maya + chip, credit card slides in | **S07a** porch, chip. **S07b** close-up on a table: an "Unexpected bill" invoice drops and bounces, a credit card slaps onto it, a red "Debt" stamp lands |
| S08 | 19.4-22.2 | Maya relief alone | Maya worried to relief, with three prop tiles (car key, invoice, pipe) ticked off one by one |
| S09a/b | 22.2-26.5 | one office shot, Maya + a small phone inset | **S09a** close-up of Maya (neutral to worried), evening grade. **S09b** wide office, Maya at the right third, pulsing phone glow |
| S10a/b | 26.5-30.4 | phone inset + bubble | **S10a** full-frame savings app: $2,600 then -$760 = $1,840, -$390 = $1,450, -$1,050 = $400. **S10b** close-up of Maya with the thought bubble |
| S12 | 31.6-35.2 | porch, a static calendar label | calendar pages physically flip Today, 6, 12, 18 months earlier |
| S13/13b | 35.2-41.7 | office, three chips | **S13** close-up of a payday envelope with bills rising. **S13b** Maya beside the envelope: Rent, Groceries, Gas tags peel away and the bills leave one by one |
| S14 | 41.7-43.9 | office, chip | close-up of Maya, an empty envelope slides in |
| S14b | 43.9-45.9 | the washed-out veil with a small phone (the empty-looking moment near 44 s) | full-colour office, Maya and a larger $80 phone sliding up |
Unchanged: S01-S04, S06, S11, S15-S17. Financial figures, narration audio and cut times are unchanged (checked below). All new shots keep Ren's approved clips untouched.

## Which characters are genuinely animated, and which are static artwork
- **Ren (S01, S06, S11, S17): genuine animation.** Approved library MP4 clips, every frame distinct, mouth closed.
- **Maya: static cut-out artwork, in every shot.** She has four poses only. Her "activity" is pose cross-fades (3 frames), camera pushes, close-ups, and props and graphics moving around her. She does not walk, reach, sit or articulate. **I could not give her purposeful physical actions beyond this without new poses**: the request for physical actions is only partly met. S07a, S09b, S10b, S14 and S14b hold a single pose.
- **Props and graphics (invoice, credit card, envelope, bills, drip, puddle, calendar pages, phone screens, tiles, ticks):** animated in code; the key, pipe and envelope are static artwork moved by code.
- **Provisional art:** the sink-leak illustration was supplied by you in a message but is not in the pack and has not been confirmed as approved artwork; treat it as provisional until you say otherwise. The credit card, bills, stamp, tiles and phone screens are drawn in code in the brand palette; the pack's provisional kitchen and dental plates were not used.

## Validation (QA 36 checks, OVERALL PASS; `reports/hybrid_qc.md`)
- Scene boundaries: 22 hard cuts, all on shot boundaries; no A-B-A inserts, no flashes; every cut changes the picture; no run of 3 graphic-only shots (longest 1); caps held (Ren 5.5 s, graphic 3.5 s).
- Unchanged shots really unchanged: S01-S04, S06, S11, S15-S17 keep their frame ranges and differ from the first pilot by at most 0.23/255 (codec noise); narration correlation with the first pilot 1.00000.
- Maya: height equals the calibrated plate perspective in every plate shot; head and feet in frame except three deliberate close-ups (S09a, S10b, S14: head in, feet out by design); sub-pixel jitter 0.051 px. The coded-floor shot S05b is scaled by eye, not plate-calibrated.
- Text inside the safe area and at least 32 px; every number from `assumptions.csv` (new displayed values: 1,840 and 1,450, both in the source).
- 24 fps constant, 1364 packets; voice: not regenerated, correlation 1.0000, no TTS code.
## Inspected by me (not "in motion at speed")
Contact sheet at 2 frames/s of the whole revised range (14.5-46.5 s, 64 frames); mid-shot stills of every new shot at 640 px (before the last render); 100% views of S10a and (revision 2) S05b; for revision 3 the S05a/b frames at 480 px and a 4-frame contact of the pipe stills at 960 px. **NOT VERIFIED:** playback at real speed, phone playback, the feel of the pacing, the audio (cannot listen).
## Known weaknesses
S09b is nearly static (one pose, push and glow). S13 (2.7 s) is an envelope with bills that rise only in the first 0.7 s, then hold. S09a/S10b/S14 close-ups enlarge the 981 px art about 1.9x, slightly soft. The evening grade (S09-S10b) is a coded colour overlay on the office plate, which still stands in for her home. Maya is still the 401(k) episode's different design.

## Revision 3 note (kitchen image)
The image is enlarged about 2.1x in S05a/b (1672 px source), so it is a little soft at 1080p. In S05b the pull-back ends on the whole right half of the image, which is narrower than the frame, so the sides are filled with a blurred, darkened enlargement of the same picture for the last second. The new check 3c confirms every crop stays right of x = 780. All other shots are as in revision 2; unchanged shots S01-S04, S06, S11, S15-S17 still match the first pilot (worst difference 0.32/255).
