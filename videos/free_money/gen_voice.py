"""Narrate scripts/Ren_Free_Money_Script.md in Ren's cloned voice, locally (Qwen3-TTS 1.7B Base).

  project/.tools/qwen-venv/bin/python videos/free_money/gen_voice.py [--sections S1 S2]

v3 rules: model Qwen/Qwen3-TTS-12Hz-1.7B-Base, English, x-vector-only voice prompt from Audio/ren_reference.wav
(x_vector_only_mode=True; the transcript is not used). No speed change, stretching or silence padding: each
scene is split at sentence ends into chunks of up to ~45 words, every chunk is generated with a fixed seed,
and chunks are joined exactly as generated (leading/trailing digital silence only is trimmed, a natural 0.25 s
tail is kept). RESUMABLE: a chunk whose WAV already exists is reused, never regenerated. Section markers
like [S1: Cold open] are planning labels and are never spoken. Writes voice/chunks/Sx_nn.wav, voice/Sx.wav
and voice/timings.json.
"""
import argparse, json, re, time
from pathlib import Path
import numpy as np, soundfile as sf, torch
from qwen_tts import Qwen3TTSModel

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "voice"
MAXW, SEED = 45, 2027


def sections(path):
    t = Path(path).read_text()
    parts = re.split(r"\*\*\[(S\d+): [^\]]*\]\*\*", t)
    return {parts[i]: " ".join(parts[i + 1].split()) for i in range(1, len(parts), 2)}


def chunks(text):
    sents = re.findall(r"[^.?!]+[.?!]+[\"”']?\s*|[^.?!]+$", text)
    out, cur = [], ""
    for s in (x.strip() for x in sents if x.strip()):
        if cur and len((cur + " " + s).split()) > MAXW:
            out.append(cur); cur = s
        else:
            cur = (cur + " " + s).strip()
    return out + ([cur] if cur else [])


def trim(a, sr):
    idx = np.where(np.abs(a) > 0.003)[0]
    if not len(idx):
        return a
    return a[max(0, idx[0] - int(0.01 * sr)): idx[-1] + int(0.25 * sr)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sections", nargs="*")
    args = ap.parse_args()
    secs = sections(ROOT / "scripts" / "Ren_Free_Money_Script.md")
    want = args.sections or list(secs)
    (OUT / "chunks").mkdir(parents=True, exist_ok=True)
    t0 = time.monotonic()
    m = Qwen3TTSModel.from_pretrained("Qwen/Qwen3-TTS-12Hz-1.7B-Base", device_map="cpu", dtype=torch.float32, attn_implementation="sdpa")
    prompt = m.create_voice_clone_prompt(ref_audio=str(ROOT / "Audio" / "ren_reference.wav"), ref_text=None, x_vector_only_mode=True)
    print(f"model and x-vector prompt ready in {time.monotonic() - t0:.0f}s", flush=True)
    tp = OUT / "timings.json"
    timings = json.loads(tp.read_text()) if tp.exists() else {}
    for sid in want:
        parts, rows, t, sr = [], [], 0.0, 24000
        for k, text in enumerate(chunks(secs[sid]), 1):
            f = OUT / "chunks" / f"{sid}_{k:02d}.wav"
            gen = 0.0
            if f.exists():
                a, sr = sf.read(f, dtype="float32")
            else:
                torch.manual_seed(SEED + 100 * int(sid[1:]) + k)
                t1 = time.monotonic()
                w, sr = m.generate_voice_clone(text=text, language="English", voice_clone_prompt=prompt, max_new_tokens=1400)
                a = trim(np.asarray(w[0], dtype=np.float32), sr)
                sf.write(f, a, sr)
                gen = time.monotonic() - t1
            d = len(a) / sr
            rows.append({"chunk": k, "text": text, "start": round(t, 3), "end": round(t + d, 3), "gen_s": round(gen, 1)})
            parts.append(a); t += d
            print(f"{sid}_{k:02d} {d:5.2f}s ({gen:5.1f}s gen, {len(text.split())}w) {text[:60]}", flush=True)
        sf.write(OUT / f"{sid}.wav", np.concatenate(parts), sr)
        timings[sid] = {"duration": round(t, 3), "sample_rate": sr, "chunks": rows}
        tp.write_text(json.dumps(timings, indent=1, ensure_ascii=False) + "\n")
        print(f"{sid}.wav {t:.1f}s", flush=True)
    print("done", round(time.monotonic() - t0), "s", flush=True)


if __name__ == "__main__":
    main()
