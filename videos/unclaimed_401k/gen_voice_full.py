"""Narrate the REST of the approved v3 script (S2 after "so she moved on." plus S3-S8) in Ren's cloned voice, locally (Qwen3-TTS 1.7B Base).

  project/.tools/qwen-venv/bin/python videos/unclaimed_401k/gen_voice_full.py

Pilot approved by the owner ("Approved", 8 Nov 2026). Same v3 rules as gen_voice.py: x-vector-only prompt from Audio/ren_reference.wav, fixed seeds,
sentence-end chunks of up to 45 words, no speed change or padding, RESUMABLE (existing chunk WAVs are reused). The pilot's P1/P2 chunks are NOT regenerated.
Sections: P3 = rest of S2, then S3..S8. Appends to voice/timings.json.
"""
import json, sys, time
from pathlib import Path
import numpy as np, soundfile as sf, torch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "free_money"))
from gen_voice import sections, chunks, trim
from qwen_tts import Qwen3TTSModel
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]; OUT = HERE / "voice"; SEED = 4011
PILOT_END = "so she moved on."

def full_sections():
    secs = sections(HERE / "script" / "narration_v3.md"); s2 = secs["S2"]
    cut = s2.index(PILOT_END) + len(PILOT_END)
    out = {"P3": s2[cut:].strip()}
    for k in ("S3", "S4", "S5", "S6", "S7", "S8"): out[k] = secs[k]
    return out

def main():
    secs = full_sections(); (OUT / "chunks").mkdir(parents=True, exist_ok=True)
    t0 = time.monotonic()
    m = Qwen3TTSModel.from_pretrained("Qwen/Qwen3-TTS-12Hz-1.7B-Base", device_map="cpu", dtype=torch.float32, attn_implementation="sdpa")
    prompt = m.create_voice_clone_prompt(ref_audio=str(ROOT / "Audio" / "ren_reference.wav"), ref_text=None, x_vector_only_mode=True)
    print(f"model ready {time.monotonic() - t0:.0f}s", flush=True)
    tp = OUT / "timings.json"; timings = json.loads(tp.read_text()) if tp.exists() else {}
    for sid, text_all in secs.items():
        parts, rows, t, sr = [], [], 0.0, 24000
        for k, text in enumerate(chunks(text_all), 1):
            f = OUT / "chunks" / f"{sid}_{k:02d}.wav"; gen = 0.0
            if f.exists(): a, sr = sf.read(f, dtype="float32")
            else:
                torch.manual_seed(SEED + 100 * int(sid[1:]) + k); t1 = time.monotonic()
                w, sr = m.generate_voice_clone(text=text, language="English", voice_clone_prompt=prompt, max_new_tokens=1400)
                a = trim(np.asarray(w[0], dtype=np.float32), sr); sf.write(f, a, sr); gen = time.monotonic() - t1
            d = len(a) / sr
            rows.append({"chunk": k, "text": text, "start": round(t, 3), "end": round(t + d, 3), "gen_s": round(gen, 1)})
            parts.append(a); t += d
            print(f"{sid}_{k:02d} {d:5.2f}s ({gen:5.1f}s gen, {len(text.split())}w) {text[:60]}", flush=True)
        sf.write(OUT / f"{sid}.wav", np.concatenate(parts), sr)
        timings[sid] = {"duration": round(t, 3), "sample_rate": sr, "text": text_all, "chunks": rows}
        tp.write_text(json.dumps(timings, indent=1, ensure_ascii=False) + "\n"); print(f"{sid}.wav {t:.1f}s", flush=True)
    print("done", round(time.monotonic() - t0), "s", flush=True)

if __name__ == "__main__":
    main()
