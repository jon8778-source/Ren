# Asset requirements report: 1-minute Short from "Three Bills in 30 Days"

Prepared before rendering (v3 Shorts rules, asset-first checkpoint). **Status: prototype (first 15 s) only; the complete Short is not rendered until the owner approves the prototype.**

## Narration
- 58.95 s, 179 words, cut from the approved full-episode narration by `short_audio.py` (excerpts: H s1-7 and s10-12, D1 s5-6, D2 s6-7, D4 s12-14, D5 s9-11, D7 s7-8): whole sentences, script order, wording unchanged.
- No new synthesis, speed change, stretching or inserted silence; excerpts start 0.05 s before the first word and keep up to 0.22 s of the original audio after the last. **The six joins between non-adjacent excerpts are tighter than in the full episode: listen to each** (I cannot hear audio).

## Inventory (hashes in `production.json`)

| Id | Kind | Path | SHA-256 (first 12) | Provenance |
|---|---|---|---|---|
| script | script | `videos/three_bills/script/SCRIPT.md` | 148013206649 | Owner's v2 script, 'Script approved' 9 Nov 2026 (SHA-256 14801320...); the full episode was approved ('Approved, good work Claude') |
| audio | audio | `videos/three_bills/short/short_audio_raw.wav` | 808428832aaf | Cut from the approved full-episode narration (voice/H, L, D1-D7), no resynthesis |
| renderer | renderer | `videos/three_bills/short/render_short.py` | e859c3d953b1 | Portrait adapter under the Shorts launcher; reuses the approved ren_stage placement and the episode's Maya and Ren rendering code |
| configuration | configuration | `videos/three_bills/short/short_spec.json` | e74a165a7e2d | Generated from short_spec.py: beats and timings tied to short_cues.json |
| maya | character | `videos/three_bills/art/cast/maya_01_neutral.png` | 6b140a9c8a70 | Owner-approved four-pose Maya sheet ('Maya images approved', 9 Nov 2026; hashes in the pack manifest) |
| ren_present | character | `assets/ren_library/ren_present_palm_left.mp4` | 4ab89972324e | Approved animated Ren library clip (mirrored); approved in the full episode |
| ren_shrug | character | `assets/ren_library/ren_shrug.mp4` | 1cacb6dd155b | Approved animated Ren library clip; approved in the full episode |
| ren_point | character | `assets/ren_library/ren_point_right.mp4` | ae725bb9225f | Approved animated Ren library clip; approved in the full episode |
| ren_open | character | `assets/ren_library/ren_open_arms.mp4` | ffe871e05afc | Approved animated Ren library clip; approved in the full episode |
| ren_nod | character | `assets/ren_library/ren_nod_yes.mp4` | ca3ef50d4b86 | Approved animated Ren library clip; approved in the full episode |
| ren_think | character | `assets/ren_library/ren_thinking.mp4` | 5451d99e3297 | Approved animated Ren library clip; approved in the full episode |
| lot | environment | `library/supporting_assets/backgrounds/Office_parking_lot_car_16x9.png` | 0dc0b4d6e623 | Approved plate (Free Money pack; used in the approved episode); 1672x941 landscape, enlarged about 2x for portrait |
| porch | environment | `library/supporting_assets/backgrounds/Porch_background_16x9.png` | b6732b5526d5 | Approved plate (used in the approved episode) |
| office | environment | `library/supporting_assets/backgrounds/Office_background_16x9.png` | bfc7066bc825 | Approved plate (used in the approved episode) |
| sage | environment | `videos/unclaimed_401k/art/plates/SAGE_4k.png` | 82282c1e7827 | Ren's approved sage home office (REN_VIDEO_RULES.md), restored from codex/ren-approved-v3 |
| kitchen | environment | `videos/three_bills/art/plates/kitchen_leak_ref.png` | 29cb65b86e55 | Sink-leak illustration supplied by the owner (9 Nov 2026); only the pipe/sink/bucket area is used; approved in the full episode ('Approved') |
| typography | font | `project/remotion/public/fonts/fredoka-latin-700-normal.woff2` | c28f2b70e6e1 | Fredoka, the established house typeface |

## Scenes

