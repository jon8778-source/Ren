# Three Bills: final visual polish pass (for owner approval)

File (local, not in git): `/output/three_bills_final/ren_three_bills_final_5m21s.mp4`. Same length and timing as the reviewed film: 320.8 s (5:21), 7,699 frames, 24 fps, 1080p. Branch `video/three-bills-30-days`. Not published; no Shorts.

## Exactly what changed (4 of 126 shots)
Each replaced shot keeps the same narration phrase, start and end frame. Only these four shots differ; **all other frames are byte-copied from the reviewed film** (278 of 7,699 frames re-rendered, widened to keyframes; narration audio copied, not regenerated).

| Shot | Time | Narration | Was | Now |
|---|---|---|---|---|
| F08 | 1:15-1:16 | "she opened a separate savings account" | one of three graphic-only shots in a row (card, phone, phone) | **Ren (ren_hold_phone, genuine clip)** raises a phone; "New account $0 / Type Savings" phone card on the right |
| F10 | 1:20-1:23 | "Fifty dollars a week, for fifty-two weeks," | Ren, ren_hold_phone | Ren, ren_thinking (so the two adjacent Ren shots differ; the film already had this shot as a Ren shot, only the clip changed) |
| F38 | 2:25-2:28 | "She looked at the savings account, tapped transfer," | graphic-only phone card | **Ren (ren_hold_phone)** holding a phone, the Savings $1,840 / Dental bill $390 card with the Transfer toggle switching on |
| F81 | 4:23-4:26 | "Five dollars, twenty dollars, fifty dollars:" | graphic-only blurred card | **Ren (ren_present_palm_left, mirrored)** presenting a "$5 $20 $50" card |
| F86 | 4:43-4:47 | "And fourth, when you use it, refill it as circumstances allow." | Maya at her desk with a phone card | **Ren (ren_hold_phone)** with the refill phone ($400, Auto on, "Refilling" bar) |
(F10 is listed because the clip changed; it is 5 edited shots counting it, 4 are the genuinely re-staged ones.)

## What this does and does not fix
- The three windows you named: 1:15-1:55 (F08, F10), 2:05-3:20 (F38 plus the existing Ren cluster), 4:20-5:10 (F81, F86). Ren shots go from 21 to 25; graphic-only share of the film 22% to 20%; the longest run of graphic-only shots stays 2; longest gap between Ren shots 29.1 s.
- **Maya's repeated standing poses and many similar cards are NOT eliminated.** I replaced the four most repetitive shots I could fix with genuine animation. Maya remains four static poses (pose cross-fades, camera pushes, props moving around her); I did not substitute image movement for animation, and I added no new Maya poses. The remaining middle sections still contain several Maya-standing shots and text/phone cards (e.g. 2:05-2:25, the three-bills tank and tiles near 3:15, and 4:30-5:00 principles).
- Ren now holds a phone in three of the 25 Ren shots (same clip, different phone content).

## Mistakes caught during this pass (disclosed)
1. My first splice came out 8 frames long (copy-cut rounding): fixed and verified at exactly 7,699 frames.
2. The QA first ran against the old shot-type report and did not test the new Ren shots: I rebuilt the report from the shot table and re-ran QA.
3. I first used ren_count_fingers for F81, then ren_open_arms: both open Ren's mouth in part of the shot. The shipped clip (present-palm) shows a closed mouth in 10 sampled frames across the shot (viewed at 200 px crops). I did **not** run the same mouth check on the other 21 Ren shots (they rest on library notes and sheets).

## QA (41 checks, OVERALL PASS; `reports/full_qc.md`)
Full decode with errors fatal; 7,699 frames, 24 fps constant; every one of 121 cuts on a shot boundary; no one-frame inserts or flashes; every boundary changes the picture (including the four joins checked as before/after frames); safe area and 32 px on 998 sampled frames; every on-screen figure from the checked source; arithmetic checks; Ren clips inside their windows, feet fixed, 175 cm scale, distinct frames, real movement, static background, Ren left / graphics right; Maya scale/jitter; pilot frames unchanged (worst difference 0.42/255); audio identical to the previous film.
**Not verified:** audio by ear; real-speed or phone playback; automated mouth detection; CFPB/FDIC sources; REN_VIDEO_RULES.md re-read.
