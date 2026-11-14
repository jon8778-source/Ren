# Black Friday: the sale that tests you: full episode report

File: ren_black_friday_full_4m05s.mp4 (local only, SHA-256 eef4d9140f170662...). 1280x720, 24 fps, 5,875 frames, **4:04.8** (narration 244.5 s + 0.25 s tail), H.264/AAC, -16.2 LUFS, true peak -1.4 dBFS. Rendered at 1920x1080 internally and scaled once to 1280x720.
Not published, not merged, no Shorts made.

## Length
The target was about 5:00, but the approved British Qwen voice reads the 728 approved words (FTC line cut) in 4:04, faster than the 150 words-a-minute planning rate. I did not slow, stretch or pad it. If you want 5:00, the options are script additions (your approval) or more story beats.

## What it is
- **108 shots** (evidence/full_shot_table.md): 40 genuine Ren library clips on the approved sage office plate (121 s, 50 %), 22 story stills (36 s), 46 code-drawn graphics over the blurred plate (88 s). The pilot's 23 shots are reused unchanged (Ren moved closer and clear of the chair, as you approved).
- Ren is never off screen for more than 13.3 s; Ren shots start every 2-17 s. That is more Ren than the baseline's 30-45 s returns, because the 2.5 s still cap and the stills available leave Ren or a card for everything else. Two runs of four consecutive graphic shots remain (sections 4 and 6); caps are met everywhere (Ren 5.5 s, still 2.5 s, graphic 3.5 s).
- Clips used: point_right (8), present_palm_left mirrored (5), thinking (5), idle_calm (4), nod_yes (4), point_down_right (3), shrug (3), idle_listen (2), hold_phone (2), wave_hello, clipboard_tick, shake_no, thumbs_up. Alex appears only as stills and never shares a frame with Ren.
- Every number and label is drawn in code from data/assumptions.csv. Displayed dollar figures are limited to a derived table by QA (10, 20, 25, 30, 32, 37, 41, 45, 48, 60, 78, 80, 90, 105, 107, 115, 120, 150, 158, 183, 205, 263, 300, 341). "Example figures" shows on shots with prices; "Educational only, not financial advice." shows for the first 4 s and the last 2.6 s; the CTA is the repo's "Check out the Money Leak Audit Workbook in the description." (never "free").

## Voice
- Narration for sections 3-8 was generated once from the approved text with the approved Qwen clone (no speed change, stretching or padding). **One chunk (S3_01) was regenerated**: the first take dropped the phrase "The coat is one hundred and twenty dollars" (Whisper heard "The and it's twenty-five percent off"). The rejected take is kept locally in voice/chunks_rejected.
- Final Whisper pass: matches the script apart from numbers read as digits, plus "coat" heard as "code" and "cart" heard as "card" (probably recognition errors, not confirmed), and three small words ("in", "night's", "about") that one pass missed and another heard. **I cannot listen: please check those spots and every number.**
- The FTC clause is cut (recorded as the assumed reading of your "Approved").

## Art and approval status
- Approved art: the coffee-v3 Alex scenes (two shots) and the Ren library clips.
- **Not approved (all other stills)**: your batch-2 picks S1 c2, S2 c2, S3 c1 (1920x1088), S4a c2 (used twice), S4b2 c2, S5 c3, S6 c2, S7 c3 (1024x576, enlarged 1.25x to the final 720p, so soft), and the first-batch stills 02_M1, 03_M2, 09_P2, 10_P3, 11_C1, 12_C2 (dark sneakers), 14_W2, 15_W3, 17_T1, 18_E1, 19_E2 (1344x768). The night shots show a paler overshirt than the approved sage, and S5 c3 is very dark.
- Ren is placed at the pilot-approved position on the calibrated OFFICE_SAGE plate geometry with a contact shadow.

## Checks
- evidence/full_qa_report.md: 14/14 automated checks pass (stream facts, frame count 5,875 = shot table, full decode with errors fatal, contiguous shots, caps, hard cuts only at shot starts (large changes inside the first 13 frames after a cut are accepted as card entrance animations: 100 such, none unexplained), no 1-2 frame shots, text >= 36 px at 1080p (= 24 px in the 720p file) and inside margins, no card text over Ren, displayed figures within the table, loudness).
- Viewed: one frame from each of the 108 shots in contact sheets (every card checked for overflow; five overflows found and fixed: email card, workbook end card, recap list, treat chips, budget label), plus the fixed cards at larger size. Mouths: the heuristic scan chose closed-mouth windows for every Ren shot (no shot lacked one), and a coarse face strip sampled every 0.5 s (small tiles) showed closed mouths; I did **not** check every frame.
- Financial check: 158+183=341, 158+105=263, 341-263=78 = 48+30, 205-158=47, 32+45+30=107, 150-105=45, 115-105=10, 300-263=37, 341-300=41: all from the checked table (tools/check_numbers.py prints MATHS OK).

## Not verified
Audio listening (pronunciation, pacing, sentence joins, the Whisper discrepancies above); playback at speed and on a phone; 100 % crops of every shot's face/feet (only the pilot's were examined closely); character likeness of the unapproved stills at 100 %; the optional FTC claim.

## Decisions for you
1. Final approval, or changes (length, stills, any shot).
2. Which unapproved stills to approve or replace; whether the 1024x576 Space stills need higher-resolution versions (API credits).
3. Whether to keep the FTC line cut.
