# Revision6 — blocked at the requested asset-quality checkpoint

Revision5 was inspected and its SHA verified against its recorded passing QA.
It remains15s,1080×1920,24fps,H.264/AAC. Original MP4/renderers/artwork/narration
are unchanged. No Revision6 MP4 or new character artwork has been produced.

## Highest-priority finding

The approved animation library decodes at1280×720 but embeds a small full-body
character. In the inspected reaction frame, a manually selected facial span is
about77pixels. A genuine chest-up camera test with5× native enlargement puts that
span at385pixels,35.6%of output width. This achieves the requested size/framing,
but100% inspection shows softened/blocky eyes, glasses and outline detail. It
fails the quality bar for production. No sharpening or AI upscaling was used.

A4× alternative was also tested. It offers less enlargement but still lacks the
facial detail needed for this camera distance. Cropping is feasible; approved
source detail is the limitation. Another enlarged full-body source would repeat
the earlier problem, so it will not be delivered as a completed Revision6.

## Approved-asset search

The v3 full-body clips and extracted approved-reference PNGs offer the same
limited source detail. Larger portraits exist under project/characters/ren but
have no verified v3 reaction-asset approval in this checkout. The supplied Long1
ZIP explicitly labels its portraits/cutouts as visual references, not approved
GitHub renderer frames. The earlier generated seated office pose is also marked
pending approval. None was silently substituted.

The laptop hand also needs the correct perspective. No suitable approved
trackpad-click insert was verified; the previously rejected rotated pointer
will not be restored. Two tightly scoped asset briefs are provided for approval.

## Proposed timing, retaining the exact Revision5 narration

-0–5s: first frame already close on Keep current plan. Approved clicking insert
  presses at0.65s. Four confirmations appear about0.9/1.85/2.8/3.75s. A short
  motivated push toward the button then a reveal of the annual sequence replaces
  the establishing hold. The narration describes the same repeated action; no
  voice acceleration, new words or synthesis is needed.
-5–9s: new approved chest-up reaction master, face25–40%of canvas width, subtle
  concern. No full-body footage, desk or foreground paper mask.
-9–15s: Plan A$2,520/year revealed, held; Plan B$840/year introduced around11.5s.
  Use equal-sized large figures on the existing physical comparison document,
  restrained navy/sage contrast and one deliberate paper reveal. Keep both readable
  after reveal. “Premiums only”/care-cost inspection finishes the twist. No net-
  saving promise, bar chart or new numbers. All prices remain code-derived.

These timings are a proposal, not a claim of checked Revision6 motion.

## Pass/fail and pending checklist

| Acceptance item | Status/evidence |
|---|---|
|Correct baseline/originals preserved|PASS: source hash matches recorded Revision5 QA; originals unchanged|
|First-frame focal point|PENDING: button close-up planned; no Revision6 output|
|Actual hand click within1s|BLOCKED: correct clicking insert required; previous pointer rejected|
|Four annual confirmations/purposeful camera movement|PENDING: existing components reusable; final motion not rendered|
|Face25–40%width/chest-up|DIAGNOSTIC ONLY:5× still gives approximately35.6%; no full-body view|
|Sharp, convincing close reaction|FAIL: approved source detail insufficient at that enlargement|
|V3 design/natural expression|Approved source used in diagnostic; new asset requires review|
|Sequential readable premium payoff|PENDING: retained valid amounts and planned9–15s sequence; no revised motion verified|
|No blue border/letterboxing|Diagnostic is full1080×1920; no completed Revision6 to certify|
|No distortion/glitches|No geometric stretch used; motion certification pending|
|Qwen narration preserved|PASS for preservation: no audio edits/new TTS; model/reference proof from Revision5 retained|
|Revision6 A/V sync/runtime/codecs/full decode|NOT RUN: no Revision6 MP4|
|Full60s production|NOT STARTED|

## Images and reproducibility

-01-baseline-opening.png: actual Revision5 frame at0.65s, clearly a baseline reference.
-02-closeup-diagnostic-not-approved.png: actual5× native-source camera test; not
  new artwork or an approved production frame.
-03-baseline-price-reveal.png: actual Revision5 frame at14.5s, a retained-asset reference.
-Source-head-detail and4×/5× tests show the resolution trade-off.

Run test_closeup.py using the existing project Python environment to reproduce
only diagnostic stills. assessment.json records source hashes/settings. Images
are delivered separately outside Git. They are audit evidence, not three verified
Revision6 screenshots. Actual listening/Android testing was not performed here.

## Required next decision

Per the user's Revision6 fallback, STOP and obtain explicit permission before
generating/substituting major artwork. Request approval for the chest-up reaction
master and correctly oriented clicking-hand insert described in ASSET_BRIEFS.md.
All other assets, the script and the approved Qwen narration should be reused.
