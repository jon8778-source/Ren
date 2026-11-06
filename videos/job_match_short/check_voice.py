"""Whisper-check each line against the script and write word_times.json (used to sync captions/graphics).

  project/.tools/qwen-venv/bin/python videos/job_match_short/check_voice.py
"""
import difflib, json, re, subprocess
from pathlib import Path
import numpy as np
from faster_whisper import WhisperModel

V = Path(__file__).resolve().parent / "voice"
NUM = {"25": "twenty five", "4": "four", "2": "two", "880": "eight hundred eighty", "90": "ninety"}

def norm(t):
    t = t.lower().replace("’", "'").replace("-", " ")
    return [w for w in re.findall(r"[a-z0-9']+", t) if w != "and"]

info = json.loads((V / "lines.json").read_text())
m = WhisperModel("medium.en", device="cpu", compute_type="int8")
wt, bad = {}, 0
for lid, v in info.items():
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(V / f"{lid}.wav"), "-ac", "1", "-ar", "16000", "-f", "f32le", "-"])
    segs = list(m.transcribe(np.frombuffer(raw, np.float32), beam_size=5, condition_on_previous_text=False, word_timestamps=True)[0])
    heard = " ".join(s.text.strip() for s in segs)
    wt[lid] = [{"word": w.word.strip(), "start": round(w.start, 3), "end": round(w.end, 3)} for s in segs for w in s.words]
    ok = norm(heard) == norm(v["text"])
    bad += not ok
    print("ok  " if ok else "DIFF", lid, v["dur"], "s | heard:", heard)
(V / "word_times.json").write_text(json.dumps(wt, indent=1))
print("all lines match" if not bad else f"{bad} line(s) differ")
