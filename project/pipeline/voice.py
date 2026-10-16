"""Stage 5: voiceover. One Kokoro voice, the same settings for every line.

  python pipeline/voice.py episodes/<id> --model kokoro-q8.onnx --voices package/voices

Synthesizes each script line, trims its edges, lays the lines out with fixed gaps (longer
between sections), and groups them into chunks under config.voice.max_chunk_s. Each chunk is
saved and checked for leading silence, loudness and pitch, then the chunks are joined into
audio/voice.wav and a loudness-normalized audio/voice.mp3. Timings go to audio/timings.json.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

sys.path.insert(0, str(Path(__file__).parent))
from common import load_config, parse_script  # noqa: E402

SR = 24000


def lufs(path):
    out = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af", "ebur128", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    vals = [l.split("I:")[1].split("LUFS")[0] for l in out.splitlines() if l.strip().startswith("I:")]
    return float(vals[-1]) if vals else None


def leading_silence(audio, thresh=0.01):
    idx = np.where(np.abs(audio) > thresh)[0]
    return float(idx[0] / SR) if len(idx) else float(len(audio) / SR)


def median_pitch_hz(path):
    import librosa
    y, sr = librosa.load(str(path), sr=SR)
    f0, voiced, _ = librosa.pyin(y, fmin=60, fmax=400, sr=sr, frame_length=1024)
    f0 = f0[voiced & ~np.isnan(f0)]
    return float(np.median(f0)) if len(f0) else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("episode")
    ap.add_argument("--model", required=True)
    ap.add_argument("--voices", required=True, help="Folder of kokoro-js voice .bin files")
    args = ap.parse_args()
    ep = Path(args.episode)
    cfg = load_config()["voice"]
    lines = parse_script(ep)
    out = ep / "audio"
    out.mkdir(exist_ok=True)

    style = sum(np.fromfile(Path(args.voices) / f"{n}.bin", dtype=np.float32).reshape(-1, 1, 256) * w
                for n, w in cfg["blend"].items())
    np.savez(out / ".voice.npz", voice=style)
    tts = Kokoro(args.model, str(out / ".voice.npz"))

    # 1. Synthesize every line with identical settings and trim its edges
    clips = []
    for l in lines:
        a, _ = tts.create(l["text"], voice="voice", speed=cfg["speed"], lang="en-us")
        idx = np.where(np.abs(a) > 0.01)[0]
        a = a[max(0, idx[0] - int(0.01 * SR)): idx[-1] + int(0.08 * SR)]
        clips.append(a.astype(np.float32))

    # 2. Group consecutive lines into chunks under the max length
    chunks, cur, cur_len = [], [], 0.0
    for i, (l, a) in enumerate(zip(lines, clips)):
        gap = 0 if not cur else (cfg["section_gap_s"] if l["section"] != lines[i - 1]["section"] else cfg["gap_s"])
        add = gap + len(a) / SR
        if cur and cur_len + add > cfg["max_chunk_s"]:
            chunks.append(cur)
            cur, cur_len, add = [], 0.0, len(a) / SR
        cur.append(i)
        cur_len += add
    chunks.append(cur)

    # 3. Build each chunk file, check it, and place it on the timeline
    timeline, chunk_meta, t = [], [], cfg["lead_s"]
    master = [np.zeros(int(cfg["lead_s"] * SR), dtype=np.float32)]
    for ci, idxs in enumerate(chunks):
        if ci:
            gap = cfg["section_gap_s"] if lines[idxs[0]]["section"] != lines[idxs[0] - 1]["section"] else cfg["gap_s"]
            master.append(np.zeros(int(gap * SR), dtype=np.float32))
            t += gap
        parts, local = [], 0.0
        for k, i in enumerate(idxs):
            if k:
                gap = cfg["section_gap_s"] if lines[i]["section"] != lines[i - 1]["section"] else cfg["gap_s"]
                parts.append(np.zeros(int(gap * SR), dtype=np.float32))
                local += gap
            d = len(clips[i]) / SR
            timeline.append({**lines[i], "start": round(t + local, 3), "end": round(t + local + d, 3), "chunk": ci})
            parts.append(clips[i])
            local += d
        chunk = np.concatenate(parts)
        path = out / f"chunk_{ci:02d}.wav"
        sf.write(path, chunk, SR)
        chunk_meta.append({"file": path.name, "start": round(t, 3), "duration": round(len(chunk) / SR, 3),
                           "leading_silence_s": round(leading_silence(chunk), 3), "lufs": lufs(path),
                           "median_pitch_hz": median_pitch_hz(path), "settings": cfg})
        master.append(chunk)
        t += len(chunk) / SR

    tail = 1.6
    master.append(np.zeros(int(tail * SR), dtype=np.float32))
    voice = np.concatenate(master)
    sf.write(out / "voice.wav", voice, SR)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(out / "voice.wav"), "-af",
                    f"highpass=f=70,loudnorm=I={cfg['target_lufs']}:TP=-1.5:LRA=9", "-ar", "48000", "-b:a", "192k",
                    str(out / "voice.mp3")], check=True)
    (out / ".voice.npz").unlink()
    result = {"settings": cfg, "duration": round(len(voice) / SR, 3), "lines": timeline, "chunks": chunk_meta}
    (out / "timings.json").write_text(json.dumps(result, indent=1) + "\n")
    for c in chunk_meta:
        print(f"{c['file']}: {c['duration']:.1f}s  lead {c['leading_silence_s']:.2f}s  {c['lufs']} LUFS  pitch {c['median_pitch_hz']:.0f} Hz")
    for l in timeline:
        print(f"  {l['start']:6.2f}-{l['end']:6.2f} [{l['id']}] {l['text']}")
    print(f"total {result['duration']:.1f}s")


if __name__ == "__main__":
    main()
