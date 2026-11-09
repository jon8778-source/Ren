"""Narrate the approved v2 script in Ren's cloned voice (Qwen3-TTS 1.7B Base, local CPU), PILOT PART ONLY (about 60 s).

  project/.tools/qwen-venv/bin/python videos/three_bills/gen_voice.py [--all]

Script v2 approval: recorded in production/OWNER_DECISIONS.md (owner "Script approved", 9 Nov 2026; SHA-256 14801320...). Voice text = script/VOICE_SCRIPT.txt
(SHA-256 efa04724...). The pilot is paragraphs 0-9 of the voice script, ending after a complete sentence ("... a chain of other decisions."). Same v3 voice rules as the
401(k) episode: model Qwen/Qwen3-TTS-12Hz-1.7B-Base, English, x-vector-only prompt from Audio/ren_reference.wav (the transcript is not used in x-vector-only mode),
fixed seeds, sentence-end chunks of up to 45 words, chunks joined exactly as generated (only digital silence at the edges is trimmed, a 0.25 s natural tail is kept),
no speed change, stretching or padding. RESUMABLE: an existing chunk WAV is reused, never regenerated. --all adds the remaining sections (full episode, not before approval).
Writes voice/chunks/*.wav, voice/<section>.wav and voice/timings.json.
"""
import argparse, json, sys, time
from pathlib import Path
import numpy as np, soundfile as sf
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]; OUT = HERE / "voice"; SEED = 9011
SECTIONS_PILOT = {"H": (0, 4), "L": (5, 9)}          # paragraph ranges of VOICE_SCRIPT.txt
def paras():
    return [" ".join(p.split()) for p in (HERE / "script" / "VOICE_SCRIPT.txt").read_text().strip().split("\n\n")]
def sections(all_):
    ps = paras(); secs = {k: " ".join(ps[a:b + 1]) for k, (a, b) in SECTIONS_PILOT.items()}
    if all_:
        rest = {"D1": (10, 16), "D2": (17, 22), "D3": (23, 27), "D4": (28, 34), "D5": (35, 39), "D6": (40, 44), "D7": (45, 48)}
        secs.update({k: " ".join(ps[a:b + 1]) for k, (a, b) in rest.items()})
    return secs
def main():
    import torch
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "free_money"))
    from gen_voice import chunks, trim   # audited helpers: sentence chunking and edge trimming
    from qwen_tts import Qwen3TTSModel
    ap = argparse.ArgumentParser(); ap.add_argument("--all", action="store_true"); args = ap.parse_args()
    secs = sections(args.all); (OUT / "chunks").mkdir(parents=True, exist_ok=True); t0 = time.monotonic()
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
                torch.manual_seed(SEED + 100 * (ord(sid[0]) % 50) + 10 * int(sid[1:] or 0) + k); t1 = time.monotonic()
                w, sr = m.generate_voice_clone(text=text, language="English", voice_clone_prompt=prompt, max_new_tokens=1400)
                a = trim(np.asarray(w[0], dtype=np.float32), sr); sf.write(f, a, sr); gen = time.monotonic() - t1
            d = len(a) / sr; rows.append({"chunk": k, "text": text, "start": round(t, 3), "end": round(t + d, 3), "gen_s": round(gen, 1)}); parts.append(a); t += d
            print(f"{sid}_{k:02d} {d:5.2f}s ({gen:5.1f}s gen, {len(text.split())}w) {text[:60]}", flush=True)
        sf.write(OUT / f"{sid}.wav", np.concatenate(parts), sr)
        timings[sid] = {"duration": round(t, 3), "sample_rate": sr, "text": text_all, "chunks": rows}; tp.write_text(json.dumps(timings, indent=1, ensure_ascii=False) + "\n"); print(f"{sid}.wav {t:.1f}s", flush=True)
    print("done", round(time.monotonic() - t0), "s", flush=True)
if __name__ == "__main__":
    main()
