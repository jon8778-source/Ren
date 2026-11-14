"""Narrate the approved Black Friday script (production/black-friday-30s/voice/VOICE_SCRIPT.txt) in Ren's Qwen British clone.
Owner approved the script in chat ("Approved", 14 Nov 2026). Same v3 voice rules as Three Bills: Qwen/Qwen3-TTS-12Hz-1.7B-Base, English, x-vector-only prompt from Audio/ren_reference.wav,
fixed seeds, sentence-end chunks <=45 words, chunks joined as generated, no speed change. Resumable. Writes voice/chunks/*.wav, voice/narration.wav, voice/timings.json.
"""
import json, sys, time
from pathlib import Path
import numpy as np, soundfile as sf
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]; OUT = HERE / "voice"; SEED = 1114
def main():
    import torch
    sys.path.insert(0, str(ROOT / "videos" / "free_money"))
    from gen_voice import chunks, trim
    from qwen_tts import Qwen3TTSModel
    text_all = " ".join((OUT / "VOICE_SCRIPT.txt").read_text().split()); (OUT / "chunks").mkdir(exist_ok=True); t0 = time.monotonic()
    m = Qwen3TTSModel.from_pretrained("Qwen/Qwen3-TTS-12Hz-1.7B-Base", device_map="cpu", dtype=torch.float32, attn_implementation="sdpa")
    prompt = m.create_voice_clone_prompt(ref_audio=str(ROOT / "Audio" / "ren_reference.wav"), ref_text=None, x_vector_only_mode=True)
    parts, rows, t, sr = [], [], 0.0, 24000
    for k, text in enumerate(chunks(text_all), 1):
        f = OUT / "chunks" / f"N_{k:02d}.wav"; gen = 0.0
        if f.exists(): a, sr = sf.read(f, dtype="float32")
        else:
            torch.manual_seed(SEED + k); t1 = time.monotonic()
            w, sr = m.generate_voice_clone(text=text, language="English", voice_clone_prompt=prompt, max_new_tokens=1400)
            a = trim(np.asarray(w[0], dtype=np.float32), sr); sf.write(f, a, sr); gen = time.monotonic() - t1
        d = len(a) / sr; rows.append({"chunk": k, "text": text, "start": round(t, 3), "end": round(t + d, 3), "gen_s": round(gen, 1)}); parts.append(a); t += d
        print(f"N_{k:02d} {d:5.2f}s ({gen:5.1f}s gen, {len(text.split())}w) {text[:60]}", flush=True)
    sf.write(OUT / "narration.wav", np.concatenate(parts), sr)
    (OUT / "timings.json").write_text(json.dumps({"duration": round(t, 3), "sample_rate": sr, "text": text_all, "chunks": rows}, indent=1) + "\n"); print(f"narration.wav {t:.2f}s", flush=True)
if __name__ == "__main__": main()
