# Full-episode QC - Ren | Unclaimed 401(k) match

File: `episode.mp4` | 8204 frames | 1920x1080 @ 24 fps | 5.70 min

Command: `project/.tools/venv/bin/python videos/unclaimed_401k/qa_full.py <mp4>`; thresholds are in the script and were not relaxed.

| Check | Result | Measured |
|---|---|---|
| 1a shots contiguous from frame 0 to the last frame | PASS | [] |
| 1b v3 shot caps (Maya action / Ren 5.5, story still 2.5, graphic 3.5) | PASS | [] |
| 1c shot mix recorded | PASS | {'CHARACTER_ACTION': 46, 'REN_ANIMATED': 24, 'GRAPHIC': 62, 'STORY_STILL': 2}, 134 shots |
| 2 shot phrases tile the whole approved script in order (S1-S8), unchanged | PASS | 1022 vs 1022 words |
| 2b script is the approved v3 text (1001 words) | PASS | 1001 |
| 3 plates, stills and all narration WAVs exist | PASS | [] |
| 4a full decode clean (-xerror) | PASS |  |
| 4b format 1920x1080 24 fps h264 + aac | PASS | 1920x1080 24/1 |
| 4c frame count equals shot frames | PASS | 8204 vs 8204 |
| 4d video and audio lengths within 0.1 s | PASS | video 341.833s audio 341.824s |
| 4e narration length equals all sections joined as generated | PASS | 341.815s; episode 5.70 min |
| 4f loudness -23..-12 LUFS, true peak <= -1 dBTP | PASS | -18.7 LUFS, -1.2 dBTP |
| 4g no silence gap over 1.4 s inside the narration (sentence pauses and section joins allowed) | PASS | [] |
| 5a hard cuts (mean diff > 14) land only on shot boundaries | PASS | off-boundary: []; 94 cuts detected |
| 5b every shot boundary changes the picture (progressive graphics and pose changes count; nothing identical across a cut) | FAIL | [('T05', 0.0), ('B07a', 0.0), ('B08', 0.0), ('B09a', 0.0), ('B14', 0.0)] |
| 5c no A-B-A one-frame inserts | PASS | [] |
| 5d no single-frame brightness flashes | PASS | [] |
| 6a all on-screen text inside the safe area (x 40..1880, y 20..950; bottom 12% empty), 788 frames incl. every shot's first and last | PASS | [] |
| 6b on-screen text at least 32 px (device screens inside props are exempt) | PASS | [] |
| 6c every on-screen number is a checked claim | PASS | ['$0', '$1', '$1,200', '$100', '$12', '$12,000', '$2,400', '$200', '$3,600', '$40', '$48', '$52', '$60,000', '1', '10', '100%', '2', '2%', '3', '4', '4%', '401', '5', '50', '6', '7', '8', '9'] |
| 7 claim arithmetic (60,000 x 4% = 2,400; 2% = 1,200; gap 1,200 = 100/mo; 12+40+48 = 100; 3 x 1,200 = 3,600; 10 x 1,200 = 12,000) | PASS |  |
| 8 Maya sub-pixel placement noise <= 0.12 px (jitter_check method) | PASS | worst 0.054px |
| 9a all 24 Ren cutaways: approved library clips inside their usable windows, feet fixed (no bobbing), scale = 175 cm standard, every frame a distinct clip frame, real movement, static camera, Ren left / graphics right | FAIL | [('M02', 'camera/background changed'), ('M14', 'camera/background changed'), ('C17', 'camera/background changed')] |
| 9b consecutive Ren shots never repeat the same clip | PASS | [] |
| 10a Maya sits on the same office floor spot in every new Maya shot; scale follows the camera zoom exactly (grounded) | PASS | [] |
| 10b every new Maya shot changes pose (no shot is only a pan or zoom over a still) | PASS | [] |
| 10c no repeated identical pose and framing across consecutive Maya shots | PASS | [] |
| 11 constant 24 fps: r/avg_frame_rate 24/1, every packet 1/24 s apart, no dropped or duplicated timestamps | PASS | 8204 packets, delta 0.04167-0.04167 |
| 12a pilot narration WAVs byte-identical to the approved pilot's (not regenerated) | PASS |  |
| 12b renderers import and call no TTS code | PASS |  |
| 12c MP4 audio matches the narration waveform (correlation >= 0.95) | PASS | 1.0000 |

## Not run / limits
- NOT RUN: listening review (pronunciation, accent, tone, joins). Speech-to-text only confirms the words.
- NOT RUN: the repo's older qa_timeline.py, validate.py, jitter_check.py (wired to the 720p free_money renderer); their checks are re-implemented here.
- Ren: genuine library clips only; mouth-closed windows chosen from library notes, checked by eye on contact sheets, not by an automated mouth detector.
- Maya is limited animation from approved keyframe poses, not a skeletal rig. Alex appears only as the approved story still.
