# Ren Health Insurance Short v2 — final production

**Ren_Health_Short_v2_Final.mp4** — 58.708333 seconds, 1,409 frames, native
1080×1920 portrait 9:16, 24fps, H.264/yuv420p with 48kHz mono AAC at192kbps.
SHA-256: `c1ccf3e809d2f55e0538781e6388bddeec397fd289c7ddaa1ebc232112928284`.

## Change log

The approved Revision6 opening (0–15s /360frames) is copied without video
re-encoding; every decoded frame is pixel-identical. Its renewal, close-up and
premium comparison stay unchanged. Rendered only the remainder: clinic bill,
phone conversation, planned-care appointment, pharmacy pickup, Ren’s bill review,
network/drug checks, out-of-pocket limits, early-bill/HSA timing, desk review,
laptop checks, three-question worksheet, annual-review timer and total-cost ending.

A worksheet hand jump found in whole-timeline review was replaced with an eased
glide. Only112frames were rerendered; the other13 new scene chunks were reused
from verified scene-scoped caches. No changes to the long-form video, main or the
original Short/prototype. No YouTube publishing or MP4 upload to GitHub.

## Reuse and new assets

Reused: exact approved opening; owner-approved high-resolution concerned Ren and
right-hand insert; approved office; existing physical laptop; existing medical
prop sheet; Fredoka; shared assumptions; existing Ren hold-phone animation,
decoded/matted at native1280×720 before one2× composition resize. The phone action
is a medium shot; close-ups use the high-detail approved PNGs. No source audio.

New: two empty illustrated portrait environments, clinic and pharmacy (native
941×1672 each), generated against the approved office/medical-prop references.
No people, new character design, financial text or labels generated into artwork.
All financial/UI text is drawn and measured in code. Additional reusable code props:
phone messages, appointment calendar, medical bill, review worksheet/folder and
physical forty-minute timer. No stock illustrations, new character artwork or
new voice generation. Clipboard candidate was audited and rejected, not used.

## Voice and audio

Approved British male Ren workflow: Qwen/Qwen3-TTS-12Hz-1.7B-Base;
Qwen/Qwen3-TTS Space; /generate_voice_clone; English; use_xvector_only=True.
Existing reference WAV/transcript hashes verified. New TTS requests:0; new
Hugging Face GPU usage:0. No fallback service, speed changes, stretching, silence
padding, music or animation-source audio.

Master first15s equals approved prototype PCM exactly; remaining samples equal
the existing Short after its already-approved4-frame quiet-pause adjustment.
Final AAC encoded once for a seamless join; its bytes differ from the prototype’s
AAC encoding, while narration/source timing is preserved. Correlation with master:
0.99997741; peak:-1.96dBFS.
The15s join falls in existing quiet audio (~−52.4dBFS); no new speech cut or gap.

## QA

- PASS: all19 shots covered continuously, exact frame counts; full fatal decode,
  uniform24fps timestamps, no missing/black/blank frames or persistent edge bands.
- PASS: measured critical text within x72–900/y180–1560; actual extrema checked
  on every rendered frame. Minimum ordinary text42px; final disclaimer36px.
- PASS: exact disclaimer remains visible for final2.958s; no permanent border,
  letterboxing, footer/banner, artificial wobble or looped presenter sequence.
- PASS: annual premiums $2,520/$840, covered in-network OOP limits $4,000/$6,500,
  checked against existing assumptions. No invented deductible, HSA opening
  balance, contribution schedule or guaranteed $1,680 saving. Total-cost takeaway.
- PASS: audio coverage matches source sample map; A/V endpoint difference0.333ms.
- PASS: first360frames pixel-identical; native Ren face/glasses/hair/shirt/hand
  crops and every scene checked. Closed-mouth narrator-led format; no lip-sync claim.
- PASS: entire58.71s played to ended in Chromium; 1409 total
  video frames, 0 dropped, no media/page errors. Report bound to final SHA.

Visual review covered the entire timeline in eight4fps sequential sheets, not just
shot midpoints, plus native detail crops and a24fps strip at the15s join. Full
playback was automated in headless Chromium, not a human listening certificate.
Initial file:// navigation was blocked by managed browser policy; supported
loopback HTTP playback worked without disabling browser/network policy.

## Remaining review limits

Ear-based listening and physical Android testing were not performed. No new ASR
word certificate is claimed; existing script/word timings and exact source-sample
coverage were preserved. Ren’s concerned close-ups deliberately reuse the approved
single expression, not a new acting/lip-sync rig. The medium phone action has the
native library’s lower detail; no sharpening or AI upscale was applied.
No technical blockers remain. Subjective final pacing/voice review remains Jon’s.

Reproduction: README.md. Full manifests, hashes, approval evidence, sample map,
validation scripts and browser playback evidence are saved on the production branch.
Videos, review images and caches stay outside Git.
