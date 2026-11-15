# Asset requirements report: ~1-minute Short from "Black Friday: the sale that tests you"

Prepared before rendering (Shorts rules, asset-first checkpoint). **Status: prototype (first 15 s) only; the complete Short is not rendered until the owner approves the prototype.**

## Narration
- 60.01 s, 195 words, cut from the approved long-video narration by `short_audio.py`: 10 excerpts of whole script sentences, in script order, wording unchanged.
- No new synthesis, speed change, stretching or inserted silence; each excerpt starts 0.05 s before its first word and keeps up to 0.22 s of the original audio after the last (never past the next word). **The nine joins between non-adjacent excerpts are tighter than in the long video: listen to each** (I cannot hear audio). Two numbers repeat (341, 107) by design.

## Inventory (hashes in `production.json`)

| Id | Kind | Path | SHA-256 (first 12) | Provenance |
|---|---|---|---|---|
| script | script | `production/black-friday-5min/script/script.md` | b0b051453fbc | Owner-approved script ('Approved', 14 Nov 2026; FTC line cut); the Short reuses whole sentences of it |
| audio | audio | `production/black-friday-5min/short/short_audio_raw.wav` | d434efabea19 | Cut from the approved long-video narration (voice/S1..S8 joined), no resynthesis |
| renderer | renderer | `production/black-friday-5min/short/render_short.py` | 0cd399c24b3a | Portrait adapter under the Shorts launcher; reuses the long film's Ren matting and the Three Bills Short layout code |
| cards | configuration | `production/black-friday-5min/short/bf_short_ui.py` | 879ae42ae0ac | Portrait card builders (code-drawn text and figures from data/assumptions.csv); hashed so a card change invalidates the approval |
| configuration | configuration | `production/black-friday-5min/short/short_spec.json` | 3cc7166e26e3 | Generated from short_spec.py: beats and timings tied to short_cues.json |
| ren_wave | character | `assets/ren_library/ren_wave_hello.mp4` | 05302f76a254 | Approved animated Ren library clip; Used in the owner-approved long video ('Approved', 14 Nov 2026, SHA-256 eef4d914...) |
| ren_point | character | `assets/ren_library/ren_point_right.mp4` | ae725bb9225f | Approved animated Ren library clip; Used in the owner-approved long video ('Approved', 14 Nov 2026, SHA-256 eef4d914...) |
| ren_present | character | `assets/ren_library/ren_present_palm_left.mp4` | 4ab89972324e | Approved animated Ren library clip (mirrored); Used in the owner-approved long video ('Approved', 14 Nov 2026, SHA-256 eef4d914...) |
| ren_calm | character | `assets/ren_library/ren_idle_calm.mp4` | 605f04dac18a | Approved animated Ren library clip; Used in the owner-approved long video ('Approved', 14 Nov 2026, SHA-256 eef4d914...) |
| ren_phone | character | `assets/ren_library/ren_hold_phone.mp4` | 470e6fc94ab5 | Approved animated Ren library clip; Used in the owner-approved long video ('Approved', 14 Nov 2026, SHA-256 eef4d914...) |
| ren_listen | character | `assets/ren_library/ren_idle_listen.mp4` | 81bc21e2fa2f | Approved animated Ren library clip; Used in the owner-approved long video ('Approved', 14 Nov 2026, SHA-256 eef4d914...) |
| ren_think | character | `assets/ren_library/ren_thinking.mp4` | 5451d99e3297 | Approved animated Ren library clip; Used in the owner-approved long video ('Approved', 14 Nov 2026, SHA-256 eef4d914...) |
| ren_point_down | character | `assets/ren_library/ren_point_down_right.mp4` | 7cfd517ef14d | Approved animated Ren library clip; Used in the owner-approved long video ('Approved', 14 Nov 2026, SHA-256 eef4d914...) |
| ren_shrug | character | `assets/ren_library/ren_shrug.mp4` | 1cacb6dd155b | Approved animated Ren library clip; Used in the owner-approved long video ('Approved', 14 Nov 2026, SHA-256 eef4d914...) |
| ren_thumbs | character | `assets/ren_library/ren_thumbs_up.mp4` | b695921a1de2 | Approved animated Ren library clip; Used in the owner-approved long video ('Approved', 14 Nov 2026, SHA-256 eef4d914...) |
| sage | environment | `videos/unclaimed_401k/art/plates/SAGE_4k.png` | 82282c1e7827 | Ren's approved sage home office (REN_VIDEO_RULES.md), used in the approved long video |
| s1c2 | environment | `production/black-friday-5min/assets/stills_batch2/candidates/S1_shop_entrance_c2.png` | 043313344a35 | Alex shop-entrance candidate (FLUX.2-dev from the approved Alex art), used in the owner-approved long video; no separate art approval; 1920x1088, enlarged about 1.8x for a portrait crop |
| cafe | environment | `production/black-friday-5min/assets/approved_alex/alex-cafe.png` | 83d61936e45f | Approved coffee-v3 art 'Alex taps to pay for coffee' (SHA-256 83d61936...), restored from codex/ren-approved-v3; 1672x941, enlarged about 2x for a portrait crop |
| typography | font | `project/remotion/public/fonts/fredoka-latin-700-normal.woff2` | c28f2b70e6e1 | Fredoka, the established house typeface |

