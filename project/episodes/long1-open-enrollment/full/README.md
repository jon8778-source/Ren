# Ren Long 1 — complete review export

**I Auto-Renewed My Health Plan for 4 Years. Then I Did the Math.**
Planned release supplied by owner:10 November2026. Nothing published automatically.
Owner approved illustrated pilot v2, then the three current-rules wording edits.

## Deliverables

- deliverables/Ren_Long_01_Auto_Renewed_My_Health_Plan.mp4 — complete5:29 film,
  landscape1280×720/24fps H.264/AAC, no music/source sound.
- deliverables/narration.wav — complete natural-rate48k24-bit narration.
- deliverables/captions.srt — exact final text, locally aligned,150 entries.
- narration.txt/script.md — final exact production text. Original supplied scripts
  remain unchanged under ../docs/ and are historical, not the final voice source.
- shot-manifest.json / shot-list.csv — all107 shots, real frame/second timings,
  gestures and narration coverage.
- deliverables/shot-contact-sheet.jpg and shot-contact-sheets.pdf — encoded shots.
- ../assumptions.json, ../calculation-results.json — shared checked illustrative math.
- SOURCE_NOTES.md, source-checks.json, wording-approval.json — claims/editorial record.
- manifest.json —20 original WAVs, settings/reference hashes, attempts and validation.
- validation.json / QA.md / quota-report.json — actual full-film checks and limits.
- asset-manifest.json, assets/ — approved reused props plus matching medical assets.

The approved61-second pilot is preserved unchanged in the parent deliverables/.
All17 previously completed originals were reused; only the3 edited passages were
new generation requests. No model/reference substitution, retry, speed change,
silence padding, paid usage, merge, GitHub media upload, Shorts or publication.
Raw audio and videos/caches stay out of Git. The delivery bundle preserves raw
WAVs and editable source separately for recovery in another task.

## Reproduce / resume

From repository root on an isolated task branch:

```sh
bash project/episodes/long1-open-enrollment/full/resume.sh
```

Completed originals validate/reuse without another HF generation or quota request.
For local rebuild only (no voice service calls):

```sh
python project/episodes/long1-open-enrollment/full/prepare.py
python project/episodes/long1-open-enrollment/full/render.py
python project/episodes/long1-open-enrollment/full/validate.py
```

Use REN_VOICE_PYTHON / REN_PYTHON overrides if the workspace interpreters differ.
Requires approved repository Audio/ren_reference.wav and its unchanged transcript
for fingerprint verification; no credential/reference is duplicated in the bundle.
Dependencies:ffmpeg/ffprobe; numpy, Pillow, scipy, soundfile, pocketsphinx,
gradio_client/huggingface_hub via the existing repository workflow. No automatic
model or new voice-service download/substitution. Upstream Space revision is pinned.

If starting from a source bundle without cached opening clips, recreate the
parent pilot locally first (same saved originals and actual v3 renderer):

```sh
mkdir -p project/episodes/long1-open-enrollment/deliverables
python project/episodes/long1-open-enrollment/prepare.py
python project/episodes/long1-open-enrollment/render.py
```

The v3 artwork chunks restore exact checksummed office/art originals automatically.
Full-film renderer reuses18 approved opening clips and native-resolution Ren actor
sources. It derives all subsequent timing from the real narration. Preserve the
left presenter/right fitted-box layout; no legacy white/static character pipeline.

Check QA.md for actual review limits: no listening or physical Android test; the
short closing segment has a coarse pitch-boundary listening flag. Re-running
validate.py produces new encoded evidence and requires actual visual review before
claiming inspection. Do not reuse old pilot/available-subset results as full-film QA.
Historical pre-edit checkpoints remain clearly labelled in QA_CHECKPOINT.md and
available-* metadata; use the final files listed above for the delivered movie.
