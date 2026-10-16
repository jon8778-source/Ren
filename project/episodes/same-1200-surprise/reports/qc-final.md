# Quality check: final

Video: `renders/full.mp4`  
Overall: **FAIL**

| Check | Result | Detail |
|---|---|---|
| Maths (assumptions table recalculated) | PASS | All totals recalculate correctly. |
| Number accuracy: script vs table | PASS | Every spoken number matches its table value. |
| Number accuracy: on-screen figures | FAIL | Hand-typed numbers found |
| Real statistics | FLAG | Possible statistic without [VERIFY] and a source |
| Voice consistency | PASS | 7 chunks, identical settings (am_michael 0.5 + am_eric 0.5, speed 0.93); leading silence 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01s; loudness -22.4, -22.7, -22.5, -22.6, -22.7, -22.5, -22.7 LUFS; pitch 131, 131, 130, 132, 132, 132, 134 Hz (spread 0.6 semitones). |
| Character consistency | PASS | 29 poses used, all byte-identical to the locked character sheets. |
| Caption sync | PASS | 79 captions; each starts within 0.25s of its speech (measured offsets +0.04s to +0.07s); text matches the script word for word; all fit in 2 lines. |
| Silence over 1 second | PASS | No gap in the voice longer than 1 second. |
| Safe-zone placement | PASS | Checked 691 frames (2 per second): nothing drawn in the bottom 130px. Captions end at y=946; all zones sit inside 96px margins (the small disclaimer pill sits at the very top by design). |
| Text readability | PASS | Smallest text 40px, captions 50px, key numbers 120px on a 1080px frame. Dark navy on white. |
| Visual changes | PASS | 74 scenes (1.9s to 14.6s long) with 310 visual changes; longest hold 5.7s at 150.7s. Slow pan/zoom runs throughout. |
| Disclaimer | PASS | On screen at the start (yes) and end (yes); in description.txt (yes). |
| File | PASS | 1920x1080, 30/1 fps, 345.5s, audio present, loudness -16.8 LUFS. |

**Number accuracy: on-screen figures**

- scenes[49].graphic.headline: '{marcus.fixed_share_pct|plain}¢ of every $1'

**Real statistics**

- [l08] Sam can't cover it, so Sam does the thing most people skip, and asks.

**Silence over 1 second**

- 343.87s–345.53s (1.66s) (end of video)
