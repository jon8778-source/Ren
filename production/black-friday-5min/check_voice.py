"""Transcribe the pilot narration (voice/S1.wav + S2.wav joined as generated) with faster-whisper medium.en (CPU, word timestamps); compare with the approved text; write voice/words_pilot.json.
Run with project/.tools/qwen-venv/bin/python (faster-whisper lives there)."""
import json, re, subprocess, difflib
from pathlib import Path
import numpy as np, soundfile as sf
from faster_whisper import WhisperModel
V = Path(__file__).resolve().parent / "voice"
a, sr = sf.read(V / "S1.wav", dtype="float32"); b, _ = sf.read(V / "S2.wav", dtype="float32"); sf.write(V / "pilot.wav", np.concatenate([a, b]), sr)
raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(V / "pilot.wav"), "-ac", "1", "-ar", "16000", "-f", "f32le", "-"])
m = WhisperModel("medium.en", device="cpu", compute_type="int8"); segs = list(m.transcribe(np.frombuffer(raw, np.float32), beam_size=5, condition_on_previous_text=False, word_timestamps=True)[0])
W = [dict(w=w.word.strip(), s=round(w.start, 3), e=round(w.end, 3)) for s in segs for w in s.words]; (V / "words_pilot.json").write_text(json.dumps(W, indent=1))
norm = lambda x: re.findall(r"[a-z0-9']+", x.lower().replace("-", " ")); ref = " ".join((V / "VOICE_SCRIPT.txt").read_text().split("\n\n")[:2]); r = norm(ref); h = [norm(x["w"])[0] for x in W if norm(x["w"])]
sm = difflib.SequenceMatcher(None, r, h, autojunk=False); print("words", len(r), len(h), "ratio", round(sm.ratio(), 3), "duration", round(len(a) / sr + len(b) / sr, 2))
for op, i1, i2, j1, j2 in sm.get_opcodes():
    if op != "equal": print(op, r[i1:i2], "->", h[j1:j2])
