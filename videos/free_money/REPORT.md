# I Said No to Free Money for 3 Years: Gate 0 report (style lock and asset check)

**Status: waiting for your approval phrase: `style lock approved`.** Nothing has been built or rendered.
This replaces the earlier report on this branch, which described a provisional Gate 2 pilot that was never approved. Nothing from that attempt is reused.

Branch: `video/free-money-v2`. Script saved unchanged at `scripts/Ren_Free_Money_Script.md` (the section markers are never spoken). Pack unzipped to `library/` with its folder names kept.

## 1. Pack against your asset map: all 15 files present, none missing
| Asset | Size | Notes |
|---|---|---|
| ren_approved/ ×8 (neutral, hand on chest, thinking bust, pointing, extra thinking FB, presenting FB, standing FB, waving FB) | 1147-1464 × 1536 JPG | white background, matted below |
| characters/Dev_pay_stub, Priya_hiking_style, Uncle_Gary | 1086 × 1448 RGBA | one pose each |
| props/HR_folder_page6_prop | 1448 × 1086 RGBA | has baked-in text (section 4) |
| backgrounds/Porch, Office, Office_parking_lot_car | 1672 × 941 | **below 1920×1080, upscaled by 1.15×**. These are soft cartoon plates, so it should be fine, but it is a real softness cost |

## 2. Ren matting (`videos/free_money/matting.py`, output in `matted/`)
Method: background is near-white connected to the image edge only (flood fill from the border), plus enclosed pure-white pockets over 400 px. The white tee (about 230-245) is never keyed. Edges are softened by about 1 px, the white halo is removed (decontaminated), and a halo-shave pass removes the pale JPG ring around the outline.
**What I looked at:** all 8 matted stills over dark `#12161e`, white and orange `#e0933a` (`sheets/matte_all_backgrounds.png`), plus 1:1 zooms of the hair and glasses, the pointing hand and sleeve, and the waving hand (`sheets/matte_zoom_head_dark.png`).
**What I fixed:** the first pass produced an empty matte (my bug), and the second pass left a faint light fringe on the hair strands on dark. Both are fixed. **Remaining:** a thin dark dotted outline on the outermost hair (invisible on any mid or dark background) and a slightly shaved outer sleeve edge on the pointing bust. Nothing visible at video size.
Hair, cowlick, glasses, navy shirt over a solid white tee, trousers and sneakers all match your design lock in every still.
**Note:** the four bust stills end in a hard flat crop at the bottom edge. They must sit flush with the bottom of the frame or on a lower-third, never float.

## 3. Style match: Ren against Dev, Priya and Gary
**What I looked at:** (A) all four at on-screen size (800 px tall) on the office plate (`style_A_office_onscreen.png`); (B) at thumbnail size, 180 px, on white and dark (`style_B_thumbnail.png`); (C) face close-ups at equal scale (`style_C_face_detail.png`); the supporting cutout edges on dark (no halos, no white boxes); and a measured texture check.
- **Same family:** thin dark outlines, flat colour fills, similar skin and eye treatment. They read as the same show.
- **Measurable difference:** the supporting characters carry more local texture and shading. Texture score (local std in flat areas) is Ren 3.7, Dev 5.0, Gary 5.8 and Priya 6.3. Flat-colour share is 78% for Ren against 64-70% for the others. The visible cause is fabric texture on Dev's overshirt and Priya's jacket, hair highlights, and Gary's stubble and wrinkles. Their eyes are a little larger and their heads a little bigger than Ren's.
- **Thumbnail test: pass.** They are distinct by hair, colour and silhouette. One watch-point: Dev wears an open overshirt over a tee with dark trousers, the same construction as Ren, so keep them apart by colour (green against navy) in two-shots.
- **Verdict: PASS, minor mismatch.**
- **Recommended: (b) accept as is.**
- **Option (a) tested on a Priya test frame** (`filter_test_priya_before_after.png`, a median filter that keeps the dark outlines): it flattens the fabric but also smears the eye shading and adds stray lines. It looks worse. Not recommended, and not applied anywhere.
- **Option (c) is available** if you want to push further. Prompt for GPT: *"Match the attached Ren reference exactly: thin dark outlines, flat cel shading, no texture or gradients, no fabric detail, simple flat colour fills, natural adult proportions, same eye size and head size as Ren. Character: [Dev / Priya / Gary as in the current file], same pose and outfit. Plain white background."* Attach the standing Ren still.

