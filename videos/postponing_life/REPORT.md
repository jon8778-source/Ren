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
