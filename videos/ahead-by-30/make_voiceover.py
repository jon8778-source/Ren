"""Generate this video's voiceover sentence by sentence and write the sentence timings.

  python make_voiceover.py --model kokoro-q8.onnx --voices package/voices

Writes assets/voiceover.mp3 and assets/voiceover-timings.json (setup: see the root README).
"""
import argparse, json, subprocess, tempfile
from pathlib import Path

import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro

ap = argparse.ArgumentParser()
ap.add_argument("--model", required=True)
ap.add_argument("--voices", required=True, help="Folder of kokoro-js voice .bin files")
args = ap.parse_args()
HERE = Path(__file__).parent
tmp = Path(tempfile.mkdtemp())
names = {"am_michael": .5, "am_eric": .5}
style = sum(np.fromfile(Path(args.voices) / f"{n}.bin", dtype=np.float32).reshape(-1, 1, 256) * w for n, w in names.items())
np.savez(tmp / "v.npz", voice=style)
k = Kokoro(args.model, str(tmp / "v.npz"))

BLOCKS = [
 (0, ["Want to be financially ahead by thirty?", "Start by finding where your money leaks.",
      "Step one: run a money leak audit.", "Go through your last three months of bank statements."]),
 (15, ["Circle every subscription, fee and impulse buy you forgot about.", "My free money leak audit workbook walks you through it.",
       "Step two: build a starter emergency fund.", "Start with one month of bills, then build to three."]),
 (30, ["Step three: pay off high-interest debt, like credit cards, before you invest.", "That interest works against you.",
       "Step four: pay yourself first.", "Set up an automatic transfer on payday, even a small amount."]),
 (45, ["Why bother?", "A thousand dollars at seven percent could grow to over seven thousand dollars in thirty years.", "Example only.",
       "Step five: review monthly.", "Small fixes beat big plans.", "Grab the free money leak audit workbook.", "Link in bio."]),
]
SR, GAP, LEAD, SPEED, BLOCK_GAP = 24000, 0.28, 0.15, 1.18, 0.35
track = np.zeros(SR * 60, dtype=np.float32); out = []; cur = 0
for start, lines in BLOCKS:
    cur = LEAD if start == 0 else cur + BLOCK_GAP
    for t in lines:
        a, _ = k.create(t, voice="voice", speed=SPEED, lang="en-us")
        # trim leading/trailing near-silence so gaps are controlled
        idx = np.where(np.abs(a) > 0.01)[0]; a = a[max(0, idx[0] - 240): idx[-1] + 480]
        i = int(cur * SR); track[i:i + len(a)] += a
        out.append({"block": start, "text": t, "start": round(cur, 2), "end": round(cur + len(a) / SR, 2)})
        cur += len(a) / SR + GAP
    print(f"block {start}: ends {cur - GAP:.2f}s")
sf.write(tmp / "vo.wav", track, SR)
json.dump(out, open(HERE / "assets/voiceover-timings.json", "w"), indent=1)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tmp / "vo.wav"), "-t", "49", "-af",
                "highpass=f=80,acompressor=threshold=-18dB:ratio=3:attack=5:release=80,loudnorm=I=-14:TP=-1.5:LRA=7",
                "-ar", "44100", "-b:a", "192k", str(HERE / "assets/voiceover.mp3")], check=True)
for o in out: print(f"{o['start']:6.2f}-{o['end']:6.2f} {o['text']}")
