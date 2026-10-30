# What If You Keep Postponing the Life You're Saving For? — REPORT

Script: `scripts/Ren_Postponing_Life_Script_v3.md` (v3, Alex only, used word for word; [S1]–[S12] markers are not spoken).
v2 is kept beside it for reference.
Branch: `video/postponing-life`.

## Gate 1 — inventory and plan (no rendering yet)

Status: **plan revised from Jon's answers; waiting for approval of script v3 and this plan.**

### Decisions (Jon, 29 Oct)

- **Palette:** navy on white. Code-built text and graphics use Fredoka with `config.json` navy `#13233F` on white `#FFFFFF`. Muted grey is for small captions. Red and green are used only where a graphic needs them.
- **Maya:** set aside. `supporting-cast.png` is not used.
- **Script:** rewritten as v3 with Alex alone. Maya is removed; her lines become Alex's own thoughts, and the friend appears only as a text message.
- **Voice:** run the Qwen3-TTS 1.7B Base model in this container, with the same reference WAV and transcript, so there's no Space quota.

### 1. Production template

**Missing.** None of `engine/`, `library/`, `videos/_new_video/`, `docs/PRODUCTION_GUIDE.md` or
`clips.json` exist on `main` or on any other branch. As instructed, the fallback is the clip library:
`assets/ren_library/` + `ren_library.json`, rendered with `project/cliplib/render_shots.py`, which
will need extending for 1920×1080, story stills, push-ins, speaker tags and the infographic.

There is no "template palette and fonts" to follow. The repo's house style (`project/config.json`)
is Fredoka with navy/green/red/gold on white. Alex's stills use warm cream/sage/rust. Proposal:
Fredoka plus the config colours for all code-built text, with stills keeping their own palette.
**Decided: navy on white.**

### 2. Ren clips

All 32 clips in `ren_library.json` are `status: ok`. None is marked "redo" anywhere.

| Use | Clips |
|---|---|
| Presenter, talking or neutral | `idle_calm`, `idle_listen`, `nod_yes`, `open_arms`, `shrug`, `thinking` |
| Point at text beside him | `point_right` (mirror for left), `present_palm_left` (mirror for right), `point_down_right`, `point_up`, `point_camera` |
| Reactions | `worried`, `relieved`, `confused`, `facepalm`, `shocked`, `celebrate_fist_pump`, `thumbs_up`, `idea`, `rub_hands`, `lean_in` |
| Props | `clipboard_tick` (budget, S7), `hold_phone` (S6), `count_fingers`, `empty_pockets` |
| Entrances and exits | `walk_in_left`, `walk_off_right`, `walk_in_place_profile`, `wave_hello`, `wave_bye` |

Known problems:
- **`explain_hands`: unusable.** Its window is 9.0–28.0s, but the file (replaced on 26 Oct) is 9.98s long.
- **Format and resolution:** clips are 1280×720 on a near-white background. At 1920×1080 they are scaled up 1.5×, so Ren will look slightly soft. The renderer keys the off-white background to pure white. That changes the background only; Ren himself is untouched.
- **`hold_phone`:** black rectangle near his hand at about 8s. Cut before it.
- **`idle_calm`:** turns and shifts about 15px at 1.5–3.5s. Avoid that stretch as filler.
- **`walk_in_left`:** its `x_offset_px` of 0 leaves Ren about 14px off his mark at the end.
- **Open mouth during voice:** `shocked`, `celebrate_fist_pump`, `empty_pockets`, `relieved`, `idea`, `rub_hands`, `thumbs_up`, `worried`, `count_fingers` and `clipboard_tick` have open-mouth or grin notes.
- **Long gestures:** most last about 5–7s, which sets the pace of the presenter shots.

### 3. Alex stills

`library/characters/alex/` does not exist, and **there is no `laptop_trip_pinned` still anywhere**.
I can't say whether its photo reads as being on a fridge. **No fridge appears in any existing art.**

What does exist is on branch `codex/retirement-ease-off-v3`, in
`project/prototypes/coffee-minute-v3/artwork/`, stored as base64 chunks. All four decoded to images
whose checksums match their manifest:

