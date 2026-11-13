# Human review notes: prototype (15 s) of the 401(k) Short

Reviewer: Claude (technical inspection, contact sheet at 1.6 fps and 100% stills), then the owner (Jon) reviewed the delivered prototype and replied "Approved" on 8 Nov 2026.

What was inspected: every second of the prototype as a contact sheet, plus full-size stills of the phone close-up (two states) and the armchair shots. Findings and resolutions:
- Phone close-up: UI text measured below 42 px after the perspective warp (QA error); fixed by enlarging the close-up and the nominal font sizes. The thumb covered the end of "Ends today"; the label is now "Ended". Left edge of the hand was cropped; repositioned.
- No QA warnings remained (no persistent borders, no frozen runs beyond 3 frames, all text in the safe area, exact end disclaimer for the last 2.2 s).
- Not verified by Claude: audio (accent, pace, joins), phone playback, reading time. Known limits: soft upscaled plates, limited Maya animation, Ren not yet shown in the first 15 s.

## Re-binding after a renderer change (disclosed)
The full render failed QA on one thing the prototype does not contain: the closing call-to-action card ("Audit Workbook") was wider than its card and crossed the safe area. I fixed the card (`short_ui.cta_card`) and regenerated the manifest, which changes the renderer/configuration hashes and made the recorded approval stale. I re-rendered the 15 s prototype through the launcher and confirmed it is byte-identical to the file the owner approved (SHA-256 637b145a1f1865aa52ca15a0a924fa6bb4533782dff518f20a7c874ba5f0f4ab), then re-recorded the same approval ("Approved", 8 Nov 2026) against the new fingerprint. No new owner message was involved.
