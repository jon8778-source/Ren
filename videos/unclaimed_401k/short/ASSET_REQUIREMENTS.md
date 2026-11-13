# Asset requirements report: 1-minute Short from "Ren | Unclaimed 401(k) match"

Prepared before rendering, under the v3 Shorts rules (asset-first checkpoint). **Status: prototype (first 15 s) only; the complete Short is not rendered until the owner approves the prototype.**

## Narration
- 58.72 s, 173 words, cut from the approved long-form narration (`videos/unclaimed_401k/voice/*.wav`) by `short_audio.py`: whole sentences, script order, wording unchanged (excerpts: P1 s1-7, S3 s5-6 and s8-9, S8 s6 and s11-15).
- No new synthesis, speed change, stretching or inserted silence. Excerpts start 0.05 s before the first word and keep up to 0.22 s of the original audio after the last word; joined exactly as cut.
- Joins between non-adjacent excerpts are tighter than in the long video: **listen to every join** (I cannot hear audio).

## Inventory (hashes in `production.json`)

| Id | Kind | Path | SHA-256 (first 12) | Provenance |
|---|---|---|---|---|
| script | script | `videos/unclaimed_401k/script/narration_v3.md` | e4a422f4957e | Owner's v3 script, 'Script approved' 8 Nov 2026; narration used word for word |
| audio | audio | `videos/unclaimed_401k/short/short_audio_raw.wav` | 601281ceddc1 | Cut from the approved long-form narration (voice/P1..S8.wav), no resynthesis; pilot narration approved ('Approved'); full episode delivered 8 Nov 2026 |
| renderer | renderer | `videos/unclaimed_401k/short/render_short.py` | 3b562836e8d6 | Portrait adapter under the Shorts launcher; reuses the approved ren_stage placement and the episode's Maya and Ren rendering code |
| configuration | configuration | `videos/unclaimed_401k/short/short_spec.json` | e09d7b2658a5 | Generated from short_spec.py: beats and timings tied to short_cues.json |
| maya | character | `videos/unclaimed_401k/art/poses/stool_03.png` | f8372002baca | Maya pose cut-outs from the owner's approved identity sheets ('Yea to both', 'Approved'); armchair/stool variants derived by segmentation (unchair.py) |
| hand_phone | character | `videos/unclaimed_401k/art/poses/props_01.png` | 2774143093e7 | Hand-and-phone close-up from the approved prop sheet; owner 'Approved' the props |
| ren_point_right | character | `assets/ren_library/ren_point_right.mp4` | ae725bb9225f | Approved animated Ren library clip (assets/ren_library, status ok); owner 'Approved' the pilot with Ren cutaways |
| ren_shrug | character | `assets/ren_library/ren_shrug.mp4` | 1cacb6dd155b | Approved animated Ren library clip; used in the approved pilot |
| ren_present | character | `assets/ren_library/ren_present_palm_left.mp4` | 4ab89972324e | Approved animated Ren library clip (mirrored to present right) |
| ren_wave | character | `assets/ren_library/ren_wave_bye.mp4` | 2dd94fde6cce | Approved animated Ren library clip; mouth stays closed through the wave |
| ren_arms | character | `assets/ren_library/ren_open_arms.mp4` | ffe871e05afc | Approved animated Ren library clip |
| ren_camera | character | `assets/ren_library/ren_point_camera.mp4` | c81a0fbcf66b | Approved animated Ren library clip |
| ren_nod | character | `assets/ren_library/ren_nod_yes.mp4` | ca3ef50d4b86 | Approved animated Ren library clip |
| h1 | environment | `videos/unclaimed_401k/art/plates/H1_4k.png` | dbfb21d9e33e | Living-room plate H1, owner 'Approved' 8 Nov 2026 (2.3x upscale of 1672x941) |
| sage | environment | `videos/unclaimed_401k/art/plates/SAGE_4k.png` | 82282c1e7827 | Ren's approved sage home office (office.png, listed in REN_VIDEO_RULES.md), restored from branch codex/ren-approved-v3 |
| typography | font | `project/remotion/public/fonts/fredoka-latin-700-normal.woff2` | c28f2b70e6e1 | Fredoka, the established house typeface |

