# Ren puppet rig (test)

A cut-out rig of Ren for the 15-second 9:16 test clip. It is separate from the episode pipeline: episodes
still use the locked busts in `characters/`.

| Step | Command | Output |
|---|---|---|
| Cut parts | `.tools/venv/bin/python rig/build_parts.py` | `rig/ren/parts/*.png` + `parts.json` |
| Build rig | `.tools/venv/bin/python rig/make_rig.py` | `rig/ren/rig.json`, copied to `remotion/public/rig/ren/` |
| Still | `cp rig/ren/rig.json remotion/src/rig/ren-rig.json && cd remotion && npx remotion still src/index.ts ren-rig-still ../rig/ren/checks/rig-neutral.png` | neutral pose (add `--props` with `{"debug": true}` for pivot dots) |
| Face grid | `npx remotion still src/index.ts ren-face-grid ../rig/ren/checks/face-grid.png` | every eye set and mouth on the head (`--props '{"guides":true}'` adds anchors and the 40% ticks) |
| Hand grid | `npx remotion still src/index.ts ren-hand-grid ../rig/ren/checks/hand-grid.png` | every hand on its forearm at 0, 45 and 90 degrees (`--props '{"guides":true}'` adds the forearm axis and wrist anchor) |
| Poses | `npx remotion still src/index.ts ren-pose ../rig/ren/checks/poses/<name>.png --props '{"name":"<name>"}'`, and `ren-pose-sheet` for all eight | pose library in `remotion/src/rig/poses.ts` |
| Hand test | `npx remotion still src/index.ts ren-rig-hands ../rig/ren/checks/rig-hands.png` | four poses with sheet hands |
| Compare | `.tools/venv/bin/python rig/compare.py` | `rig/ren/checks/rig-vs-original.png` |

In the cloud container, add `--browser-executable /opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell`.

- Sources (`rig/ren/source/`): the owner's six images, saved as JPG (they arrived as JPG, not PNG).
- Renderer: `remotion/src/rig/RenRig.tsx`. Forward kinematics; angles in degrees, 0 = hanging straight
  down from the parent, positive = clockwise. Slots swap eyes, brows, mouth and hands.
- Layers (back to front): shins, thighs, shoes, torso, hands, forearms, upper arms, head, nose, mouth,
  eyes, brows, glasses. Sleeve and pants coloured discs sit behind elbows and knees.

## Test clip
- Lip sync needs Rhubarb once: `rig/setup_rhubarb.sh` (into `.tools/rhubarb/`).
- Voice and lip-sync track: `.tools/venv/bin/python rig/test_voice.py` (writes `rig/test-clip/` and copies
  for Remotion).
- Explainer-style version: `cd remotion && npx remotion render src/index.ts ren-rig-explainer ../rig/test-clip/ren-rig-explainer.mp4`
  (`remotion/src/rig/Explainer.tsx`; shared pose blending in `remotion/src/rig/motion.ts`).
- Checks (boots vs body, foot drift, eases, mouth holds, explainer stillness): `cd remotion && npx tsx src/rig/checkClip.ts`.
- Clip: `cd remotion && npx remotion render src/index.ts ren-rig-test ../rig/test-clip/ren-rig-test.mp4`
  (`remotion/src/rig/RigTest.tsx` holds the timeline). Report: `rig/test-clip/report.md`.
