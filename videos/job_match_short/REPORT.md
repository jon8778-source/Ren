# Ren short: "My Job Offered Free Money. I Said No."

**File:** `ren_job_match_short.mp4`. 1080x1920, 30 fps, H.264 + AAC (48 kHz mono), **14.38 s** (limit 15.0 s). Loudness -17.2 LUFS, true peak -2.7 dBTP. No music.

## Voiceover timing (real, measured from the generated audio; Whisper word times drive captions and graphics)
| Line | Start | End | Text |
|---|---|---|---|
| L1 | 0.12 | 3.01 | At twenty-five, my job matched up to four percent. |
| L2 | 3.15 | 5.95 | I put in two, because my car lease felt urgent. |
| L3 | 6.09 | 9.88 | That's about eight hundred eighty dollars a year of free money, gone. |
| L4 | 10.02 | 11.13 | Check your match tonight. |
| L5 | 11.27 | 12.80 | It takes ninety seconds. |
| L6 | 12.94 | 13.88 | Story Friday. |

Scenes were fitted to this audio, not the target times: 0.00-1.22 keys, 1.22-3.11 HR folder, 3.11-10.18 the "2%" chip and the ghost jar, 10.18-12.95 phone, 12.95-14.38 Story Friday (last 0.5 s is a held frame). Scenes 1 and 2 are shorter than the targets and scene 3 is longer because the voice runs faster than the brief's targets. Whisper heard every line correctly. It writes numerals ("25", "$880", "90") where the script has number words.

## Assets used
- Ren clips from `assets/ren_library`: `ren_idle_calm` (scenes 1-2, plus the tail of scene 3), `ren_point_down_right` (scene 3), `ren_point_right` (scene 4), `ren_wave_hello` (scene 5). All are closed-mouth clips. Ren is cut out of the near-white backdrop with the existing `RenShot`/`cut_out` code, onto pure white (255,255,255).
- Voice: Qwen3-TTS 1.7B Base clone, run locally on CPU. Reference: `Audio/ren_reference.wav` and its transcript. Seeds are fixed (`gen_voice.py`).
- Font: Fredoka 500/700 (`project/remotion/public/fonts`).
- Coded in `videos/job_match_short/build_short.py`: lease keys with sparkle, "Age 25" tag, HR folder ("4%" turns green), "2%" chip, ghost jar with the red "-$880/yr" label (one pulse on "eight hundred eighty", drains and fades on "gone"), phone settings UI with the 2% to 4% toggle, "90 seconds" badge, Story Friday card with a "Part 2" tag, word-by-word captions, disclaimer. Nothing is an AI-generated image.

## Checks (run on the final MP4)
- 1080x1920, 30 fps, AAC audio present. Runtime 14.37 s.
- All 431 frames: no tint, gradient or coloured area at the edges. The corner pixel is exactly 255,255,255. Frames 33-41 touch the edge only because Ren is sliding in during the 0.25 s slide transition.
- Nothing in the top 150 px. Static graphics stay clear of the right 130 px and the bottom limit (only sliding content crosses the right strip during transitions).
- One still per scene checked for clipping and caption sync. The live (green) caption word matches the spoken word in each.

## Gaps, deviations and risks
1. **No younger Ren and no puppet rig in the repo.** I used standard Ren with an "Age 25" tag. Without a rig there is **no coded mouth flap**, and the project rule is no artificial talking motion. Ren's mouth stays closed in the reused clips.
2. **Keys are drawn over Ren's hand** and tracked to its position. They do not deform with his fingers. In scenes 4-5 he has no keys (he is pointing and waving).
3. **Accent is unchecked.** The voice is the existing Ren clone. I cannot listen to audio. Please check the accent (light Manchester), pronunciation and tone. The Qwen model reproduces the reference recording and does not follow the accent description.
4. **Disclaimer is at the bottom (y about 1750) as requested.** It is tiny and low-contrast. YouTube Shorts and TikTok UI usually covers the bottom of the frame, so it may be hidden there. The top (y 150) is a safer spot if that matters.
5. Loudness is -17.2 LUFS rather than exactly -16, because the limiter caps the peaks (true peak -2.7 dBTP).
6. Scenes 1-2 are short (1.2 s and 1.9 s) because the real audio is quicker than the brief's targets. Ren's idle clip is a calm hold, so the "rushed" feel in scene 3 comes only from the jiggling keys and the chip.
