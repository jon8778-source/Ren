"""Narrate a script's sections in Ren's cloned voice with Qwen3-TTS run locally (no Space, no quota).

  project/.tools/qwen-venv/bin/python project/cliplib/qwen_local_voice.py \\
      scripts/Ren_Postponing_Life_Script_v3.md --sections S1 S2 --out videos/postponing_life/voice

Uses Qwen/Qwen3-TTS-12Hz-1.7B-Base (the model behind the Space's Voice Clone tab) with
Audio/ren_reference.wav and its exact transcript, building the voice prompt once and reusing it for
every line. Each paragraph of a section is one line: lines/S1_01.wav ... Lines are joined into S1.wav,
S2.wav ... with config voice.gap_s between them, and timings.json records where each line sits and
whether it is a quoted (speaker-tagged) line. A fixed seed per line makes re-runs repeatable.
"""
import argparse
import json
import re
import time
from pathlib import Path

import numpy as np
import soundfile as sf
import torch
from qwen_tts import Qwen3TTSModel

ROOT = Path(__file__).resolve().parents[2]
REF = ROOT / "Audio"
CONFIG = ROOT / "project" / "config.json"


def read_sections(path):
    """{"S1": [line, ...]} from the script body; section markers and notes are not spoken."""
    body = Path(path).read_text().split("\n---\n")[1]
    out = {}
    for sid, text in re.findall(r"\[(S\d+) — [^\]]+\]\n(.*?)(?=\n\[S\d+ — |\Z)", body, flags=re.S):
        out[sid] = [p.strip() for p in text.split("\n\n") if p.strip()]
    return out


def trim(a, sr):
    idx = np.where(np.abs(a) > 0.01)[0]
    return a[max(0, idx[0] - int(0.01 * sr)): idx[-1] + int(0.08 * sr)] if len(idx) else a


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("script")
    ap.add_argument("--sections", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", default="Qwen/Qwen3-TTS-12Hz-1.7B-Base")
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--seed", type=int, default=1234)
    args = ap.parse_args()
    gap_s = json.loads(CONFIG.read_text())["voice"]["gap_s"]
    sections = read_sections(args.script)
    out = Path(args.out)
    (out / "lines").mkdir(parents=True, exist_ok=True)

    t0 = time.monotonic()
    model = Qwen3TTSModel.from_pretrained(
        args.model, device_map=args.device,
        dtype=torch.bfloat16 if args.device.startswith("cuda") else torch.float32,
        attn_implementation="sdpa")
    ref_text = (REF / "ren_reference.txt").read_text().strip().strip('"“”').strip()
    prompt = model.create_voice_clone_prompt(ref_audio=str(REF / "ren_reference.wav"), ref_text=ref_text,
                                             x_vector_only_mode=False)
    print(f"model and voice prompt ready in {time.monotonic() - t0:.0f}s", flush=True)

    timings_path = out / "timings.json"
    timings = json.loads(timings_path.read_text()) if timings_path.exists() else {}
    for sid in args.sections:
        parts, lines, t, sr = [], [], 0.0, None
        for k, text in enumerate(sections[sid], 1):
            torch.manual_seed(args.seed + k)
            t1 = time.monotonic()
            wavs, sr = model.generate_voice_clone(text=text, language="English", voice_clone_prompt=prompt,
                                                  max_new_tokens=2048)
            took = time.monotonic() - t1
            a = trim(np.asarray(wavs[0], dtype=np.float32), sr)
            sf.write(out / "lines" / f"{sid}_{k:02d}.wav", a, sr)
            if parts:
                parts.append(np.zeros(int(gap_s * sr), dtype=np.float32))
                t += gap_s
            d = len(a) / sr
            lines.append({"line": k, "text": text, "start": round(t, 3), "end": round(t + d, 3),
                          "quote": text.startswith("“"), "gen_s": round(took, 1)})
            parts.append(a)
            t += d
            print(f"{sid}_{k:02d}: {d:5.2f}s audio in {took:6.1f}s  {text[:70]}", flush=True)
        sf.write(out / f"{sid}.wav", np.concatenate(parts), sr)
        timings[sid] = {"duration": round(t, 3), "sample_rate": sr, "lines": lines}
        timings_path.write_text(json.dumps(timings, indent=1, ensure_ascii=False) + "\n")
        print(f"{sid}.wav: {t:.2f}s", flush=True)
    print(f"total {time.monotonic() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
