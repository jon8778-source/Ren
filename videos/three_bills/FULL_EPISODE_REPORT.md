# Three Bills in 30 Days: full episode report (for owner final review)

File (local, not in git): `/output/three_bills_full/ren_three_bills_full_5m21s.mp4`, 1920x1080, 24 fps, 320.8 s (**5 min 21 s**), 126 shots (67 Maya, 21 Ren, 32 graphic, 6 story still).
Authorised by the owner's pilot approval (rev3) with conditions 1-8. Branch `video/three-bills-30-days`. Nothing merged, published or Shorts-produced.

## Length
5:21, not 6:00: the approved v2 script is 937 words and the Qwen voice reads it at its natural pace (about 0.34 s/word). I did not slow, stretch or pad the voice, so the film is about 40 s short of "approximately six minutes".

## Conditions, one by one
1. Rules followed: REN_LONGFORM_BASELINE.md / CHECKLIST (read in full); `REN_VIDEO_RULES.md` NOT re-read this session (applied from earlier work and the pilot).
2. Pilot preserved: pilot frames 0 to its closing-disclaimer lead-in match the approved rev3 within 0.42/255 (codec noise), narration correlation 1.00000. The pilot's closing disclaimer is not repeated mid-film.
3. Maya-with-phone: share of Maya screen time using the two phone poses is 7%; longest stretch with neither Ren nor a phone-free Maya pose is 7.3 s; Maya moves across porch, parking lot and office (longest same-plate run 3 shots) with object interactions (key turn, smoking engine, spending tiles, suitcase, coffee cups, envelopes, refill phone). **Her motion is still limited**: four static poses.
4. Ren: 21 genuine library clips, 10 distinct clips, never the same clip twice in a row, longest gap between Ren shots 29.1 s.
5. Repetitive cards: no more than 2 graphic-only shots in a row; graphic-only screen time 22%. The four-principles section (about 4:15-5:00) alternates Maya in the office/porch/lot, Ren and phone/envelope props; it is still text-led.
6. Voice and figures: approved Qwen clone, all sections generated once from the approved v2 script (SHA-256 verified), no regeneration of the pilot audio; every on-screen figure from `assumptions.csv`; arithmetic and "1,050 < 1,450" checked.
7. QA: 41 checks, OVERALL PASS (`reports/full_qc.md`). Includes full decode, every cut on a shot boundary, no one-frame inserts or flashes, safe area and 32 px minimum on 998 frames, Ren and Maya scale/grounding, jitter 0.051 px, constant 24 fps.
8. Unverified, stated plainly below.

## Not verified
- **Audio, by ear**: accent, pace, pronunciation, joins. Whisper confirms the words (differences are digits only).
- **Playback**: I did not watch the film at speed or on a phone. Visual review was the 160-frame contact sheet (one frame per 2 s over the whole film), earlier 100% crops of Ren and Maya in the pilot, and 2-frame-per-second sheets of the new shots during development; I did not look at all 126 shots at full size, and viewed only a few cuts as before/after pairs.
- Ren's mouth-closed state rests on library notes and sheets, not a detector. Mobile readability = minimum font size and safe area only.
- Sources: CFPB/FDIC pages in the pack were not opened; the script makes no sourced statistic beyond the story's own fictional figures.
- The repo's older qa_timeline.py / validate.py / jitter_check.py were not run (tied to the 720p renderer; re-implemented here).

## Honest limits to judge
- **Maya is static artwork** (four poses). Pose cross-fades, camera pushes and moving props are not character animation; she never walks, reaches or sits. She looks different from the 401(k) episode's Maya (owner-approved art).
- Her home scenes use the porch and corporate-office plates as stand-ins (no approved home plate). The sink-leak illustration was supplied by you and is treated as provisional; only its pipe/sink/bucket area is used (the woman in it is cropped out).
- Many graphics are my own code designs (phones, tiles, tank, dominoes, strike-through chips): some sections (the four principles, 4:15-5:00) lean on text cards. A few shots start on a near-empty blurred backdrop for a moment before a card slides in (about 98 s and 282 s).
- Close-ups enlarge 981 px art about 1.9-2.1x (slightly soft). Evening/sunrise grades are coded colour overlays.

## Files
`ren_three_bills_full_5m21s.mp4`, `contact_sheet.jpg`, `full_qc.md`, `Full_Shot_Inventory.csv` (shot-by-shot: animated vs static), `REN_BASELINE_COMPLIANCE_REPORT.md` and `SHOT_PLAN_FULL.md` (earlier gates).
