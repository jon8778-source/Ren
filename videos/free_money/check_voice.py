"""Whisper-check the generated scene narration against the script and write word timings.

  project/.tools/qwen-venv/bin/python videos/free_money/check_voice.py S1 S2

Transcribes voice/Sx.wav (faster-whisper medium.en, CPU) with word timestamps, writes voice/words_Sx.json
and voice/check.json, and prints heard-vs-script differences. Speech-to-text is a stand-in for listening: it
catches wrong, missing or runaway words, not accent or tone.
"""
import difflib, json, re, subprocess, sys
from pathlib import Path
import numpy as np
from faster_whisper import WhisperModel

HERE = Path(__file__).resolve().parent
V = HERE / "voice"
ROOT = HERE.parents[1]
NUM = {"28": "twenty eight", "25": "twenty five", "6": "six", "2": "two", "4": "four", "3": "three"}


def script_sections():
    parts = re.split(r"\*\*\[(S\d+): [^\]]*\]\*\*", (ROOT / "scripts" / "Ren_Free_Money_Script.md").read_text())
    return {parts[i]: " ".join(parts[i + 1].split()) for i in range(1, len(parts), 2)}


def norm(t):
    t = t.lower().replace("’", "'").replace("-", " ").replace(",", "")
    t = re.sub(r"\$(\d+)(?:,(\d{3}))?", lambda m: " dollars " + m.group(1) + (m.group(2) or ""), t)
    return [w for w in re.findall(r"[a-z0-9']+", t) if w not in ("and",)]


def main():
    secs = script_sections()
    m = WhisperModel("medium.en", device="cpu", compute_type="int8")
    res = {}
    for sid in sys.argv[1:] or list(secs):
        raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(V / f"{sid}.wav"), "-ac", "1", "-ar", "16000", "-f", "f32le", "-"])
        segs = list(m.transcribe(np.frombuffer(raw, np.float32), beam_size=5, condition_on_previous_text=False, word_timestamps=True)[0])
        words = [{"word": w.word.strip(), "start": round(w.start, 3), "end": round(w.end, 3)} for s in segs for w in s.words]
        (V / f"words_{sid}.json").write_text(json.dumps(words, indent=1))
        heard = " ".join(w["word"] for w in words)
        want, got = norm(secs[sid]), norm(heard)
        sm = difflib.SequenceMatcher(None, want, got)
        diffs = [(op, " ".join(want[i1:i2]), " ".join(got[j1:j2])) for op, i1, i2, j1, j2 in sm.get_opcodes() if op != "equal"]
        res[sid] = {"ratio": round(sm.ratio(), 4), "differences": diffs, "heard": heard}
        print(sid, "match ratio", round(sm.ratio(), 4), "| differences:", diffs, flush=True)
        print("  heard:", heard, flush=True)
    old = json.loads((V / "check.json").read_text()) if (V / "check.json").exists() else {}
    old.update(res)
    (V / "check.json").write_text(json.dumps(old, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
