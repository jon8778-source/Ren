# Asset requirements report: 1-minute Short from "I Said No to Free Money for 3 Years"

Prepared before rendering, under the v3 Shorts rules (asset-first checkpoint). **Status: prototype (first 15 s) only; the complete Short is not rendered until the owner approves the prototype.**

## Narration
- 56.66 s, 192 words, cut from the approved long-form narration (`videos/free_money/voice/S1..S7.wav`) by `short_audio.py`: whole sentences, script order, wording unchanged.
- No new synthesis, speed change, stretching or inserted silence. Excerpts start 0.05 s before the first word and keep up to 0.22 s of the original audio after the last word; they are joined exactly as cut.
- Joins between non-adjacent sentences are therefore tighter than in the long video: **listen to every join** (owner ear check; I cannot hear audio).

## Inventory (all approved, hashes in `production.json`)

| Id | Kind | Path | SHA-256 (first 12) | Provenance |
|---|---|---|---|---|
| script | script | `scripts/Ren_Free_Money_Script.md` | 48be8a065cd3 | Owner supplied the script 7 Nov 2026; narration used word for word; Gate 3 'rough cut approved' |
| audio | audio | `videos/free_money/short/short_audio_raw.wav` | 6656d8c4c67f | Cut from the approved long-form narration (voice/S1-S7.wav), no resynthesis; owner approved the long video narration at Gate 3 ('rough cut approved') and 'Approved, great' on the final |
| renderer | renderer | `videos/free_money/short/fm_short.py` | f123c0ff8986 | Adapter under the Shorts launcher; reuses the approved ren_stage placement (owner request 7 Nov 2026) |
| configuration | configuration | `videos/free_money/short/short_spec.json` | 948751c76782 | Generated from short_spec.py: beats and timings tied to short_cues.json |
| ren_r1 | character | `videos/free_money/matted/Ren_1_neutral.png` | b2ae0b7e51b5 | Approved Ren still (library/ren_approved/Ren_1_neutral.jpg), matted; owner 'style lock approved' 7 Nov 2026 |
| ren_r2 | character | `videos/free_money/matted/Ren_2_hand_on_chest_talking.png` | 04b66658e4d1 | Approved Ren still, matted; 'style lock approved' |
| ren_r3 | character | `videos/free_money/matted/Ren_3_thinking_bust.png` | af33fbdcfa11 | Approved Ren still, matted; 'style lock approved' |
| ren_fs | character | `videos/free_money/matted/Ren_full_body_standing.png` | 294bc1cd9187 | Approved Ren still, matted; 'style lock approved' |
| ren_fp | character | `videos/free_money/matted/Ren_full_body_presenting.png` | 26547449bf87 | Approved Ren still, matted; 'style lock approved' |
| dev | character | `library/supporting_assets/characters/Dev_pay_stub.png` | d92a7e3abcb0 | Supporting character from the owner's asset pack; style option (b) accepted at 'style lock approved' |
| porch | environment | `library/supporting_assets/backgrounds/Porch_background_16x9.png` | b6732b5526d5 | Owner's asset pack plate; 'style lock approved' |
| office | environment | `library/supporting_assets/backgrounds/Office_background_16x9.png` | bfc7066bc825 | Owner's asset pack plate; 'style lock approved' |
| lot | environment | `library/supporting_assets/backgrounds/Office_parking_lot_car_16x9.png` | 0dc0b4d6e623 | Owner's asset pack plate; 'style lock approved' |
| folder | prop | `library/supporting_assets/props/HR_folder_page6_prop.png` | 53c8b225ffd8 | Owner's asset pack prop; baked-in text accepted for this video at 'style lock approved' |
| typography | font | `project/remotion/public/fonts/fredoka-latin-700-normal.woff2` | c28f2b70e6e1 | Fredoka, the established house typeface |

## Scenes

