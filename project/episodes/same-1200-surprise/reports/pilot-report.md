# Pilot report: "Same $1,200 Bill, 5 Different Incomes"

Pilot: `renders/pilot.mp4`, 1920x1080, 30 fps, 57.7 seconds. It covers the hook and the start of Level 1
(meet Sam, a normal month, the bill arriving). It was built with the real pipeline: assumptions → script →
scene list → locked character art → voiceover → Remotion and FFmpeg → quality check.
Full automated results are in `qc-pilot.md`. Overall: **PASS**.

## Results
| Area | Result |
|---|---|
| Voice consistency | One voice, identical settings in both chunks (52.4s and 2.9s, each under 60s). Leading silence 0.01s, chunk loudness −22.7 and −22.4 LUFS, pitch 130 and 139 Hz (1.1 semitones apart, limit 1.5). I can't listen to audio, so please check pronunciation ("twenty-two thousand", "Tuesday", "dental"). |
| Character consistency | 14 poses used, every one byte-identical to the locked sheets (hash-checked). |
| Number accuracy | Assumptions table recalculates (Sam: $2,400 − $2,170 − $80 = $150 left). Every spoken number matches the table, and every on-screen figure is pulled from it, not typed. Money graphics carry an "Example figures" tag. No real statistics used. |
| Caption sync | 15 captions, word for word from the script, each 0.04–0.05s after its speech starts (limit 0.25s), at most two lines. |
| Text readability and safe zone | Smallest text 40px, captions 50px, key numbers 120px. On 115 sampled frames, nothing is drawn in the bottom 130px (YouTube controls). Content zones keep 96px side margins. |
| Visual change | 15 scenes, 60 visual changes; the longest hold is 2.7s (limit 7s). Slow pan and zoom on every scene. |
| Silence over 1 second | None during speech. The only silence is the 1.7s end hold. |
| Disclaimer | On screen at the start and end, and in `description.txt`. |
| Final loudness | −16.8 LUFS. |

## What went wrong (all fixed)
- **Cutouts:** the first background removal also erased white shirts and hoodie strings, because some source
  images have a white band or gaps under the clothes. I fixed `cutout.py` and checked all 25 poses on a coloured
  background.
- **Quality check false alarms:** the first QC run flagged scene ids as hand-typed numbers, and measured caption
  sync against the end of the previous sentence. I fixed both checks; the video itself was fine.
- **Layout:** the "Surprise!" stamp covered the bill's title, and the "Example figures" tag touched the taller
  cards. Both are moved.

## Recommended changes before scaling up
1. **Confirm the cast:** Sam (L1), Nina (L2), Claire (L3), Marcus (L4), Richard (L5) are my placeholder names and
   assignments. Change any of them before the full script.
2. **More poses per character:** five busts each will feel repetitive over 1:30 per level. Two or three more would
   help, for example holding the bill, on the phone, and relieved. The same prompt style works.
3. **Keep Ren present in level segments:** right now Ren disappears after the hook. A small Ren cutaway every
   20–30 seconds would keep him as the guide.
4. **Finalize Levels 2–5 numbers with the script:** their figures are drafts (only incomes appear in the pilot),
   and each level's unique surprise should drive them.
5. **New scene templates for the other levels:** a five-way comparison bar, a lifestyle-creep chart, a credit-card
   balance graphic and a mid-video teaser card, so the segments don't look the same.
6. **Pace:** speed 1.05 gives about 150 words a minute, which fits roughly 1,500 words into 10 minutes. Tell me if
   it feels too slow or fast.
7. **Workbook link:** `description.txt` has a `[WORKBOOK LINK]` placeholder to fill in.
8. **Render time:** about 1.6 minutes per minute of video here, so the full 10 minutes takes about 15–20 minutes.
