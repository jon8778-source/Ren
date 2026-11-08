# Ren v3 — permanent Shorts production standards

These owner-requested standards apply to every new Short, including derivatives
of long videos. Read with AGENTS.md and REN_VIDEO_RULES.md. They supersede older
Shorts layouts, silence-spacing helpers and exceptions recorded in historical
QA reports. They do not change long-form production. A completed older Short is
not a template approval under these rules.

## Purpose-built portrait storytelling

Compose natively at **1080×1920, 9:16, 24fps**, H.264/yuv420p with AAC audio.
Environmental artwork fills the canvas. No permanent navy/blue surround,
letterboxing, embedded landscape window or decorative frame. Navy remains a
brand colour for objects/text, not a border around resized footage.

Tell the story through illustrated actions, environments, prop close-ups and
character interactions. Ren appears when relevant, not continuously. Presenter
shots keep Ren left and explanatory content right where portrait space permits;
use another purposeful composition instead of squeezing a landscape slide.
Avoid faces, hands and furniture under text. Use close-ups and cutaways, not
repeated presenter poses or generic PowerPoint infographics. Large simple
numbers/graphics belong to the story's phone, receipt, plan card or environment.

Aim for a **meaningful visual change every 2–4 seconds**: action, prop reveal,
reaction, reframing or motivated cut. This is not permission to flash unreadable
text. Important figures can remain visible across several actions/cuts. Explain
any longer reading hold or shorter beat in the shot manifest. Do not relabel an
unchanged frame as multiple scenes to satisfy timing. Retain applicable v3 shot
limits unless an intentional reading hold is explicitly justified and reviewed.

Motion must explain an action or consequence. Vary framing and gesture; no
arbitrary wobble, endless zoom, automatic mirroring or repeated loops without
an explicit narrative justification. Transitions follow objects, gaze or action.

## Character and audio identity

Use the actual approved v3 Ren: same hair, glasses, clothing, proportions,
linework and restrained shading. Decode animation at native resolution before
matting; resize once and protect opaque white clothing/trainers. Inspect edges,
face and temporal stability at output size. No stock/AI substitute character.
Use only approved supporting-character appearances and suitable environments.
A legacy character-manifest entry is not proof of v3 approval.

Preserve the approved British Qwen Ren voice/reference/settings unless the owner
explicitly requests a different voice. Reuse the exact approved audio for
visual-only revisions. No silent substitutions, speed changes, time stretching,
silence padding, paid fallback or blind retries. Use existing resumable voice
workflow when new narration is authorized. Discard animation-clip audio; no music
unless explicitly requested. Current narrator-led mouth-closed convention remains;
lip sync is not implied by a successful timestamp check.

## Asset-first checkpoint (before rendering)

1. Analyse the script scene by scene, independent of narration segment boundaries.
2. Inventory actual approved characters, environments, animations and props.
   Inspect candidate images/clips, source resolution, duration and gesture direction.
3. Save an **asset requirements report** with scene IDs, reusable paths/hashes,
   approval provenance, missing items, intended composition and action.
4. Draw numbers, interfaces, simple props and infographics in code. Generate
   missing illustrations only when necessary, using approved reference images.
   For each missing item supply a numbered brief, shot, required reference paths
   and intended use. Do not substitute unrelated stock artwork.
5. New character designs or major style changes require explicit owner approval.
   Required artwork must be approved before full rendering. Temporary graphics
   must be labelled temporary in the report, never passed off as approved art.

Use `project/shorts/production.example.json` as a manifest contract. It is an
intentionally blocked example, not an approved production. Bind all assets,
script, audio, renderer and configuration dependencies by SHA-256. Include
approval source/evidence per asset. Resolve missing assets before production.

## Mandatory 15-second prototype gate

First render **15 seconds** (360 frames) in portrait with at least **three
actually distinct compositions**, approved character styling, full-screen
environmental artwork, purposeful animation and readable typography. Preview
encoding may use a faster preset/higher CRF; composition and canvas stay native.
Do not use a low-resolution preview to certify character sharpness.

Run technical QA, inspect the complete prototype in motion, and deliver the MP4,
actual runtime, asset report, QA findings and unresolved issues. **STOP and ask
for explicit Jon approval. Do not render the complete Short before it arrives.**
Successful encoding, an old approval or silence is not approval. This is a
specific owner-required gate. No new approval is needed for the identical
prototype unless it or the script/assets/settings change materially.

