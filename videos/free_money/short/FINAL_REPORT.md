# 1-minute Short: complete render, QA and review notes

**File (local only, not in git):** `/output/short/free_money_short_FULL_57s.mp4`. 1080x1920, 24 fps, H.264/yuv420p + AAC, **56.667 s (1,360 frames)**, -16.3 LUFS, peak -1.6 dBFS, 12.0 MB. SHA-256 `eb202f7e26ad05e1...`.
**Status:** launcher QA `technical-pass-review-required`, 0 errors, 0 warnings. **Nothing uploaded, published or merged. Waiting for the owner's review.**

## What it is
21 beats of about 2-4 s, narrated by the approved long-form voice, cut as whole sentences in script order (192 words, wording unchanged; no resynthesis, speed change, stretching or inserted silence). The video ends exactly with the narration (A/V end difference 0.007 s).
Stub close-up with the example plan, porch question, "stomach dropped", three years, age 25, salary, lease in the parking lot, $489 on the phone, folder page 6, dollar-for-dollar coins, "We match 100% / up to 4%", the 2% decision against the limit, the urgent lease, the two jars, "Never paid", the $880 ledger, the app toggle 2% to 4%, the "90 seconds" badge, "3 years late", "Don't skip the free part", and the close with the exact end disclaimer.

## Checks run on the final file
- Launcher QA: resolution/aspect, 24 fps, codecs, 1,360 frames, uniform timestamps, full fatal decode, A/V start 0.0 s and end 0.007 s, no blank frames or bars, longest identical run 10 frames (a hold), asset hashes, unique scene IDs, 2-4 s beats (two justified), measured text.
- Measured layout (`layout.json`, 21 scenes): all text inside x 72-900, y 180-1560; none under 42 px (the disclaimer is 32 px); the exact disclaimer shows at the start (0.33-3.92 s) and continuously for the last 2 s.
- My own: no one- or two-frame inserts and no brightness flashes. The first 312 frames match the approved prototype to within 6/255 (encoder differences from a different segment split; the layout is identical). The prototype's 13-15 s disclaimer is correctly absent here, as the end disclaimer moved to the end.
- Viewed: one frame per second for the whole Short on two contact sheets, and 100% crops of the lease phone, folder strip, benefits screen, jars, ledger and app badge.
- Fixed after looking: the "90 seconds" badge covered the contribution percentage and the "4%"; the closing Ren was too far to the right; the Short ended 0.84 s after the narration (the first full render failed the A/V check); the end disclaimer and timeline now end with the audio.

## Not verified: please check
1. **Audio, whole Short (I cannot hear it).** Every join between excerpts, at about 5.4, 11.4, 21.9, 33.3, 43.1 and 50.0 s, is tighter than in the long video because no silence may be added. Also the accent and pace.
2. **I did not watch it in motion at speed**, nor on a phone. Motion was judged from per-second frames and the stills.
3. **Reading time.** Shorter beats (1.6-2.0 s: three years, the match strip, the free-part card) were judged by eye, not tested with viewers.
4. **Repeated moves.** The phone slide-in is used for the lease, the urgent lease and the app: purposeful, but check it does not feel repetitive.

## Limits
- Ren stands (no seated pose exists) and the mouth is closed (v3 rules); no articulated animation, no captions.
- The pay-stub paper is soft at 3-4.7x enlargement; landscape plates are shown 2x enlarged and are blurred behind the graphics.
- The 2027 IRS limit is not mentioned in the Short, so the unverified figure doesn't affect it.

## Approval record
Your word "approved" is recorded against the 15-second prototype (SHA-256 7498467423aa351c...). Twice I had to change the renderer or timeline length, which the launcher treats as stale; both times I re-rendered the prototype, confirmed it was **byte-identical** to the approved file, and re-bound the approval (see `human-review.md`). No new message from you was involved. Say if you object to that.
