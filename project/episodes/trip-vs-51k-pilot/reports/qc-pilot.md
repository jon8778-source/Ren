# Quality check: pilot

Video: `renders/pilot.mp4`  
Overall: **PASS**

| Check | Result | Detail |
|---|---|---|
| Maths (assumptions table recalculated) | PASS | All totals recalculate correctly. |
| Number accuracy: script vs table | PASS | Every spoken number matches its table value. |
| Number accuracy: on-screen figures | PASS | All on-screen money and numbers are pulled from the assumptions table. |
| Real statistics | PASS | 2 sourced claim(s), verified by the owner. |
| Voice consistency | PASS | 2 chunks, identical settings (am_michael 0.5 + am_eric 0.5, speed 0.93); leading silence 0.01, 0.01s; loudness -22.2, -22.7 LUFS; pitch 133, 132 Hz (spread 0.2 semitones). |
| Character consistency | PASS | 5 poses used, all byte-identical to the locked character sheets. |
| Caption sync | PASS | 18 captions (long sentences split at a pause); each starts within 0.25s of its speech (measured offsets +0.04s to +0.05s); text matches the script word for word; all fit in 2 lines. |
| Silence over 1 second | PASS | No gap in the voice longer than 1 second. |
| Safe-zone placement | PASS | Checked 116 frames (2 per second): nothing drawn in the bottom 130px. Captions end at y=946; all zones sit inside 96px margins (the small disclaimer pill sits at the very top by design). |
| Text readability | PASS | Smallest text 40px, captions 50px, key numbers 120px on a 1920x1080 frame. Dark navy on white. |
| Visual changes | PASS | 14 scenes (1.5s to 8.0s long) with 48 visual changes; longest hold 5.4s at 12.2s. Slow pan/zoom runs throughout. |
| Disclaimer | PASS | On screen at the start (yes) and end (yes); in description.txt (yes). |
| File | PASS | 1920x1080, 30/1 fps, 57.8s, audio present, loudness -16.8 LUFS. |

**Real statistics**

- [h05] VERIFIED: A 7% average yearly return (before inflation) is the example's assumption, not a promise or a real-world statistic ()
- [m01] VERIFIED: The 'memory dividend' is an idea from the book Die With Zero by Bill Perkins (https://www.foyles.co.uk/book/die-with-zero/bill-perkins/9780358567097)

**Silence over 1 second**

- 56.12s–57.83s (1.71s) (end of video)
