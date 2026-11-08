# Ren production instructions (repository-wide)

These are standing instructions for Codex and other development agents starting in this repository. Before any Ren video task, identify the active Git branch, check that the required files and assets are actually available, and read the applicable rules. Do not infer approval from the existence of a file.

## Long-form videos

For every new or substantially revised long-form Ren video, read:
- `project/REN_LONGFORM_BASELINE.md`
- `project/REN_VIDEO_RULES.md`
- `project/REN_LONGFORM_CHECKLIST.md`
- `project/DECISIONS.md`

Use approved story-led hybrid animation, genuine Ren animation clips, illustrated environments, Qwen British voice cloning, and the owner approval gates. The normal gate sequence is: verified research and claims; explicit script approval; asset inventory; approximately 60-second animated pilot; explicit pilot approval; full video; technical/visual/audio/financial QA; owner final approval. Never synthesize voice before required script approval, render the full video before pilot approval, or publish without separate authorization.

## Shorts

For every new or revised Ren Short, additionally read `project/REN_SHORTS_RULES.md`. Require its asset-first review and 15-second portrait prototype. Stop for explicit owner approval before producing a complete Short. Do not infer a Short's approval from an approved long-form video.

## Precedence and asset verification

Approved current hybrid/Qwen instructions take precedence over older white-background, static-bust, and Kokoro procedures in `CLAUDE.md` or `project/DECISIONS.md`; the latter remain available for legacy episodes. Explicit owner instructions for a task take precedence when consistent with the required approvals.

These policy files live on `main` so new Codex sessions can find them. Some source media, animation helpers, templates and episode-specific QA scripts are maintained on production/reference branches (including `video/free-money-v2` and `codex/ren-approved-v3`), not necessarily on `main`. **Verify actual paths, clip approvals, tool availability and test results on the working branch before claiming anything was inspected, executed or approved.** If required assets or tools are absent, report the blocker and use an authorized production branch or request a scoped implementation; do not silently substitute assets, voice, QA or renderer.

Make changes on an isolated working branch, preserve existing episodes, and use a reviewed pull request for integration. Do not merge unfinished episode source or large video binaries merely to propagate production rules.
