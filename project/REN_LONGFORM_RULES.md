# Ren long-form production rules — story-first v1
Status: owner-approved direction, 7 November 2026.
Scope: Ren long-form YouTube episodes, typically 6 minutes (up to 8 minutes when justified).
Read together with project/REN_VIDEO_RULES.md. This document supplements, not replaces, the approved v3 character, Qwen voice, financial accuracy, rendering and validation safeguards.

## Creative goal
Make a compelling, responsible personal-finance story for a primarily US audience aged 25–45, not a narrated slide deck. Ren is the recognisable host and guide; Alex, Maya and other approved characters can experience the decisions, stakes and outcomes. Do not force supporting characters into every scene. Ground the narrative in a relatable human choice and a clear financial insight.

## Narrative architecture
- Cold open: first 0–15 seconds present a specific decision, consequence, surprising contrast or unanswered question. Avoid generic introductions, greetings or long disclaimers.
- By 30 seconds, establish whose story this is, what is at stake and why the viewer should continue.
- Build through setup, tension/trade-off, discovery, decision and payoff. Financial teaching should emerge naturally from the story, not interrupt it with long lectures.
- Use concrete, believable moments, distinct character motivations and conversational dialogue when helpful.
- Include a meaningful payoff and actionable takeaway; avoid exaggerated promises, fabricated personal experiences or unsupported claims.
- Check narrative momentum throughout. If a scene neither advances the story nor clarifies a key idea, shorten or remove it.
- Retention planning is editorial guidance, not a guarantee of YouTube performance.

## Visual direction
- Default Ren presenter composition: Ren on the left by his desk, key text/figures/graphics on the right, when a presenter shot is appropriate. This is not a mandate for every scene.
- Prefer illustrated environments, supporting-character action, object close-ups and over-the-shoulder perspectives over prolonged talking-head layouts.
- Alternate presenter shots, story cutaways and clear financial visualisations; avoid PowerPoint-like sequences of floating boxes, generic icons, repeated charts or static documents.
- Apply the shot-duration and gesture restrictions in REN_VIDEO_RULES.md, unless a specific approved scene justifies an exception.
- Use meaningful movement, scene changes and visual progression rather than decorative zooms, wobble or repeated loops.
- Preserve approved Ren v3 and supporting-character art style. Do not introduce generic AI-looking or stock-like artwork.
- Keep typography, financial labels and critical actions readable on mobile, even in 16:9.

## Asset-first workflow
1. Read AGENTS.md, REN_VIDEO_RULES.md and this file.
2. Review the script, fact-check claims and establish the scene-by-scene story arc.
3. Inventory existing approved Ren, Alex, Maya, backgrounds, props, expressions and animation clips.
4. Produce an asset requirements list: reusable, missing, new, approval-needed; identify the intended use for each.
5. Reuse approved assets first. Request owner approval for new major character designs or material art-style changes before rendering.
6. Lock approved character proportions, outfit, voice and visual palette across scenes.

## Narration and financial accuracy
- Use the established British male Qwen voice and configuration in REN_VIDEO_RULES.md. Reuse approved narration for visual-only edits.
- Do not silently switch TTS providers or invent voice settings. Stop and report unavailable voice resources or quotas.
- Keep dialogue natural, with measured energy and enough space for key ideas.
- Distinguish illustrative examples, premiums, deductibles, total costs, contributions, investments, taxes and actual savings. Validate displayed calculations and caveats against the approved source.
- Do not invent citations, statistics or financial outcomes. US-specific terminology must be checked for relevance and accuracy.

## Mandatory 60-second pilot gate
- Before producing the full episode, render a roughly one-minute prototype showing the opening hook, at least one story-driven cutaway, a financial explanation and representative Ren presenter framing.
- Include the intended approved Qwen narration, production artwork, scene transitions and mobile-readable figures.
- Deliver the pilot and a concise asset/QA summary; STOP and wait for explicit owner approval.
- Do not treat script or storyboard approval as approval for the full render.
- After approval, lock the pilot's creative direction and reuse approved scenes/audio where technically feasible. Only revise approved material to fix defects or at the owner's request.
- A narrowly scoped edit to an existing finished video may use a shorter replacement preview when the owner explicitly authorises that exception.

## Full-production QA
- Check narrative continuity, hook clarity, varied framing, supporting-character consistency, transitions, repetitive poses, visible financial accuracy, and mobile readability.
- Inspect every shot and actual rendered frames, not just metadata. Follow REN_VIDEO_RULES.md for native-resolution character rendering, full decode, audio continuity, frame counts and calculation validation.
- Preserve working source files, use resumable/cached assets and avoid unnecessary full rerenders.
- Deliver full MP4, change log, asset reuse/new-asset summary and QA results. Do not publish without owner permission.
- Work on a separate branch; do not merge or alter main without instruction.

## Relationship to other rules
- REN_VIDEO_RULES.md governs general v3 art, voice, technical quality and accuracy.
- REN_LONGFORM_RULES.md governs long-form narrative structure, asset planning and the one-minute approval gate.
- REN_SHORTS_RULES.md applies to Shorts only and must not impose 9:16 or a 15-second gate on long-form episodes.
