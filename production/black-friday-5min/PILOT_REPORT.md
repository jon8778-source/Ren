# Black Friday long-form: pilot report (sections 1-2)

Delivered file: ren_black_friday_pilot_50s.mp4 (local only, SHA-256 b1b392a7c15146c9...). 1280x720, 24 fps, 1,215 frames, **50.6 s** (narration 50.36 s + 0.25 s tail), H.264/AAC, -16.2 LUFS, true peak -1.6 dBFS. Rendered at 1920x1080 internally and scaled once to 1280x720.
**It is shorter than the ~60 s target**: the approved script's sections 1-2 are 156 words, which the Qwen voice reads in 50 s. Say if you want the pilot extended into rule one (needs about 10 s more narration).

## What you are looking at
- Narration: the approved British Qwen clone, generated once for sections 1-2 (4 chunks, seed 1114, no speed change, stretching or padding), joined as generated. Whisper medium.en matches the script word for word apart from numbers read as digits (300, 341, 263, 78, 5). The FTC line is cut (recorded as the assumed reading of your "Approved"; see script/APPROVAL.md).
- 23 shots (evidence/pilot_shot_table.md): 10 genuine Ren library clips on the approved sage office plate (wave_hello, point_right, present_palm_left mirrored once, idle_calm, point_down_right, nod_yes x2, idle_listen, shrug, thinking), 7 stills, 6 code-drawn graphics over the blurred plate. Ren shots are 3-4 s; the longest gap between Ren shots is 12 s.
- Stills: your S1 c2 pick (shop entrance, 1920x1088 cropped 4+4 px, scaled once), the approved coffee-v3 art for "Meet Alex" and "Alex has a holiday budget", and the earlier stills 02_M1 (coat) and 03_M2 (gift), which are 1344x768 enlarged about 1.43x (**soft**). The charger still (04_M3, flagged for its odd seated pose) was not used; a code-drawn charger card stands in. **S1 c2, M1 and M2 are not approved art.**
- Every figure and label is drawn in code from data/assumptions.csv (300, 341, 263, 78); the checker proves 158+183=341, 158+105=263, 341-263=78 and 48+30=78. "Example figures" shows on the shots with numbers; "Educational only, not financial advice." shows for the first 4 s. The pilot has no end disclaimer because it stops mid-story.

## Checks
- evidence/pilot_qa_report.md: 14/14 automated checks pass (stream facts, frame count 1,215 = shot table, full decode with errors fatal, contiguous shots, caps Ren 5.5 / still 2.5 / graphic 3.5 s, hard cuts only at shot starts, no 1-2 frame shots, text >= 36 px at 1080p (24 px in the delivered 720p) and inside margins, no card over Ren's bounding box, displayed dollar figures only from the checked table, loudness). **One rule of the cut check is mine:** large frame changes inside the first 13 frames after a cut are accepted as the pop/slide entrance animation (21 of them were inside entrance animations, none unexplained).
- Mouth-closed: a heuristic scan (evidence/mouth_scan.json) picked windows with no open mouth; I then looked at face crops of every Ren shot every 0.25 s in the final MP4 (not every frame) and saw a closed mouth throughout. `ren_count_fingers` has no 2 s closed window so it was replaced by `ren_point_down_right` for "five rules".
- Contact sheets of two frames per shot were viewed; I also viewed the full-size graphics after enlarging them 1.35x.

## Limits and what I could not verify
- **I cannot hear the audio**: pronunciation (especially the numbers), pacing and sentence joins are unchecked. Please listen.
- Ren is small on the sage plate (the calibrated OFFICE_SAGE scale, same as the 401(k) baseline); the full-screen graphics are plain cards over the blurred plate. Six of 23 shots are graphics-only, so the look is cleaner than the 401(k) opening but not richer.
- Alex appears only as stills (no cut-out poses exist), so Alex and Ren never share a frame.
- Not viewed: the video playing at speed, a phone playback, every frame (only sampled frames, contact sheets and crops). Face crops were sampled, not exhaustive.
- Gate record: script approval was given as "Approved" without naming the FTC option; I assumed the FTC line is cut.

## Decision needed
Approve the pilot (and which of the stills to keep), or tell me what to change. I will not start the full video, generate the remaining narration or publish anything before then.
