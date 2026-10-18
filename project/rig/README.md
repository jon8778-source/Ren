# Ren puppet rig (test)

A cut-out rig of Ren for the 15-second 9:16 test clip. It is separate from the episode pipeline: episodes
still use the locked busts in `characters/`.

| Step | Command | Output |
|---|---|---|
| Cut parts | `.tools/venv/bin/python rig/build_parts.py` | `rig/ren/parts/*.png` + `parts.json` |
| Build rig | `.tools/venv/bin/python rig/make_rig.py` | `rig/ren/rig.json`, copied to `remotion/public/rig/ren/` |
| Still | `cp rig/ren/rig.json remotion/src/rig/ren-rig.json && cd remotion && npx remotion still src/index.ts ren-rig-still ../rig/ren/checks/rig-neutral.png` | neutral pose (add `--props` with `{"debug": true}` for pivot dots) |
| Hand test | `npx remotion still src/index.ts ren-rig-hands ../rig/ren/checks/rig-hands.png` | four poses with sheet hands |
| Compare | `.tools/venv/bin/python rig/compare.py` | `rig/ren/checks/rig-vs-original.png` |

In the cloud container, add `--browser-executable /opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell`.

- Sources (`rig/ren/source/`): the owner's six images, saved as JPG (they arrived as JPG, not PNG).
- Renderer: `remotion/src/rig/RenRig.tsx`. Forward kinematics; angles in degrees, 0 = hanging straight
  down from the parent, positive = clockwise. Slots swap eyes, brows, mouth and hands.
- Layers (back to front): shins, thighs, shoes, torso, hands, forearms, upper arms, head, nose, mouth,
  eyes, brows, glasses. Sleeve and pants coloured discs sit behind elbows and knees.
