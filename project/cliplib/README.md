# Ren hybrid animation template

This is the new prototype route requested on 27 October 2026. It combines real Ren animation clips,
brief character/story cutaways and animated infographics. The older `render_shots.py` and episode
renderer remain available for existing videos. Use this route for new animation prototypes.

## Quick start (repository root)

Requires Python 3.10+, ffmpeg and ffprobe on PATH.

```sh
python -m pip install -r project/cliplib/requirements.txt
python project/cliplib/render_hybrid.py project/cliplib/shots/hybrid_coffee.json --validate-only
python project/cliplib/render_hybrid.py project/cliplib/shots/hybrid_coffee.json --silent-preview
```

The example renders a 24.5-second 1280×720, 24fps visual pilot at
`project/cliplib/out/hybrid/video.mp4`, plus per-shot clips and a timing report.
The simple office and Max portrait are **template placeholders**, not a recreation of the approved
26 October office/Alex art. Set `background_image` to the approved office file and a story's `image`
to the appropriate approved narrative still; paths are relative to the shot-list JSON.

## Generate new words in Ren's voice

The repository already contains a reference WAV and transcript in `Audio/`. These are a reusable
voice reference. They are not trained model weights. The existing Qwen Base model supplies the TTS
engine; no separate model training is needed.

Hosted option (uses the public Qwen demo, subject to availability and quota):

```sh
python project/cliplib/qwen_voice.py project/cliplib/shots/hybrid_coffee.json --out project/cliplib/out/hybrid-voice
python project/cliplib/render_hybrid.py project/cliplib/shots/hybrid_coffee.json --voice-dir project/cliplib/out/hybrid-voice
```

Optional `HF_TOKEN` belongs in the runtime environment; never commit it. No paid compute is started
by these scripts. The public Space can sleep, change its API or run out of free quota. If it fails,
stop and report the error; never silently replace the voice with Kokoro or another speaker.

Local/self-hosted option (install separately on a suitable computer or GPU host):

```sh
python -m pip install -r project/cliplib/requirements-voice-local.txt
python project/cliplib/local_voice.py project/cliplib/shots/hybrid_coffee.json --out project/cliplib/out/hybrid-voice
python project/cliplib/render_hybrid.py project/cliplib/shots/hybrid_coffee.json --voice-dir project/cliplib/out/hybrid-voice
```

This downloads `Qwen/Qwen3-TTS-12Hz-1.7B-Base` on first run, builds a voice prompt from the same WAV
and exact transcript once, then reuses it across every line. Default device is `cuda:0`; `--device cpu`
is supported by the wrapper but performance has not been benchmarked here. This code runs on a
compute host, not inside Android or GitHub's file viewer. GitHub stores the code and reference files.
The voice description documents the intended persona; the Base cloning API uses the WAV and
transcript, not that prose description. Check the transcript exactly matches the recording.

## Editing a shot list

- `kind: "ren"`: approved clip name without `.mp4`, `duration`, optional `in_s`, `mirror`,
  `background_image`, `title`, `subtitle`, `voice`. Maximum 5.5 seconds; real clip audio is discarded.
- `kind: "story"`: `image`, `duration`, `title`, `subtitle`, `voice`. Maximum 2.5 seconds with a gentle
  image push-in. Transparent character art is fitted without chopping off the face.
- `kind: "graphic"`: `duration`, `title`, `value`, optional `prefix`, `subtitle`, `voice`. Maximum
  3.5 seconds. The number counts up and its bar fills. Values are illustrative, not sourced statistics.

Write narration in short beats. Audio must fit its shot with 0.1 seconds to spare; if it runs long,
rewrite or split the line and add another visual beat. Never speed up the voice or automatically
hold idle footage. Rendering is silent only when explicitly requested with `--silent-preview`.
Cuts are deliberate; no repeated dissolve on every beat. Aim to return to animated Ren after each
short cutaway. Art is reused, character proportions are locked, and no artificial talking motion is
added. The soft white key inherits the clip renderer's approach; inspect pale clothing and edges
against the final office background. Library notes may flag source mouth movement; choose/trim
those clips deliberately and check playback before approval.

## Verification

```sh
python -m unittest discover -s project/cliplib/tests
python -m py_compile project/cliplib/render_hybrid.py project/cliplib/local_voice.py
```

The renderer validates clip bounds against both library metadata and actual media duration, rejects
unapproved mirroring, and measures text wrapping. Inspect the pilot at mobile size and check every
scene boundary, voice pronunciation and final sound before treating it as a publishing candidate.
Existing episode QC is designed for the older renderer and is not claimed as a pass for this route.

Official API references:
- https://github.com/QwenLM/Qwen3-TTS (voice cloning and reusable voice prompts)
- https://huggingface.co/spaces/Qwen/Qwen3-TTS (hosted Voice Clone/Base demo)