Record approval only from an actual explicit user message, including who, when,
message reference/quote, actual human review notes (resolving QA warnings),
prototype file SHA and production-input fingerprint.
`record-approval` never obtains permission; it records permission already given.
The launcher rejects missing/stale approval. Changed script/audio/art/layout/
renderer invalidates the fingerprint and requires a fresh preview/review.

## Safe areas, readability and accuracy

Default critical-text safe rectangle at 1080×1920: **x=72…900, y=180…1560**.
These are conservative project margins, not a guarantee about every YouTube UI.
Backgrounds/actions extend to canvas edges. Keep critical faces and gestures
clear of right controls/bottom metadata too. Review a phone-sized playback.

Measure actual font bounding boxes, including animated positions, in final-canvas
coordinates. Save `layout.json` evidence for every scene (explicit empty list for
scenes without text). `LayoutRecorder` captures Pillow text at its actual font;
other renderers must emit equivalent measured bounds, not guessed boxes. Sample
all extrema of motion or every frame. Minimum default sizes: text 42px, captions
40px, disclaimer 30px. Review contrast/reading time; size alone does not prove
readability. A safe-area check cannot OCR unrecorded baked-in text: inspect it.

Keep correct financial totals fixed while animating other objects. Use shared
assumptions/calculations, labelled illustrative figures and source-backed claims.
Never turn a premium difference into guaranteed net savings. Display at the end:
**Educational content only, not financial advice.**
Keep it legible for at least two seconds; also preserve applicable opening
educational wording. Store exact text/times in the measured layout record.

## Enforced workflow and commands

From repository root (existing project Python environment):

    python project/pipeline/shorts_standards.py preflight --manifest PATH/production.json
    python project/pipeline/shorts_standards.py run --manifest PATH/production.json --stage prototype --output PATH/prototype.mp4 -- COMMAND ARGS
    # Deliver preview, then STOP for explicit approval.
    python project/pipeline/shorts_standards.py record-approval --manifest PATH/production.json --prototype PATH/prototype.mp4 --report PATH/prototype.qa.json --by Jon --evidence 'Actual approval message reference and exact quote' --review-notes PATH/human-review.md
    python project/pipeline/shorts_standards.py run --manifest PATH/production.json --stage full --output PATH/final.mp4 -- COMMAND ARGS

Adapters must honour `REN_SHORTS_STAGE` and `REN_SHORTS_MAX_FRAMES`, render only
that interval, and write current layout evidence before post-render QA. The
launcher is an orchestration/QA layer around the chosen approved renderer, not
a replacement renderer or a security sandbox. Direct historical render scripts
are not compliant future entrypoints. `pipeline/shorts.py` now routes to this
workflow rather than running the legacy fixed-gap extraction path.

`qa` checks an already rendered stage; `inspect` audits old media without
rendering. JSON + concise Markdown reports accompany each result. Hard failures
block release. Heuristic border/freeze warnings must be resolved in human review;
never suppress a real border to make QA green. Approval is bound to the report
and exact media bytes, not just its filename. Reports are evidence, not proof
that someone listened or that storytelling is good.

## Technical and human QA

Automate resolution/aspect/fps/codecs, duration/frame counts, full fatal decode,
frame timestamp gaps/duplicates, blank frames, suspicious persistent edge bands,
long frozen runs, asset existence/hashes, measured text bounds, declared visual
variety/repeated scene or animation IDs, cue timeline bounds and A/V endpoint
agreement. Repeated animations require a justification; scene IDs must be unique.
A/V endpoints do not verify spoken words or lip sync. Pixel-level duplicate frames
can be deliberate holds; flag and review rather than silently dropping them.

Human review must watch the whole prototype and final in motion, listen to
narration/joins, check sharpness, consistent characters, full-bleed environments,
visual motivation, repeated loops, text reading time, UI safety, mouth convention,
figures and financial context. Identify device/listening checks not performed.
No automatic QA result replaces explicit prototype approval.

## Efficiency and recovery

Hash-cache approved artwork/mattes/native decoded animation and rendered scenes
using text/assets/settings/renderer hashes. Check frame count/codec before reuse.
Keep scene IDs stable; replace only changed scenes, then remux compatible video
chunks with preserved narration. Validate joins and decode the complete result.
Do not reuse stale audio after text/settings change. The helper `scene_cache_key`
provides dependency-based keys. `SceneCache` validates geometry, frame count,
fatal decode and SHA before reusing video-only chunks; render adapters use it
for their actual scene rendering/assembly. Narration stays a separate track.

Record checkpoints and exact resume commands. Keep media, credentials and caches
out of Git; source manifests/rules/reports belong on a feature branch. No merge,
YouTube publication or large video GitHub upload without explicit instruction.