| File | Size | Content |
|---|---|---|
| `alex-home.png` | 1672×941 | Alex pours French-press coffee in a sage kitchen |
| `alex-cafe.png` | 1672×941 | Alex taps his phone to pay in a café |
| `office.png` | 1672×941 | Empty home office with a laptop on the desk; no people |
| `supporting-cast.png` | 1536×1024 | Line-up of Alex, a woman, and a second man |

Alex: short wavy auburn hair, sage-green overshirt over a cream tee, dark trousers. **Flag:**
`supporting-cast.png`'s source name is "Centered Maya in illustrated character lineup". That
conflicts with "Maya has no approved design". **Set aside (Jon).**
These stills are 1672×941, so 1920×1080 is a 1.15× upscale. Fine.

### 4. Ren's voice

- **What it should be:** the Qwen3-TTS voice clone on the `Qwen/Qwen3-TTS` Space (1.7B Base model), with `Audio/ren_reference.wav` and its transcript as the reference for every line. The script `project/cliplib/qwen_voice.py` does this.
- **Network:** now that `huggingface.co` is allowed, the Space connects.
- **No usable allowance:** anonymous calls have 0s of free GPU time left. The token pasted on 26 Oct now returns 401 Unauthorized, so it has been deleted or has expired. No line has been generated yet.
- **Ways to get it working:**
  1. A new token in the environment (`HF_TOKEN`), ideally on PRO (40 min of GPU time a day).
  2. Running the same model ourselves. Branch `codex/ren-hybrid-template` has `local_voice.py`: the same model, the same reference, no quota. This container has 4 CPU cores, 15 GB of memory and no GPU. The speed here is untested; it's likely slow but workable for about 1,000 words.
  3. You supply S1.wav, S2.wav and so on.
- **Placeholder:** until then, timing can use a placeholder voice (Kokoro, as in earlier videos), with every file named `…PLACEHOLDER_VOICE…`.

### 5. Timing

At about 150 wpm with short pauses: **984 words (v2), about 7:05; v3 is 960 words, about 6:55**, not the script's "about 6½ minutes".
The S1+S2 pilot is 148 words, about 64s. Real timings come from the real voice.

### 6. Shot plan

Scene types: **P** presenter (Ren clip on white, text beside him), **S** story still (slow push-in),
**D** detail crop of a still, **I** code-built infographic. Visuals change at least every 7s, and cuts
fall on sentence ends. Every on-screen word is a code overlay. Speaker tags appear only while Ren reads a quote.

| § | Time | Beats → scene type, asset | On-screen text | Fridge |
|---|---|---|---|---|
| S1 | 0:00–0:42 | "photo…fridge" **D** fridge photo, push-in → "never been there" **S** fridge door, wider → "researched cabins…socks" **S** Alex at laptop with cabin listings → "ready for four years" **D** photo again → "Next year…" **S** Alex at laptop → "some reasons are very good" **P** `thinking` → "I'm Ren…" **P** `wave_hello` | "4 years"; **Alex:** tag on his line; title card "What If You Keep Postponing the Life You're Saving For?" | **Yes**: aspiration |
| S2 | 0:42–1:04 | "car had just broken down" **S** broken-down car → "debt…optimism" **P** `worried` → "they waited… retirement" **I** 3-step ticks: pay down the card → emergency savings → retirement → "Waiting helped" **P** `nod_yes` | step labels; "Waiting helped" | — |
| S3 | 1:04–1:48 | "the trip came up again" **D** mountain photo, quick → "Alex opened his accounts" **S** Alex at laptop → "Let's get a little more comfortable" quote → "photo stayed on the fridge" **D** fridge, slower push → "raise… target" **I** savings target line moving up → "moving summit" **I** mountain summit icon sliding up | **Alex:** tag; "Savings target" | **Yes**: still waiting |
| S4 | 1:48–2:13 | "looking at cabins again" **S** Alex at laptop, prices changed → his two questions to himself **D** crop on Alex's face → "He didn't have an answer" **P** `thinking` | **Alex:** tags | — |
| S5 | 2:13–3:02 | Ren steps out **P** `walk_in_left` → `open_arms`/`present_palm` with text beside him: "Alex isn't foolish" → "permission" → cabin growing **I** two nights → a week, simple → big windows → "helping each other postpone" **P** `shrug` | Key phrases beside Ren | — |
| S6 | 3:02–3:45 | friend's picture **S** phone in Alex's hand; the message and the trail photo are drawn on its screen in code → Alex's first and second thoughts → "what he actually wants" **I** three icons: days outside, breakfast without work messages, time off from house jobs → "smaller size" **P** `idea` | **Alex:** tags; message text; 3 labels | — |
| S7 | 3:45–4:26 | "sit down with their budget" **S** Alex at laptop with spreadsheet → "Alex is delighted" **P** `rub_hands` → budget **I** categories (stay, gas, food, park fees, buffer) ticked one by one, no $ → "trade-off" **P** `clipboard_tick` | Categories; caption "Example only, not financial advice" whenever the budget is shown | — |
| S8 | 4:26–4:52 | "clicks book" **I** "Book" button press → "thinks about canceling" **P** `worried` → plan re-check **I** ticks: bills covered, savings on track → "isn't evidence…" **P** `point_camera` | "Bills covered", "Savings on track" | — |
| S9 | 4:52–5:15 | **P** `open_arms` → **I** three icons: local walk, free event, afternoon with someone | 3 labels | — |
| S10 | 5:15–5:41 | rain **S** rainy cabin window → "forgets the coffee" **S** Alex staring into an empty mug → walk **S** Alex alone on a muddy trail | — | — |
| S11 | 5:41–6:19 | home **D** fridge → second photo appears beside the mountain (animated in) → "mud on his jeans" **D** crop on weekend photo → "a month later" **P** `nod_yes` → "proof…" **P** `relieved` | — | **Yes**: second photo |
| S12 | 6:19–7:05 | challenge **P** `point_camera` → 3 steps **I** pick one → ask what you want → find a version that fits → "give someday a next step" **P** `thumbs_up` → fridge, both photos **D** slow push-out → CTA and sign-off **P** `wave_bye` | Steps; "What's still on your fridge?"; "Educational only, not financial advice" (house rule) | **Yes**: final shot |

