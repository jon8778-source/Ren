# Approved Ren hybrid video rules — v3

Jon approved the 61.625-second coffee prototype v3 on 29 October 2026.
Use this as the visual direction for future hybrid prototypes. These rules
supersede conflicting legacy white-only/static-bust/Kokoro instructions for
this route. Existing production episodes remain unchanged.

## Publication status

The v3 renderer, all four approved original artworks, pinned dependencies,
run instructions and validation are now published in
project/prototypes/coffee-minute-v3/. The approved artwork is stored losslessly
as text chunks in artwork/; render.py restores the exact original PNG bytes
into assets/ and verifies their SHA-256 hashes. No artwork was regenerated.

The historical baseline at published commit bf193aee2c042651884143bec1cf1be9febc0b11
successfully rendered 1280×720 H.264/AAC, 24 fps, 61.625 seconds (1,479 frames).
All 19 shots were inspected. All 1,479 frames passed comparison with the
approved reference (minimum SSIM 0.992776, mean 0.997893). Full decoding passed
with errors fatal. All 209 calculation frames kept fixed, correct equations.
Narration continuity and artwork checksums passed; new voice requests: zero.
The baseline evidence is retained in validation-approved-baseline.json.
The current renderer corrects an avoidable character-resolution loss by decoding
Ren at native 1280×720 instead of 640×360 before matting and compositing.
See README.md, validate.py and validation.json for current checks and evidence.

Included approved originals:
- Welcoming sage-accented home office.png — desk and chair remain visible.
- Centered Maya in illustrated character lineup.png — Alex, revised Maya, Sam.
- Alex taps to pay for coffee.png.
- Alex pours French press coffee.png — corrected ONE-mug home scene.

The approved reference remains Ren_61s_Coffee_Prototype_v3.mp4 in the owner's
ChatGPT files. The newly reproduced MP4 is supplied separately with this handover.

## Characters and editing

- Preserve Ren's recognisable face, glasses, outfit, proportions and illustration
  style. Supporting characters and environments must match that visual world.
- No large white panel obscuring the office desk/chair, Ren/Finance heading,
  bottom yellow progress bar or persistent footer.
- Alternate wider and closer Ren shots. Use brief story cutaways and purposeful
  motion in objects, receipts, calendars and comparisons.
- Decode and matte Ren at native source resolution. Never halve the source
  resolution before enlarging him into the scene. Inspect 100% face and edge
  crops in both wide and close framing; frame-count checks do not catch blur.
- Reuse the existing animation library. No new animation batch is required.
  V3 used ren_present_palm_left, ren_nod_yes, ren_shake_no and ren_thinking.
- Keep the mouth closed for the current narrator-led format. No random talking
  motion. Accurate lip sync is a separate future feature.
- Inspect actual gesture direction; filenames can be misleading. Palm-left
  presents to screen left. Never mirror automatically or point away from content.
- Check source duration before using metadata intervals. The explain-hands
  metadata describes a longer interval than the actual short source supports.
- Maximum shot lengths: Ren 5.5 seconds, story still 2.5 seconds, graphic 3.5
  seconds. Avoid repeated poses across consecutive shots. Narration continues
  naturally across cuts.
- No decorative body wobble. Preserve white shirt/trainers when removing the
  white background; inspect edges, hands and clothing for damage.
- Fredoka text, navy/sage/cream graphics, clear mobile-readable layouts. Keep
  text away from faces, gestures and furniture. Disclaimer at start and end,
  without a large banner.

## Maths and editorial accuracy

- Calculate figures in code from shared assumptions. Draw prices, labels and
  equations in code, never inside generated artwork.
- Every displayed equation must be true on EVERY frame. Never show an
  intermediate count-up result beside a completed equation. Keep the correct
  total fixed and animate a separate calendar or object.
- Illustrative coffee example:
  $4 × 365 = $1,460.
  $4 − $1 = $3 per day.
  ($4 − $1) × 365 = $1,095.
- Distinguish total spending from savings after replacement costs. Label example
  figures. Do not invent statistics, guarantees, claims or sources.
- Follow existing research and script review gates for new episodes. Approval
  of this one-minute style reference does not approve a full episode.

## Voice and quota

- Preserve approved British male narration and the established reference.
  Model: Qwen/Qwen3-TTS-12Hz-1.7B-Base.
  Space: Qwen/Qwen3-TTS.
  Endpoint: /generate_voice_clone.
  English; use_xvector_only=True.
