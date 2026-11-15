"""Synthesise the Short's two NEW lines (owner-approved wording, 15 Nov 2026) with the approved British Qwen clone (Qwen3-TTS-12Hz-1.7B-Base, CPU, x-vector-only prompt from Audio/ren_reference.wav).
  project/.tools/qwen-venv/bin/python production/black-friday-5min/short/gen_new_lines.py
Same v3 rules as the long film: fixed seeds, no speed change/stretching/padding, only digital silence at the edges trimmed (0.25 s natural tail kept). RESUMABLE: an existing WAV is reused. Writes voice_new/<name>.wav and voice_new/timings.json."""
import json, sys, time
from pathlib import Path
import numpy as np, soundfile as sf
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[2]; OUT = HERE / "voice_new"; SEED = 1115
LINES = {"hook": "He saved one hundred and seven dollars on Black Friday... but spent more money!", "closing": "Watch the full Black Friday video to see all five rules."}
def main():
    import torch
    sys.path.insert(0, str(ROOT / "videos" / "free_money")); from gen_voice import trim
    from qwen_tts import Qwen3TTSModel
    OUT.mkdir(exist_ok=True); t0 = time.monotonic(); m = Qwen3TTSModel.from_pretrained("Qwen/Qwen3-TTS-12Hz-1.7B-Base", device_map="cpu", dtype=torch.float32, attn_implementation="sdpa")
    prompt = m.create_voice_clone_prompt(ref_audio=str(ROOT / "Audio" / "ren_reference.wav"), ref_text=None, x_vector_only_mode=True); tp = OUT / "timings.json"; tm = json.loads(tp.read_text()) if tp.exists() else {}
    for k, (name, text) in enumerate(LINES.items(), 1):
        f = OUT / f"{name}.wav"
        if f.exists(): a, sr = sf.read(f, dtype="float32"); gen = 0.0
        else:
            torch.manual_seed(SEED + k); t1 = time.monotonic(); w, sr = m.generate_voice_clone(text=text, language="English", voice_clone_prompt=prompt, max_new_tokens=1400); a = trim(np.asarray(w[0], dtype=np.float32), sr); sf.write(f, a, sr); gen = time.monotonic() - t1
        tm[name] = {"text": text, "duration": round(len(a) / sr, 3), "sample_rate": sr, "seed": SEED + k}; tp.write_text(json.dumps(tm, indent=1)); print(f"{name} {len(a) / sr:5.2f}s ({gen:5.1f}s gen) {text}", flush=True)
if __name__ == "__main__": main()
