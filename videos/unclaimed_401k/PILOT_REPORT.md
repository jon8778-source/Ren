# Pilot report: Ren | Unclaimed 401(k) match (Gate B, awaiting owner review)

Local file (not in git): `/output/unclaimed_401k/ren_401k_match_pilot_53s.mp4`, 1920x1080, 24 fps, 53.125 s, H.264/AAC, 19 shots
(15 CHARACTER_ACTION, 3 GRAPHIC, 1 STORY_STILL). Narration: approved v3 script, Qwen clone, pilot part only (all of S1, S2 up to
"so she moved on."), joined exactly as generated, no speed change or padding. It is 53 s, not 60 s, because that is how long the real audio is.

QA (`qa_pilot.py`, `reports/hybrid_qc.md`): all checks pass: shot list and caps, phrases tile the narration, clean full decode, A/V length,
loudness -18.2 LUFS, cuts only on shot boundaries, no inserts or flashes, text inside the safe area and at least 32 px, every on-screen number
a checked claim, Maya placement noise 0.054 px (limit 0.12). NOT RUN: listening review; the repo's `qa_timeline.py`, `validate.py`,
`jitter_check.py` (tied to the 720p free_money renderer; re-implemented in `qa_pilot.py`).

## Honest limits
- Maya is **limited animation from approved keyframe poses** (cross-fade over 3 frames where poses are close, hard cut where not), not a skeletal rig.
  Genuinely moving: pose changes, the pen hand tracing the tick, the walk cycle, the coin, the code UI. See `reports/Shot_Inventory.csv`.
- **Continuity compromise:** P01-P03 use the armchair; P04-P12 have her on a stool at the coffee table, because there is no armchair+laptop pose.
- Laptop screens face away from camera, so the portal is shown as full-frame graphics (P06, P07, P11) and insets, never on the laptop.
- The 4-pose walk cycle repeats one step, so it looks stylised; the sit-down is two poses.
- Plates are 2.3x upscales, not perspective-calibrated; scale was matched by eye. O1 is mirrored and both O1 and O2 had their own stool removed.
- Armchair poses had Maya's baked chair removed by colour segmentation; check shoes for specks.
- The style sheet and nine UI screens from the original pack never arrived: the finance UI is my own code design and needs your review.
- I cannot hear the audio. Please check accent, pace, "four-oh-one-k", the numbers lines, and the joins.
Nothing is merged or published; the rest of the episode is not started.
