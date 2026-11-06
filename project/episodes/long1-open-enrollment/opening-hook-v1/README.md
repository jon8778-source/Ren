# Ren health-plan opening improvement — approval preview

Scope is only the completed film's opening. The source329-second MP4 is locked by
SHA-256 in source.json and has never been overwritten. New work lives here on
codex/long1-opening-hook, based on completed source checkpoint983888a.

**STOP for Jon's explicit approval of Ren_Health_Plan_Opening_Preview.mp4.**
review-gate.json is false and records the precise reviewed preview hash. Do not
assemble Ren_Health_Plan_Revised_Opening.mp4 based on older pilot approvals.

See CHANGELOG.md for original0–20.667 replacement boundary and frame496 keyframe.
Only18.38s of new Qwen narration/new hook video was produced. The23.79s preview
reuses the original car-story tail; it does not represent a new full episode.
No remaining scene, voice segment, ending, example, artwork or music was changed.

## Saved review files

- deliverables/Ren_Health_Plan_Opening_Preview.mp4 — preview only.
- script.md/segments.json — exact minor opening-only adaptation; requested-hook.txt
  preserves the proposed wording for comparison.
- audio/ original WAV + manifest.json — one completed free Qwen request, same clone.
- timing.json, source.json, preview-build.json, validation.json — actual timings,
  source identity, packet/frame preservation and technical/visual evidence.
- CHANGELOG.md and QA.md — what changed, what was encoded and review limits.

Source video tail is stream-copied exactly. Preview audio alone is AAC encoded
from normalized new narration and untouched decoded source PCM. Full-film audio
splice is not assembled/certified. After approval, keep source video from496 onward
as a copy wherever technically compatible and report any audio-boundary encoding.

## Rebuild the small preview only

From repository root with existing approved v3 fonts/office/native actor caches:

```sh
python project/episodes/long1-open-enrollment/opening-hook-v1/build_preview.py
python project/episodes/long1-open-enrollment/opening-hook-v1/validate_preview.py
```

Requires existing project dependencies/ffmpeg; current renderer interpreter is
/workspace/Ren/project/.tools/venv/bin/python. These commands reuse the saved WAV
and do not call Hugging Face or render any remaining full-film scenes. Only if a
voice request is actually missing would voice.py use the existing free-ZeroGPU
workflow; it refuses automatic replay of an invalid/failed/inflight/stale request.
Do not regenerate the completed hook merely to re-render its graphics.

Recovery bundle contains the original completed MP4 under source/, encoded hook
clips, saved processed/original hook WAVs and review data. In another checkout,
point source.json's actual_path to that restored source (same locked SHA-256).
Existing approved repository artwork/reference is required only for rebuilding
from source or voice validation; neither credentials nor the clone reference is
included anew. No media/cache/token is in Git. No push, merge or publication.
