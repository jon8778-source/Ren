# Asset requirements report: ~1-minute Short from "Black Friday: the sale that tests you"

Prepared before rendering (Shorts rules, asset-first checkpoint). **Status: prototype (first 15 s) only; the complete Short is not rendered until the owner approves the prototype.**

## Narration
- 32.74 s, 107 words, cut from the approved long-video narration by `short_audio.py`: 6 excerpts of whole script sentences from the approved long-video audio, plus two NEW lines (the owner's hook and a closing prompt to watch the full video) synthesised with the approved Qwen clone after the owner approved the wording.
- No new synthesis, speed change, stretching or inserted silence; each excerpt starts 0.05 s before its first word and keeps up to 0.22 s of the original audio after the last (never past the next word). **The joins between the excerpts and the two new lines are tighter than in the long video: listen to each** (I cannot hear audio). The figure 107 repeats by design.

## Inventory (hashes in `production.json`)

| Id | Kind | Path | SHA-256 (first 12) | Provenance |
|---|---|---|---|---|
| script | script | `production/black-friday-5min/short/REVISION_PLAN.md` | 0a20e05e43e4 | Revision 2 narration, approved by the owner ('Approved, proceed with existing stills', 15 Nov 2026); the long film's script was approved 14 Nov 2026 |
| audio | audio | `production/black-friday-5min/short/short_audio_raw.wav` | 4da2ee5d5593 | Owner approved the narration of this revision ('Approved, proceed with existing stills', 15 Nov 2026); two new lines (hook, closing) synthesised with the approved Qwen clone, the rest cut from the approved long-video audio |
| renderer | renderer | `production/black-friday-5min/short/render_short.py` | 9c4c9d7a81a8 | Portrait adapter under the Shorts launcher; reuses the long film's Ren matting and the Three Bills Short layout code |
| cards | configuration | `production/black-friday-5min/short/bf_short_ui.py` | f22648f70d6a | Portrait card builders (code-drawn text and figures from data/assumptions.csv); hashed so a card change invalidates the approval |
| configuration | configuration | `production/black-friday-5min/short/short_spec.json` | c37a06dd1c28 | Generated from short_spec.py: beats and timings tied to short_cues.json |
| ren_phone | character | `assets/ren_library/ren_hold_phone.mp4` | 470e6fc94ab5 | Approved animated Ren library clip; Used in the owner-approved long video ('Approved', 14 Nov 2026, SHA-256 eef4d914...) |
| ren_point | character | `assets/ren_library/ren_point_right.mp4` | ae725bb9225f | Approved animated Ren library clip; Used in the owner-approved long video ('Approved', 14 Nov 2026, SHA-256 eef4d914...) |
| ren_present | character | `assets/ren_library/ren_present_palm_left.mp4` | 4ab89972324e | Approved animated Ren library clip (mirrored); Used in the owner-approved long video ('Approved', 14 Nov 2026, SHA-256 eef4d914...) |
| ren_listen | character | `assets/ren_library/ren_idle_listen.mp4` | 81bc21e2fa2f | Approved animated Ren library clip; Used in the owner-approved long video ('Approved', 14 Nov 2026, SHA-256 eef4d914...) |
| ren_point_down | character | `assets/ren_library/ren_point_down_right.mp4` | 7cfd517ef14d | Approved animated Ren library clip; Used in the owner-approved long video ('Approved', 14 Nov 2026, SHA-256 eef4d914...) |
| sage | environment | `videos/unclaimed_401k/art/plates/SAGE_4k.png` | 82282c1e7827 | Ren's approved sage home office (REN_VIDEO_RULES.md), used in the approved long video |
| s1c2 | environment | `production/black-friday-5min/assets/stills_batch2/candidates/S1_shop_entrance_c2.png` | 043313344a35 | Alex shop-exit candidate (FLUX.2-dev from the approved Alex art), used in the owner-approved long video; no separate art approval; 1920x1088, enlarged about 1.8x for a portrait crop |
| s2c2 | environment | `production/black-friday-5min/assets/stills_batch2/candidates/S2_compare_coats_c2.png` | de7a99a9146a | Alex compares-coats candidate, used in the owner-approved long video; no separate art approval; 1920x1088, enlarged about 1.8x |
| s3c1 | environment | `production/black-friday-5min/assets/stills_batch2/candidates/S3_checkout_c1.png` | 56415d857095 | Alex checkout candidate, used in the owner-approved long video; no separate art approval; 1920x1088, enlarged about 1.8x (two crops) |
| home | environment | `production/black-friday-5min/assets/approved_alex/alex-home.png` | 5ff172badddb | Approved coffee-v3 art 'Alex pours French press coffee' (SHA-256 5ff172ba...), restored from codex/ren-approved-v3; 1672x941, enlarged about 2x |
| typography | font | `project/remotion/public/fonts/fredoka-latin-700-normal.woff2` | c28f2b70e6e1 | Fredoka, the established house typeface |

## Scenes

| Scene | Frames | Seconds | Composition | Action | Assets |
|---|---|---|---|---|---|
| hook-saved | 0-50 | 2.08 | alex-leaves-shop-107 | Alex walks out of the shop with two bags (slow push); a green 'Saved $107' chip slides in; opening educational chip | s1c2 |
| hook-checkout | 50-82 | 1.33 | alex-checkout-face | Alex at the checkout counter, placing a coat, a gift and a charger box (crop on Alex) | s3c1 |
| hook-spent | 82-112 | 1.25 | alex-checkout-items-spent-more | Closer crop of the checkout items; a red 'Spent MORE' card lands | s3c1 |
| website | 112-165 | 2.21 | ren-left-website | Ren holds a phone; a 'Shop website' card | ren_phone, sage |
| clock | 165-203 | 1.58 | countdown-clock | A navy countdown clock counts down in code | sage |
| badge | 203-247 | 1.83 | only-3-left | A red ONLY 3 LEFT badge pops | sage |
| announces | 247-322 | 3.12 | ren-left-saved-107 | Ren points at the store's '$107 saved' card | ren_point, sage |
| thing | 322-352 | 1.25 | alex-compares-coats | Alex compares two coats in the shop (slow push) | s2c2 |
| not-saved | 352-418 | 2.75 | ren-left-struck-107 | Ren listens; the '$107 saved' figure is struck through | ren_listen, sage |
| spend-183 | 418-461 | 1.79 | parts-183 | The three items $48 + $105 + $30 add to $183 | sage |
| rule-4 | 461-526 | 2.71 | ren-left-rule4 | Ren points down-right; RULE 4 tag | ren_point_down, sage |
| sleep | 526-599 | 3.04 | moon-to-sun | A moon becomes a sun: 'Still want it tomorrow?' | sage |
| tally-a | 599-632 | 1.38 | alex-relaxed-37-under | Approved art of Alex at ease in the kitchen; a '$37 under budget' card | home |
| tally-b | 632-701 | 2.88 | ren-left-78-less | Ren presents (mirrored palm); the '$78 less' card | ren_present, sage |
| closing | 701-786 | 3.54 | ren-left-full-video | Ren points at a 'Watch the full video' card; the exact disclaimer holds for the last two seconds | ren_point, sage |

Drawn in code (never generated art): every number, card, clock, badge, bar and the disclaimers.

## Missing items and risks

1. **No portrait-native art.** The sage office plate is a 4K landscape and is cropped to 9:16 (about 1.85x), as in the Three Bills Short; the three API stills (1920x1088) are enlarged about 1.8x and the approved coffee art (1672x941) about 2x for portrait crops, so they are softer than the landscape film. **Brief for portrait-native Alex shopping art, if wanted:** "Alex browsing a clothes rack, holding a price tag, queueing with bags, carrying bags out of a shop: same character, hair, sage overshirt, white sneakers and flat 2D style as the approved coffee art, vertical 9:16 at 1080x1920 or larger, blank signs and tags" (not generated: the Hugging Face API credits ran out).
2. **Alex cutaways are limited to the existing sharp stills**: shop exit, checkout (two crops), compares coats, and the approved kitchen art (5 of 15 beats). The other stills would enlarge 2.5-3.3x in portrait and are not used. S1 c2, S2 c2 and S3 c1 were used in the owner-approved long film but never approved as separate art.
3. Ren is in 6 of 15 beats (2-3.5 s each) and never shares a frame with Alex (Alex exists only as stills). Ren's mouth windows come from the long film's frame scan (closed); Ren stands at the Three Bills Short's approved portrait position beside the chair.
4. No captions are planned (not required); say if you want word-by-word captions.
