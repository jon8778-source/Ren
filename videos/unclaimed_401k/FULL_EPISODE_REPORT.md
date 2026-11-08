# Full episode report: Ren | Unclaimed 401(k) match (Gate: awaiting owner review)

Local file (not in git): `/output/unclaimed_401k_full/ren_401k_match_full_5m42s.mp4`, 1920x1080, 24 fps, 341.8 s (5 min 42 s), 134 shots
(46 Maya action, 24 Ren cutaways, 62 graphics, 2 story stills). The first 53.1 s are the approved pilot, unchanged.
Narration: the full approved v3 script (1,001 words) in the Qwen clone; the pilot WAVs were reused (byte-identical), the rest was synthesised
after the owner's "Approved" (P3, S3-S8 = 288 s). No speed change, stretching or padding. Whisper confirms every word (differences are digits only).
Full QA: `reports/full_qc.md`, 32 checks, OVERALL PASS. Shot list: `reports/Full_Shot_Inventory.csv`.
Final-mix note: the episode audio has a 0.3 dB gain trim so the true peak is under -1 dBTP (-1.2 dBTP, -18.7 LUFS); the pilot narration alone is unchanged.

## Bug found and fixed (affects any Ren render)
`ren_stage._mip` cached pre-scaled images by `id(img)`. In the episode render a new Ren frame could reuse a freed image's id and get the OLD
image's pixels (a stretched or wrong Ren for single frames or whole seconds). Fixed (identity-checked cache) with a regression test; the
first full render was discarded. The approved pilot was not affected (its Ren frames stay alive for the whole render; checked by QA).

## Honest limits
- Maya is limited animation from approved keyframes, not a rig. Office shots alternate 1.3x and 1.55x framing; Maya sits on one floor spot.
- Alex appears only as the approved story still (no rig). The "Alex, a colleague" still is the existing D_alex_laptop art.
- Ren cutaways reuse nine library clips; gestures repeat across the video (thumbs-up and wave_hello were avoided for open-mouth frames).
  His mouth is closed in the chosen windows (library notes + eye check); there is no lip sync.
- The 62 graphics are my own code design (the style sheet and UI screens never arrived); many are text cards: please review pace and density.
- Plates are upscaled 2.3x; the home plate is used only in the pilot's first minute.
- I cannot hear audio. Please check the new narration (S2 rest to S8): accent, pace, joins, "four-oh-one-k", the numbers, and "Check out the Money Leak Audit Workbook in the description."
- Not run: the repo's older qa_timeline.py / validate.py / jitter_check.py (720p renderer); their checks are re-implemented in qa_full.py.
- The 2027 limit mentioned in the Free Money video is not in this script; every number here is from the approved v3 claims (all arithmetic checked).
Nothing is merged or published. Branch: `video/unclaimed-401k-match-maya`.