### 7. Missing assets and the cheapest fix

| Asset | Used in | Cheapest fix |
|---|---|---|
| Fridge door, no photos | S1, S3, S11, S12 | **New still**, prompt A. Photos are composited on in code, so all four appearances match and the second photo can animate in. |
| Mountain photo | S1, S3, S11, S12 | **New still**, prompt B, composited onto the fridge |
| Weekend photo | S11, S12 | **New still**, prompt C: Alex alone, a selfie |
| Alex at laptop | S1, S3, S4, S7 | **New still**, prompt D. Screen content (cabins, spreadsheet) is added in code, so one still covers all four. |
| Broken-down car | S2 | **New still**, prompt E. Or, cheaper: a code-built icon card. |
| Phone in Alex's hand | S6 | **New still**, prompt F. Screen content added in code. |
| Rainy cabin window, empty mug | S10 | **New still**, prompt G |
| Alex on a muddy trail | S10 | **New still**, prompt H |
| Infographics: 3 steps, target line, cabin growth, budget, book button, icons | S2–S12 | **Code-built**, no new art |
| Kitchen and café stills (`alex-home`, `alex-cafe`) | — | Reusable only as Alex's background life (S5 "money in the bank means options"); not essential |

**Ready-to-paste image prompts.** Shared style line for all of them:
"Flat illustrated storybook style, clean confident outlines, restrained soft shading, warm cream,
sage green and muted rust palette, soft natural light, no text, no lettering, no logos, 16:9."
Alex: "a man in his early 30s with short wavy auburn hair, sage-green overshirt with rolled
sleeves over a cream T-shirt, dark trousers".

- **A, fridge door:** "Close view of a cream retro fridge door in a sage-green kitchen, a few plain magnets, an empty clear space at eye level for a photo, no photos, no paper, no people. [style]"
- **B, mountain photo:** "A slightly faded printed travel photo of a snowy mountain above a pine forest and a lake, white photo border, a strip of tape on the top edge, straight-on, isolated on a plain background. [style]"
- **C, weekend photo:** "A printed selfie snapshot with a white border: [Alex] alone on a forest trail in light rain, grinning, mud on his jeans, holding a slightly squashed sandwich, casual and unglamorous. [style]"
- **D, Alex at laptop:** "[Alex] sits at a wooden desk in a cosy home office, side-on, looking at an open laptop, the screen blank and facing the viewer at an angle, thoughtful expression, plants and a window. [style]"
- **E, broken-down car:** "A small dusty hatchback at the side of a quiet road with its hood up and hazard lights on, cloudy sky, no people. [style]"
- **F, phone in hand:** "A man's hand and sage-green shirt cuff holding a smartphone towards the viewer, blank bright screen, cosy living-room background softly out of focus. [style]"
- **G, rainy window:** "[Alex] at a small wooden cabin table by a rain-streaked window, staring into an empty coffee mug with mock despair, forest outside, morning light. [style]"
- **H, muddy trail:** "[Alex] walking along a muddy forest trail towards a viewpoint, seen from three-quarter behind, small backpack, misty valley ahead. [style]"

