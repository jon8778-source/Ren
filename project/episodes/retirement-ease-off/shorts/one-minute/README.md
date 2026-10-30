# One-minute retirement Short

Owner-authorized Short derived from the existing revised long-form MP4.
It uses its closing three complete narration segments (s012–s014), approximately
61 seconds. No new narration, voice calls, music, speech-speed changes or padding.

Portrait format: 720×1280, 9:16, 24 fps, H.264/yuv420p and AAC at 48 kHz.
Decode the existing 1280×720 video at native resolution. Office shots crop Ren
at native size, centred away from the right-side controls. Existing graphic-card
pixels are arranged vertically. Fredoka headlines are redrawn for readability;
these are shot headings, not word-synchronised captions. Essential text/cards
stay above y=1000 and left of x=620, following the proportional Shorts safe area.

The opening on-screen question supplies context for the excerpt's first spoken
line, “Revisit the plan each year…”. The clip continues through the emotional
problem, the condition for easing off, and the original closing question and
Ren sign-off. Whole segments preserve sentence endings and the original order.
No mathematical scenario or qualification is selectively edited.

From repository root, using the episode's pinned Python dependencies:

```bash
/workspace/ren-voice-test-venv/bin/python project/episodes/retirement-ease-off/shorts/one-minute/render.py
```

Requires the revised long video and existing narration master at their episode
paths, pinned by SHA-256. Rebuild those from the episode source and completed WAVs
if unavailable. Do not regenerate audio. The long video, coffee prototype and
main are preserved. Output is in ignored deliverables/, separate from Git.

See validation.json and shots.json for exact timing and source provenance.
Listening/word verification limits from the existing narration still apply.
Do not claim audio was listened to based on sample comparison. No YouTube upload.
