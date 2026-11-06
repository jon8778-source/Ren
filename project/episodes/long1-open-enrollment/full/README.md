# Full Long 1 — resumable production

Jon explicitly approved illustrated-prop pilot revision 2 on 6 November 2026.
Full production continues here; the pilot and original assets/files remain intact
in the parent directory. No Shorts, merge, GitHub media upload or publication.

## Current checkpoint

17 of 20 original narration WAVs are saved. Three are reused byte-identically
from the approved pilot, and 14 are new single-request Qwen generations. All raw
originals pass duration/silence/corruption checks; normalization/edge trimming is
restricted to derived files. Reference/model/settings match the approved pilot.
No paid fallback, retries, tempo changes, time stretch or silence padding.

Remaining source-gated IDs: **s005, s014, s017**. They contain the 2027 employer
cost forecast, HSA limit and Marketplace deadlines respectively. No generation
request has been submitted for these three. Live primary sources remain blocked
by the enforced cloud policy. A narrow network draft was saved; it is not active
until the owner reviews/saves and publishes the environment configuration.

Full script is fixed in script.md and segments.json; per-segment text/settings/
reference hashes, attempts, original paths, acoustic checks and quota are in
manifest.json. source-checks.json is deliberately unverified. Proposed neutral
replacements await an explicit owner answer; see PROPOSED_SOURCE_SAFE_REPLACEMENTS.md.
Do not infer approval from elapsed time or render/generation completion.

## Resume

From repository root, after source claims are checked and the source record
updated (or explicitly authorised replacements applied consistently):

```sh
bash project/episodes/long1-open-enrollment/full/resume.sh
```

The launcher validates completed WAVs and fingerprints, skips source-held text,
refuses replay of an inflight/failed/invalid/stale request and uses only free
ZeroGPU. It stops at quota limits with exact remaining IDs/reset in the report.
Only when all audio/source gates pass does it assemble narration, derive actual
shot timings, render, and validate the full video. No partial movie is assembled
with silent placeholders. Re-running source files does not mean the blockers
have been resolved. Never mark a source `verified` without retained evidence.

Interpreter overrides: REN_VOICE_PYTHON for HF/Gradio, REN_PYTHON for rendering.
Default current workspace interpreters are used if available; otherwise python.
Dependencies: existing approved v3 renderer/assets/fonts/native Ren clips plus
numpy, Pillow, scipy, soundfile, pocketsphinx, gradio_client, huggingface_hub and
ffmpeg/ffprobe. No credential or approved cloning reference is bundled anew.

## Independent work while source checks are blocked

```sh
python project/episodes/long1-open-enrollment/full/prepare.py --available
python project/episodes/long1-open-enrollment/full/visuals.py
python project/episodes/long1-open-enrollment/full/render.py --available
```

These commands validate/normalize/align completed segments, draw reusable scene
boards and encode independent complete-segment clips. No partial/full movie or
master narration is assembled. `available-timing.json` and
`available-shot-manifest.json` contain subset coordinates, NOT final episode
timestamps; source-held passages are absent. Final preparation assigns the real
continuous timeline after the missing text is resolved/generated.

All critical labels/amounts/equations derive from the parent's shared assumptions
and calculation module. Generated car/phone/key and medical props have blank
labels; all finance figures/UI text are rendered in code. No new character
portraits were invented. Dev/Priya and other supporting dialogue use offscreen
messages/props rather than unrelated artwork. Ren remains native decoded/matted,
left full-body with fitted right panels, mouth closed, no mirroring/zoom changes.

The renderer extends the approved implementation and reuses the 18 approved
opening video-only clips. Source animation sound is discarded. Final output
will be landscape 1280×720, 24fps H.264/AAC, matching approved source fidelity.
The natural narration runtime is measured; no padding to force six minutes.

## Quality limits

Full-film decode, final timestamps and final audio/visual continuity cannot pass
until missing narration is available. Local forced alignment is not independent
transcription/listening. New audio requires listening review. The simple acoustic
check flags the boundary s019→s020 for attention (not an automatic identity failure
or authorisation to regenerate); unchanged reference/model/settings are verified.
Physical Android playback is untested. Do not call this a finished video.

Raw WAVs, derived audio, renders and caches stay out of Git. A downloadable
checkpoint bundle must include the original WAVs so a fresh task can recover
without new generation. Keep tokens only in configured secrets/environment.

Before source-held passages are released, update their scene graphics from the
verified evidence as well. The forecast board currently reads “Source check
required” and is intentionally not among the encoded available clips. It must
never be exported as a finished scene. Keep the exact checked numeric value/year
and source in a shared evidence record before drawing any sourced percentage.