- Reuse approved audio when changing visuals. Preserve original WAVs and hashes.
  No substitute voice, speech-speed changes, stretching or silence padding.
  Discard source animation audio; no music.
- Follow the existing pilot's resumable quota workflow for new narration. Reuse
  completed segments. Stop at quota limits; no paid fallback or blind retry of
  failed or uncertain requests.
- Store HF_TOKEN only in configured runtime secrets/environment. Never commit
  credentials or print them in reports/logs.

## Validation and branches

- Inspect every shot's layout and any uncertain mouth/gesture interval.
- Check each encoded shot's frame count before assembly. Treat FFmpeg demux
  errors as failures even when its default exit code is zero.
- Decode the complete final MP4 with errors treated as fatal. Check duration,
  audio continuity, displayed calculations and layout.
- Verified v3 baseline: 1280×720, 24 fps, H.264/AAC, 61.625 seconds.
- Keep prototypes on a separate branch. Do not merge to main or replace an
  existing production episode without the owner's instruction.

## Character scale, grounding and smooth motion (added 7 November 2026, owner request, from the Free Money production)

These fix three faults found in review: Ren too small beside furniture, Ren apparently floating, and Ren shaking. They apply to
every Ren long-form video. The code is `project/cliplib/ren_stage.py` (tests: `project/cliplib/tests/test_ren_stage.py`).

**Scale: never size a standing figure by eye.**
- Every plate has a measured perspective (horizon row and camera height, `PLATE_GEOM` in `ren_stage.py`, calibrated from objects of
  known size). A standing person at floor row y is `175 cm x (y - horizon) / camera height` pixels tall. Use `ren_stage.stand()`.
- Supporting characters use the same rule with their own height (Priya 170 cm, Uncle Gary 178 cm, Dev 175 cm). Their heights against
  Ren are assumptions: say so in the report, and ask the owner if a story needs a different height.
- A new plate must be calibrated before use: find two or more objects of known size at different depths, solve the horizon and
  camera height, add it to `PLATE_GEOM`, and check it with a figure beside the object (desk top at the hip, chair back at the chest).
- Check the result against furniture: a desk top should sit at Ren's hip, not his chest, and a car roof below his head if he is nearer
  the camera than the car.

**Grounding: feet on the floor, never on the frame edge.**
- Place the feet at a floor point inside the frame with visible floor below them. Never put a full-body figure's feet on the bottom
  edge of the frame as if it were a bust. Busts crop flat at the frame bottom and that is the only case for it.
- Every standing figure has a tight contact shadow under its feet (`contact_shadow()`), not a soft wide cloud.
- If no seated pose exists in the approved art, Ren stands beside the chair. Do not hide his lower body behind a desk or laptop to fake
  sitting (that produced the floating-torso fault). A real seated pose is new artwork and needs owner approval.
- Cards, tags and graphics keep clear of the standing figure's whole bounding box; a standing figure takes more width than a bust.

**Smooth motion: sub-pixel placement only.**
- Never resize a figure to whole-pixel dimensions and paste it at whole-pixel positions on a frame that moves: the rounding makes it
  tremble by up to about 1 px. Use `paste_smooth()` / `place_smooth()` (float position and size, one sharp pre-scale per size step).
  Draw shadows the same way.
- Slow camera pushes are fine; the figure and its shadow must move with them smoothly. No decorative wobble (unchanged rule).
- Prove it: `videos/free_money/jitter_check.py` moves and scales each approved Ren still and fails above 0.12 px of placement noise
  (the old whole-pixel placement measured 0.36 px; the standard measured 0.06 px).

**Cut frames: a cut frame belongs to the shot that starts on it.**
- Look up each frame's shot with a half-open interval `[start, end)`. The earlier `start <= t < end + epsilon` lookup gave the cut frame
  to the outgoing shot, so every cut was one frame late and a page peel showed one stray frame of the previous shot.

**Required checks before sending any long-form video** (all run on the final MP4, supplementing, not replacing, looking at frames):
- `videos/free_money/qa_timeline.py`: contiguous frame-aligned shots, shots in script order, assets present, full decode, no one- or
  two-frame inserts, every hard cut on a shot start, clean hand-over at each page peel, no flashes. It must also fail on a known-bad
  file (the old rev03 render).
- `videos/free_money/validate.py` and `jitter_check.py` as above.
- View the middle of every shot, every scene boundary, and 100% crops of faces, feet and shadows. Say what was and was not viewed.
