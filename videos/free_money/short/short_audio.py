"""Build the 1-minute Short's narration by CUTTING whole sentences from the approved long-form narration (voice/S1..S7.wav).

  project/.tools/venv/bin/python videos/free_money/short/short_audio.py

v3 Shorts rules: reuse the exact approved audio. No new synthesis, no speed change, no stretching, no silence padding. Each excerpt
starts a hair before its first word (LEAD) and ends where the original audio next has speech or after TAIL of the ORIGINAL audio
(whatever the original contains, never inserted silence). Excerpts are joined exactly as cut. Writes short_audio_raw.wav and
short_cues.json (the script words with their times on the Short's timeline) next to this file.
"""
import json, re, sys
from pathlib import Path
import numpy as np
import soundfile as sf

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import fm_pilot as fp  # noqa: E402  (aligned_word_times: script word -> time in the scene audio)
import plan_data as pd  # noqa: E402

VOICE = HERE.parent / "voice"
LEAD, TAIL = 0.05, 0.22
# (scene, first sentence, last sentence): whole script sentences, in script order, unchanged wording
EXCERPTS = [
    ("S1", 0, 1),      # I was 28 when Dev held up my pay stub and asked me one question. "Who's keeping the difference?"
    ("S1", 3, 4),      # Then he pointed at one line, and my stomach dropped. For three years, I'd been turning down free money.
    ("S2", 0, 2),      # Twenty-five. First real job. Forty-four thousand a year, and I felt like I'd made it.
    ("S2", 3, 3),      # So I did what felt right and leased a brand-new car, ... a month.
    ("S2", 7, 7),      # Somewhere on page six it said the company would match every dollar ... of my salary.
    ("S2", 9, 9),      # I picked two percent, because two sounded responsible, and the lease sounded urgent.
    ("S3", 2, 6),      # I put in two, so they put in two. The other two percent? ... That was eight hundred and eighty dollars the first year.
    ("S4", 11, 13),    # I went home, opened the app on my phone, and changed two to four. It took ninety seconds. Ninety seconds, three years late.
    ("S6", 14, 15),    # You don't have to max it out. You just don't want to skip the free part.
    ("S7", 2, 2),      # Before you cut a single thing, collect what you're already owed.
]


def sentences(sid):
    words = pd.scene_text()[sid].split()
    out, cur = [], []
    for i, w in enumerate(words):
        cur.append(i)
        if re.search(r'[.?!]["”]?$', w):
            out.append(cur); cur = []
    if cur:
        out.append(cur)
    return words, out


def main():
    sr = 24000
    track, cues, t0 = [], [], 0.0
    for sid, s0, s1 in EXCERPTS:
        words, sents = sentences(sid)
        wt = fp.aligned_word_times(sid)
        audio, r = sf.read(VOICE / f"{sid}.wav", dtype="float32")
        assert r == sr
        first, last = sents[s0][0], sents[s1][-1]
        a = max(0.0, wt[first][0] - LEAD)
        nxt = wt[last + 1][0] - 0.03 if last + 1 < len(wt) else len(audio) / sr
        b = min(wt[last][1] + TAIL, nxt, len(audio) / sr)
        seg = audio[int(a * sr):int(b * sr)]
        track.append(seg)
        for i in range(first, last + 1):
            cues.append({"scene": sid, "word": words[i], "start": round(t0 + wt[i][0] - a, 3), "end": round(t0 + wt[i][1] - a, 3),
                         "sentence_start": i in [x[0] for x in sents[s0:s1 + 1]]})
        t0 += len(seg) / sr
        print(f"{sid}.{s0}-{s1}: {a:6.2f}-{b:6.2f} ({b - a:5.2f} s) {' '.join(words[first:last + 1])[:70]}")
    out = np.concatenate(track)
    sf.write(HERE / "short_audio_raw.wav", out, sr)
    (HERE / "short_cues.json").write_text(json.dumps({"duration": round(len(out) / sr, 3), "words": cues}, indent=1, ensure_ascii=False))
    print("total narration:", round(len(out) / sr, 2), "s,", len(cues), "words")


if __name__ == "__main__":
    main()
