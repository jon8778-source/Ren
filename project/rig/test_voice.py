"""Voice, lip-sync track and caption timings for the 15-second rig test clip.

  .tools/venv/bin/python rig/test_voice.py

Ren's usual voice (config.json: Kokoro am_michael + am_eric 50/50, speed 0.93). Each line is placed at its
slot in the brief's timing. Mouth shapes come from Rhubarb Lip Sync (phoneme-based; install it with
rig/setup_rhubarb.sh), run on each line with its text, then mapped to Ren's mouths (MOUTH_FOR) and evened out
so every mouth is held for at least MIN_HOLD frames. "rest" marks frames with no speech; the clip picks the
resting mouth (closed, smile or wince) for those.
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

# Rhubarb shapes (https://github.com/DanielSWolf/rhubarb-lip-sync#mouth-shapes) -> Ren's mouths.
# Only D (wide open, as in "father") uses the wide mouth.
MOUTH_FOR = {"A": "closed",  # M, B, P: lips pressed
             "B": "open",    # most consonants, "ee": slightly open
             "C": "open",    # "eh", "ae": open
             "D": "wide",    # "aa": wide open
             "E": "o",       # "ao", "er": slightly rounded
             "F": "o",       # "uw", "ow", "w": puckered
             "G": "open",    # F, V
             "H": "open",    # L
             "X": "rest"}    # silence
MIN_HOLD = 3
RHUBARB = PROJECT / ".tools" / "rhubarb" / "rhubarb"
n = int(round(duration * FPS))
shape = ["X"] * n
for i, (start, text, a) in enumerate(clips):
    wav, dlg, js = OUT / f".line{i}.wav", OUT / f".line{i}.txt", OUT / f".line{i}.json"
    sf.write(wav, a, SR)
    dlg.write_text(text + "\n")
    subprocess.run([str(RHUBARB), "-q", "-f", "json", "-d", str(dlg), "-o", str(js), str(wav)], check=True)
    for cue in json.loads(js.read_text())["mouthCues"]:
        f0, f1 = round((start + cue["start"]) * FPS), round((start + cue["end"]) * FPS)
        for f in range(max(0, f0), min(n, f1)):
            shape[f] = cue["value"]
    for f_ in (wav, dlg, js):
        f_.unlink()
mouth = [MOUTH_FOR[x] for x in shape]


def runs(seq):
    out, i = [], 0
    while i < len(seq):
        j = i
        while j < len(seq) and seq[j] == seq[i]:
            j += 1
        out.append([seq[i], j - i])
        i = j
    return out


# Even out: a run shorter than MIN_HOLD first borrows frames from a neighbour that can spare them (so a short
# closed-lip "m" still shows), otherwise it is absorbed into its longer neighbour.
r = runs(mouth)
changed = True
while changed:
    changed = False
    for i, (m, k) in enumerate(r):
        if k >= MIN_HOLD:
            continue
        need = MIN_HOLD - k
        nb = sorted([j for j in (i - 1, i + 1) if 0 <= j < len(r)], key=lambda j: -r[j][1])
        donor = next((j for j in nb if r[j][1] - need >= MIN_HOLD), None)
        if donor is not None:
            r[donor][1] -= need
            r[i][1] += need
        elif nb:
            r[nb[0]][1] += k
            del r[i]
        changed = True
        break
    # merge equal neighbours created by absorption
    merged = []
    for m, k in r:
        if merged and merged[-1][0] == m:
            merged[-1][1] += k
        else:
            merged.append([m, k])
    r = merged
mouth = [m for m, k in r for _ in range(k)]
assert len(mouth) == n and min(k for _, k in runs(mouth)) >= MIN_HOLD
speaking = [any(c["start"] - 0.05 <= f / FPS <= c["end"] + 0.05 for c in captions) for f in range(n)]

timeline = {"fps": FPS, "duration": duration, "captions": captions, "mouth": mouth, "speaking": speaking, "rhubarb": "".join(shape)}
(OUT / "timeline.json").write_text(json.dumps(timeline) + "\n")
pub = PROJECT / "remotion" / "public" / "rig" / "test"
pub.mkdir(parents=True, exist_ok=True)
shutil.copy(OUT / "voice.mp3", pub / "voice.mp3")
shutil.copy(OUT / "timeline.json", PROJECT / "remotion" / "src" / "rig" / "test-timeline.json")
for c in captions:
    print(f"{c['start']:5.2f}-{c['end']:5.2f}  {c['text']}")
sp = [m for m, s_ in zip(mouth, speaking) if s_]
print("duration", duration, "mouth frames while speaking:", {m: sp.count(m) for m in sorted(set(sp))},
      "shortest hold:", min(k for _, k in runs(mouth)), "changes/s while speaking:",
      round(sum(1 for f in range(1, n) if speaking[f] and mouth[f] != mouth[f - 1]) / (sum(speaking) / FPS), 2))
