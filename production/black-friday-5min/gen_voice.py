"""Narrate the approved Black Friday long-form script in Ren's Qwen British clone (Qwen3-TTS-12Hz-1.7B-Base, CPU, x-vector-only prompt from Audio/ren_reference.wav).
  project/.tools/qwen-venv/bin/python production/black-friday-5min/gen_voice.py [--all]
PILOT = sections 1-2 (voice/VOICE_SCRIPT.txt paragraphs 0-1); --all adds sections 3-8 (not before pilot approval). Fixed seeds, sentence-end chunks <= 45 words, chunks joined as generated,
no speed change/stretching/padding. RESUMABLE: an existing chunk WAV is reused. Writes voice/chunks/*.wav, voice/<sec>.wav, voice/timings.json."""
import argparse, json, sys, time
from pathlib import Path
import numpy as np, soundfile as sf
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]; OUT = HERE / "voice"; SEED = 1114
def main():
    import torch
    sys.path.insert(0, str(ROOT / "videos" / "free_money")); from gen_voice import chunks, trim
    from qwen_tts import Qwen3TTSModel
    ap = argparse.ArgumentParser(); ap.add_argument("--all", action="store_true"); args = ap.parse_args()
    paras = [" ".join(p.split()) for p in (OUT / "VOICE_SCRIPT.txt").read_text().strip().split("\n\n")]; secs = {f"S{i + 1}": p for i, p in enumerate(paras)}
    if not args.all: secs = {k: v for k, v in secs.items() if k in ("S1", "S2")}
    (OUT / "chunks").mkdir(parents=True, exist_ok=True); t0 = time.monotonic()
    m = Qwen3TTSModel.from_pretrained("Qwen/Qwen3-TTS-12Hz-1.7B-Base", device_map="cpu", dtype=torch.float32, attn_implementation="sdpa")
    prompt = m.create_voice_clone_prompt(ref_audio=str(ROOT / "Audio" / "ren_reference.wav"), ref_text=None, x_vector_only_mode=True); print(f"model ready {time.monotonic() - t0:.0f}s", flush=True)
    tp = OUT / "timings.json"; timings = json.loads(tp.read_text()) if tp.exists() else {}
    for sid, text_all in secs.items():
        parts, rows, t, sr = [], [], 0.0, 24000
        for k, text in enumerate(chunks(text_all), 1):
            f = OUT / "chunks" / f"{sid}_{k:02d}.wav"; gen = 0.0
            if f.exists(): a, sr = sf.read(f, dtype="float32")
            else:
                torch.manual_seed(SEED + 100 * int(sid[1:]) + k); t1 = time.monotonic()
                w, sr = m.generate_voice_clone(text=text, language="English", voice_clone_prompt=prompt, max_new_tokens=1400); a = trim(np.asarray(w[0], dtype=np.float32), sr); sf.write(f, a, sr); gen = time.monotonic() - t1
            d = len(a) / sr; rows.append({"chunk": k, "text": text, "start": round(t, 3), "end": round(t + d, 3), "gen_s": round(gen, 1)}); parts.append(a); t += d; print(f"{sid}_{k:02d} {d:5.2f}s ({gen:5.1f}s gen, {len(text.split())}w) {text[:60]}", flush=True)
        sf.write(OUT / f"{sid}.wav", np.concatenate(parts), sr); timings[sid] = {"duration": round(t, 3), "sample_rate": sr, "text": text_all, "chunks": rows}; tp.write_text(json.dumps(timings, indent=1, ensure_ascii=False) + "\n"); print(f"{sid}.wav {t:.1f}s", flush=True)
    print("done", round(time.monotonic() - t0), "s", flush=True)
if __name__ == "__main__": main()
