# Pilot revision 2: Ren host cutaways, armchair continuity, larger office Maya

File (local, not in git): `/output/unclaimed_401k_rev2/ren_401k_match_pilot_rev2_53s.mp4`, 1920x1080, 24 fps, 53.125 s, 19 shots (14 Maya action, 2 graphic, 1 story still, **2 Ren cutaways**).
Narration is the existing audio, **not re-synthesised**: P1/P2 WAVs are byte-identical (hashes in `voice_hashes.json`; file times predate the first pilot) and the MP4 audio correlates 1.0000 with them. The spoken script is unchanged (QA 2b).
Full QA: `reports/hybrid_qc.md`, 44 checks, OVERALL PASS. Shot-by-shot inventory: `reports/Shot_Inventory.csv`, `reports/Asset_Inventory.csv`.

## What changed, by request
1. **Ren cutaways (2, both on narration beats).** P08 (18.5-21.6 s, "Her employer was willing to put that into her retirement account,") and P11 (26.5-29.0 s, "This isn't a story about a secret investment trick."). Spoken words untouched.
2. **Genuine approved clips only.** P08 `ren_point_right.mp4` (library window 1.0-6.38 s, plays 1.30-4.38 s), P11 `ren_shrug.mp4` (plays 1.30-3.80 s): native 1280x720 decode and background removal, every frame a distinct clip frame, mouth closed (checked on 100% crops), no bobbing (feet row std 0.5-0.6 px), static camera (background unchanged in every rendered frame).
3. **Layout.** Ren stands on the left of the approved sage office, scaled by the repo standard (new plate geometry `OFFICE_SAGE` in `ren_stage.py`; 175 cm measures 815-818 px against 816 expected), contact shadow under his feet. Graphics are on the right: the Employer -> 401(k) token card (P08) and the "not a secret trick" icons fading from a plain $100 / month line (P11). A small "Ren" name chip marks his first appearance.
4. **Maya's story preserved.** Opening, the $100 / month and $1,200 / year portal graphics (P06, P07) and the discovery beats are unchanged.
5. **Continuity fixed.** Maya now stays in the living-room armchair for every home shot (P01-P05, P09, P10, P12); the stool poses were converted to armchair poses by removing the baked stool. QA 10a checks that no stool pose or repositioning occurs in any home frame.
6. **Office scale and acting.** Office shots are framed closer (1.25-1.55x of a 4K plate, same floor spot, scale follows the zoom exactly): P14 typing / sip / phone, P15 key press + coin, P16 receipt wince (knees-up close-up), P19 drawer.
7. **Genuine-movement check.** Every character shot changes pose or moves a hand/prop (QA 10d); Ren shots show real in-box motion and no camera move (9d, 9e). STORY_STILL P17 is by definition only a light shift.
9. **Validation.** Cuts only on shot boundaries, no A-B-A or flashes, constant 24 fps (every packet 1/24 s), Maya and Ren feet fixed, caps respected, text in the safe area, numbers checked.

## Honest limits
- Armchair legs: P01-P03 are crossed-leg poses, P04 onward are legs-down (the laptop poses come from the stool sheet), so legs change at the P03->P04 cut.
- The stool-removal art has small leftover specks (pale slivers, ragged shoe soles) in a few poses; check at full size.
- Ren's key leaves a faint dotted fringe on dark edges at 100%; his plate (1672x941) is upscaled 2.3x and the scale was fitted by eye to the desk and chair (horizon not well constrained).
- Maya is still limited animation from keyframes, not a rig; office close-ups use 600 px art at up to 1.9x total enlargement and are soft.
- Ren stands in front of the desk and chair, partly covering them.
- I cannot hear audio; accent, pace, joins and "four-oh-one-k" still need your listening check.
- Not run: the repo's older `qa_timeline.py`, `validate.py`, `jitter_check.py` (tied to the 720p renderer; re-implemented in `qa_pilot.py`).
Nothing is merged or published; the six-minute episode is not started.