| Scene | Frames | Seconds | Composition | Action | Assets |
|---|---|---|---|---|---|
| stub-hook | 0-94 | 3.92 | stub-closeup-plan-panel | Dev's pay stub fills the frame; the match line glows and a panel shows one employer's example plan: You 2%, Employer 2%, the limit ghosted at 4% | dev, porch |
| porch-question | 94-162 | 2.83 | porch-two-shot | Ren and Dev stand on the porch; the question appears; slow push toward Dev and the stub | ren_fs, dev, porch |
| stub-line | 162-233 | 2.96 | stub-line-closeup | The glowing 'Employer match: 2%' line pulses, then darkens and sinks | dev, porch |
| three-years | 233-273 | 1.67 | bust-with-three-stubs | Ren thinks while three pay stubs, each with the same 2% match, stack in above him | ren_r3, office |
| office-age25 | 273-333 | 2.50 | office-standing-age25 | Ren stands by the desk and laptop; a single 'Age 25' label appears | ren_fs, office |
| salary-card | 333-403 | 2.92 | bust-salary-card | Ren, hand on chest; one salary card '$44,000 salary' appears on the word | ren_r2, office |
| lot-lease | 403-469 | 2.75 | parking-lot-standing | Ren stands in the parking lot beside the car; slow push | ren_fs, lot |
| phone-489 | 469-526 | 2.38 | phone-lease-closeup | A phone slides up showing 'Car lease' and $489 per month | office |
| folder-page6 | 526-588 | 2.58 | folder-page6-closeup | The HR folder slides in; the camera pushes to the PAGE 6 tab | folder, office |
| match-coins | 588-652 | 2.67 | you-and-employer-coins | One employee coin is matched by one employer coin, then stacks grow equally | office |
| match-strip | 652-691 | 1.62 | folder-match-strip | The 'We match 100%' strip lights up on the folder page; 'up to 4%' appears | folder |
| picked-two | 691-765 | 3.08 | benefits-screen-two-percent | The contribution slider moves to 2%; the dashed 'up to 4%' appears | office |
| lease-urgent | 765-826 | 2.54 | phone-lease-urgent | A 'Payment due' banner drops onto the lease phone | office |
| jars-two | 826-884 | 2.42 | two-jars | You and Employer jars fill to 2%; a dashed ghost level rises above the employer's | office |
| never-paid | 884-964 | 3.33 | ghost-jar-never-paid | The ghost level is labelled 'Never paid' | office |
| missed-880 | 964-1034 | 2.92 | ledger-880 | A ledger shows Age 25, $44,000 and 'Missed match: $880' | office |
| toggle-app | 1034-1125 | 3.79 | phone-app-toggle | The retirement app slides in at 2% and the toggle moves to 4% | office |
| ninety-seconds | 1125-1177 | 2.17 | ninety-seconds-badge | A '90 seconds' badge pops on the phone | office |
| three-years-late | 1177-1240 | 2.62 | bust-three-years-late | Ren, rueful, with a '3 years late' tag | ren_r1, office |
| free-part | 1240-1288 | 2.00 | bust-free-part | Ren, hand on chest, with the line as a card | ren_r2, office |
| collect-owed | 1288-1360 | 3.00 | office-standing-collect | Ren presents toward the desk; 'Collect what you're owed' card; the disclaimer holds for the last two seconds | ren_fp, office |

Drawn in code (never generated artwork): every number, label, card, jar, coin, phone screen, toggle, badge, ledger and the disclaimer.

## Missing items and risks

1. **No portrait-native plates.** The approved office, porch and parking-lot plates are 1672x941 landscape. A 9:16 crop is 529x941 plate pixels shown at 1080x1920, a 2.04x enlargement. The art is flat and soft, so this may look slightly soft; I will judge it on the prototype at full size. **Brief, only if the owner finds it too soft:** "Extend the approved [office / porch / parking lot] plate to a vertical 9:16 full-bleed image at 1080x1920 or larger. Preserve the exact room, furniture, colours, lighting and flat 2D linework of the attached approved plate. Background only: no people, text, labels or borders." Reference: the exact plate file named above. New plate approval required.
2. **Ren is standing, not seated** (no seated pose exists); he is placed with the shared ren_stage scale and grounding rules.
3. **Supporting character** Dev has one pose; the stub close-ups are enlarged about 3x from a 160 px stub and will be soft: the glowing line is drawn in code and stays sharp.
4. **HR folder text** is baked into the supplied art (accepted for this video only at the style lock).
5. No captions are planned (not required by the rules); say if you want word-by-word captions.
