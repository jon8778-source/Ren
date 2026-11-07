# Gate 3: rough cut S1-S7 (draft quality)

**File (local only, not in git):** `/output/free_money_S1_S7_rough_cut.mp4`. 1280×720, 24 fps, H.264 (draft CRF 23) + AAC, **237.34 s (3 min 57 s)**, 5,696 frames, 112 shots, -16.2 LUFS, true peak -1.5 dBTP.
**Status: STOP. Waiting for `rough cut approved`.** No final render, no package zip, no upload. Gate 4 has not started.
**Real timings:** `shot_plan_actual.csv` (every shot with its real start, end and narration), `sheets/rough/contact_sheet_all_shots.png`, `scene_boundaries.png`, `crops100.png`, `changed_shots.png`.

## What it is
- **S1 and S2:** the approved rev03.1 shots, unchanged. The first 1,190 frames match rev03.1 to within encoder noise (max difference 2.1 on a 0-255 scale). The last 1.7 s of S2 differs only because that closing shot now ends at the S3 cut, so its slow push-in runs over a shorter time.
- **S3 to S7:** built to the approved Gate 1 plan, with the real narration timing.
  - **S3 (the quiet years, 35.9 s):** You and Employer jars fill to 4%, then 2%, the "never paid" ghost level, the Age / salary / "Missed match" ledger ($880, $920, $960 and a fixed "3 years = about $2,760"), three ghost jars, the $489 lease card against about $77/month.
  - **S4 (back on the porch, 27.0 s):** Dev's three questions as cards, the stub line 2% to 4%, the unpaid 2% flowing to the employer ("stays with the employer"), the retirement-app phone toggling 2% to 4% with the "90 seconds" badge.
  - **S5 (the sting and the twist, 35.5 s):** $2,760 on a 30-year timeline with "hypothetical 7%/yr" and the sticker "$2,760 at a hypothetical 7%/yr for 30 years = about $21,000. Not a promise.", the pay-stub card "only about $32 per paycheck (pre-tax)", a pre-tax flow diagram, the $32 coins fading, and the car.
  - **S6 (what I check now, 59.5 s):** the parking-lot plate with an "8 years later" tag (plain plate: the grade was not approved), full match + more, Priya and Gary cutaways with their own cards, the three-item checklist with ticks, a vesting bar that opens a lock, the 2027 limit card ($25,500, up from $24,500, "Milliman projection, not confirmed"), "IRS: not yet confirmed (as of end of October)".
  - **S7 (handoff and close, 27.9 s):** the folder handed over, page 6, the "Collect first" list (the match, the HSA money, the stuff in the folder), the Age 25 shot, the "Next week" teaser, and the full-body wave as the sign-off with the disclaimer tag.
- Narration for S3-S7 was generated locally with the same x-vector-only setting as S1-S2. S1-S7 are joined exactly as generated (no stretching or padding), then gained to -16 LUFS.

## Checks
| Check | Result |
|---|---|
| `qa_timeline.py` (17 checks) | **PASS**. Contiguous frame-aligned shots, shot frames equal video frames, shots in script order (732 of 732 words, S1 to S7), assets present, full decode with errors fatal, no one- or two-frame inserts, every hard cut on a shot start, both page peels (age 25, "8 years later") hand over cleanly, no flashes. Proven to FAIL on the old buggy rev03 file. |
| `validate.py` | **PASS**: clean full decode, no layout overlaps, no audio gaps (five 0.6-0.7 s pauses, each at a sentence end). |
| v3 shot caps (Ren 5.5 s, story 2.5 s, graphic 3.5 s) | **PASS**: none over, with 112 shots (average 2.1 s). |
| Narration against the script | Whisper's S1-S7 wording matches the script, apart from digits (it writes "$25,500" and "24 500" for the spoken numbers). Three non-digit differences ("plan" as "planned", "of" dropped, "if" dropped) are Whisper artefacts: with padding added in front, Whisper hears them correctly. **I can't hear audio.** |
| Equations true on every frame | The ledger total shows only with all three amounts; both match stacks grow together; the jar percentages show only when settled. |

## What I looked at (on the final MP4)
- The middle of every one of the 112 shots on a contact sheet (the previous render for 107 of them, and the final file for the five I changed), the six scene boundaries (four frames each), and 100% crops of Priya, Gary, the jars with the ghost level, the timeline sticker, the checklist and the pay-stub card.
- **Fixed after looking:** two shots over their caps (the "8 years later" shot and "Twenty-five-year-old me") split to fit; a mid-fill percent label in the jars; the sticker covering the "$2,760" pill; low-contrast timeline labels; the "never paid" text overflowing a narrow jar; the IRS pill running to the frame edge; "Everyone's different" and "the match works the same" shown under one pose across a sentence break; the car-lease phone (not the retirement app) shown when he "opened the app"; and the whole background sliding with the phone.
- **Not looked at:** the last and first frame of all 111 shot boundaries one by one. The automated cut checks cover those, and I looked at the six scene boundaries.

## Uncertain or not verified
1. **Audio by ear (yours):** "lease" (heard as "least" in S2), the accent and the pace, and S7's first word: the audio starts almost on the first sound, so the opening may feel abrupt.
2. **Pace:** the cut averages 2.1 s per shot, which is fast. It follows from the v3 caps. If it feels busy, the only lever is a cap exception.
3. **"8 years later" car:** a plain plate with a tag, because the desaturated grade wasn't approved. Say so if you want the grade.
4. **Priya, Gary and Dev** have one pose each, moved by camera only. Style option (b) (accept as is) was used.
5. **Draft quality:** CRF 23. Gate 4 renders at final quality (CRF 18), which is slower.
6. **Shot plan CSV:** `shot_plan.csv` is the Gate 1 estimate. `shot_plan_actual.csv` is the real one and will be the one packaged at Gate 4.
7. **2027 limit:** the Milliman figures are the script's. I re-check them at Gate 4 and flag any change, without editing the wording.
8. **Resolution:** 1280×720 (v3), not 1080p.

## Next, only after `rough cut approved` (Gate 4)
Re-check the IRS 2027 limit and flag it; render final quality at 1280×720 (or 1080p if you choose it); run validator, timeline checks and visual check; build `free_money_final_package.zip` locally (final video, narration, script, outline, shot plan, assets used, contact sheet, REPORT); stop for `approved to publish`. No upload, no merge.
