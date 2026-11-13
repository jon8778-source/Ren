# Hybrid QC - Ren | Unclaimed 401(k) match, pilot

File: `pilot_rev2.mp4`  |  frames 1275  |  1920x1080 @ 24 fps

Commands: `project/.tools/venv/bin/python videos/unclaimed_401k/qa_pilot.py <mp4>`; thresholds are in the script and were not relaxed.

| Check | Result | Measured |
|---|---|---|
| 1a shots contiguous | PASS | [] |
| 1b shot frames add up to the video | PASS | 1275 vs 1275 |
| 1c v3 shot caps (CHARACTER_ACTION 5.5, STORY_STILL 2.5, GRAPHIC 3.5) | PASS | [] |
| 1d shot mix: 14 Maya action, 2 graphic, 1 story still, 2 Ren cutaways | PASS | [14, 2, 1, 2] |
| 1e one or two Ren cutaways, each within the 5.5 s cap | PASS |  |
| 2 phrases tile the approved narration in order | PASS | 166 vs 166 words |
| 2b spoken text equals the approved script (S1 + S2 up to 'so she moved on.'), unchanged | PASS |  |
| 3 plates, voice and props exist | PASS | [] |
| 4a full decode clean (-xerror) | PASS |  |
| 4b format 1920x1080 24 fps h264 + aac | PASS | 1920x1080 24/1 h264/aac |
| 4c frame count equals shot frames | PASS | 1275 vs 1275 |
| 4d video and audio lengths within 0.1 s | PASS | video 53.125s audio 53.120s |
| 4e narration length equals P1+P2 as generated | PASS | 53.095s |
| 4f loudness -23..-12 LUFS, true peak <= -1 dBTP | PASS | -18.2 LUFS, -1.0 dBTP |
| 4g no silence gap over 1.2 s inside the narration (natural 0.6-1.0 s sentence pauses allowed) | PASS | [(8.36, 0.88), (11.18, 0.61), (37.87, 0.67), (49.6, 0.65)] |
| 5a hard cuts (mean diff > 14) land only on shot boundaries | PASS | off-boundary: []; detected 14 cuts |
| 5b every shot boundary is a visible cut (diff >= 2 (pose-only changes are small); the portal label swap P06->P07 is allowed to be small) | PASS | [('P07', 0.0)] |
| 5c no A-B-A one-frame inserts | PASS | [] |
| 5d no single-frame brightness flashes | PASS | [] |
| 6a all on-screen text inside the safe area (x 40..1880, y 20..950; bottom 12% empty), 213 sampled frames | PASS | [] |
| 6b on-screen text at least 32 px (device screens inside props are exempt) | PASS | [] |
| 6c every on-screen number is a checked claim | PASS | ['$1,200', '$100', '$60,000', '1', '2', '2%', '3', '31', '401'] |
| 7 claim arithmetic (60,000 x 2% = 1,200; match gap 1,200/yr = 100/mo) | PASS |  |
| 8 Maya sub-pixel placement noise <= 0.12 px over a 60-frame move and scale (jitter_check method) | PASS | worst 0.054px; stool_01 x=0.030 y=0.054; stool_05 x=0.032 y=0.037; maya_nochair_02 x=0.012 y=0.030; walk_sit_01 x=0.013 y=0.028; receipt_laptop_04 x=0.033 y=0.045 |
| 9a P08 uses approved library clip ren_point_right.mp4 inside its usable window (1.0-6.38 s) | PASS | plays 1.30-4.38 s; shot 3.08 s <= 5.5 |
| 9b P08 Ren feet fixed on the floor (no bobbing): bottom row std 0.50px | PASS | min 884.2 max 885.4 |
| 9c P08 Ren scale matches the plate standard (175 cm = 816px): measured 815px | PASS |  |
| 9d P08 Ren genuinely moves: mean in-box change 1.82/255, moving in 59 of 73 frame steps, 74 distinct clip frames | PASS |  |
| 9e P08 no camera move or pan: background region unchanged in every rendered frame (max change 0/255; encoded video 0.05, codec noise only) | PASS |  |
| 9f P08 Ren on the left, graphics on the right, no text over Ren | PASS | Ren x 371-750 |
| 9a P11 uses approved library clip ren_shrug.mp4 inside its usable window (1.12-10 s) | PASS | plays 1.30-3.80 s; shot 2.50 s <= 5.5 |
| 9b P11 Ren feet fixed on the floor (no bobbing): bottom row std 0.59px | PASS | min 883.0 max 884.2 |
| 9c P11 Ren scale matches the plate standard (175 cm = 816px): measured 818px | PASS |  |
| 9d P11 Ren genuinely moves: mean in-box change 1.51/255, moving in 58 of 59 frame steps, 60 distinct clip frames | PASS |  |
| 9e P11 no camera move or pan: background region unchanged in every rendered frame (max change 0/255; encoded video 0.46, codec noise only) | PASS |  |
| 9f P11 Ren on the left, graphics on the right, no text over Ren | PASS | Ren x 233-731 |
| 10a living room: Maya stays in the armchair in every home shot (no stool pose, no repositioning) | PASS | ([], []) |
| 10b office: Maya sits on the same floor spot in every shot and her scale follows the camera zoom exactly | PASS | [] |
| 10c office Maya is larger than in the first pilot (zoom 1.25-1.55x on P14-P16, P19 vs 1.0x) | PASS | {'P13': 1.0, 'P14': 1.3, 'P15': 1.25, 'P16': 1.55, 'P19': 1.3} |
| 10d every character shot changes pose or moves a prop/hand (no shot is only a pan or zoom over a still) | PASS | [] |
| 11 constant 24 fps: r_frame_rate and avg_frame_rate 24/1, every packet 1/24 s apart, no dropped or duplicated frame timestamps | PASS | ('24/1', '24/1'), 1275 packets, delta min 0.04167 max 0.04167 |
| 12a narration WAVs are byte-identical to the ones generated for the first pilot (no new synthesis) | PASS | P1 4ee4f6273b36 P2 b620ffd31309 |
| 12b renderer imports and calls no TTS code (no qwen_tts / torch / transformers import, no generate_voice_clone call) | PASS |  |
| 12c MP4 audio matches the original narration waveform (correlation >= 0.95) | PASS | 1.0000 |

## Not run / limits
- NOT RUN: listening review (pronunciation, accent, tone, joins). Speech-to-text only confirms the words; see voice_check_summary.json.
- NOT RUN: the original repo `qa_timeline.py`, `validate.py` and `jitter_check.py`. They are wired to the 1280x720 free_money renderer and Ren stills; `qa_pilot.py` re-implements their checks for this renderer (half-open shot lookup, caps, A-B-A, flashes, cuts on boundaries, decode, jitter).
- Ren: genuine library clips only; mouth-closed windows were chosen from the library notes and checked by eye on 100% crops, not by an automated mouth detector.
- Motion is limited animation: Maya is a set of approved keyframe poses with pose-to-pose changes (3-frame cross-fade where the poses are close, hard cut otherwise), plus code-driven props, pen path, coin and UI. It is not a skeletal rig.
- Plates are 2.3x upscales of 1672x941 art and are not perspective-calibrated; scale was matched by eye to the plate furniture.