## 4. HR folder baked-in text
**What I looked at:** the folder at 1500 px wide on the office plate at 1:1 (`folder_on_screen_1080p.png`, `folder_text_1to1_*.png`).
- "HR ENROLLMENT", "PAGE 6", "EMPLOYEE BENEFITS & RETIREMENT PLAN" and "EMPLOYEE BENEFITS" are **sharp, correctly spelled and legible** at that size. The rest of the page is non-text bars and icons.
- It will be small at normal two-shot size. Use it only as a detail crop (about 1300-1600 px wide), as the pilot plan does.
- It breaks your no AI-generated text rule, and the text says "Employee Benefits & Retirement Plan" but nothing about a 4% match.
- **Your decision:** (i) accept it for this video only, with "Page 6: We match 100% up to 4%" as a code overlay on the highlighted yellow row, or (ii) regenerate a blank folder and use code overlays for all the text. I recommend (i).

## 5. Known gaps: proposed cover
| Gap | Cover |
|---|---|
| Ren worried | Ren_1_neutral with a slow push-in and a code-built darkening. Alternative: Ren_3_thinking_bust. |
| Ren thumbs up | Ren_4_pointing (the thumb-up hand reads as a thumbs-up at bust size). |
| Ren wave (bust) | Ren_full_body_waving, only for the sign-off, as you said. |
| Leased car cutout | The parking-lot plate, with a slow push-in on the car for S2. |
| 8-year-old car (S6) | **Proposal only, not built:** the same parking-lot plate with a code-built grade (about 55% desaturation, a warm dull tint, a faint dusty overlay) and a code-built "8 years later" tag. I would show you one test frame before using it. |
| Closed folder | Skip it. The open page-6 folder slides in on "HR gave me a folder", so no closed folder is needed. |
| Hand with phone | A code-built phone overlay with a settings screen and a 2% to 4% toggle, shown beside Ren. No hand. |

## 6. Voice generation: what works from here
- **The hosted Space cannot be used from here.** It ran out of free quota, and the Hugging Face token you shared earlier is now invalid (401). I won't ask for a new token unless you want the Space.
- **Local Qwen3-TTS works in this container** (`project/cliplib/qwen_local_voice.py`, `gen_voice.py`). It is the same Qwen3-TTS 1.7B Base model as the Space's Voice Clone tab, built from `Audio/ren_reference.wav` and its corrected transcript, with fixed seeds. The 4.3 GB model is cached here. The first load can take several minutes. I generated the six short-video lines this way yesterday.
- **No placeholder voice needed.** I'd generate the real clone locally, one WAV per scene (S1.wav, S2.wav...), and check each line with Whisper.
- **Limits:** I can't hear audio, so please check accent, pronunciation and tone. The clone copies the reference recording, not the written accent description. Your supplied S1.wav, S2.wav... would also work and would replace mine.
- **Time:** about 732 spoken words is roughly 5 minutes of audio. On this CPU I'd allow 40-60 minutes in total, in the background.

## 7. Things I noticed in the brief and script (for you to decide)
1. **Pilot length:** S1 + S2 is 166 words (about 65 s), not the roughly 225 words / 85 s in the brief. The whole script is 732 words, about 4.8 minutes at this voice's pace. A pilot of about 65-70 s is what you will get unless you tell me otherwise.
2. **Maths I checked in the script:** 2% of $44,000 is $880. The raises give $920 and $960, so the total is $2,760. $2,760 at 7% for 30 years is about $21,000, and about $77 a month is the average missed. These all hold. The about $32 per paycheck take-home drop is plausible, but it depends on pay frequency and tax bracket.
3. **2027 limit:** the script says Milliman projects $25,500 and the IRS hadn't confirmed it by the end of October. I will re-check at Gate 4 and flag it, not edit it.
4. **Single poses:** Dev, Priya and Gary each exist in one pose only, and Ren has 4 busts and 4 full-body poses for about 5 minutes. The Gate 1 plan will add cutaways (props, infographics, code-built cards) to cover that.

## Files in this commit
`library/` (the unzipped pack), `scripts/Ren_Free_Money_Script.md`, `videos/free_money/matting.py`, `matted/` (8 transparent Ren PNGs), `sheets/` (the contact sheets named above), this report.

## 8. Amendment: v3 production rules now apply (added 7 November 2026)
Your answer was "Yes v3 rules please". I copied `AGENTS.md`, `project/REN_VIDEO_RULES.md`, `project/GITHUB_TASK_WORKFLOW.md` and `project/REN_SHORTS_RULES.md` from `codex/health-short-cinematic-v2` into this branch, read the first three in full, and amended the plan as below. Gate 0 findings (matting, style, folder text) are unchanged. I found no "story-first" document anywhere in the repo, so that part still rests on your script's own structure.

