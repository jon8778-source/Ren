"""Narrate the 15s short in Ren's cloned voice (Qwen3-TTS 1.7B Base, local CPU), one WAV per sentence.

  project/.tools/qwen-venv/bin/python videos/job_match_short/gen_voice.py

Same model, reference WAV, exact transcript and fixed seeds as project/cliplib/qwen_local_voice.py.
Numbers are written as spoken ("twenty-five") so the model reads them naturally.
"""
import json, sys, time
from pathlib import Path
import numpy as np, soundfile as sf, torch
from qwen_tts import Qwen3TTSModel

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "voice"
LINES = [
    ("L1", "At twenty-five, my job matched up to four percent."),
    ("L2", "I put in two, because my car lease felt urgent."),
    ("L3", "That's about eight hundred eighty dollars a year of free money, gone."),
    ("L4", "Check your match tonight."),
    ("L5", "It takes ninety seconds."),
    ("L6", "Story Friday."),
]

def trim(a, sr):
    idx = np.where(np.abs(a) > 0.01)[0]
    return a[max(0, idx[0] - int(0.01 * sr)): idx[-1] + int(0.08 * sr)] if len(idx) else a

seed = int(sys.argv[1]) if len(sys.argv) > 1 else 1234
OUT.mkdir(exist_ok=True)
t0 = time.monotonic()
m = Qwen3TTSModel.from_pretrained("Qwen/Qwen3-TTS-12Hz-1.7B-Base", device_map="cpu", dtype=torch.float32, attn_implementation="sdpa")
ref = (ROOT / "Audio/ren_reference.txt").read_text().strip().strip('"“”').strip()
p = m.create_voice_clone_prompt(ref_audio=str(ROOT / "Audio/ren_reference.wav"), ref_text=ref, x_vector_only_mode=False)
info = {}
for k, (lid, text) in enumerate(LINES, 1):
    torch.manual_seed(seed + k)
    t1 = time.monotonic()
    w, sr = m.generate_voice_clone(text=text, language="English", voice_clone_prompt=p, max_new_tokens=512)
    a = trim(np.asarray(w[0], dtype=np.float32), sr)
    sf.write(OUT / f"{lid}.wav", a, sr)
    info[lid] = {"text": text, "dur": round(len(a) / sr, 3), "gen_s": round(time.monotonic() - t1, 1)}
    print(lid, info[lid], flush=True)
(OUT / "lines.json").write_text(json.dumps(info, indent=1))
print("done", round(time.monotonic() - t0), "s")
