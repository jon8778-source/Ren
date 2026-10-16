# Quality check: final

Video: `renders/full.mp4`  
Overall: **FAIL**

| Check | Result | Detail |
|---|---|---|
| Maths (assumptions table recalculated) | PASS | All totals recalculate correctly. |
| Number accuracy: script vs table | PASS | Every spoken number matches its table value. |
| Number accuracy: on-screen figures | PASS | All on-screen money and numbers are pulled from the assumptions table. |
| Real statistics | FLAG | Claims needing a verified source ([VERIFY] in sources.json) |
| Voice consistency | PASS | 6 chunks, identical settings (am_michael 0.5 + am_eric 0.5, speed 0.93); leading silence 0.01, 0.01, 0.01, 0.01, 0.01, 0.01s; loudness -22.2, -22.1, -22.4, -22.3, -22.1, -22.0 LUFS; pitch 133, 133, 133, 132, 132, 135 Hz (spread 0.4 semitones). |
| Character consistency | PASS | 29 poses used, all byte-identical to the locked character sheets. |
| Caption sync | FLAG | 85 captions; each starts within 0.25s of its speech (measured offsets +0.04s to +0.07s); text matches the script word for word; all fit in 2 lines. |
| Silence over 1 second | PASS | No gap in the voice longer than 1 second. |
| Safe-zone placement | FAIL | Checked 564 frames (2 per second): nothing drawn in the bottom 130px. Captions end at y=946; all zones sit inside 96px margins (the small disclaimer pill sits at the very top by design). |
| Text readability | PASS | Smallest text 40px, captions 50px, key numbers 120px on a 1920x1080 frame. Dark navy on white. |
| Visual changes | PASS | 69 scenes (1.3s to 12.6s long) with 254 visual changes; longest hold 5.2s at 70.8s. Slow pan/zoom runs throughout. |
| Disclaimer | PASS | On screen at the start (yes) and end (yes); in description.txt (yes). |
| File | PASS | 1920x1080, 30/1 fps, 282.1s, audio present, loudness -16.8 LUFS. |

**Real statistics**

- [r03] UNVERIFIED: Retirees with large savings spend down very little of them, even nearly two decades into retirement (https://www.ebri.org/crawler/view/asset-decumulation-or-asset-preservation-what-guides-retirement-spending)

**Caption sync**

- 'He eats the cheapest meals, skips every …' needs 3 lines
- 'Research on retirees suggests this is su…' needs 3 lines

**Silence over 1 second**

- 280.43s–282.11s (1.68s) (end of video)

**Safe-zone placement**

- content in the controls area at 129.0s
- content in the controls area at 129.5s
- content in the controls area at 130.0s
- content in the controls area at 130.5s
- content in the controls area at 131.0s
- content in the controls area at 131.5s
- content in the controls area at 132.0s
- content in the controls area at 132.5s
- content in the controls area at 133.0s
- content in the controls area at 133.5s
- content in the controls area at 134.0s
- content in the controls area at 134.5s
- content in the controls area at 135.0s
- content in the controls area at 135.5s
- content in the controls area at 136.0s
- content in the controls area at 136.5s
- content in the controls area at 137.0s
- content in the controls area at 137.5s
- content in the controls area at 138.0s
- content in the controls area at 138.5s
- content in the controls area at 139.0s
- content in the controls area at 139.5s
