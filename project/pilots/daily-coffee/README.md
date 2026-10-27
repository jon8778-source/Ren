# Daily coffee pilot checkpoint

This is a separate hybrid pilot, never a production episode or a merge into main.
Script authorisation is in the task request. Target: 4:45–5:15 at a natural pace.
Illustrative calculations are in `assumptions.json`; no investment-return assumptions or statistics.
The saved script has stable paragraph IDs. Narration spans multiple independent visual cuts.

## Resume in this task or a fresh checkout

Use the existing checkout on `codex/ren-coffee-pilot`; each cloud task is already isolated.
Do not create a Git worktree unless explicitly requested. Restore this branch from GitHub in a
new task. No files from `/tmp`, `/workspace/ren-xvector-review` or the former task's live processes
are needed once the initial checkpoint has been saved. The imported diagnostic WAV and safe
provenance metadata are included here; no tokens are stored.

From the repository root, prepare the interpreter if necessary:

```sh
python3 -m venv /workspace/ren-pilot-venv
/workspace/ren-pilot-venv/bin/pip install --no-cache-dir -r project/pilots/daily-coffee/requirements.txt
```

`ffmpeg`, `ffprobe`, HTTPS Git proxy access and a working `HF_TOKEN` runtime binding are required.
Use that interpreter for the commands below (or activate it). The original onboarding interpreter
`/workspace/ren-voice-test-venv/bin/python` also works while it exists.

```sh
python project/cliplib/pilot.py status
python project/cliplib/pilot.py resume --publish-checkpoints
python project/cliplib/pilot.py verify
python project/cliplib/pilot.py assemble
```

Exact resume command, after activating the venv:
`python project/cliplib/pilot.py resume --publish-checkpoints`

Only `resume` can generate speech. It selects only missing/pending or explicitly rejected segments;
completed originals are hash-checked and reused. There is no automatic voice retry or fallback.
Quota is checked before each request. The conservative budget is 120 free GPU-seconds per next
request, for the demo's 60-second GPU allocation; unused quota is left for the next session.
If quota is insufficient, no request is submitted. Reset times, observed quota changes and elapsed
request times are recorded separately. There is no paid hardware or endpoint API in this workflow.
If quota cannot be read, Space hardware is not ZeroGPU, or a request fails, generation stops.

`--publish-checkpoints` commits and pushes only this pilot directory to `codex/ren-coffee-pilot`.
It never merges or pushes main. It saves an inflight intent before requesting speech, then saves each
original/result immediately. If an interruption leaves `inflight`, it never replays the unknown
request: recover any already-returned original and validate it first, or explicitly reject it after
investigation. A failed durable push is a blocker to further requests, not permission to keep spending.
Never commit environment dumps, token values, login files, Gradio caches or model downloads.
Processed tracks and render caches are ignored; original WAVs, script, manifests and reports are durable.

## Validation and explicit review

The model/reference/transcript hashes and settings are saved before generation. The selected
configuration is the duration-passing 2.457-second diagnostic: Qwen 1.7B Base, English,
`use_xvector_only=True`, reference recording unchanged, no other generation parameter changes.
That test did not establish pronunciation, British accent or speaker identity by itself.

Original WAVs are never trimmed or normalised. Technical checks reject corrupt, silent, clipped,
runaway, implausibly fast/slow output or long unexpected internal gaps. The original coffee sentence
retains its 10-second guard. Paragraph duration bounds scale with word count. Rejected original
bytes and error details are retained for investigation. Changing text/settings/reference hashes marks
audio stale; it cannot be silently reused or regenerated.

For explicit rejection/revision, preserving the previous history and original:

```sh
python project/cliplib/pilot.py reject --segments s002 --reason "Owner rejected incorrect words" --publish-checkpoints
python project/cliplib/pilot.py resume --publish-checkpoints
```

No ASR service is called. If `faster-whisper` and an appropriate local model are already available,
run `verify --asr-model /absolute/local/model/directory` for CPU transcription and word-error checks.
Otherwise all segments are marked for owner listening review. Do not describe words/voice as approved
until they have been checked. Acoustic pitch comparison flags possible discontinuities, but does
not establish voice identity. Listen across every adjacent segment boundary.

```sh
python project/cliplib/pilot.py approve --segments s001 --reason "Owner listened: words and Ren voice correct" --publish-checkpoints
```

Only use `approve` after an actual owner confirmation. An ASR mismatch blocks assembly until reviewed.
Edge-only excessive silence is removed from derived files, retaining room tone; internal pauses
are preserved. FFmpeg performs proper resampling and two-pass level matching with headroom.
There are no speed changes, inserted inter-paragraph gaps or duration padding.

## Visuals and final delivery

`assemble` refuses an incomplete narration or a natural duration outside 285–315 seconds. If duration
is outside target, revise meaningful script content and explicitly reject only the affected segments;
never stretch narration or pad silence. The continuous narration track is independent of visual cuts.
Visuals use approved animated Ren clips, brief existing character cutaways and moving infographics.
Source clip audio is discarded; no music. The bundled office and narrative stills are template
placeholders, not the approved office/Alex artwork. All figures are labelled illustrative.

The full video is `renders/video.mp4`; complete narration is `build/narration.wav`.
One midpoint frame per shot is exported to `build/review-frames/` for visual inspection. The brief
`quality-report.json` lists review gaps honestly; legacy episode QC is not a pass for this renderer.
Incomplete work produces `checkpoint-report.json`, not a partial video labelled finished.
Full narration, video and derived processing can be rebuilt from the committed originals.
