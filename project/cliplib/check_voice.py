"""Transcribe each generated narration line and flag any whose words differ from the script.

  project/.tools/qwen-venv/bin/python project/cliplib/check_voice.py videos/postponing_life/voice

Reads timings.json written by qwen_local_voice.py, runs faster-whisper (medium.en, CPU) on every
lines/<section>_<nn>.wav, and compares words after normalising case, punctuation and spelled-out
numbers. Also flags lines faster than --max-wpm. Writes voice_check.json beside timings.json and exits
non-zero if any line fails. Speech-to-text is a stand-in for listening: it catches wrong, missing or
runaway words, not accent or tone.
"""
import argparse
import difflib
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
from faster_whisper import WhisperModel

NUMBER_WORDS = {"4": "four", "365": "three hundred sixty five"}


def words(text):
    text = text.lower().replace("’", "'").replace("-", " ")
    for digits, spoken in NUMBER_WORDS.items():
        text = re.sub(rf"\b{digits}\b", spoken, text)
    return [w for w in re.findall(r"[a-z0-9']+", text) if w != "and"]


def load(path):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", "16000",
                                   "-f", "f32le", "-"])
    return np.frombuffer(raw, np.float32)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("voice_dir")
    ap.add_argument("--model", default="medium.en")
    ap.add_argument("--max-wpm", type=float, default=230)
    args = ap.parse_args()
    voice = Path(args.voice_dir)
    timings = json.loads((voice / "timings.json").read_text())
    model = WhisperModel(args.model, device="cpu", compute_type="int8")
    report, failed = {}, 0
    for sid, sec in timings.items():
        for line in sec["lines"]:
            path = voice / "lines" / f"{sid}_{line['line']:02d}.wav"
            segs, _ = model.transcribe(load(path), beam_size=5, condition_on_previous_text=False)
            heard = " ".join(s.text.strip() for s in segs)
            want, got = words(line["text"]), words(heard)
            ratio = difflib.SequenceMatcher(None, want, got).ratio()
            dur = line["end"] - line["start"]
            wpm = len(want) / dur * 60 if dur else 0
            problems = []
            if want != got:
                problems.append("words differ")
            if wpm > args.max_wpm:
                problems.append(f"fast ({wpm:.0f} wpm)")
            failed += bool(problems)
            report[path.name] = {"text": line["text"], "heard": heard, "match": round(ratio, 3),
                                 "duration_s": round(dur, 2), "wpm": round(wpm), "problems": problems}
            mark = "FAIL" if problems else "ok  "
            print(f"{mark} {path.name} {dur:5.2f}s {wpm:4.0f}wpm  heard: {heard}"
                  + (f"   [{'; '.join(problems)}]" if problems else ""), flush=True)
    (voice / "voice_check.json").write_text(json.dumps(report, indent=1, ensure_ascii=False) + "\n")
    print(f"{failed} line(s) need attention" if failed else "all lines match the script")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
