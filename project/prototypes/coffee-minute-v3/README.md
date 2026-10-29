# Approved Ren coffee prototype v3

Renderer recovered from GitHub blob `ba896a3752ba6bfbafef1eede46fffc085fdf5f8`.
Original shot design and timing are preserved. Changes add lossless artwork
unpacking and fatal FFmpeg error handling, including a complete final decode.

## Fresh checkout

Requires Python 3.12+, FFmpeg 6.1+ and ffprobe on PATH, with libx264 and AAC.
Run from repository root:

```sh
python3 -m venv project/prototypes/coffee-minute-v3/.venv
project/prototypes/coffee-minute-v3/.venv/bin/python -m pip install -r project/prototypes/coffee-minute-v3/requirements.txt
project/prototypes/coffee-minute-v3/.venv/bin/python project/prototypes/coffee-minute-v3/render.py
```

The renderer automatically restores all four approved PNGs into `assets/` and
checks their SHA-256 hashes. The original PNG bytes are stored losslessly as
base64 text chunks in `artwork/` because large binary connector uploads could
not be completed. This is packaging only: no artwork was regenerated,
compressed again, edited or substituted. `artwork/manifest.json` identifies the
approved sources and ordered chunks. To restore images without rendering:

```sh
python3 project/prototypes/coffee-minute-v3/unpack_artwork.py
```

Output: `project/prototypes/coffee-minute-v3/Ren_61s_Coffee_Prototype_v3.mp4`.
`--preview` produces `build/contact.jpg` and shot midpoints without encoding.
`revision-report.json` records shot timing, narration hash and zero voice calls.

## Approved artwork

| Restored file | Original approved source |
| --- | --- |
| assets/alex-cafe.png | Alex taps to pay for coffee.png |
| assets/alex-home.png | Alex pours French press coffee.png — corrected single mug |
| assets/supporting-cast.png | Centered Maya in illustrated character lineup.png |
| assets/office.png | Welcoming sage-accented home office.png |

The supporting cast lineup is included for reuse; this prototype uses Alex only.
All animation and audio dependencies are already tracked in this repository:
`assets/ren_library/ren_library.json`, `ren_present_palm_left.mp4`,
`ren_nod_yes.mp4`, `ren_shake_no.mp4`, `ren_thinking.mp4` in that same directory;
`project/remotion/public/fonts/fredoka-latin-600-normal.woff2`; and
`project/pilots/daily-coffee/deliverables/narration.wav`.

Only the first 61.625 seconds of existing narration are used. No voice API,
Hugging Face request, music, source animation audio, speed change or padding.
The 19 shots total 1,479 frames at 24 fps, 1280×720 H.264/AAC.
The renderer verifies each shot frame count and decodes the complete MP4 with
errors fatal. See `validation.json` for recorded verification results once run.
Follow `project/REN_VIDEO_RULES.md`. Do not merge into main without Jon's instruction.

## Verification

The fresh checkout at `bf193aee2c042651884143bec1cf1be9febc0b11` rendered
successfully with the pinned dependencies in a new venv. All 19 shot midpoints
were inspected. The final video has 1,479 frames at 24 fps, 1280×720, 61.625
seconds, H.264/AAC, and passes a complete decode with errors fatal. All 209
source calculation frames retain identical, correct equation text. All 1,479
encoded frames were compared with the approved reference: minimum SSIM
0.992776, mean 0.997893. Narration comparison covers 2,958,000 samples with
correlation 0.999970. No new voice requests. See `validation.json` for hashes
and detailed results; `revision-report.json` records all shot timings.

After rendering, rerun structural, audio and equation checks with:

```sh
project/prototypes/coffee-minute-v3/.venv/bin/python project/prototypes/coffee-minute-v3/validate.py
```

For the full frame comparison, append `--reference /absolute/path/to/approved.mp4`
using the approved Library reference (SHA-256 recorded in `validation.json`).
The reference is optional for future structural checks; it is not downloaded
or replaced by the scripts.

The output MP4 is generated locally and supplied separately in the handover.
Only source, approved artwork, dependencies, documentation and verification
reports are stored on this prototype branch. Main remains unchanged.
