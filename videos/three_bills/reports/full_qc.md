# Full-episode QC - Three Bills in 30 Days

File: `episode.mp4` | 7699 frames | 1920x1080 @ 24 fps | 5.35 min

Command: `project/.tools/venv/bin/python videos/three_bills/tb_qa_full.py <mp4> <pilot rev3 mp4>`; thresholds are in the script.

| Check | Result | Measured |
|---|---|---|
| 1a shots contiguous from frame 0 to the last frame | PASS | [] |
| 1b shot caps (Ren / Maya action 5.5 s, story still 2.5 s, graphic 3.5 s) | PASS | [] |
| 1c shot mix recorded | PASS | {'CHARACTER_ACTION': 67, 'REN_ANIMATED': 21, 'STORY_STILL': 6, 'GRAPHIC': 32}, 126 shots |
| 1d no run of 3 or more consecutive graphic-only shots (baseline: avoid card sequences) | PASS | longest run 2 |
| 1e Ren returns at least every 45 s (baseline: roughly every 30-45 s) | PASS | 21 Ren shots; longest gap 29.1s; gaps over 40 s: [] |
| 1f graphic-only screen time share recorded | PASS | 22% of the film |
| 2a shot phrases tile the whole approved v2 voice script (937 words) in order, unchanged | PASS | 947 vs 947 words |
| 2b SCRIPT.md and VOICE_SCRIPT.txt match the approved SHA-256 | PASS |  |
| 3a pack assets on disk match ASSET_MANIFEST.json hashes | PASS | [] |
| 3b plates, kitchen image, voice reference and all narration WAVs exist | PASS | [] |
| 3c kitchen illustration used only right of x = 780 (the woman, not the approved Maya, never appears) | PASS | crop left edges [780, 800, 780, 780] |
| 4a full decode clean (-xerror) | PASS |  |
| 4b format 1920x1080 24 fps h264 + aac | PASS | 1920x1080 24/1 |
| 4c frame count equals shot frames | PASS | 7699 vs 7699 |
| 4d video and audio lengths within 0.1 s | PASS | video 320.792s audio 320.789s |
| 4e narration length equals all sections joined as generated; episode about six minutes | PASS | 320.787s = 5.35 min |
| 4f loudness -23..-12 LUFS, true peak <= -1 dBTP | PASS | -18.6 LUFS, -1.0 dBTP |
| 4g no silence gap over 1.4 s inside the narration | PASS | [] |
| 5a hard cuts (mean diff > 14) land only on shot boundaries | PASS | off-boundary: []; 121 cuts detected |
| 5b every shot boundary changes the picture | PASS | [] |
| 5c no A-B-A one-frame inserts | PASS | [] |
| 5d no single-frame brightness flashes | PASS | [] |
| 6a all on-screen text inside the safe area (x 40..1880, y 20..1040), 998 frames incl. every shot's first, middle and last | PASS | [] |
| 6b on-screen text at least 32 px | FAIL | [(4704, 'F57', 'Savings', 26), (4707, 'F57', 'Savings', 25)] |
| 6c every on-screen number appears in production/assumptions.csv, the script, or is a day/month label | PASS | ['0', '1', '1,050', '1,450', '1,840', '12', '16', '18', '2,200', '2,600', '20', '27', '3', '30', '390', '400', '5', '50', '52', '6', '600', '760', '80'] |
| 7 claim arithmetic (50 x 52 = 2,600; 2,600-760 = 1,840; -390 = 1,450; -1,050 = 400; total 2,200; 1,050 < 1,450 'enough') and check_numbers.py | PASS |  |
| 8 Maya sub-pixel placement noise <= 0.12 px (jitter_check method, all four poses) | PASS | worst 0.051px |
| 9a all 21 Ren shots: approved library clips inside their usable windows, feet fixed, 175 cm plate scale, every frame a distinct clip frame, real movement, static camera, Ren left / graphics right | PASS | [] |
| 9b consecutive Ren shots never repeat the same clip | PASS | [] |
| 9c Ren clip variety recorded | PASS | {'ren_hold_phone': 1, 'ren_nod_yes': 3, 'ren_open_arms': 3, 'ren_point_camera': 1, 'ren_point_right': 3, 'ren_point_up': 1, 'ren_present_palm_left': 3, 'ren_shake_no': 1, 'ren_shrug': 3, 'ren_thinking': 2} |
| 10a Maya's measured height equals the calibrated plate perspective (165 cm, within 3%); head and feet in frame except deliberate close-ups (head in) | PASS | ([], []) |
| 10b every Maya shot changes pose or carries a moving prop/overlay (no shot is only a camera move over a still) | PASS | [] |
| 10c no long stretch in which Maya only holds a phone pose (worried/relief) while graphics change: longest stretch without a Ren shot or a phone-free Maya pose <= 20 s | PASS | longest 7.3s at 15-22 s; phone-pose share of Maya screen time 7% |
| 10d no more than 4 consecutive Maya shots on the same plate (environmental variety) | PASS | longest same-plate run 3 |
| 11 constant 24 fps: every packet 1/24 s apart, no dropped or duplicated timestamps | PASS | 7699 packets, delta 0.04167-0.04167 |
| 12a voice runner config: Qwen/Qwen3-TTS-12Hz-1.7B-Base, English, x_vector_only_mode=True, Audio/ren_reference.wav, fixed seeds, no speed change | PASS |  |
| 12b renderers import and call no TTS code | PASS |  |
| 12c MP4 audio matches the joined narration WAVs (correlation >= 0.95) | PASS | 1.0000 |
| 12d spoken-word check against the script (Whisper) | PASS | see voice_check_summary.json |
| 13a approved pilot frames (0 to 80% of S17) unchanged in the full episode (max per-frame mean difference at 480x270) | FAIL | worst 12.26/255 over 1345 frames |
| 13b pilot narration unchanged in the full episode (correlation over the pilot's length) | PASS | 1.00000 |

## Not run / limits
- NOT RUN: listening review (accent, pace, pronunciation, joins). Whisper only confirms words.
- NOT RUN: the repo's older qa_timeline.py, validate.py, jitter_check.py (wired to the 720p free_money renderer); their checks are re-implemented here.
- Ren mouth-closed is not detected automatically: it rests on the library notes and on contact sheets I viewed.
- 'Mobile readability' is checked as a minimum font size (32 px at 1080p) and the safe area; no phone playback was possible.
- Maya is static artwork (four poses): pose cross-fades, camera pushes and moving props; none of this is character animation.
