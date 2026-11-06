# Asset-first audit and health insurance Short test proposal

This is an implementation audit and **proposed** test, not authorization to render
or an artwork approval. No voice generation, new artwork or movie rendering was
performed for the production-system task.

## Inspected existing implementation

- `../pipeline/shorts.py`: historical long-video line extraction inserted fixed
  lead/gap/tail silence and copied legacy scenes. CLI now dispatches to the new
  standards workflow. Long-form assembler/voice/QC functions remain unchanged.
- `../episodes/long1-open-enrollment/portrait-short-01/render.py`: current derivative
  used native 610×680 Ren/office crops inside a permanent navy surround, plus
  code-drawn cards. Audio reuse is useful; the framed layout is noncompliant now.
- `../episodes/open-enrollment-short-01/revision-02/render.py`: native actor
  decoding and purposeful cursor/stopwatch motion can inform reusable components;
  its surround/character glow and sustained presenter layout are not new standards.
- `../prototypes/coffee-minute-v3/render.py`, artwork manifest: approved character
  matting/native decode, Fredoka and navy/sage/cream design remain source methods.
- `../../assets/ren_library/ren_thinking.mp4` and companion library clips exist.
  Actual intervals/direction/mouth closure must be inspected when selecting them;
  this system-only task did not claim a new motion approval.
- `../characters/manifest.json` is a legacy registry. Do not interpret every pose
  or supporting character there as approved v3 artwork.

## Reusable assets for a future 15-second prototype

| Item | Existing source | Use/constraint |
|---|---|---|
| Ren v3 | Approved v3 artwork/library and existing full film | Reuse exact appearance; no redesign |
| Office | `prototypes/coffee-minute-v3/assets/office.png`, 1672×941 | Approved landscape room; plan portrait framing first |
| Alternate office source | `episodes/open-enrollment-short-01/assets/ren-seated-office.png`, 1672×941 | Historical generated scene; verify specific approval before use |
| Narration | Revised completed health-plan MP4 | Reuse British Qwen voice samples unchanged; source hash in existing edit manifest |
| Medical illustrations | `episodes/long1-open-enrollment/full/assets/medical-props.png`,1536×1024 | Existing illustrations; useful after hook, not required for first 15s |
| Typography | `remotion/public/fonts/fredoka-latin-600-normal.woff2` | Existing Fredoka |
| Email/button/plan cards/stopwatch | Existing full-film/Short interface code | Redraw as integrated portrait props, not permanent slide panels |

## Missing items and numbered briefs

1. **Portrait office coverage, only if approved artwork cannot frame cleanly.**
   Intended shots: opening email arrival and reaction. First try a portrait camera
   crop of the existing office while keeping desk/chair proportions and native
   character detail. If insufficient, brief: “Extend the approved sage home office
   vertically to a 9:16 full-bleed room. Preserve desk/chair design, cream walls,
   sage accents, lighting, flat 2D linework. Leave a clean laptop action area.
   Background only; no new people, embedded labels, borders or text.” Required
   references: exact approved office original from the v3 artwork pack and approved
   Ren reference for scale (do not regenerate Ren). New scene approval required.
2. **Desk/laptop close-up environment if the existing approved desk detail is too
   soft.** Intended shots: cursor click, renewals and comparison. Brief: “Portrait
   close-up of the same approved desk/laptop, same materials and illustration
   style; empty screen for code-generated UI; no people, baked-in labels or
   redesigned furniture.” Required references: approved office original and chosen
   crop showing desk/laptop. Prefer code-drawn screen/props over image generation.

No new character design is needed. Do not generate either illustration until
layout tests establish it is necessary. Any unresolved required item blocks
production preflight; the example manifest intentionally contains missing inputs.

## Proposed test: existing health insurance Short

1. Copy the manifest example into a new isolated Short directory. Retain the
   old MP4 unchanged as an audit baseline, not the portrait visual template.
2. Inventory/hash approved script/audio/art, renderer dependencies and asset report.
   Resolve the two conditional gaps above; record actual approval provenance.
3. Storyboard first 15 seconds in five connected ~3-second beats: full-screen
   office email arrival → laptop/cursor close-up → successive annual confirmations
   → plan cards on the desk → Ren noticing total-cost terms. At least three real
   compositions; vary motivated action without cycling a character loop.
4. Reuse the existing hook narration at natural speed. Coordinate source phrase
   boundaries with the prototype; do not accelerate or insert silence. The test
   demonstrates the opening, not a completed miniature argument.
5. Instrument actual final-coordinate text bounds, including motion extrema;
   reserve x72–900/y180–1560 for critical text. Keep the correct premium amounts
   fixed at $2,520/year and $840/year; “premiums only” must remain explicit.
6. Run gated prototype rendering and QA, then watch/listen to the whole 15 seconds
   and inspect 100% crops/phone-sized playback. Provide the prototype and findings.
   **STOP for explicit Jon approval.** No full health Short is rendered in this task.
7. After approval only, extend story/action beats, reuse audio and cache scenes;
   make one visual-only scene change and demonstrate that other chunks and audio
   hashes remain unchanged. Verify concatenated joins/full decode again.

## Existing media audit (decode only)

`health-plan-existing-media-audit.json/.md` records a fresh decode of the existing
58.875-second Short: 1,413 frames, valid portrait output, continuous timestamps,
0s A/V start offset and ~0.01s duration difference. The persistent-edge heuristic
correctly flags the navy surround for human review. Source implementation confirms
that it is an actual decorative canvas surround, so this older export is **not
compliant with the new visual standard**, despite its technical media pass.
No current per-frame measured layout evidence or new 15-second approval exists.
No claim is made that this audit listened to audio or tested physical Android.
