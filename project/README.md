# Ren explainer pipeline (16:9, long form)

Repeatable pipeline for animated personal-finance explainers narrated by Ren.
First episode: `episodes/same-1200-surprise/` ("Life at Every Income Level: The Same $1,200 Surprise").
Built: the 60-second pilot and the full video (about 5:45).

## Folders
- `config.json`: frame size, safe zones, font sizes, colours, voice settings, QC limits.
- `characters/`: locked character sheets (transparent PNGs) and `manifest.json` with each file's hash.
  Ren (guide), Sam (L1), Nina (L2), Claire (L3), Marcus (L4), Richard (L5). Poses: neutral, happy, shocked,
  thinking, worried (Ren has his eight).
- `episodes/<id>/`: `assumptions.csv` → `assumptions.json/.md`, `script.md`, `scenes.json`, `description.txt`,
  `audio/` (voice + timings), `reports/` (quality checks), `renders/` and `build/` (generated, not committed).
- `pipeline/`: one script per stage. `remotion/`: the scene templates that render `scenes.json`.

## Stages
| # | Stage | Command | Output |
|---|---|---|---|
| 1 | Plan / numbers | `python3 pipeline/calc.py episodes/<id>` | assumptions.json + .md; exits 1 on any maths mismatch |
| 2 | Script | edit `script.md` (numbers written as spoken, each line tagged with the table values it says) | |
| 3 | Scene list | edit `scenes.json` (layout, character + pose, graphic, beats; numbers only as `{refs}`) | |
| 4 | Assets | `python pipeline/cutout.py SRC.png characters/<id>/<pose>.png`, then update `manifest.json` | |
| 5 | Voiceover | `python pipeline/voice.py episodes/<id> --model kokoro-q8.onnx --voices package/voices` | audio/voice.mp3, chunks < 60s, timings.json |
| 6 | Assembly | `python3 pipeline/assemble.py episodes/<id> --out renders/pilot.mp4 [--browser-executable PATH]` | Remotion render + FFmpeg finish |
| 8 | Thumbnails | `python3 pipeline/thumbnails.py episodes/<id> [--browser-executable PATH]` | renders/thumbnail-a/b/c.png (1280x720) |
| 7 | Quality check | `python pipeline/qc.py episodes/<id> --video renders/full.mp4 --name final` | reports/qc-final.md/.json |

Preview and scrub in Remotion Studio (after an assemble has written `build/props.json`):
`cd remotion && npx remotion studio --props=../episodes/<id>/build/props.json`

## Setup
- Node 22+, FFmpeg, then `cd remotion && npm install`.
- Python 3 with `kokoro-onnx soundfile librosa pillow scipy numpy`.
- Voice model (Kokoro-82M, Apache-2.0): `npm pack kokoro-q8-shards@1.0.0 kokoro-js@1.2.1`, extract both,
  `cat package/kokoro-q8.part{0..5}.bin > kokoro-q8.onnx` (sha256 `fbae9257…a1478`); voices are in `package/voices/`.
- Voice: Ren's voice from the shorts (`am_michael` + `am_eric` 50/50), at 0.93× for long form (about 165 words a minute).

## Rules the checks enforce
- Every spoken number matches the assumptions table; every on-screen number comes from it; maths recalculates.
- Every story claim ("Richard's leaks are bigger than Sam's paycheck") is a line in `claims.txt`, checked against the table.
- Characters hold still apart from their entrance and a small pop on pose changes (no bob or sway).
- Real statistics need `[VERIFY]` and a source, or get cut. Money graphics carry an "Example figures" tag.
- Nothing drawn in the bottom 12% of the frame (YouTube controls); text 40px or larger, captions 50px.
- A new visual at least every 7 seconds; no silence over 1 second; captions within 0.25s of their speech.
- "Educational only, not financial advice" on screen at the start and end, and in the description.
