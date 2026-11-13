# Ren videos

@AGENTS.md

Animated personal-finance videos narrated by Ren, the mascot. The owner (the channel creator) reviews at
fixed gates. This file adds Claude Code specifics to the shared rules in `AGENTS.md` (imported above).

## Precedence

1. The owner's explicit instruction for the task (consistent with the approval gates below).
2. Current rules: `AGENTS.md`, `project/REN_LONGFORM_BASELINE.md`, `project/REN_VIDEO_RULES.md`,
   `project/REN_LONGFORM_CHECKLIST.md`, and for Shorts `project/REN_SHORTS_RULES.md`.
3. Legacy: `project/LEGACY_WORKFLOW.md` ("Existing episodes only") and the older sections of
   `project/DECISIONS.md`. Use these only to maintain an existing episode.

If two current files disagree and you cannot tell which is newer, do not guess: stop and ask. Known open
questions are listed under "Open TODOs" at the end of this file.

## Preflight (before any Ren video task)

Do these and report the result before claiming anything was inspected, run or approved:

1. Identify the branch: `git branch --show-current`. Work only on an isolated working branch.
2. Read the applicable rules (long-form: the three `project/REN_LONGFORM_*`/`REN_VIDEO_RULES` files plus
   `project/DECISIONS.md`; Shorts: also `project/REN_SHORTS_RULES.md`).
3. Check that the files and tools you need exist on **this** branch (`ls`, `git ls-tree`), including
   `ffmpeg`/`ffprobe`, Python deps, and the browser (see "Browser path").
4. Do not infer approval from a file's existence. Clip, character and artwork approvals need evidence.
5. If something is missing, report the blocker and use an authorized production branch or ask for a scoped
   implementation. Never silently substitute assets, voice, QA or renderer.

Not all production assets are on `main`. Verified by listing the remote branches:

| Needed for | Where it lives | On `main`? |
|---|---|---|
| Ren animation clips (`assets/ren_library/`, `ren_library.json`) | `main` | yes |
| Qwen voice reference (`Audio/ren_reference.wav`, `.txt`) and `project/cliplib/` voice scripts | `main` | yes |
| `project/cliplib/ren_stage.py` (scale, grounding, smooth placement) and its tests | `video/free-money-v2`, `codex/ren-longform-baseline` | no |
| `videos/free_money/` QA scripts (`qa_timeline.py`, `validate.py`, `jitter_check.py`) | `video/free-money-v2`, `codex/ren-longform-baseline` | no |
| `project/pipeline/shorts_standards.py`, `project/shorts/production.example.json` | `video/free-money-v2`, `codex/shorts-production-standards` | no |
| `project/prototypes/coffee-minute-v3/` (approved v3 renderer and artwork) | `codex/ren-approved-v3`, `codex/shorts-production-standards` | no |

Re-verify this table against the branch you are on; branches move. Do not merge these branches into your
working branch just to obtain files. Check them out read-only or copy what is authorized.

## Gate sequence (long-form)

Stop at each gate and wait for the owner's explicit reply. An encoded preview or silence is not approval.

1. Verified research and claims; calculate and label every illustrative figure.
2. **Explicit script approval.** Do not synthesize voice before this gate.
3. Asset inventory: provenance, character continuity, clip durations, approvals, gaps.
4. Approximately 60-second animated pilot using the real production workflow.
5. **Explicit pilot approval.** Do not render the full video before this gate.
6. Full video, reusing approved material.
7. Technical, visual, audio and financial QA, including every scene boundary.
8. **Owner final approval.**
9. **Publishing needs separate explicit authorization.** Neither final approval nor a merge authorizes it.

A script the owner explicitly supplies as production-approved need not be approved again. Record real
approval evidence and input/output hashes. Say what you did not do (listening, device playback, claim checks).

### Shorts

Read `project/REN_SHORTS_RULES.md`: asset-first review, then a 15-second portrait prototype. Stop for explicit
owner approval before producing a complete Short. A long-form approval is not a Short approval.

## Current visual and audio system

- Hybrid story-led animation: genuine Ren MP4 clips from the approved library, illustrated environments,
  code-drawn graphics. Moving or zooming a still is not character animation. Details and shot caps are in
  `project/REN_VIDEO_RULES.md` and `project/REN_LONGFORM_BASELINE.md`.
