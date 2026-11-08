# Hybrid QC - Ren | Unclaimed 401(k) match, pilot

File: `pilot_draft.mp4`  |  frames 1275  |  1920x1080 @ 24 fps

Commands: `project/.tools/venv/bin/python videos/unclaimed_401k/qa_pilot.py <mp4>`; thresholds are in the script and were not relaxed.

| Check | Result | Measured |
|---|---|---|
| 1a shots contiguous | PASS | [] |
| 1b shot frames add up to the video | PASS | 1275 vs 1275 |
| 1c v3 shot caps (CHARACTER_ACTION 5.5, STORY_STILL 2.5, GRAPHIC 3.5) | PASS | [] |
| 1d shot types match the plan (15 action, 3 graphic, 1 story still) | PASS |  |
| 2 phrases tile the approved narration in order | PASS | 166 vs 166 words |
| 3 plates, voice and props exist | PASS | [] |
| 4a full decode clean (-xerror) | PASS |  |
| 4b format 1920x1080 24 fps h264 + aac | PASS | 1920x1080 24/1 h264/aac |
| 4c frame count equals shot frames | PASS | 1275 vs 1275 |
| 4d video and audio lengths within 0.1 s | PASS | video 53.125s audio 53.120s |
| 4e narration length equals P1+P2 as generated | PASS | 53.095s |
| 4f loudness -23..-12 LUFS, true peak <= -1 dBTP | PASS | -18.2 LUFS, -1.0 dBTP |
| 4g no silence gap over 1.2 s inside the narration (natural 0.6-1.0 s sentence pauses allowed) | PASS | [(8.36, 0.88), (11.18, 0.61), (37.87, 0.67), (49.6, 0.65)] |
| 5a hard cuts (mean diff > 14) land only on shot boundaries | PASS | off-boundary: []; detected 12 cuts |
| 5b every shot boundary is a visible cut (diff >= 2 (pose-only changes are small); the portal label swap P06->P07 is allowed to be small) | PASS | [('P07', 0.0)] |
| 5c no A-B-A one-frame inserts | PASS | [] |
| 5d no single-frame brightness flashes | PASS | [] |
| 6a all on-screen text inside the safe area (x 40..1880, y 20..950; bottom 12% empty), 213 sampled frames | PASS | [] |
| 6b on-screen text at least 32 px (device screens inside props are exempt) | PASS | [] |
| 6c every on-screen number is a checked claim | PASS | ['$1,200', '$100', '$60,000', '1', '2', '2%', '3', '31', '401'] |
| 7 claim arithmetic (60,000 x 2% = 1,200; match gap 1,200/yr = 100/mo) | PASS |  |
| 8 Maya sub-pixel placement noise <= 0.12 px over a 60-frame move and scale (jitter_check method) | PASS | worst 0.054px; stool_01 x=0.030 y=0.054; stool_05 x=0.032 y=0.037; maya_nochair_02 x=0.018 y=0.039; walk_sit_01 x=0.008 y=0.021; receipt_laptop_04 x=0.009 y=0.022 |

## Not run / limits
- NOT RUN: listening review (pronunciation, accent, tone, joins). Speech-to-text only confirms the words; see voice_check_summary.json.
- NOT RUN: the original repo `qa_timeline.py`, `validate.py` and `jitter_check.py`. They are wired to the 1280x720 free_money renderer and Ren stills; `qa_pilot.py` re-implements their checks for this renderer (half-open shot lookup, caps, A-B-A, flashes, cuts on boundaries, decode, jitter).
- Motion is limited animation: Maya is a set of approved keyframe poses with pose-to-pose changes (3-frame cross-fade where the poses are close, hard cut otherwise), plus code-driven props, pen path, coin and UI. It is not a skeletal rig.
- Plates are 2.3x upscales of 1672x941 art and are not perspective-calibrated; scale was matched by eye to the plate furniture.
