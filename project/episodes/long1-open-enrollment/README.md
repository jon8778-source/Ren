# Long 1 — Open Enrollment: pilot checkpoint

Title: I Auto-Renewed My Health Plan for 4 Years. Then I Did the Math.
Planned publication date supplied by owner: 10 November 2026. Nothing published.

**STOP for explicit owner pilot approval.** This is the continuous opening pilot,
not the full episode. The supplied ZIP's revised candidate is the voice source;
the original pasted narration and supplied documents are preserved in docs/.
Material cost/HSA corrections are recorded in SOURCE_VERIFICATION_STATUS.md.
No later narration, thumbnail production or Shorts have been generated.

## Output

Ren_Long_01_Open_Enrollment_60s_Pilot.mp4: 61.041667s, landscape 1280×720,
24fps, H.264/AAC. Narration: 61.0275s. No speech retiming, music, source audio
or silence padding. The final 14ms is video-frame quantisation only.
Three raw Qwen originals are saved in audio/ with settings/hashes in manifest.json.
The episode reuses the actual v3 office, Fredoka and native-resolution Ren clips.
All scene/interface props are code-drawn. Supplied scene PNGs are concepts only.

## Reproduce from this repository

Requires Python 3, ffmpeg/ffprobe, numpy, Pillow, scipy, soundfile,
pocketsphinx 5.0.4, gradio_client and huggingface_hub. Renderer reuses the approved
project/prototypes/coffee-minute-v3 modules/artwork chunks, Fredoka font and
assets/ren_library/ren_thinking.mp4 and ren_nod_yes.mp4. Do not replace those.
From repository root, with the dependencies installed:

```sh
python project/episodes/long1-open-enrollment/calculations.py
mkdir -p project/episodes/long1-open-enrollment/deliverables
python project/episodes/long1-open-enrollment/prepare.py
python project/episodes/long1-open-enrollment/render.py
python project/episodes/long1-open-enrollment/validate.py
```

These commands reuse saved original WAVs and do not contact Hugging Face.
The source bundle includes the required render assets and original WAVs.
Approved voice reference and reference transcript remain in the repository's
Audio/; they are not duplicated in this delivery bundle.

Voice checkpoint verification (all originals are already complete):

```sh
python project/episodes/long1-open-enrollment/voice.py
```

This validates fingerprints/settings/hashes and returns without generation when
all segments are complete. Do not delete/reject segments or extend segments.json
before the pilot is approved. Missing/rejected generation requires configured
HF_TOKEN, the unchanged approved reference and free ZeroGPU allowance; no token
is included. There is no automatic retry or paid fallback.

## Review / remaining work

See QA.md, validation.json, asset-manifest.json and shot-manifest.json.
The full candidate is planned but not produced. Later 2027 statistics, HSA limits
and Marketplace deadlines await primary-source verification; none is in pilot.
Full-episode voice, scenes and publication are not authorised by pilot completion.
This is a local branch checkpoint with a downloadable source bundle; no remote
publication, main changes or GitHub media upload is claimed.
