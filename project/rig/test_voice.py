"""Voice, lip-sync track and caption timings for the 15-second rig test clip.

  .tools/venv/bin/python rig/test_voice.py

Ren's usual voice (config.json: Kokoro am_michael + am_eric 50/50, speed 0.93). Each line is placed at its
slot in the brief's timing. The mouth for every video frame comes from the voice's loudness: closed when
silent, then slightly open, "O" and wide as it gets louder, held for at least 2 frames so it doesn't flicker.
Writes rig/test-clip/voice.wav + voice.mp3 + timeline.json, and copies them for Remotion.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
OUT = HERE / "test-clip"
OUT.mkdir(exist_ok=True)
SR, FPS = 24000, 30
LINES = [  # (start in seconds, text): one line per 3-second beat of the brief
    (1.75, "Hi, I'm Ren!"),
    (3.35, "These boots cost sixty dollars."),
    (6.35, "These ones cost three hundred."),
    (9.35, "So which pair is actually cheaper?"),
    (11.85, "The answer might surprise you. Follow to find out!"),
]

cfg = json.loads((PROJECT / "config.json").read_text())["voice"]
voices = PROJECT / ".tools" / "voices"
style = sum(np.fromfile(voices / f"{n}.bin", dtype=np.float32).reshape(-1, 1, 256) * w for n, w in cfg["blend"].items())
np.savez(OUT / ".voice.npz", voice=style)
tts = Kokoro(str(PROJECT / ".tools" / "kokoro-q8.onnx"), str(OUT / ".voice.npz"))

clips = []
for start, text in LINES:
    a, _ = tts.create(text, voice="voice", speed=cfg["speed"], lang="en-us")
    idx = np.where(np.abs(a) > 0.01)[0]
    clips.append((start, text, a[max(0, idx[0] - int(0.01 * SR)): idx[-1] + int(0.08 * SR)].astype(np.float32)))

end = max(s + len(a) / SR for s, _, a in clips)
duration = max(15.0, round(end + 0.6, 2))
track = np.zeros(int(duration * SR), dtype=np.float32)
captions = []
for start, text, a in clips:
    i = int(start * SR)
    track[i:i + len(a)] += a
    captions.append({"text": text, "start": start, "end": round(start + len(a) / SR, 3)})
sf.write(OUT / "voice.wav", track, SR)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(OUT / "voice.wav"), "-af", f"highpass=f=70,loudnorm=I={cfg['target_lufs']}:TP=-1.5:LRA=9",
                "-ar", "48000", "-b:a", "192k", str(OUT / "voice.mp3")], check=True)

# Loudness per video frame -> mouth shape
n = int(duration * FPS)
hop = SR // FPS
rms = np.array([np.sqrt(np.mean(track[f * hop:(f + 1) * hop] ** 2)) for f in range(n)])
rms = np.convolve(rms, [0.25, 0.5, 0.25], mode="same")
peak = np.percentile(rms[rms > 0.005], 95) if (rms > 0.005).any() else 1
level = rms / peak
mouth = np.where(level < 0.12, "closed", np.where(level < 0.42, "open", np.where(level < 0.75, "o", "wide"))).tolist()
for f in range(1, n - 1):  # no single-frame flicker
    if mouth[f] != mouth[f - 1] and mouth[f] != mouth[f + 1]:
        mouth[f] = mouth[f - 1]
speaking = [any(c["start"] - 0.05 <= f / FPS <= c["end"] + 0.05 for c in captions) for f in range(n)]

timeline = {"fps": FPS, "duration": duration, "captions": captions, "mouth": mouth, "speaking": speaking,
            "level": [round(float(x), 3) for x in level]}
(OUT / "timeline.json").write_text(json.dumps(timeline) + "\n")
pub = PROJECT / "remotion" / "public" / "rig" / "test"
pub.mkdir(parents=True, exist_ok=True)
shutil.copy(OUT / "voice.mp3", pub / "voice.mp3")
shutil.copy(OUT / "timeline.json", PROJECT / "remotion" / "src" / "rig" / "test-timeline.json")
for c in captions:
    print(f"{c['start']:5.2f}-{c['end']:5.2f}  {c['text']}")
print("duration", duration, "mouth frames:", {m: mouth.count(m) for m in set(mouth)})
