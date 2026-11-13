# Pilot revision 3.1: bug fixes, root causes and timeline QA

**File (local only, not in git):** `/output/free_money_S1_S2_pilot_rev03_1.mp4`, 1280×720, 24 fps, 51.58 s, -16.2 LUFS. The audio is bit-identical to rev03, rev02 and the pilot (MD5 `f927e4f3…`). Same story, narration, art and approved scenes, with only the two fixes below, and nothing else changed visually.
**Status: STOP. Waiting for your approval.** The full six-minute render has not started.

## 1. Root causes
**Issue 2, the one-frame insert at about 19.04 s.**
- **What it was:** frame 457 of rev03 was a full frame of the previous shot ("Let me take you back", Ren presenting wide) sitting between the last frame of the page peel and the desk shot.
- **Root cause:** the renderer picked each frame's shot with `start <= T < end + 1e-9`. On an exact cut frame `T == end`, so the **outgoing** shot still matched, and it was found first. The page-peel logic only runs for `T < start of the desk shot`, so on that frame nothing hid the outgoing shot.
- **Wider than reported:** the same line made **every one of the 21 cuts one frame late**. At ordinary hard cuts the extra frame is invisible, which is why only the peel showed it. The same line is in `fm_pilot.py`, `fm_rev02.py` and `fm_rev03.py`, so those older renders carry the one-frame delay at every cut too. I did not edit them, and kept them as history.
- **Fix:** the shot lookup is now half-open, `[start, end)`, so a cut frame belongs to the shot that starts on it. No fade or extra transition was added.

**Issue 1, the floating head and torso at about 19 s.**
- **What it was:** a front-facing Ren bust placed "behind" the laptop, with the plate's desk redrawn over his lower body.
- **Root cause:** the office plate does not contain a place for a seated person. The cubicle partition sits right behind the desk, so he was inside the partition. The plate's chair faces away from the camera and is empty, and the laptop lid hid his chest. My redrawn polygon also left a see-through triangle where it cut the lid.
- **Fix:** no seated pose exists in the approved stills. I replaced the seated attempt with a corrected composition: **Ren stands at the desk, full body, drawn once on top of the plate with no hiding or occlusion**, with the desk, laptop, chair and cubicle beside and behind him. He uses the approved full-body stills: thinking (hand on chin, glancing toward the desk) for the salary shot, presenting (palm toward the desk) for the folder shot. Anatomy is intact and he is in front of everything he stands in front of. The lit laptop screen now fits the lid exactly (the old quad was larger than the lid).
- **Also applied to shot 15 ("gave me a folder")** because it had the same seated composition.
- **Honest limit:** this is a standing composition, not seated. "Naturally seated" cannot be built from the approved stills without a new seated pose.

## 2. Before and after
- Desk composition: `videos/free_money/sheets/rev031/desk_before_after.png` (shot 9 at about 21 s and shot 15 at about 33 s, rev03 against rev03.1).
- **Frame-by-frame, 18.88 s to 19.21 s (frames 453-461):** `sheets/rev031/frames_before.png` and `frames_after.png`.

| Frame | 453 | 454 | 455 | 456 | **457** | 458 | 459 | 460 |
|---|---|---|---|---|---|---|---|---|
| Diff to previous frame, rev03 | 15 | 17 | 14 | 11 | **45 (stray wide shot)** | **44** | 0.5 | 0.5 |
| Diff to previous frame, rev03.1 | 12 | 16 | 13 | 11 | **8 (peel ending)** | **0.6** | 0.3 | 0.4 |

In rev03.1 the peel runs through frame 457 and the desk shot is steady from frame 458. The out-of-place frame is gone with no extra effect.

## 3. Complete timeline QA
**Automated (`qa_timeline.py`, new): 16 of 16 pass on rev03.1.** On the old rev03 file the same checks **fail**: they flag frame 457 as a one-frame insert and show a stray cut at one frame after every shot start (21 cuts), so the checks catch the bug they were written for.
Checks: shot list contiguous and frame-aligned; shot frames add up to the video; v3 caps; scene order equals the script (166 of 166 words, S1 then S2); approved assets present and the matted Ren stills not blank; full decode with errors fatal; frame count; no one-frame or two-frame inserts; every hard cut lands on a shot start (none late); the peel hands over cleanly; no single-frame brightness flashes. Also `validate.py`: **PASS** (clean decode, -16.2 LUFS, no gaps, no layout overlaps).
**Visual (I looked at these; the automated checks do not replace this):**
- All 21 boundaries, last frame against first frame, on `sheets/rev031/all_boundaries.png`. Every pair is an intended hand-off. No stray frame, no character appearing or vanishing unintentionally, no objects jumping unexplained (the salary card leaves when the shot changes, by design).
- Floating or disconnected parts: none found. Ren is whole in all 22 shots; the two corrected shots were checked at full size.
- Layering: Ren is in front of the desk and chair in shots 9 and 15; the phone clip, the lot and porch shots are unchanged.
- Overlapping text and graphics: the layout check reports none, and I saw none on the sheets.
**What I did not verify:** audio by ear (I can't hear it), including "lease" (heard as "least") and the accent.

## 4. Remaining limitations
- **Standing, not seated:** no seated pose is available.
- Ren is smaller in the two desk shots (a full-body figure) than in the earlier bust close-ups.
- The detection thresholds in `qa_timeline.py` were tuned on this 51 s clip, so a future video may need adjusting.
- 1280×720 only, and articulated animation is still not available, as in rev03.