| v3 rule | What it changes here |
|---|---|
| Voice: `Qwen/Qwen3-TTS-12Hz-1.7B-Base`, English, `use_xvector_only=True` | Narration will be generated with the x-vector-only prompt (`x_vector_only_mode=True` locally), not the transcript-conditioned prompt (`False`) my earlier scripts used. **Discrepancy:** `project/cliplib/qwen_voice.py` and `qwen_local_voice.py` both default to `False`, while the v3 rules say `True`. I follow the rules and will compare against the reference. |
| No speed changes, stretching or silence padding | Lines are laid on the timeline as generated. Gaps between lines come only from the model's own silence and from cuts. I will not insert extra pauses. |
| Space workflow, resumable on quota, no paid fallback or blind retry | The Space is out of quota and the token is dead, so narration runs locally. Completed lines are kept and reused, and a failed line is inspected before it is retried. |
| Native-resolution Ren, 100% face and edge checks | The stills are matted from the full 1352-1464 px sources. Each gate's check includes 100% face, glasses and edge crops in wide and close framing. |
| Reuse the existing animation library (present_palm_left, nod_yes, shake_no, thinking), closed mouth, no random talking motion, inspect gesture direction | The plan will use those clips in presenter moments next to the approved stills, with palm-left never mirrored automatically. This is a change to your still-based brief, so the Gate 1 table will mark which shots are clips and which are stills. I will confirm each clip's real duration and direction before use. |
| Max shot length: Ren 5.5 s, story still 2.5 s, graphic 3.5 s. No repeated pose in consecutive shots. | The plan will be cut to those limits, with many more cutaways than before. The briefed push-ins on the folder and car count against the 2.5 s story-still limit unless you grant an exception. |
| No decorative wobble, no large white panel over desk or chair, text away from faces | Applied to every layout. |
| Disclaimer at start and end, no large banner | The briefed "Educational content only, not financial advice" lower-third will be small and shown at the start and end. |
| Every displayed equation true on every frame | Fixed totals, with a separate animated calendar or jar. The year counter and "Missed" amounts will never sit beside a wrong total. |
| Format: baseline 1280x720, 24 fps, H.264/AAC | I will build at 1280x720 and 24 fps. **This overrides the 1920x1080 in your brief.** The matted stills and plates can be re-rendered at 1080p later if you want it. |
| Branches | Stays on `video/free-money-v2`. No merge to `main`, no upload. |
| GitHub workflow | Checkpoint commits, remote verification, and `project/GITHUB_TASK_STATUS.md` kept up to date. |

**Still needs your decision:** whether to keep the 2.5 s story-still cap for the porch, folder and car shots, or allow longer holds on those specific shots.