## Scenes

| Scene | Frames | Seconds | Composition | Action | Assets |
|---|---|---|---|---|---|
| hook | 0-48 | 2.00 | ren-left-title | Ren waves hello in his office; a 'Black Friday / a test' card slides in; opening educational chip | ren_wave, sage |
| spend-saving | 48-99 | 2.12 | alex-leaves-shop-tag | Alex walks out of the shop with two bags (slow push); a price tag flips 'Spending' to 'Saving' | s1c2 |
| budget | 99-174 | 3.12 | ren-left-budget | Ren points at a '$300 budget' card | ren_point, sage |
| two-plans | 174-225 | 2.12 | alex-pays-plans-card | Approved art of Alex paying; a Plan A / Plan B card slides up | cafe |
| plan-a | 225-288 | 2.62 | ren-left-341 | Ren presents (mirrored palm); the $341 card appears | ren_present, sage |
| plan-b | 288-351 | 2.62 | total-263 | A big $263 card pops over the blurred office | sage |
| apart | 351-436 | 3.54 | ren-left-78-apart | Ren stands calm; both totals and a '$78 apart' chip | ren_calm, sage |
| website | 436-488 | 2.17 | ren-left-website | Ren holds a phone; a 'Shop website' card | ren_phone, sage |
| clock | 488-527 | 1.62 | countdown-clock | A navy countdown clock counts down in code | sage |
| badge | 527-571 | 1.83 | only-3-left | A red ONLY 3 LEFT badge pops | sage |
| saved-107 | 571-645 | 3.08 | ren-left-saved-107 | Ren points at the store's '$107 saved' card | ren_point, sage |
| not-saved | 645-741 | 4.00 | ren-left-struck-107 | Ren listens; the '$107 saved' figure is struck through | ren_listen, sage |
| spend-183 | 741-785 | 1.83 | parts-183 | The three items $48 + $105 + $30 add to $183 | sage |
| rule-2 | 785-875 | 3.75 | ren-left-rule2 | Ren thinks; a RULE 2 tag | ren_think, sage |
| smaller-bill | 875-953 | 3.25 | equation-341 | The finished equation $158 + $183 = $341 | sage |
| over-341 | 953-1013 | 2.50 | ren-left-341-total | Ren points right at 'Alex is at $341' | ren_point, sage |
| over-budget | 1013-1056 | 1.79 | budget-bar | A budget bar fills past $300; '$41 over' lands | sage |
| rule-4 | 1056-1120 | 2.67 | ren-left-rule4 | Ren points down-right; RULE 4 tag | ren_point_down, sage |
| question | 1120-1195 | 3.12 | ren-left-question | Ren shrugs; a 'Need it, or did the timer?' card | ren_shrug, sage |
| sleep | 1195-1268 | 3.04 | moon-to-sun | A moon becomes a sun: 'Still want it tomorrow?' | sage |
| tally | 1268-1371 | 4.29 | ren-left-tally | Ren presents; the '$37 under budget' card changes to '$78 less' on the second figure | ren_present, sage |
| cta | 1371-1440 | 2.88 | ren-left-end-card | Ren gives a thumbs up; the workbook card; the exact disclaimer holds for the last two seconds | ren_thumbs, sage |

Drawn in code (never generated art): every number, card, clock, badge, bar and the disclaimers.

## Missing items and risks

1. **No portrait-native art.** The sage office plate is a 4K landscape and is cropped to 9:16 (about 1.85x), as in the Three Bills Short; the two Alex stills (1920x1088 and the approved 1672x941) are enlarged about 1.8x and 2x for portrait crops, so they are softer than the landscape film. **Brief, only if you find them too soft:** "Extend the approved Alex scene art to vertical 9:16 full-bleed images at 1080x1920 or larger, keeping the exact character, colours and flat 2D linework".
2. **Only two Alex story beats.** The other Alex stills in the long film are 1024x576 (Space) or 1344x768 and would enlarge 2.5-3.3x in portrait, so they are not used. The pressure story is told with Ren and code-drawn clock, badge and figures; 13 of 22 beats are Ren shots (the long film is also about half Ren).
3. Ren and Alex never share a frame (Alex exists only as stills). Ren's mouth windows come from the long film's frame scan (closed); Ren stands at the Three Bills Short's approved portrait position beside the chair.
4. No captions are planned (not required); say if you want word-by-word captions.
