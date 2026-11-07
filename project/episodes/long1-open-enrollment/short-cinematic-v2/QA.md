# Revision4 prototype QA — approval pending

15.000s,1080×1920,9:16,24fps,H.264/yuv420p,AAC48kHz mono,360frames.
Five shots:84/48/72/72/84frames. No full Short or long film rendered.

Changes requested by Jon:
- Open on the renewal button; actual approved Ren hand approaches/presses the
  trackpad at spoken “click”, followed by four annual page changes.
- Waist-up reaction replaces full-body presenter views. The actual closed-mouth
  confused gesture changes expression without a repeated loop or invented face.
- One unfolding comparison document holds much larger prices:158px. Other story
  labels48–130px, disclaimer36px. No small burnt-in caption boxes; separate SRT.
- Wood/object continuity replaces the generic green desktop. Right-hand office
  crop remains behind Ren, with foreground documents motivating the reaction.

Technical QA passes without errors/warnings: exact360frames/duration, full fatal
decode, regular timestamps, no black/blank frames or persistent borders, matching
A/V endpoints, source/dependency hashes, measured text safe areas and exact final
educational disclaimer. Every displayed price is complete and fixed, derived
from shared assumptions: illustrative annual premiums$2,520 and$840. No saving
or better-total-cost guarantee. “Premiums only” / “Care costs?” cue the catch.

Voice verification is stronger than settings alone:
- All AAC packets and decoded PCM match Revision3 exactly; peak−2.00dBFS.
- The saved Qwen-generated WAV hash matches its successful generation manifest.
- After proper sample-rate conversion, its first13.84s correlates0.999456 with
  the current narration. No sample-rate relabelling/time stretching.
- Model Qwen/Qwen3-TTS-12Hz-1.7B-Base,Space Qwen/Qwen3-TTS,endpoint
  /generate_voice_clone,English,use_xvector_only=True. Reference/transcript SHA
  verified. No new TTS/image requests or HF quota consumption.
These establish lineage, not an ear-based confirmation of voice identity/accent.

Inspection:60 encoded samples at quarter-second intervals across all15s, shot
joins, and100% Ren face/glasses/hair/hand/white-shirt and price crops. The raised
arm's enclosed background pocket and the hand crop's unrelated body-edge sliver
are removed; shirt alpha is asserted for all native reaction frames. No sharpening,
AI character upscale, mirroring, mouth flaps or source animation audio.

Limits: existing720p animation sets the detail limit for the2.6× waist-up framing.
That enlargement is disclosed; no higher-resolution character artwork was invented.
No new real-time listening or physical Android test was performed. Subjective
voice delivery, animation naturalness and visual quality remain for Jon's review.
Earlier MP4s/reference/artwork are preserved. STOP for explicit prototype approval.