### 8. Things I'm unsure about

1. **The friend's message in S6:** shown as text on Alex's phone. Is a friend existing off-screen OK?
2. **Disclaimer wording:** the house rule is "Educational only, not financial advice" at the start and end, and in the description. Your prompt adds "Example only, not financial advice" for budget scenes. I've planned both.
3. **Frame rate:** your prompt says 24 fps; the main pipeline's config uses 30. I'll follow your 24.

### Voice update (30 Oct)

- **Fixed reference:** `Audio/ren_reference.txt` didn't match `Audio/ren_reference.wav` (it was a different take). That made Qwen run on to its 163s limit on almost every line. Corrected to the transcript of the recording (Jon approved).
- **S1 and S2:** narrated locally with Qwen3-TTS 1.7B Base in `voice/`: S1.wav 29.65s and S2.wav 18.27s, about **48s** in total, not the estimated 64s.
- **Checked:** `project/cliplib/check_voice.py` (faster-whisper medium.en) heard every one of the 15 lines word for word. Four short lines are faster than 230 wpm; the average is about 205 wpm. Results are in `voice/voice_check.json`.
- **Loudness:** before mixing, -18.0 LUFS (S1) and -17.5 LUFS (S2). The final mix normalises to -16.
- **Speed here (4 CPU cores):** about 6 minutes to load the model, then 26–68s per line. The whole script would take roughly 1–1½ hours.
- **Pace (Jon, 30 Oct):** keep the natural pace. No slow-down.

## Gate 2 — 60-second pilot (S1 + S2)

Status: **revision 2 rendered (Ren in the office); waiting for Jon's review.** Files: `pilot/pilot_S1-S2.mp4`, voice only
`pilot/pilot_S1-S2_voice.wav`, checks `pilot/pilot_report.json`. Built by `build_pilot.py`. Rendered videos and voice-only mixes are not stored in git (Jon, 30 Oct); rebuild with `build_pilot.py` / `build_video.py`, or ask for them to be sent.

- **Duration:** 50.1s. Ren's natural pace is quicker than the 150 wpm estimate, so it's under the 60 seconds aimed for.
- **Format:** 1920×1080, 24 fps, H.264 + AAC 192k.
- **Narration:** -16.2 LUFS integrated, true peak -1.2 dBTP. The voice is the only audio; no music or clip audio.
- **Validator:** this is my own check, because the template's validator doesn't exist. Format OK; no text touches Ren on any frame; no Ren clip is repeated. **Flag:** two shots last 7.3s and 7.2s (shot 2, the laptop; shot 9, the infographic), just over the 7s rule. Each covers one unbroken sentence and keeps moving (scrolling listings, ticks), so I didn't cut mid-sentence.

| # | Time (s) | Type | Asset | Narration |
|---|---|---|---|---|
| 1 | 0.00–4.96 | story still, push-in to the photo | A_fridge + B_mountain_photo composited; opening disclaimer | S1 lines 1–2 |
| 2 | 4.71–11.98 | story still | D_alex_laptop + code-built cabin listings scrolling on the screen | S1 line 3 |
| 3 | 11.73–14.02 | detail crop, slow push | fridge photo close-up; "4 years / and still waiting" | S1 line 4 |
| 4 | 13.77–18.68 | story still, closer | D_alex_laptop; **Alex:** tag and quote card during his line | S1 lines 5–6 |
| 5 | 18.43–24.82 | presenter | `ren_thinking` (1.25–7.6s of the clip); "Some of those reasons are very good." | S1 lines 7–9 |
| 6 | 24.57–30.57 | presenter | `ren_wave_hello` (1.12–7.1s); title | S1 line 10 |
| 7 | 30.32–34.39 | story still, push-in | E_car | S2 line 1 |
| 8 | 34.14–40.15 | presenter | `ren_worried` (whole 1.25–7.0s window + 0.3s `idle_calm`); three labels on their words | S2 line 2 |
| 9 | 39.90–47.07 | infographic | code-built 3 steps; ticks on "card", "savings", "retirement" | S2 lines 3–4 |
| 10 | 46.82–50.12 | presenter | `ren_nod_yes` (4.71–8.0s, ending on its neutral frame); "Waiting helped." | S2 line 5 |