## Scenes

| Scene | Frames | Seconds | Composition | Action | Assets |
|---|---|---|---|---|---|
| armchair-phone | 0-63 | 2.62 | armchair-settle-phone | Maya settles into the living-room armchair and raises her phone; the opening educational chip shows | maya, h1 |
| phone-cancel | 63-132 | 2.88 | hand-phone-closeup | Close-up of a hand and phone: thumb hovers, presses Cancel plan, the app turns green 'Canceled' | hand_phone, h1 |
| armchair-email | 132-222 | 3.75 | armchair-smile-email | Maya reads the phone and gives a small smile; a confirmation email card slides in | maya, h1 |
| armchair-laptop | 222-281 | 2.46 | armchair-lid-lift | Maya lifts the laptop lid in the armchair | maya, h1 |
| armchair-alert | 281-357 | 3.17 | armchair-lean-alert | Maya leans in, eyes widen; a benefits alert pops up | maya, h1 |
| portal-numbers | 357-445 | 3.67 | portal-card-swap | The portal card shows $100 / month, then the label swaps to $1,200 / year | h1 |
| ren-employer-flow | 445-519 | 3.08 | ren-left-flow-card | Ren raises his arm and points at the Employer to 401(k) card while a token travels into the account | ren_point_right, sage |
| armchair-field | 519-567 | 2.00 | armchair-finger-hover | Maya's finger hovers over the laptop; the Contribution % field highlights | maya, h1 |
| armchair-two-percent | 567-619 | 2.17 | armchair-think-two | Maya sits back and exhales; a '2%' card appears | maya, h1 |
| ren-match-cards | 619-723 | 4.33 | ren-left-match-cards | Ren shrugs; the Maya card, then the Employer card, appear on their words | ren_shrug, sage |
| ren-half-meter | 723-782 | 2.46 | ren-left-half-meter | Ren presents toward a match meter that is half full | ren_present, sage |
| missing-half | 782-845 | 2.62 | missing-half-card | A card names the missing half: $1,200 / year | h1 |
| ten-years | 845-895 | 2.08 | ten-year-tiles | Ten year tiles tick on one by one | h1 |
| twelve-thousand | 895-964 | 2.88 | twelve-thousand-card | A card shows 10 years x $1,200 = $12,000 | h1 |
| not-included | 964-1085 | 5.04 | not-included-list | Three chips light up in turn: investment growth, changes in salary, changes to the plan | h1 |
| ren-intro | 1085-1196 | 4.62 | ren-left-next-move | Ren waves, then a card says the next useful money move isn't earning more | ren_wave, sage |
| ren-table | 1196-1265 | 2.88 | ren-left-on-the-table | Ren opens his arms toward a card: the match | ren_arms, sage |
| ren-cta | 1265-1344 | 3.29 | ren-left-cta | Ren points at the camera beside the workbook card | ren_camera, sage |
| ren-disclaimer | 1344-1409 | 2.71 | ren-left-disclaimer | Ren nods; the exact disclaimer holds for the whole beat | ren_nod, sage |

Drawn in code (never generated artwork): every number, label, card, meter, tile, phone screen and the disclaimers.

## Missing items and risks

1. **No portrait-native plates.** The approved plates are landscape 1672x941; a 9:16 crop is about 529x941 plate pixels at 1080x1920 (2.04x enlargement), so backgrounds are soft. **Brief, only if the owner finds it too soft:** "Extend the approved [living room / sage office] plate to a vertical 9:16 full-bleed image at 1080x1920 or larger. Preserve the room, furniture, colours, lighting and flat 2D linework of the attached approved plate. Background only: no people, text, labels or borders." New plate approval required.
2. **Ren is life-size on the plate** (ren_stage standard), so in portrait he fills the left of the frame and cards sit in the narrow right column. A portrait-native office plate with more floor would allow a smaller, wider composition.
3. **Maya is limited animation from keyframes**; all Short shots use the living-room armchair poses (the office poses are not used).
4. No captions are planned (not required by the rules); say if you want word-by-word captions.
