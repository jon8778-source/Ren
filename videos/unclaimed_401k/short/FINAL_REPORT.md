# Final report: 1-minute Short from "Ren | Unclaimed 401(k) match" (status: technical-pass-review-required)

Local file (not in git): `videos/unclaimed_401k/short/final.mp4`, copy in `/output/unclaimed_401k_short/`. 1080x1920, 24 fps, 58.708 s (1409 frames), H.264/yuv420p + AAC.
Rendered through the Shorts launcher after the owner's "Approved" of the 15 s prototype (recorded in `prototype-approval.json`, notes in `human-review.md`).

Narration: 173 words cut as whole sentences from the approved long-form narration (P1, S3 twice, S8 twice); no new synthesis, speed change or padding.
Beats: 19 (7 Maya/armchair shots, 7 Ren cutaways, 5 graphics); the $100 / month to $1,200 / year card, "half the match", $1,200 missing, ten years = $12,000, what the total leaves out,
Ren's close with the workbook line and the exact disclaimer for the last 2.7 s. Opening educational chip for the first 3 s.
Launcher QA: 0 errors, 0 warnings (format, clean decode, A/V equal to 0.0003 s, no persistent borders, no frozen runs beyond 3 frames, all text in the safe rectangle and at least 42 px effective).

## Disclosures
- The first full render failed QA once (the CTA card text crossed the safe area). I fixed the card and, because that changed the renderer hash, re-rendered the prototype, confirmed it was byte-identical to the approved file (637b145a...), and re-bound the approval without a new owner message (noted in `human-review.md`).
- Not verified by me: audio (accent, pace, the joins between excerpts at about 23.6, 29.9, 35.0 and 44.9 s), phone playback, reading time of the cards.
- Limits: soft upscaled plates cropped to portrait; Maya is limited animation from keyframes; Ren is life-size on the plate, so cards in the right column overlap his shoulder in a few shots; card text is large but dense in the closing section.
Nothing is merged or published.