Cuts sit midway through the pauses between lines, with 0.25s dissolves.

**Flags and unsure points**
- **Open mouth during narration:** `ren_worried`'s notes say "Gritted teeth ~2s", and it plays under S2's debt line.
- **Shots ending early:** `ren_thinking` and `ren_wave_hello` end 0.6s and 0.1s before their neutral frames; the dissolves cover it.
- **Shots starting mid-gesture:** `ren_nod_yes` starts 3.6s into its window, mid-nod, with the dissolve covering the start.
- **Ren's sharpness:** his clips are scaled up 1.5× from 1280×720, so he's slightly softer than the stills.
- **Text I added:** "and still waiting" (shot 3) isn't in the script; it's on-screen only. Easy to drop.
- **Disclaimer:** "Educational only, not financial advice" shows for the first 3s (house rule). There's no budget on screen, so no "Example only" caption yet.
- **The fridge photo** reads as being on the fridge: the code composite of B on A, with tape and a soft shadow.

### Revision 2 (Jon: "use Ren in the office background")

- **Ren's backdrop:** all four presenter shots now place Ren in front of the approved `office.png` (from `codex/retirement-ease-off-v3`, checksum verified, copied to `stills/`). The office is softly blurred, and a faint shadow sits at his feet. This replaces the house "plain white background" rule for this video, at Jon's request.
- **How Ren is cut out:** only white that touches the edge of the frame, plus enclosed pure-white pockets (such as the gap under a waving arm), is removed. His pale T-shirt stays solid; a simple colour key had made it see-through, and that's now fixed. His edges are cleaned of white fringing. His frames are not otherwise changed.
- **Unchanged:** the story stills, the infographic (still on white), the timing, the narration (-16.2 LUFS) and the length (50.1s).


## Gate 3 — full production (S1–S12)

Status: **rendered; waiting for Jon's review.** Approved by Jon ("approved for full production").
Files: `final/postponing_life.mp4`, voice only `final/postponing_life_voice.wav`, checks
`final/postponing_life_report.json`, YouTube description `description.txt`. Built by `build_video.py`,
which reuses the approved pilot's shots for S1–S2. Rendered videos and voice-only mixes are not stored in git (Jon, 30 Oct); rebuild with `build_pilot.py` / `build_video.py`, or ask for them to be sent.

- **Duration:** 327.9s (5:28) at 1920×1080, 24 fps. The script's estimate was 6½–7 minutes; Ren's natural pace is quicker.
- **Narration:** -16.3 LUFS integrated, true peak -1.0 dBTP. All 97 lines are in Ren's cloned voice (Qwen3-TTS 1.7B Base, run locally), checked by speech-to-text (`voice/voice_check.json`).
- **Lines to listen to:** speech-to-text heard S3_03 "he just hit" (script: "he'd just hit"), S5_03 "he started" (script: "he's started") and S3_05 "photos stayed" (script: "photo stayed"). Two other mismatches are checker artefacts ("3" for "three", "Wren" for "Ren").
- **Validator:** no text touches Ren in any of 61 shots. Same clip back to back: none.
- **Ren clips used twice:** ren_count_fingers, ren_nod_yes, ren_open_arms, ren_point_camera.
- **Shots over 7s:** D_alex_laptop + listings (7.3s), savings vs a moving target (8.7s), ren_walk_in_left (8.5s), the cabin grows (9.1s), F_phone_in_hand + friend's message (8.0s), ren_idle_listen (7.8s), what he actually wants (8.7s), weekend budget categories (no $) (11.8s), G_empty_mug, close on Alex and the mug (7.7s), D_alex_laptop + accounts screen, a month later (8.3s), challenge steps (7.7s). Each covers one unbroken sentence and keeps moving (graphics revealing on the narration, Ren walking in, camera pushes or cards appearing). The final fridge shot was split so it ends on the fridge.
- **Open-mouth notes during narration:** `ren_worried`, `ren_count_fingers` (twice), `ren_rub_hands`, `ren_celebrate_fist_pump`, `ren_thumbs_up`.
- **Fixes after reviewing every shot:**
  - Alex's face kept in frame on the laptop shots.
  - Quote cards kept inside the frame.
  - Gestures that returned to neutral after 1s now start partway in and end on their neutral frame.
  - Long holds split at natural pauses.
  - Thumbs-up moved to a line long enough for the whole gesture.
  - The S10 mug shots are cropped so the French press never shows (it contradicted "he forgets the coffee").
