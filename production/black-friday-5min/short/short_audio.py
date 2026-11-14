"""Build the Black Friday Short's narration by CUTTING whole sentences from the approved full-episode narration (voice/S1..S8.wav joined = voice/full.wav).
  project/.tools/venv/bin/python production/black-friday-5min/short/short_audio.py
Shorts rules: reuse the exact approved audio; no new synthesis, speed change, stretching or silence padding. Each excerpt starts LEAD before its first word and ends TAIL after its last word of the ORIGINAL
audio (never past the next spoken word); excerpts are joined exactly as cut. Writes short_audio_raw.wav and short_cues.json (script words with times on the Short's timeline)."""
import difflib, json, re, sys
from pathlib import Path
import numpy as np, soundfile as sf
HERE = Path(__file__).resolve().parent; BF = HERE.parent; VOICE = BF / "voice"; LEAD, TAIL = 0.05, 0.22
# whole script sentences, in script order, wording unchanged: each excerpt is one contiguous run of the approved narration
EXCERPTS = [
    "Black Friday has a clever trick. It can make spending feel like saving. Today, Alex heads into the sales with a three hundred dollar budget and two very different plans. One plan ends at three hundred and forty-one dollars. The other ends at two hundred and sixty-three. Same shop, same sales, seventy-eight dollars apart.",
    "Then Alex opens a shop's website. A countdown clock is ticking. A badge says only three left.",
    "The website cheerfully announces that Alex has saved one hundred and seven dollars.",
    "And here's the thing. Alex hasn't saved one hundred and seven dollars. Alex is about to spend one hundred and eighty-three.",
    "Rule two: do the math. A discount isn't a saving. It's just a smaller bill. Add the list to the cart and Alex is at three hundred and forty-one dollars, which is forty-one dollars over budget.",
    "Rule four: let it sit for twenty-four hours.",
    "Do I need this, or did the timer need me to buy it?",
    "It just means the answer has to survive a night's sleep.",
    "That's thirty-seven under budget, and seventy-eight dollars less than the impulse cart.",
    "Check out the Money Leak Audit Workbook in the description.",
]
norm = lambda s: re.findall(r"[a-z0-9'-]+", s.lower().replace("’", "'"))
def main():
    script = (VOICE / "VOICE_SCRIPT.txt").read_text(); flat = norm(script); W = json.loads((VOICE / "words_full.json").read_text())
    hyp = [(re.findall(r"[a-z0-9']+", x["w"].lower()) or [""])[0] for x in W]; ref = [w.replace("-", " ").split()[0] if False else w for w in flat]
    # compare on a hyphen-free token stream; remember where each script word starts in that stream
    toks, owner = [], []
    for i, w in enumerate(flat):
        for p in w.split("-"): toks.append(p); owner.append(i)
    sm = difflib.SequenceMatcher(None, toks, hyp, autojunk=False); idx = {}
    for a, b, k in sm.get_matching_blocks():
        for j in range(k): idx[a + j] = b + j
    known = sorted(idx); T = {}
    for i in range(len(toks)):
        if i in idx: T[i] = (W[idx[i]]["s"], W[idx[i]]["e"])
        else:
            lo = max([k for k in known if k < i], default=None); hi = min([k for k in known if k > i], default=None)
            T[i] = (W[idx[lo]]["e"] + 0.04 * (i - lo), W[idx[lo]]["e"] + 0.04 * (i - lo) + 0.2) if lo is not None else (W[idx[hi]]["s"] - 0.1, W[idx[hi]]["s"])
    first_tok = {}; last_tok = {}
    for i, o in enumerate(owner): first_tok.setdefault(o, i); last_tok[o] = i
    audio, sr = sf.read(VOICE / "full.wav", dtype="float32"); track, cues, t0 = [], [], 0.0
    for ex in EXCERPTS:
        q = norm(ex); n = len(q); starts = [i for i in range(len(flat) - n + 1) if flat[i:i + n] == q]; assert len(starts) == 1, (ex[:40], starts)
        f, l = starts[0], starts[0] + n - 1; a = max(0.0, T[first_tok[f]][0] - LEAD); nxt = T[first_tok[l + 1]][0] - 0.03 if l + 1 < len(flat) else len(audio) / sr
        b = min(T[last_tok[l]][1] + TAIL, nxt, len(audio) / sr); seg = audio[int(a * sr):int(b * sr)]; track.append(seg)
        for i in range(f, l + 1): cues.append({"word": flat[i], "start": round(t0 + T[first_tok[i]][0] - a, 3), "end": round(t0 + T[last_tok[i]][1] - a, 3)})
        print(f"{a:7.2f}-{b:7.2f} ({b - a:5.2f} s) {ex[:70]}"); t0 += len(seg) / sr
    out = np.concatenate(track); sf.write(HERE / "short_audio_raw.wav", out, sr)
    (HERE / "short_cues.json").write_text(json.dumps({"duration": round(len(out) / sr, 3), "sentences": EXCERPTS, "words": cues}, indent=1, ensure_ascii=False))
    print("total narration:", round(len(out) / sr, 2), "s,", len(cues), "words,", int(len(out) / sr * 24), "frames")
if __name__ == "__main__": main()
