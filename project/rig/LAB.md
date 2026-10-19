# Animated Ren: lab notes

Status: first test (15-second 9:16 clip, 2026-10-18) built and rejected by the owner ("many errors").
Nothing from here is used in episodes.

## Second pass (gated, 2026-10-18)
- **Gate 1, face calibration:** `make_rig.py` now places every eye and mouth by its bounding-box centre on
  one anchor per slot (lens centres; mouth at head px 768, 1431 on the face's centre line) and fits each
  scale so the part stays inside its region (lens opening less 3 px; face inside the jaw less 30 px and below
  the nose). Mouths are 14-36% of the face width (cap 40%). Values in `rig.json` -> `face`. Check:
  `rig/ren/checks/face-grid.png`. Approved.
- **Gate 2, hand setup:** each hand's wrist is measured from the band of pixels at its cut end. Rest angle
  (`bone`) = perpendicular to the wrist, wrist anchor (`pivot`) = on that line, 10 rig units inside the cut,
  attached at the forearm's end. Sheet hands share one scale (x0.537, was x0.476) so their wrists are 85% of
  the cuff width. Neutral wrists turn in 5 degrees so the relaxed fingers point straight down. Values in
  `rig.json` -> `hands`. Check: `rig/ren/checks/hand-grid.png`. Approved.
- **Gate 3, pose library:** `remotion/src/rig/poses.ts` holds eight named poses (neutral, wave, holdOne,
  holdBoth, pointFloor, thumbsUp, wince, celebrate): joint angles, a hand per side (wrist angle or a world
  tilt), a face, and boots held or on the floor. Holding uses new `hand-holdout-*` parts (the other side's
  hold art, so the grip opens outward) with a grip point and a finger clip in `rig.json`; the renderer draws
  the fingers again in front of the boot. Boots moved to `remotion/src/rig/Boot.tsx`, tags above the shaft.
  Boots on his right are mirrored so every toe points away from him. Wince and celebrate fists follow
  the forearm (knuckles down, knuckles up). Stills: `rig/ren/checks/poses/`. Approved.
- **Gate 4, test clip re-render:** `remotion/src/rig/RigTest.tsx` now blends library poses (9-10 frame eases,
  hand swaps mid-move), walks in over 1.4 s with planted feet (leg IK in `remotion/src/rig/legs.ts`), squats
  to set the boots down either side, points at both. Lip sync from Rhubarb (`rig/setup_rhubarb.sh`,
  `rig/test_voice.py`), mouths held 3+ frames. Checks: `remotion/src/rig/checkClip.ts`. Report:
  `rig/test-clip/report.md`.
- **Smoothing and claymation passes:** sine/overshoot easing with overlapping joints, body on twos with a
  faint boil, squash and stretch, foreshortened knees (`legs.ts`, stretch support in `RenRig.tsx`), a walk
  towards the camera and a crouch-and-bow set-down. Waiting for review.

## What exists
- `rig/build_parts.py`: cuts the owner's sheets (`rig/ren/source/`) into transparent parts.
- `rig/make_rig.py`: pivots, attach points, scales and layers, written to `rig/ren/rig.json`.
- `rig/compare.py`: side-by-side and overlay against `ren-original`.
- `remotion/src/rig/RenRig.tsx`: forward-kinematics renderer, plus the `ren-rig-still` and `ren-rig-hands`
  checks.
- `remotion/src/rig/RigTest.tsx` + `rig/test_voice.py`: the 15-second test clip. Results are in
  `rig/test-clip/report.md`.
- Commands: `rig/README.md`.

## Known problems from the first test
- **Walk:** all parts are front-facing. Scissor legs cross; the march replacement still skates.
  This needs side-view or three-quarter legs, feet and torso.
- **Body pieces:** the hip half-disc bulges below the shirt hem. Shoulder caps show seams when an arm is
  raised. Knees have mannequin bumps. Shoulders are about 10% narrower than the original's.
- **Face:** sheet eyes have brown irises (the original's are near-black), and the closed mouth is flatter
  than the original's smile. Raised brows vanish under the fringe. There's no nose part (taken from the
  original), and the fringe differs a little from the original's.
- **Hands:** the thumbs-up sits beside the cuff. Hand swaps happen too early in a move. There's no
  forward-pointing hand.
- **Lip sync:** volume only, no phonemes, and no m/b/p closed mouths.
- **Props:** the boot drop slides sideways instead of falling straight down.
- **Source files:** the owner's sources arrived as JPG; PNG with transparency would cut cleaner.

## Ideas for the next attempt
- Ask for side-view and three-quarter part sheets, or keep Ren standing (no walking).
- Phoneme lip sync timed from the script text.
- A named pose library with eased transitions.
- Decide early which episode rules (no bob or breathing) the animated version may break.
