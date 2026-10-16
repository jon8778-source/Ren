# Pilot report: The Man Who Died With $2 Million

`renders/pilot.mp4`: 1920x1080, 30 fps, 58.0 s. Covers the hook, "meet the three" and the start of Frank's
section (the first minute of the real video). Built with the full pipeline. Automated results: `qc-pilot.md`,
overall **PASS**.

| Area | Result |
|---|---|
| Voice consistency | Same Ren voice and settings as the last episode (am_michael + am_eric, 0.93x). 2 chunks (53.3 s, 2.2 s), leading silence 0.01 s, loudness -22.2 / -21.7 LUFS, pitch 133 / 139 Hz (0.8 semitones apart). Please listen for pronunciation: I can't hear audio. |
| Character consistency | 10 poses used (Frank 70+, Frank 25, Yara 25, Bea 25, Ren), all byte-identical to the locked sheets. |
| Number accuracy | Maths recalculates; all 13 story claims hold (Frank at 65 $2,223,597, at 85 $3,978,833). Every spoken number matches the table; every on-screen number comes from it. Money cards are tagged "Example figures". |
| Caption sync | 19 captions, word for word, 0.04-0.06 s after speech starts. |
| Visual change | 17 scenes, 64 visual changes, longest hold 4.3 s (limit 7 s). One scene runs 9.6 s ("Frank's smart start" list) but adds a new line every 2-3 s. |
| Silence over 1 s | None during speech (1.7 s hold at the end only). |
| Safe zone / readability | Nothing in the bottom 130 px on 116 sampled frames; smallest text 40 px. |
| Disclaimer | On screen at start and end; in description.txt. |

## What went wrong (fixed)
- Character sheets: the first split erased tall dark strips of hair and clothing. The splitter now only removes
  near-black divider lines. All 36 poses checked on a coloured background.
- Three-person lineups were drawn too small, "Meet Frank, Yara and Bea" showed each name twice, and the
  "$2,000,000" card had no "Example figures" tag. All fixed.
- The QC flagged character ids such as "frank-25" as typed numbers. Fixed in the checker, not the video.

## Recommended before the full video
1. Listen to the voice, especially "eighty-five", "Yara" and "Bea".
2. Hook pacing: the first 14 seconds stay on old Frank with the brochure. A short cut to his bank statement or
   desk could add variety; say if you want it.
3. Yara 70+ neutral has sunglasses on her head and her other 70+ poses don't. I'll avoid cutting between them.
4. Still to confirm: the EBRI figure for the [VERIFY] line in Scene 5 (open the brief and check
   "median savings down less than 11% after 18 years" for the highest-savings group). If unconfirmed, I'll cut it.