- **Not done:** no music; no shorts or thumbnails (not part of this brief).

| # | Time (s) | Lines | Type | Asset |
|---|---|---|---|---|
| 1 | 0.0–5.0 | S1_01–S1_02 | story still | A_fridge + B_mountain_photo |
| 2 | 4.7–12.0 | S1_03 | story still | D_alex_laptop + listings |
| 3 | 11.7–14.0 | S1_04 | detail crop | fridge photo close; 4 years |
| 4 | 13.8–18.7 | S1_05–S1_06 | story still | D_alex_laptop close; Alex: tag |
| 5 | 18.4–24.8 | S1_07–S1_09 | presenter | ren_thinking |
| 6 | 24.6–30.6 | S1_10 | presenter | ren_wave_hello |
| 7 | 30.3–34.4 | S2_01 | story still | E_car |
| 8 | 34.1–40.1 | S2_02 | presenter | ren_worried |
| 9 | 39.9–47.1 | S2_03–S2_04 | infographic | three steps |
| 10 | 46.8–49.6 | S2_05 | presenter | ren_nod_yes |
| 11 | 49.4–53.6 | S3_01–S3_02 | story still | D_alex_laptop + accounts screen |
| 12 | 53.3–59.5 | S3_03 | presenter | ren_shake_no |
| 13 | 59.2–62.0 | S3_04 | story still | D_alex_laptop close; Alex: tag |
| 14 | 61.8–64.2 | S3_05 | story still | fridge (anchor: still waiting) |
| 15 | 64.0–72.7 | S3_06–S3_08 | infographic | savings vs a moving target |
| 16 | 72.5–78.9 | S3_09–S3_10 | presenter | ren_point_up |
| 17 | 78.7–82.0 | S3_11 | detail crop | fridge photo close: a moving summit |
| 18 | 81.7–88.9 | S4_01–S4_02 | story still | D_alex_laptop + listings |
| 19 | 88.7–93.0 | S4_03 | story still | D_alex_laptop close; Alex: tag |
| 20 | 92.8–96.0 | S4_04–S4_05 | presenter | ren_count_fingers |
| 21 | 95.7–99.3 | S4_06 | story still | D_alex_laptop, face; Alex: tag |
| 22 | 99.0–103.2 | S4_07–S4_08 | presenter | ren_shrug |
| 23 | 103.0–111.5 | S5_01–S5_02 | presenter | ren_walk_in_left |
| 24 | 111.2–115.9 | S5_03 | infographic | planned expense → emergency? |
| 25 | 115.6–121.2 | S5_04–S5_05 | presenter | ren_open_arms |
| 26 | 120.9–130.0 | S5_06–S5_08 | infographic | the cabin grows |
| 27 | 129.8–135.5 | S5_09–S5_10 | presenter | ren_confused |
| 28 | 135.2–139.0 | S5_11 | story still | D_alex_laptop + listings, slow push |
| 29 | 138.8–146.7 | S6_01–S6_03 | story still | F_phone_in_hand + friend's message |
| 30 | 146.5–154.3 | S6_04–S6_05 | presenter | ren_idle_listen |
| 31 | 154.1–162.7 | S6_06 | infographic | what he actually wants |
| 32 | 162.5–168.4 | S6_07–S6_08 | presenter | ren_present_palm_left (mirrored) |
| 33 | 168.2–175.2 | S7_01–S7_02 | story still | D_alex_laptop + budget sheet |
| 34 | 175.0–178.2 | S7_03–S7_04 | presenter | ren_rub_hands |
| 35 | 178.0–184.8 | S7_05 | infographic | checks before spending |
| 36 | 184.5–196.4 | S7_06–S7_07 | infographic | weekend budget categories (no $) |
| 37 | 196.1–203.2 | S7_08–S7_09 | presenter | ren_point_down_right |
| 38 | 202.9–206.3 | S8_01–S8_02 | infographic | the Book button |
| 39 | 206.1–211.1 | S8_03–S8_04 | presenter | ren_celebrate_fist_pump |
| 40 | 210.9–215.4 | S8_05 | story still | D_alex_laptop + budget sheet, closer |
| 41 | 215.2–219.9 | S8_06 | infographic | the plan, checked again |
| 42 | 219.7–225.0 | S8_07–S8_08 | presenter | ren_point_camera |
| 43 | 224.7–230.4 | S9_01 | presenter | ren_point_right |
| 44 | 230.1–234.8 | S9_02–S9_03 | presenter | ren_open_arms |
| 45 | 234.6–241.6 | S9_04 | infographic | free things to look forward to |
| 46 | 241.3–246.0 | S10_01–S10_02 | story still | G_empty_mug (cropped clear of the French press) |
| 47 | 245.8–253.5 | S10_03–S10_04 | story still | G_empty_mug, close on Alex and the mug |
| 48 | 253.2–258.6 | S10_05 | story still | H_trail, wide |
| 49 | 258.4–263.9 | S10_06 | story still | H_trail, closer on Alex |
| 50 | 263.6–269.1 | S11_01 | story still | fridge, mountain photo |
| 51 | 268.9–272.1 | S11_02 | story still | fridge: the weekend photo goes up (anchor) |
| 52 | 271.9–277.3 | S11_03–S11_04 | detail crop | C_weekend_selfie |
| 53 | 277.1–285.3 | S11_05–S11_06 | story still | D_alex_laptop + accounts screen, a month later |
| 54 | 285.1–292.2 | S11_07 | presenter | ren_thumbs_up |
| 55 | 291.9–296.3 | S12_01–S12_02 | presenter | ren_point_camera |
| 56 | 296.0–303.7 | S12_03–S12_04 | infographic | challenge steps |
| 57 | 303.5–309.8 | S12_05 | presenter | ren_count_fingers |
| 58 | 309.5–311.9 | S12_06 | presenter | ren_nod_yes |
| 59 | 311.7–317.7 | S12_07–S12_08 | story still | fridge: both photos |
| 60 | 317.5–321.3 | S12_09 | presenter | ren_hold_phone |
| 61 | 321.1–327.9 | S12_10 | story still | fridge: both photos (final shot) |

