# Ren on the left — silent layout experiment

Owner-approved on 30 October 2026 as the default office layout for future
landscape v3 videos. Completed episodes and approved coffee originals remain
unchanged. See project/REN_VIDEO_RULES.md for standing rules. The reusable
layout.json saves the exact approved coordinates, scale, content bounds and
reference hash. Future episode renderers must reuse this preset instead of
the older right-side Ren placement in historical renderers.

Ren stays at one full-body size and position for two five-second shots.
The existing thinking and nod gestures are not mirrored. Text, a three-step
worksheet and a brief booking confirmation occupy the clear right-hand wall;
they do not cover the desk or chair. The approved office itself is unchanged.
Ren naturally stands in front of part of the furniture on the left.

Uses the actual approved v3 artwork restoration, Fredoka font, native-resolution
matte and frame-count checks. Sources are decoded at 1280×720, then the matted
character is resized once to 90%. No generated artwork, sharpening, upscaling,
new voice requests, source-clip audio or music. There is no audio stream.

Run from the repository root using the v3 Python dependencies:

```sh
python project/prototypes/ren-left-layout/render.py
```

Generated file: `deliverables/Ren_Left_Layout_10s_Silent.mp4`.
Output: 1280×720, 24 fps, H.264/yuv420p, exactly 240 frames / 10 seconds.
Both source clips are 10.005 seconds; the actual interval used is 1.25–6.25
seconds. Each encoded shot is checked for 120 frames. Full final decoding
treats errors as fatal. See `validation.json` for hashes and review evidence.
Generated media/cache stay outside Git. No changes to main, existing episodes,
approved coffee files, animation sources or voice reference.