**(Gate 0 stop line: satisfied. `style lock approved` received.)**
## 9. Gate 1: plan and outline (added 7 November 2026)
**Waiting for: `plan approved`.** Files: `shot_plan.csv`, `PLAN_TABLE.md` (the same plan as a readable table), `outline.md`, `plan_data.py` (the plan as data, with the checks below).
- **Defaults I took from "style lock approved":** style option (b), the folder text accepted for this video with a code overlay for the match line, and local voice generation with `use_xvector_only=True`. The 8-year-old car grade is in the plan **only as a pending item** and is built only if you approve it at this gate. Otherwise S6 shot 1 uses the plain plate with the same tag.
- **Plan checks, all passed:** the 130 phrases tile the script exactly, in order, with nothing added and nothing dropped. Every shot is within the v3 caps (Ren 5.5 s, story still 2.5 s, graphic 3.5 s) with a 0.1-0.3 s margin for estimate error, which is why there are 130 shots (48 Ren, 28 story, 54 graphic). No Ren pose repeats in adjacent shots, and the longest stretch without Ren on screen is 8 shots.
- **Estimated length** is 4.8 min, from word counts. Real timings come from the Whisper-checked narration. It is generating now (about 45 min; chunks are saved as they finish), and I will re-time the whole plan from it before Gate 2.
- **Repeated gestures:** with 4 busts and 4 full-body poses against about 4.8 minutes, Ren stills are used 49 times (R1 8, R3 8, R4 7, R2 6, FS 6, FP 5, FT 1, FW 1) plus 12 clips (shake_no 4, nod_yes 4, present_palm_left 3, thinking 1). How I'm avoiding visible repetition: no pose in adjacent shots, at least one cutaway between reuses, a different push direction each time, wide and close alternating, and the clips used for gestures that need real motion ("no", "yes", "present"). The weakest spots are S3 (R1 and R3 recur within about 7 shots) and S6 (4 busts in 12 shots).
- **Needs your call:** 130 shots in about 4.8 minutes is fast cutting (about 2.2 s average). It follows from the v3 caps (story stills can't exceed 2.5 s) and I think it is right, but if you want slower pacing the only lever is to allow longer holds, which means a cap exception.
- **Notes:** (1) the porch and parking-lot plates have no Ren-friendly floor space on the car side, so Ren stands on the left. (2) FS and the two-shot on the porch use Dev's single pose, since he has no other.

**(Gate 1 stop line: satisfied. `plan approved` received.)**
## 10. Gate 2: pilot S1 + S2 (added 7 November 2026)
**Waiting for: `pilot approved`.** The MP4 is **local only** at `/output/free_money_S1_S2_pilot.mp4` and is not in git, as you asked. This branch holds only the code, the narration WAVs and the reports.

| | |
|---|---|
| Format | H.264 + AAC (mono, 48 kHz), 1280x720, 24 fps, 1,238 frames |
| Duration | **51.58 s** video, 51.56 s audio (S1 19.03 s + S2 31.93 s of narration + 0.6 s visual hold). **Shorter than the 85 s in your brief:** S1 + S2 is only 166 words, and this voice speaks at about 3.3 words per second. |
| Loudness | **-16.2 LUFS**, true peak -1.6 dBTP (gain only; no speed change, stretching or padding) |
| Shots | 30 (11 in S1, 19 in S2); none over the v3 caps. One cut was pulled in by about 1 frame to meet the 2.5 s cap. |
| Validator (`validate.py`) | **PASS.** Full decode with errors fatal: clean. Format correct. Frame count equals duration. Shot frames add up to the video frames. No layout overlaps. One 0.63 s pause inside the narration, which falls right after "...of my salary." and is the model's own sentence-end pause. |
| Assets used, with timestamps | `videos/free_money/GATE2_assets_used.md` (every shot, file by file) |

**What I looked at (on the final MP4, not just on code output):** the first frame and the middle of all 30 shots on four contact sheets; the page-peel at four points; 100% crops of Ren's face in close busts (R1, R3), the wide full-body still, the shake_no clip and a library clip, and Dev's face; and a recheck of the shots I changed. All checked clean after fixes.
**What I fixed after looking:** Dev's head cut off in the porch close-up; half of Dev's face showing in the stub close-ups; the library clips were mostly idle filler (the planner kept only 0.3 s of real motion), so they now play the real footage from 1.30 s and cut on the action; the page-flip squeezed Ren horizontally, so it is now a page peel that never distorts him; an empty card box visible on some cut frames; a stray dot where the 2% chip starts; stray "T" and HR-label bits in the folder crops; a Day-one/Age-25 tag sitting over a desk drawer; and Ren's full-body stills too small against the office.
**Shots in the pilot:** present-day Ren as presenter on the office plate; the porch cold open with Dev and the pay stub; the code-built glowing "Employer match: 2%" line warped onto the stub; the page peel to age 25; the office and parking-lot plates with an "Age 25" tag; the HR folder as a detail crop with a slow push-in; and the code-built card where "Age 25: $44,000 salary", "Lease: $489/month" and "Page 6: We match 100% up to 4%" appear in sync with the words. The small "Educational content only, not financial advice" tag shows for the first 5 s and the last 4 s.

**Uncertain or not verified (please check):**
1. **Voice.** I can't hear audio. Whisper matches the script in both scenes. The differences it reports are only digits spelled as numerals, plus an invented "Thank you for watching…" at the tail of S1. That tail is not in the audio: all those words are stamped on the same instant at a near-silent tail.
   - **"lease" vs "least":** Whisper heard "least" in the last S2 line ("and the lease sounded urgent"). Please listen to that word. If it is wrong I can regenerate that chunk and compare.
   - **Accent and pace:** the voice is generated with the x-vector-only setting from the v3 rules, and it is faster than the earlier clone (about 3.3 against 2.55 words per second). Please check the accent and that the pace feels right.
2. **Resolution.** Built at 1280x720 per the v3 rules, not 1920x1080 from your brief. A final render at 1080p is possible if you want it.
3. **Library clip gestures.** The shake_no clip shows a raised open hand, not a head shake, and the clips are cut mid-gesture on hard cuts. The thinking and nod clips look right. Please confirm the gestures read well.
4. **Present-day Ren and the flashback share the office plate;** only the "Age 25" tag and the page peel separate them. Say if you want a different present-day background.
5. **Dev has one pose.** The stub close-ups crop his face out of frame.
6. **Ren's stills are static with slow push-ins;** the mouth stays closed, with no talking motion, as the v3 rules say.
7. **Validation limits:** this used my own `validate.py`, not the existing repo validator, and there is no approved reference MP4 to compare frames against.
8. The 2.5 s story-still cap forced the folder and car shots to be short. No exceptions were needed in the pilot.

**Narration status:** S1 and S2 are done and checked. The background job for S3-S7 stopped after the first two S3 chunks (likely memory pressure while rendering). It is resumable and I restarted it. S3-S7 are not yet generated or checked.

**STOP. Waiting for: `pilot approved`.**

