"""Generate a short's voiceover locally with the Kokoro-82M TTS model.

Each line is "START_SECONDS|text"; it is placed START_SECONDS + LEAD into the track.

  python scripts/voiceover.py --model kokoro-q8.onnx --voices node_modules/kokoro-js/voices \
      --duration 15 --out public/monthly-vs-yearly.mp3 \
      "0|That's what a nine ninety-nine subscription really costs!" \
      "3.6|It doesn't feel like much. Until you stack it."

Setup (see README): pip install kokoro-onnx soundfile; ffmpeg on PATH.
"""

import argparse
import subprocess
import tempfile
from pathlib import Path

import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

LEAD = 0.2  # seconds of breathing room after each scene cut

p = argparse.ArgumentParser()
p.add_argument("--model", required=True, help="Kokoro ONNX model file")
p.add_argument("--voices", required=True, help="Folder of kokoro-js voice .bin files")
p.add_argument("--voice", default="am_michael:0.5,am_eric:0.5",
               help='One voice ("am_puck") or a weighted blend ("am_michael:0.5,am_eric:0.5")')
p.add_argument("--speed", type=float, default=1.18)
p.add_argument("--duration", type=float, required=True, help="Video length in seconds")
p.add_argument("--out", required=True, help="Output .mp3")
p.add_argument("lines", nargs="+", help='"START_SECONDS|text"')
args = p.parse_args()

with tempfile.TemporaryDirectory() as tmp:
    # kokoro-js voices are raw float32 style vectors; kokoro-onnx reads them from an .npz
    # A blend is the weighted average of the voices' style vectors.
    style = 0
    for part in args.voice.split(","):
        name, _, weight = part.partition(":")
        vec = np.fromfile(Path(args.voices) / f"{name}.bin", dtype=np.float32).reshape(-1, 1, 256)
        style = style + vec * float(weight or 1)
    npz = Path(tmp) / "voices.npz"
    np.savez(npz, voice=style)
    tts = Kokoro(args.model, str(npz))

    sr = 24000
    track = np.zeros(int(args.duration * sr), dtype=np.float32)
    for line in args.lines:
        start, text = line.split("|", 1)
        audio, sr = tts.create(text, voice="voice", speed=args.speed, lang="en-us")
        at = int((float(start) + LEAD) * sr)
        end = at + len(audio)
        if end > len(track):
            raise SystemExit(f"Line runs past the end of the video ({end / sr:.2f}s): {text}")
        track[at:end] += audio
        print(f"{float(start) + LEAD:5.2f}s - {end / sr:5.2f}s  {text}")

    wav = Path(tmp) / "vo.wav"
    sf.write(wav, track, sr)
    # Trim rumble, gently compress, and normalize loudness for social platforms (-14 LUFS)
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-i", str(wav), "-af",
         "highpass=f=80,acompressor=threshold=-18dB:ratio=3:attack=5:release=80,loudnorm=I=-14:TP=-1.5:LRA=7",
         "-ar", "44100", "-b:a", "192k", args.out],
        check=True,
    )
print(f"Wrote {args.out}")
