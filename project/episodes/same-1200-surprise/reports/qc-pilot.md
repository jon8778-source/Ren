# Quality check: pilot

Video: `renders/pilot.mp4`  
Overall: **PASS**

| Check | Result | Detail |
|---|---|---|
| Maths (assumptions table recalculated) | PASS | All totals recalculate correctly. Draft figures (only incomes used in this pilot): claire, marcus, nina, richard. |
| Number accuracy: script vs table | PASS | Every spoken number matches its table value. |
| Number accuracy: on-screen figures | PASS | All on-screen money and numbers are pulled from the assumptions table. |
| Real statistics | PASS | No real-world statistics are used; all figures are labelled examples. |
| Voice consistency | PASS | 2 chunks, identical settings (am_michael 0.5 + am_eric 0.5, speed 1.05); leading silence 0.01, 0.01s; loudness -22.7, -22.4 LUFS; pitch 130, 139 Hz (spread 1.1 semitones). |
| Character consistency | PASS | 14 poses used, all byte-identical to the locked character sheets. |
| Caption sync | PASS | 15 captions; each starts within 0.25s of its speech (measured offsets +0.04s to +0.05s); text matches the script word for word; all fit in 2 lines. |
| Silence over 1 second | PASS | No gap in the voice longer than 1 second. |
| Safe-zone placement | PASS | Checked 115 frames (2 per second): nothing drawn in the bottom 130px. Captions end at y=946; all zones sit inside 96px margins (the small disclaimer pill sits at the very top by design). |
| Text readability | PASS | Smallest text 40px, captions 50px, key numbers 120px on a 1080px frame. Dark navy on white. |
| Visual changes | PASS | 15 scenes (1.7s to 6.9s long) with 60 visual changes; longest hold 2.7s at 11.8s. Slow pan/zoom runs throughout. |
| Disclaimer | PASS | On screen at the start (yes) and end (yes); in description.txt (yes). |
| File | PASS | 1920x1080, 30/1 fps, 57.7s, audio present, loudness -16.8 LUFS. |

**Silence over 1 second**

- 56.01s–57.68s (1.67s) (end of video)
