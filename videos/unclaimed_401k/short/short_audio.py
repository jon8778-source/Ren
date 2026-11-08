"""Build the Short's narration by CUTTING whole sentences from the approved long-form narration (voice/P1..S8.wav). 

  project/.tools/venv/bin/python videos/unclaimed_401k/short/short_audio.py

v3 Shorts rules: reuse the exact approved audio. No new synthesis, speed change, stretching or silence padding. Each excerpt starts a hair before
its first word (LEAD) and ends where the original audio next has speech or after TAIL of the ORIGINAL audio. Excerpts are joined exactly as cut.
Writes short_audio_raw.wav and short_cues.json (script words with their times on the Short's timeline).
"""
import json, re, sys
from pathlib import Path
import numpy as np, soundfile as sf
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent)); sys.path.insert(0, str(HERE.parents[2] / "project" / "cliplib"))
import render_full as RF
VOICE = HERE.parent / "voice"
LEAD, TAIL = 0.05, 0.22
# (section, first sentence, last sentence): whole script sentences, in script order, unchanged wording
EXCERPTS = [
    ("P1", 0, 6),    # Maya saved twelve dollars ... $100 a month. $1,200 a year. Her employer was willing ... one change.
    ("S3", 4, 5),    # But Maya's been putting in two percent. That's twelve hundred a year from her, with twelve hundred matched by work.
    ("S3", 7, 8),    # She's been getting half the match she could receive. The missing half is another twelve hundred dollars a year.
    ("S8", 5, 5),    # Leave it unclaimed for ten more years, and that's twelve thousand dollars ... changes to the plan.
    ("S8", 10, 14),  # I'm Ren. And sometimes ... on the table. Check out the Money Leak Audit Workbook in the description. Educational only, not financial advice.
]

def sentences(sec):
    words = RF.TM[sec]["text"].split(); out, cur = [], []
    for i, w in enumerate(words):
        cur.append(i)
        if re.search(r'[.?!]["”]?$', w): out.append(cur); cur = []
    if cur: out.append(cur)
    return words, out

def main():
    sr = 24000; track, cues, t0 = [], [], 0.0
    for sec, s0, s1 in EXCERPTS:
        words, sents = sentences(sec); wt = RF.aligned_word_times(sec)
        audio, r = sf.read(VOICE / f"{sec}.wav", dtype="float32"); assert r == sr
        first, last = sents[s0][0], sents[s1][-1]
        a = max(0.0, wt[first][0] - LEAD)
        nxt = wt[last + 1][0] - 0.03 if last + 1 < len(wt) else len(audio) / sr
        b = min(wt[last][1] + TAIL, nxt, len(audio) / sr)
        seg = audio[int(a * sr):int(b * sr)]; track.append(seg)
        for i in range(first, last + 1):
            cues.append({"section": sec, "word": words[i], "start": round(t0 + wt[i][0] - a, 3), "end": round(t0 + wt[i][1] - a, 3), "sentence_start": i in [x[0] for x in sents[s0:s1 + 1]]})
        t0 += len(seg) / sr
        print(f"{sec}.{s0}-{s1}: {a:6.2f}-{b:6.2f} ({b - a:5.2f} s) {' '.join(words[first:last + 1])[:70]}")
    out = np.concatenate(track); sf.write(HERE / "short_audio_raw.wav", out, sr)
    (HERE / "short_cues.json").write_text(json.dumps({"duration": round(len(out) / sr, 3), "words": cues}, indent=1, ensure_ascii=False))
    print("total narration:", round(len(out) / sr, 2), "s,", len(cues), "words,", int(len(out) / sr * 24), "frames")

if __name__ == "__main__":
    main()
