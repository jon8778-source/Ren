"""Build the Three Bills Short's narration by CUTTING whole sentences from the approved full-episode narration (voice/H.wav, L.wav, D1..D7.wav).

  project/.tools/venv/bin/python videos/three_bills/short/short_audio.py

v3 Shorts rules: reuse the exact approved audio; no new synthesis, speed change, stretching or silence padding. Each excerpt starts a hair before its first word (LEAD)
and ends after TAIL of the ORIGINAL audio (never past the next spoken word); excerpts are joined exactly as cut. Writes short_audio_raw.wav and short_cues.json.
"""
import json, re, sys
from pathlib import Path
import numpy as np, soundfile as sf
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent)); sys.path.insert(0, str(HERE.parents[1] / "unclaimed_401k")); sys.path.insert(0, str(HERE.parents[2] / "project" / "cliplib"))
import tb_full as TF
VOICE = HERE.parent / "voice"; LEAD, TAIL = 0.05, 0.22
# (section, first sentence, last sentence): whole script sentences, in script order, wording unchanged
EXCERPTS = [
    ("H", 0, 6),    # Three bills. Thirty days. First, Maya's car broke down. Then ... urgent dental bill. And just when ... kitchen sink. The total? Two thousand two hundred dollars.
    ("H", 9, 11),   # But when Maya opened her savings app afterward ... I've gone backwards. Here's why she hadn't.
    ("D1", 4, 5),   # Once the card was paid off ... every week. Fifty dollars a week, for fifty-two weeks, gave her two thousand six hundred dollars.
    ("D2", 5, 6),   # But this time, she had an answer. The money was already there.
    ("D4", 11, 13), # Three bills in thirty days. Two thousand two hundred dollars gone. Four hundred dollars left.
    ("D5", 8, 10),  # An emergency fund is supposed to get smaller ... Using it isn't failure. That's literally the job it was hired to do.
    ("D7", 6, 7),   # What bill would have shaken you a year ago ...? I'd love to hear it in the comments.
]
def sentences(sec):
    words = TF.TM[sec]["text"].split(); out, cur = [], []
    for i, w in enumerate(words):
        cur.append(i)
        if re.search(r'[.?!]["”]?$', w): out.append(cur); cur = []
    if cur: out.append(cur)
    return words, out
def main():
    sr = 24000; track, cues, t0 = [], [], 0.0
    for sec, s0, s1 in EXCERPTS:
        words, sents = sentences(sec); wt = TF.aligned(sec); audio, r = sf.read(VOICE / f"{sec}.wav", dtype="float32"); assert r == sr
        first, last = sents[s0][0], sents[s1][-1]; a = max(0.0, wt[first][0] - LEAD); nxt = wt[last + 1][0] - 0.03 if last + 1 < len(wt) else len(audio) / sr
        b = min(wt[last][1] + TAIL, nxt, len(audio) / sr); seg = audio[int(a * sr):int(b * sr)]; track.append(seg)
        for i in range(first, last + 1): cues.append({"section": sec, "word": words[i], "start": round(t0 + wt[i][0] - a, 3), "end": round(t0 + wt[i][1] - a, 3), "sentence_start": i in [x[0] for x in sents[s0:s1 + 1]]})
        t0 += len(seg) / sr; print(f"{sec}.{s0}-{s1}: {a:6.2f}-{b:6.2f} ({b - a:5.2f} s) {' '.join(words[first:last + 1])[:70]}")
    out = np.concatenate(track); sf.write(HERE / "short_audio_raw.wav", out, sr)
    (HERE / "short_cues.json").write_text(json.dumps({"duration": round(len(out) / sr, 3), "words": cues}, indent=1, ensure_ascii=False))
    print("total narration:", round(len(out) / sr, 2), "s,", len(cues), "words,", int(len(out) / sr * 24), "frames")
if __name__ == "__main__": main()