- Voice: British Qwen clone only. No fallback voice, speed change, stretching or silence padding. No music
  unless the owner authorizes it. Discard animation-clip audio. Narrator-led mouths stay closed.
- Route and scripts for hybrid prototypes: `project/cliplib/README.md` and `project/cliplib/render_hybrid.py`.

### Where the Qwen voice settings live

Verified on `main`; there is no single config file:

- Reference audio: `Audio/ren_reference.wav`; exact transcript: `Audio/ren_reference.txt` (strip the stray
  leading quote mark only; keep every word).
- Descriptor: `Audio/ren_voice_description.txt` (British male, 30-35, light Manchester-influenced). The Base
  cloning API uses the WAV and transcript, not this prose. It documents intent only.
- Model/Space/endpoint: `Qwen/Qwen3-TTS-12Hz-1.7B-Base`, Space `Qwen/Qwen3-TTS`, `/generate_voice_clone`,
  English, set in `project/cliplib/qwen_voice.py` (hosted) and `project/cliplib/local_voice.py` /
  `qwen_local_voice.py` (local). Prose summary: `project/cliplib/README.md`.
- `HF_TOKEN` comes from the runtime environment only. Never commit or print it.

TODO (owner): the current rules say `use_xvector_only=True`, but `project/cliplib/qwen_voice.py` on `main`
passes `use_xvector_only=False`. Do not change either until the owner says which is approved. The "resumable
quota workflow" named in `project/REN_VIDEO_RULES.md` is not documented on `main`.

## Maths and editorial rules (always)

- Never invent statistics, sources or guarantees. A real statistic needs `[VERIFY]` plus a source link, or it
  is cut. Unsourced "most people"-style claims are not allowed.
- Calculate figures in code from one assumptions source; draw numbers in code, never inside generated art.
  Every displayed equation must be correct on every frame.
- The disclaimer "Educational only, not financial advice" appears on screen (start and end for long-form;
  see the Shorts rules for Shorts) and in the description.
- You cannot listen to audio. Say so plainly, and ask the owner to check pronunciation, pace and joins.

## Git rules

- Commit on the working branch only. Never push to `main`. Never merge. Open a pull request only when the
  owner asks (a PR is also how work reaches `main`, after review).
- Do not commit large video files (MP4/MOV/WAV renders, caches, decoded frames) or credentials. Source,
  manifests, rules and reports belong on a feature branch.
- Preserve existing episodes. Do not merge unfinished episode source merely to share rules.
- No YouTube publication or merge without separate explicit instruction.

## Browser path (Remotion, legacy renderer, thumbnails)

Do not hardcode a Chromium version. Use an environment variable, else a glob:

```sh
BROWSER="${REN_BROWSER_EXECUTABLE:-$(ls -d /opt/pw-browsers/chromium_headless_shell-*/*/headless_shell \
  /opt/pw-browsers/chromium_headless_shell-*/*/chrome-headless-shell 2>/dev/null | sort -V | tail -n 1)}"
# then: --browser-executable "$BROWSER"   (only if $BROWSER is non-empty)
```

Verified: this container has `chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell`,
a different layout from the older `chromium_headless_shell-1194/chrome-linux/headless_shell`, so the glob
covers both.

## Other code

`src/` (Remotion) and `videos/` (HyperFrames) hold older one-off 9:16 shorts and episode-specific scripts.
Leave them alone unless asked. The legacy episode pipeline and its "New episode" workflow are in
`project/LEGACY_WORKFLOW.md`.

## Open TODOs (do not guess these)

- TODO (owner): Shorts length. `project/REN_SHORTS_RULES.md` requires a 15-second prototype but gives no
  full-Short length; legacy docs say about 30 seconds. Ask before fixing a target length.
- TODO (owner): Is the "Money Leak Audit Workbook" call to action still used? Legacy docs require it; the
  current rules are silent. Do not add or remove it without confirmation.
- TODO (owner): Do thumbnails (3 options, owner picks) and "2 shorts per episode" remain part of new
  long-form work? The current gate sequence omits both; legacy included them.
- TODO (owner): Long-form output size. Legacy was 1920x1080; the approved v3 prototype was 1280x720.
- TODO (owner): Exact disclaimer wording and placement (legacy "Educational only, not financial advice";
  Shorts rules "Educational content only, not financial advice.").
