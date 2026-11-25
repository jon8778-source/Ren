# Ren long-form production baseline

Owner direction, 8 November 2026: the overall visual and storytelling direction
of `ren_401k_match_full_5m42s.mp4` is the new long-form baseline. Its opening is
the strongest reference; improve on its extended graphic-heavy middle. The owner
approved the overall direction, not every asset or unverified factual claim.
Reference provenance and current verification limits: `REN_LONGFORM_REFERENCE.md`.

Read alongside `REN_VIDEO_RULES.md` and use `REN_LONGFORM_CHECKLIST.md`.
Document map (added 25 November 2026): this baseline is canonical for story
direction and the production gates. Visual, technical and voice
specifications are canonical in `REN_VIDEO_RULES.md`; Shorts are governed by
`REN_SHORTS_RULES.md`. Where a specification appears in more than one
document, the canonical document governs. Existing
scale, perspective calibration, grounding, contact shadows, sub-pixel smoothing,
camera, native-resolution matting, 5.5/2.5/3.5-second shot caps, half-open cuts,
transition checks and Qwen voice requirements remain in force. Explicit owner
instructions for a particular episode take precedence. The six-minute duration
is a planning target within a 4-8 minute range, not a reason to accelerate
speech or pad silence. At the script gate, apply the cut test: every scene
must name the decision or the number it changes; a scene that changes
neither is cut or merged.

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

## Story structure (added 25 November 2026)

**The hook comes first.** The first five seconds carry the hook: the problem
or the payoff, spoken over genuine Ren animation (point-camera or lean-in)
with one code-drawn promise graphic. No title card, logo or context-setting
beat opens the film. The start disclaimer is a small overlay during the
hook, never a standalone opening beat (see `REN_VIDEO_RULES.md`).

**Six-beat outline.** Every long-form script is outlined in six beats:
(1) hook/promise, (2) the character's situation, (3) the mistake or tension
- which must land by about 0:45 - (4) Ren explains the mechanism with the
numbers, (5) the decision and its consequence, (6) the payoff and a one-line
recap. The outline is part of the script-approval submission.

**The ending is a beat, not a stop.** The final fifteen seconds contain a
closing beat inside the film: the one-line recap, one specific next-video
recommendation on a code-drawn end card, and the subscribe prompt. The film
does not end on the final explanation or the disclaimer alone.

## Pacing and editing

Avoid long runs of similar rectangular cards or graphics. Alternate explanation
with real presenter animation, character activity and environmental storytelling.
Plan returns to Ren normally every 30–45 seconds when the story allows; never
force a cutaway that interrupts a meaningful action or necessary reading time.
Each return to Ren should carry one forward reference to a payoff still to
come (an open loop), so the return also gives the viewer a reason to stay.
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

Music experiment (added 25 November 2026): the no-music rule stands. A single
pilot may include a low, licensed music bed and subtle graphic sound effects
for owner A/B judgement at the pilot gate. The experiment changes nothing
unless the owner approves that pilot on that basis and the change is recorded
here.

For every new long-form video, unless the owner explicitly overrides a gate:

1. Research the topic, check claims against appropriate sources and calculate
   each illustrative financial example; flag material uncertainty.
2. Obtain owner approval of the script. Do not synthesize voice before this gate.
3. Inventory assets, verify approvals and character continuity, and identify gaps.
4. Produce an approximately 60-second animated pilot with the actual workflow.
5. Obtain explicit owner pilot approval before full production.
6. Produce the full approximately six-minute video, reusing approved material.
7. Run technical, financial, visual and audio QA, including every scene boundary
   and a captions track generated from the approved script and checked against
   the audio.
8. Obtain owner final approval.
9. Packaging: obtain owner approval of the title, thumbnail, description and
   pinned comment as a set. Publication then needs separate explicit
   authorization.

An explicitly supplied production-approved script need not be approved again.
Record actual approval evidence and the hashes of the approved inputs and output;
neither an encoded preview nor silence constitutes approval. Disclose any
unperformed listening, playback, claim-verification or device checks.

## Legacy precedence

`CLAUDE.md` and `DECISIONS.md` retain older white-background/static-bust/Kokoro
decisions for historical projects. They do not govern new long-form production.
The coffee v3 implementation remains a valid approved method and reference; its
historical footage and quality metrics are not automatic approval for new work.
