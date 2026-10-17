# Quality check: final

Video: `renders/short-lena.mp4`  
Overall: **PASS**

| Check | Result | Detail |
|---|---|---|
| Maths (assumptions table recalculated) | PASS | All totals recalculate correctly. |
| Number accuracy: script vs table | PASS | Every spoken number matches its table value. |
| Number accuracy: on-screen figures | PASS | All on-screen money and numbers are pulled from the assumptions table. |
| Real statistics | PASS | No real-world statistics are used; all figures are labelled examples. |
| Voice consistency | PASS | 1 chunks, identical settings (am_michael 0.5 + am_eric 0.5, speed 0.93); leading silence 0.02s; loudness -22.3 LUFS; pitch 133 Hz (spread 0.0 semitones). |
| Character consistency | PASS | 5 poses used, all byte-identical to the locked character sheets. |
| Caption sync | PASS | 9 captions (long sentences split at a pause); each starts within 0.25s of its speech (measured offsets +0.05s to +0.06s); text matches the script word for word; all fit in 3 lines. |
| Silence over 1 second | PASS | No gap in the voice longer than 1 second. |
| Safe-zone placement | PASS | Checked 59 frames (2 per second): nothing drawn in the bottom 420px. Captions end at y=1490; all zones sit inside 60px margins (the small disclaimer pill sits at the very top by design). |
| Text readability | PASS | Smallest text 35px, captions 54px, key numbers 104px on a 1080x1920 frame. Dark navy on white. |
| Visual changes | PASS | 8 scenes (2.0s to 6.5s long) with 21 visual changes; longest hold 6.2s at 11.9s. Slow pan/zoom runs throughout. |
| Disclaimer | PASS | On screen at the start (yes) and end (yes); in description.txt (yes). |
| File | PASS | 1080x1920, 30/1 fps, 29.6s, audio present, loudness -16.9 LUFS. |

**Silence over 1 second**

- 27.88s–29.61s (1.73s) (end of video)
