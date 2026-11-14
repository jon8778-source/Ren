"""Transcribe voice/narration.wav (faster-whisper medium.en, CPU, word timestamps) and compare to the approved text. Writes voice/words.json and voice/beats.json (beat start/end by aligned words)."""
import json, re, difflib
import subprocess
import numpy as np
from pathlib import Path
from faster_whisper import WhisperModel
V = Path(__file__).resolve().parent / "voice"
m = WhisperModel("medium.en", device="cpu", compute_type="int8"); raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(V / "narration.wav"), "-ac", "1", "-ar", "16000", "-f", "f32le", "-"]); segs = list(m.transcribe(np.frombuffer(raw, np.float32), beam_size=5, condition_on_previous_text=False, word_timestamps=True)[0])
W = [dict(w=w.word.strip(), s=round(w.start, 3), e=round(w.end, 3)) for s in segs for w in s.words]; (V / "words.json").write_text(json.dumps(W, indent=1))
norm = lambda x: re.sub(r"[^a-z0-9' ]", "", x.lower().replace("-", " ")).split()
beats = [l for l in (V / "VOICE_SCRIPT.txt").read_text().splitlines() if l.strip()]; ref = [(i, w) for i, b in enumerate(beats) for w in norm(b)]; hyp = [norm(x["w"])[0] if norm(x["w"]) else "" for x in W]
sm = difflib.SequenceMatcher(None, [w for _, w in ref], hyp, autojunk=False); idx = {}
for a, b, n in sm.get_matching_blocks():
    for k in range(n): idx[a + k] = b + k
out = []
for i, b in enumerate(beats):
    ks = [k for k, (bi, _) in enumerate(ref) if bi == i and k in idx]; out.append(dict(beat=i + 1, text=b, start=W[idx[ks[0]]]["s"] if ks else None, end=W[idx[ks[-1]]]["e"] if ks else None, matched=len(ks), words=len(norm(b))))
(V / "beats.json").write_text(json.dumps(out, indent=1)); print("ratio", round(sm.ratio(), 3))
for o in out: print(o["beat"], o["start"], o["end"], f'{o["matched"]}/{o["words"]}', o["text"][:50])
print("heard:", " ".join(x["w"] for x in W))
