# Shot plan outline and asset inventory (Gate 3 inputs; to be confirmed by Claude Code after script approval)

Caps from repo rules: Ren shot 5.5s, story still 2.5s, graphic 3.5s. Return to Ren about every 30-45s. Expect about 90-110 shots. Ren on the left, graphics on the right. No white-slide-dominated sections, no long runs of similar cards.

## Section plan (times follow the script estimate)
| Time | Section | Ren | Story and graphics |
|---|---|---|---|
| 0:00-0:31 | Hook | ren_wave_hello then ren_point_right at a code-drawn "$341 vs $263" card | brief Alex shop cutaway; start disclaimer |
| 0:31-1:02 | Meet Alex | Ren returns ~0:55: ren_idle_calm or ren_thinking | Alex stills (coat, gift, charger), budget tag $300 |
| 1:02-1:36 | Rule one | ren_clipboard_tick, then ren_point_right | list card, price tags, three sale prices, $158 vs $205 |
| 1:36-2:32 | The pressure | ren_shake_no return ~2:05 (avoid ren_shocked and ren_worried: their notes show open mouth or gritted teeth, which breaks the mouth-closed rule) | Alex at laptop at night, countdown clock, ONLY 3 LEFT badge, email pop-up, cart grows, "saved $107" vs "$183" |
| 2:32-3:12 | Rules two and three | ren_point_right at calculator; ren_thinking at price history | $158 + $183 = $341, "$41 over"; was $150, usually $115, real saving $10 |
| 3:12-4:02 | Rule four | ren_nod_yes return ~3:40 | laptop closes, night to morning, kitchen, cart decisions, air fryer and bundle removed, earbuds stay |
| 4:02-4:39 | The tally | ren_point_right or ren_present_palm_left (check direction) | side-by-side card: $341 over by $41 vs $263 under by $37, difference $78 |
| 4:39-5:00 | Rule five and close | ren_count_fingers for the recap, then ren_thumbs_up | recap list, end card with the workbook line, end disclaimer |

Check gesture direction by looking at the clip, not the filename. ren_present_palm_left presents to screen left; mirror only deliberately and inspect it. Mouth-closed clips only; discard clip audio.

## Asset inventory
| Asset | Status |
|---|---|
| Ren MP4 clips | Reuse: `assets/ren_library/` on main (32 clips, windows in `ren_library.json`) |
| Office, porch, parking-lot plates | Reuse: `library/supporting_assets/backgrounds/` on main; perspective in `PLATE_GEOM` (`project/cliplib/ren_stage.py`) |
| Alex (approved art) | VERIFY: approved in the coffee v3 art (Alex taps to pay; Alex pours coffee; character lineup) on branch `codex/ren-approved-v3`, `project/prototypes/coffee-minute-v3/artwork/`. NOT on main. If it cannot be found, report the blocker and ask Jon; do not invent Alex |
| Alex story stills (19) | GENERATED, TEMPORARY, NOT APPROVED: `assets/stills/` (see `manifest/stills_manifest.json`, hashes, prompts, references, known issues). Made by FLUX.2-dev image-to-image from the approved coffee-v3 Alex art. Needs Jon's approval before use as Alex story art; reject any that drift off-model |
| Props | Partly covered inside the stills (coat, gift, charger, air fryer, earbuds, mystery box, piggy bank). Separate cut-out props only if needed |
| Any new plate (shop, bedroom, kitchen) | Needs PLATE_GEOM calibration before use, and Jon's approval |
| Countdown clock, badges, email pop-up, calculator, price tags, comparison card, captions, end card | Draw in code (Fredoka, navy, sage, cream). Never AI lettering |
| Voice | Not generated. Approved British Qwen clone only, after script approval |

The portrait environments from the 30-second Short package are Shorts-only (9:16, temporary, unapproved) and are not used here. The episode's Shorts are cut later from the approved long video's lines per the repo workflow.

## Gates (record who/when/exact message and file hashes)
1. Claims and numbers checked (`tools/check_numbers.py` prints MATHS OK; claims.txt reviewed).
2. Jon approves the script. STOP here. No voice before this.
3. Asset inventory, continuity check, shot plan. List every missing asset; STOP if Alex art or approved plates are missing.
4. About 60-second animated pilot using the real workflow. STOP for Jon's approval.
5. Full video, about 5 minutes, reusing approved audio and assets.
6. Technical, financial, visual and audio QA, every scene boundary. Disclose what you could not listen to or view.
7. Jon's final approval. Publishing needs separate authorization.


## Stills by section (story still cap 2.5s each; vary framing, push or pan only when it explains the action)
| Section | Stills |
|---|---|
| 1 Hook | 01_H1_shop_window |
| 2 Meet Alex | 02_M1_old_coat, 03_M2_gift, 04_M3_charger |
| 3 Rule one | 05_L1_writing_list, 06_L2_coat_rack |
| 4 The pressure | 07_P1_laptop_night, 08_P4_alex_tempted, 09_P2_phone_ping, 10_P3_cart_items |
| 5 Rules two and three | 11_C1_calculator, 12_C2_price_history |
| 6 Rule four | 13_W1_closing_laptop, 14_W2_morning_kitchen, 15_W3_old_pan, 16_W4_old_earbuds |
| 7 The tally | 17_T1_sofa_bags |
| 8 Close | 18_E1_phone_transfer, 19_E2_piggy_jar |

No still repeats across sections except by deliberate callback. Gap to review: sections 1, 3 and 7 have only 1-2 stills each; if the shot plan needs more variety there, list numbered briefs rather than reusing a still. Blank screens, tags and banners are for code-drawn overlays.
