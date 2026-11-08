# Ren long-form production baseline

Owner direction, 8 November 2026: the overall visual and storytelling direction
of `ren_401k_match_full_5m42s.mp4` is the new long-form baseline. Its opening is
the strongest reference; improve on its extended graphic-heavy middle. The owner
approved the overall direction, not every asset or unverified factual claim.
Reference provenance and current verification limits: `REN_LONGFORM_REFERENCE.md`.

Read alongside `REN_VIDEO_RULES.md` and use `REN_LONGFORM_CHECKLIST.md`. Existing
scale, perspective calibration, grounding, contact shadows, sub-pixel smoothing,
camera, native-resolution matting, 5.5/2.5/3.5-second shot caps, half-open cuts,
transition checks and Qwen voice requirements remain in force. Explicit owner
instructions for a particular episode take precedence. The six-minute duration
is a planning target, not a reason to accelerate speech or pad silence.

## Story and appearance

Tell a connected story through Ren's decisions and consequences, supporting
characters such as approved Maya and Alex when suitable, illustrated environments,
and clear financial explanations. Ren is the recognisable presenter, normally on
the left at/by his desk, with readable graphics on the right. Use actual approved
Ren MP4 animation for presenter movement; moving, zooming or translating a still
is not character animation. Approved stills may be used for story cutaways when
appropriate, within the existing limits; label their use accurately.

Use purposeful character actions, object interactions and camera changes. Maintain
character identity, proportions, glasses, hair, wardrobe, lighting and established
illustration style. Supporting characters must match their approved assets; do not
invent a new appearance or describe a placeholder as approved. Respect physical
perspective and layering: no floating heads, detached arms, false seated poses,
floating feet, obscured faces or furniture, or unwanted white-clothing transparency.

Use the approved office and other appropriate illustrated settings, not a video
dominated by white slides. Use Fredoka and navy, sage, cream and warm wood. Avoid
permanent footer/banner treatments and large panels hiding the office furniture.
Financial labels, numbers and equations are generated in code, derived from one
checked assumptions source, and correct on every displayed frame.

## Pacing and editing

Avoid long runs of similar rectangular cards or graphics. Alternate explanation
with real presenter animation, character activity and environmental storytelling.
Plan returns to Ren normally every 30–45 seconds when the story allows; never
force a cutaway that interrupts a meaningful action or necessary reading time.
Vary framing and use movement to communicate action or consequence, not decorative
wobble, repeated loops or constant zoom. Sustain the first-minute pilot's quality
through the full film. Keep mobile text readable and safely away from faces,
hands and furniture; inspect the actual output, not just coordinates.

## Voice and production gates

Use the approved British Ren clone: `Qwen/Qwen3-TTS-12Hz-1.7B-Base`, English,
`use_xvector_only=True`, existing reference WAV and matching transcript. Hosted
workflow: `Qwen/Qwen3-TTS`, `/generate_voice_clone`. No unapproved substitute,
paid fallback, speed changes, stretching or padding. Preserve completed audio,
hashes and settings across interruptions. Discard source-clip audio; no music
unless specifically authorized. Narrator-led characters keep their mouths closed
unless a separately approved, genuinely aligned lip-sync workflow is available.

For every new long-form video, unless the owner explicitly overrides a gate:

1. Research the topic, check claims against appropriate sources and calculate
   each illustrative financial example; flag material uncertainty.
2. Obtain owner approval of the script. Do not synthesize voice before this gate.
3. Inventory assets, verify approvals and character continuity, and identify gaps.
4. Produce an approximately 60-second animated pilot with the actual workflow.
5. Obtain explicit owner pilot approval before full production.
6. Produce the full approximately six-minute video, reusing approved material.
7. Run technical, financial, visual and audio QA, including every scene boundary.
8. Obtain owner final approval. Publication needs separate explicit authorization.

An explicitly supplied production-approved script need not be approved again.
Record actual approval evidence and the hashes of the approved inputs and output;
neither an encoded preview nor silence constitutes approval. Disclose any
unperformed listening, playback, claim-verification or device checks.

## Legacy precedence

`CLAUDE.md` and `DECISIONS.md` retain older white-background/static-bust/Kokoro
decisions for historical projects. They do not govern new long-form production.
The coffee v3 implementation remains a valid approved method and reference; its
historical footage and quality metrics are not automatic approval for new work.
