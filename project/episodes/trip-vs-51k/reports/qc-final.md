# Quality check: final

Video: `renders/full.mp4`  
Overall: **PASS**

| Check | Result | Detail |
|---|---|---|
| Maths (assumptions table recalculated) | PASS | All totals recalculate correctly. |
| Number accuracy: script vs table | PASS | Every spoken number matches its table value. |
| Number accuracy: on-screen figures | PASS | All on-screen money and numbers are pulled from the assumptions table. |
| Real statistics | PASS | 4 sourced claim(s), verified by the owner. |
| Voice consistency | PASS | 5 chunks, identical settings (am_michael 0.5 + am_eric 0.5, speed 0.93); leading silence 0.01, 0.01, 0.01, 0.01, 0.01s; loudness -22.2, -22.3, -22.3, -22.5, -22.5 LUFS; pitch 133, 132, 132, 133, 132 Hz (spread 0.2 semitones). |
| Character consistency | PASS | 6 poses used, all byte-identical to the locked character sheets. |
| Caption sync | PASS | 65 captions (long sentences split at a pause); each starts within 0.25s of its speech (measured offsets +0.04s to +0.08s); text matches the script word for word; all fit in 2 lines. |
| Silence over 1 second | PASS | No gap in the voice longer than 1 second. |
| Safe-zone placement | PASS | Checked 468 frames (2 per second): nothing drawn in the bottom 130px. Captions end at y=946; all zones sit inside 96px margins (the small disclaimer pill sits at the very top by design). |
| Text readability | PASS | Smallest text 40px, captions 50px, key numbers 120px on a 1920x1080 frame. Dark navy on white. |
| Visual changes | PASS | 56 scenes (1.5s to 10.3s long) with 180 visual changes; longest hold 6.6s at 117.7s. Slow pan/zoom runs throughout. |
| Disclaimer | PASS | On screen at the start (yes) and end (yes); in description.txt (yes). |
| File | PASS | 1920x1080, 30/1 fps, 233.8s, audio present, loudness -16.8 LUFS. |

**Real statistics**

- [h05] VERIFIED: A 7% average yearly return (before inflation) is the example's assumption, not a promise or a real-world statistic ()
- [m01] VERIFIED: The 'memory dividend' is an idea from the book Die With Zero by Bill Perkins (https://www.foyles.co.uk/book/die-with-zero/bill-perkins/9780358567097)
- [b02] VERIFIED: Perkins suggests 'time buckets': planning experiences by decade of life (https://www.foyles.co.uk/book/die-with-zero/bill-perkins/9780358567097)
- [g02] VERIFIED: Die With Zero is not about running out: it assumes you keep enough for the rest of your life (https://www.foyles.co.uk/book/die-with-zero/bill-perkins/9780358567097)

**Silence over 1 second**

- 232.16s–233.83s (1.67s) (end of video)
