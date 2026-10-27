"""Generate a shot list's voice lines with Ren's cloned voice on the Qwen/Qwen3-TTS Space.

  .tools/venv/bin/python cliplib/qwen_voice.py cliplib/shots/<name>.json [--out ../voice/lines]

Calls the Space's Voice Clone (Base) endpoint, /generate_voice_clone, with the 1.7B model and the
same reference (Audio/ren_reference.wav + Audio/ren_reference.txt) for every line, and saves one
WAV per shot as line_01.wav, line_02.wav, ... for render_shots.py --voice-dir. If the environment
has HF_TOKEN set, it is passed to the Space (it is never written anywhere). Any error from the
Space, including quota or rate limits, stops the run: there is no fallback voice.
"""
import argparse
import json
import math
import os
import shutil
import subprocess
import time
from pathlib import Path

from gradio_client import Client, handle_file

PROJECT = Path(__file__).resolve().parent.parent
REF = PROJECT.parent / "Audio"
SPACE = "Qwen/Qwen3-TTS"
COFFEE_TEST_TEXT = "What if your coffee is worth keeping?"
COFFEE_TEST_MAX_SECONDS = 10.0


def validate_generated_duration(text, audio):
    """Reject malformed/overlong test output before accepting or converting it."""
    duration = float(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "csv=p=0", str(audio),
    ]))
    if not math.isfinite(duration) or duration <= 0:
        raise ValueError("generated audio has an invalid duration")
    if text.strip() == COFFEE_TEST_TEXT and duration > COFFEE_TEST_MAX_SECONDS:
        raise ValueError(
            f"generation failed: coffee test returned {duration:.3f}s; "
            f"maximum is {COFFEE_TEST_MAX_SECONDS:g}s. "
            "Output rejected; do not trim it or retry automatically."
        )
    return duration


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("shots")
    ap.add_argument("--out", default=str(PROJECT.parent / "voice" / "lines"))
    ap.add_argument("--only", type=int, nargs="*", help="Line numbers to (re)generate, 1-based")
    ap.add_argument("--xvector-only", action="store_true", help="Use speaker embedding only for voice cloning")
    args = ap.parse_args()
    shots = json.loads(Path(args.shots).read_text())["shots"]
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    # The transcript file opens with a stray quote mark; strip quotes only, keep every word as written
    ref_text = (REF / "ren_reference.txt").read_text().strip().strip('"“”').strip()
    try:
        client = Client(SPACE, token=os.environ.get("HF_TOKEN") or None, verbose=False)
    except Exception as e:
        raise SystemExit(f"Cannot connect to {SPACE}: {type(e).__name__}: {e}") from e

    for k, shot in enumerate(shots, 1):
        if args.only and k not in args.only:
            continue
        text = shot.get("voice", "").strip()
        if not text:
            continue
        t0 = time.monotonic()
        try:
            audio, status = client.predict(
                ref_audio=handle_file(str(REF / "ren_reference.wav")),
                ref_text=ref_text,
                target_text=text,
                language="English",
                use_xvector_only=args.xvector_only,
                model_size="1.7B",
                api_name="/generate_voice_clone",
            )
        except Exception as e:  # quota, rate limit, Space asleep or down: stop, never fall back
            raise SystemExit(f"line {k}: the Space failed: {type(e).__name__}: {e}")
        took = time.monotonic() - t0  # elapsed queue + generation + transfer, not billed GPU-seconds
        if not audio or status.startswith("Error"):
            raise SystemExit(f"line {k}: {status}")
        try:
            dur = validate_generated_duration(text, audio)
        except ValueError as e:
            rejected = out / f"rejected_line_{k:02d}{Path(audio).suffix}"
            shutil.copyfile(audio, rejected)
            raise SystemExit(f"line {k}: {e} Original preserved at {rejected}") from e
        path = out / f"line_{k:02d}.wav"
        if Path(audio).suffix.lower() == ".wav":
            shutil.copyfile(audio, path)
        else:
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", audio, str(path)], check=True)
        print(f"{path.name}: {dur:.2f}s of audio in {took:.1f}s  {text}  ({status})")


if __name__ == "__main__":
    main()
