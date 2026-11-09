# Hybrid QC - Three Bills in 30 Days, pilot

File: `pilot.mp4` | 1364 frames | 1920x1080 @ 24 fps | 56.8 s

Command: `project/.tools/venv/bin/python videos/three_bills/tb_qa.py <mp4>`; thresholds are in the script.

| Check | Result | Measured |
|---|---|---|
| 1a shots contiguous from frame 0 to the last frame | PASS | [] |
| 1b shot caps (Ren / Maya action 5.5 s, story still 2.5 s, graphic 3.5 s) | PASS | [] |
| 1c shot mix recorded | PASS | {'CHARACTER_ACTION': 14, 'REN_ANIMATED': 4, 'STORY_STILL': 0, 'GRAPHIC': 5} |
| 1d no run of 3 or more consecutive graphic-only shots (long-form baseline: avoid card sequences) | PASS | longest run 1 |
| 1e Ren returns at least every 45 s | PASS | Ren shots start at [0.0, 12.4, 30.4, 52.9]; longest gap 22.5s |
| 2a shot phrases tile the approved v2 voice script, paragraphs 1-9, in order, unchanged | PASS | 164 vs 164 words |
| 2b SCRIPT.md and VOICE_SCRIPT.txt match the approved SHA-256 (14801320..., efa04724...) | PASS |  |
| 3a pack assets on disk match ASSET_MANIFEST.json hashes (Maya poses, props, plates) | PASS | [] |
| 3b approved plates, narration WAVs and the voice reference exist | PASS | [] |
| 4a full decode clean (-xerror) | PASS |  |
| 4b format 1920x1080 24 fps h264 + aac | PASS | 1920x1080 24/1 |
| 4c frame count equals shot frames | PASS | 1364 vs 1364 |
| 4d video and audio lengths within 0.1 s | PASS | video 56.833s audio 56.832s |
| 4e narration length equals H + L (cut after the pilot's last sentence) as generated | PASS | 56.808s vs 56.808s |
| 4f loudness -23..-12 LUFS, true peak <= -1 dBTP | PASS | -18.6 LUFS, -1.0 dBTP |
| 4g no silence gap over 1.4 s inside the narration | PASS | [] |
| 5a hard cuts (mean diff > 14) land only on shot boundaries | PASS | off-boundary: []; 22 cuts detected |
| 5b every shot boundary changes the picture | PASS | [] |
| 5c no A-B-A one-frame inserts | PASS | [] |
| 5d no single-frame brightness flashes | PASS | [] |
| 6a all on-screen text inside the safe area (x 40..1880, y 20..1040), 266 frames incl. every shot's first and last | FAIL | [(402, 'Unexpected bill', [580, -577, 960, -525]), (408, 'Unexpected bill', [580, -290, 960, -238]), (1055, 'Savings', [1387, 1183, 1554, 1228]), (1055, '$80', [1402, 1299, 1538, 1371]), (1055, 'Eighty dollars', [1332, 1 |
| 6b on-screen text at least 32 px | PASS | [] |
| 6c every on-screen number appears in production/assumptions.csv (or is a day/month label) | PASS | ['1,050', '1,450', '1,840', '12', '18', '2,200', '2,600', '3', '30', '390', '400', '6', '600', '760', '80'] |
| 7 claim arithmetic (760 + 390 + 1,050 = 2,200; 2,600 - 2,200 = 400; 50 x 52 = 2,600) and check_numbers.py | PASS |  |
| 8 Maya sub-pixel placement noise <= 0.12 px (jitter_check method, all four poses) | PASS | worst 0.051px |
| 9 all 4 Ren cutaways: approved library clips inside their usable windows, feet fixed, 175 cm plate scale, every frame a distinct clip frame, real movement, static camera, Ren left / graphics right | PASS | [] |
| 10a Maya's measured height equals the calibrated plate perspective (ren_stage height_px for 165 cm, within 3%) and feet are inside the frame | FAIL | ([], [('S12', 759, [697, -76, 975, 928]), ('S12', 761, [697, -76, 975, 928]), ('S12', 763, [697, -76, 975, 928])]) |
| 10b every Maya shot changes pose or carries a moving prop/overlay (no shot is only a camera move over a still) | FAIL | ['S09b'] |
| 11 constant 24 fps: every packet 1/24 s apart, no dropped or duplicated timestamps | PASS | 1364 packets, delta 0.04167-0.04167 |
| 12a voice runner config: Qwen/Qwen3-TTS-12Hz-1.7B-Base, English, x_vector_only_mode=True, Audio/ren_reference.wav, fixed seeds, no speed change | PASS |  |
| 12b renderer imports and calls no TTS code | PASS |  |
| 12c MP4 audio matches H + L waveform (correlation >= 0.95) | PASS | 1.0000 |
| 12d spoken-word check against the script (Whisper) | PASS | see voice_check_summary.json (digits differ only) |
| 13a unaffected shots (S01-S04, S06, S11, S15-S17) keep their frame ranges and look unchanged from the first pilot (max per-frame mean difference at 480x270) | PASS | range changes []; worst 0.23/255 |
| 13b narration identical to the first pilot's audio (correlation) | PASS | 1.00000 |

## Not run / limits
- NOT RUN: listening review (accent, pace, joins, pronunciation). Whisper only confirms words.
- NOT RUN: the repo's older qa_timeline.py, validate.py, jitter_check.py (wired to the 720p free_money renderer); their checks are re-implemented here.
- These checks are metadata and frame statistics. Visual inspection is recorded separately in REN_BASELINE_COMPLIANCE_REPORT.md with exactly what was viewed.