## Short (vertical, ~60 seconds)

Jon asked for one short of about a minute. Built by `build_short.py`; checks in `short/postponing_life_short_report.json`.
The video itself is not stored in git.

- **Format:** 60.4s, 1080×1920, 24 fps. Narration -16.3 LUFS, true peak -1.1 dBTP.
- **Narration:** 20 of the long video's own narration lines, the same voice files, so it sounds identical: S1_01, S1_02, S1_04–06, S3_10–11, S6_01–05, S7_05, S8_02, S11_02, S11_04, S12_06–09.
- **Story:** the fridge photo, "Next year", the moving summit, the friend's picture, Alex's two thoughts, the check before spending (no borrowing, emergency fund untouched), "book", the weekend photo going up, "someday" a next step, and the comment question.
- **Layout** (`project/config.vertical.json`): no text below y=1500 or in the right 130px; the disclaimer at the top at the start and end; "Example only, not financial advice" on the spending checklist. Wide stills are shown whole over a blurred fill; the phone and selfie fill the frame; Ren presents from the office with text above him.
- **Validator:** no text outside the safe area and none touching Ren.

### Short revision 2 (Jon: "not very portrait friendly")

- **Too much empty screen, or zoomed too close:** wide stills were a thin 16:9 band with blur above and below, or a tall crop that zoomed in too far.
- **Stills:** now a large 4:5 panel filling the screen from the disclaimer down to YouTube's controls. That shows about 45% of each picture's width, against 32% for a full-height crop, and blends into a soft fill of the same image.
- **Ren:** shown at nearly full height (2× clip scale) with his text above his head.
- **Graphics:** the checklist and "Book" screen are enlarged to fill the frame.
- **Closing fridge shots:** kept at the widest view so both photos are always fully in frame.
- **Checks:** 60.4s, -16.3 LUFS; validator: no text outside the safe area, none touching Ren.
