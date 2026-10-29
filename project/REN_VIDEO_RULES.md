# Approved Ren hybrid video rules — v3

Jon approved the 61.625-second coffee prototype v3 on 29 October 2026.
Use this as the visual direction for future hybrid prototypes. These rules
supersede conflicting legacy white-only/static-bust/Kokoro instructions for
this route. Existing production episodes remain unchanged.

## Publication status

This commit publishes the approved RULES. The v3 renderer and newly generated
artwork have not been published with it. Do not claim that a fresh checkout can
reproduce v3 yet or silently use placeholder artwork. The approved reference
video is Ren_61s_Coffee_Prototype_v3.mp4 in the owner's ChatGPT files.

Required artwork for that later handover:
- Approved sage office, with desk and chair clearly visible.
- Approved supporting cast: Alex, revised fair-skinned Maya, and Sam.
- Alex buying coffee at a cafe.
- Alex pouring from a French press into ONE mug at home. Do not use the earlier
  dripper image that looked like two stacked cups.

## Characters and editing

- Preserve Ren's recognisable face, glasses, outfit, proportions and illustration
  style. Supporting characters and environments must match that visual world.
- No large white panel obscuring the office desk/chair, Ren/Finance heading,
  bottom yellow progress bar or persistent footer.
- Alternate wider and closer Ren shots. Use brief story cutaways and purposeful
  motion in objects, receipts, calendars and comparisons.
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