| Scene | Frames | Seconds | Composition | Action | Assets |
|---|---|---|---|---|---|
| ren-hook | 0-47 | 1.96 | ren-left-title-card | Ren (genuine clip, presenting) beside a '3 bills / 30 days' card; the opening educational chip shows | ren_present, sage |
| car-breakdown | 47-127 | 3.33 | lot-maya-car-key | Maya surprised beside the car; the car key spins and stops | maya, lot |
| dental-invoice | 127-178 | 2.12 | invoice-urgent | An urgent $390 invoice drops onto the table and the URGENT stamp lands | lot |
| porch-worse | 178-240 | 2.58 | porch-maya-worried | Maya on the porch, worried with her phone; slow push | maya, porch |
| kitchen-leak | 240-296 | 2.33 | sink-leak-portrait | The sink-leak illustration (pipe, sink, bucket) with an animated drip and ripple | kitchen |
| ren-total | 296-357 | 2.54 | ren-left-equation | Ren shrugs; the three bills and their total appear in a column | ren_shrug, sage |
| savings-app | 357-459 | 4.25 | office-maya-phone-balance | Maya at her desk looks worried at her phone; a savings card shows $2,600 falling to $400 | maya, office |
| gone-backwards | 459-552 | 3.88 | porch-maya-closeup-bubble | Close-up of Maya at dusk; a thought bubble appears | maya, porch |
| ren-why | 552-584 | 1.33 | ren-left-not-backwards | Ren points; a 'Not backwards' chip appears | ren_point, sage |
| card-paid-off | 584-661 | 3.21 | porch-maya-paid-off | Maya relieved on the porch; a 'Paid off' stamp lands on a credit card | maya, porch |
| auto-transfer | 661-742 | 3.38 | phone-auto-transfer | A phone shows the $50 automatic transfer; the toggle switches on | office |
| ren-fifty-two | 742-866 | 5.17 | ren-left-fund-equation | Ren opens his arms toward the finished sum $50 x 52 = $2,600 | ren_open, sage |
| money-was-there | 866-943 | 3.21 | lot-maya-answer | Maya relieved beside the car; 'The money was already there' card | maya, lot |
| three-bills-gone | 943-1037 | 3.92 | office-maya-fund-tank | Maya at her desk; the fund tank drains from $2,600 | maya, office |
| four-hundred | 1037-1085 | 2.00 | phone-400-left | The savings phone shows $400 left | office |
| ren-smaller | 1085-1168 | 3.46 | ren-left-fund-smaller | Ren nods; the fund tank drops from $2,600 to $400 | ren_nod, sage |
| using-it | 1168-1212 | 1.83 | porch-maya-failure-struck | Close-up of Maya, relieved; 'Failure' is struck through | maya, porch |
| its-the-job | 1212-1269 | 2.38 | lot-maya-the-job | Maya in the morning light; 'Its job: pay for emergencies' card | maya, lot |
| ren-question | 1269-1374 | 4.38 | ren-left-question | Ren thinks; the question card appears | ren_think, sage |
| closing | 1374-1415 | 1.71 | porch-maya-sunset-close | Maya at sunset on the porch; the exact disclaimer holds for the last two seconds | maya, porch |

Drawn in code (never generated art): every number, card, phone, tank, invoice, credit card, stamp and the disclaimers.

## Missing items and risks

1. **No portrait-native plates.** The approved plates are landscape 1672x941; a 9:16 crop is about 529x941 plate pixels at 1080x1920 (2.04x enlargement), so backgrounds are soft. **Brief, only if the owner finds it too soft:** "Extend the approved [parking lot / porch / office] plate to a vertical 9:16 full-bleed image at 1080x1920 or larger. Preserve the exact scene, colours, lighting and flat 2D linework of the attached approved plate. Background only: no people, text or borders." New plate approval required.
2. **Maya is static cut-out art (four poses)**: pose cross-fades, camera pushes and moving props; no walking or reaching. Ren is genuine library animation.
3. The sink-leak image is enlarged about 2x for portrait and cropped to the pipe/sink/bucket area (the figure in the image is outside every crop).
4. Ren is life-size on the plate, so in portrait he fills the left of the frame and cards sit in the narrow right column.
5. No captions are planned (not required by the rules); say if you want word-by-word captions.
