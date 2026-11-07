"""Automated timeline regression checks for a rendered Free Money pilot. Supplements visual inspection, never replaces it.

  project/.tools/venv/bin/python videos/free_money/qa_timeline.py /output/free_money_S1_S2_pilot_rev03_1.mp4

Checks (each prints PASS/FAIL, exit code 1 on any FAIL):
  1. shot list: contiguous (no gap or overlap), ordered, frame-aligned, durations add up to the video, v3 caps
  2. scene order: shots follow the script's phrase order exactly (S1 then S2, no repeats or skips)
  3. assets: every approved asset the renderer reads exists and is non-empty; matted Ren PNGs are not blank
  4. video: full decode with errors fatal; frame count equals shot frames
  5. inserts: no A-B-A pattern (a frame that differs from both neighbours while the neighbours match each other)
  6. cuts land on shot boundaries: every hard cut in the video sits exactly on a frame where a shot starts (or inside the
     declared page-peel window), and every boundary that should be a hard cut is one (catches one-frame-late cuts)
  7. flashes: no single frame whose brightness jumps and returns within 2 frames
"""
import json, subprocess, sys
from pathlib import Path
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FPS = 24
CAPS = {"ren": 5.5, "story": 2.5, "graphic": 3.5}
mp4 = Path(sys.argv[1])
rep = json.loads((mp4.parent / (mp4.stem + "_report.json")).read_text())
shots = rep["shots"]
results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    print(("PASS " if ok else "FAIL ") + name + (f"  [{detail}]" if detail else ""), flush=True)


# 1. shot list
fr = lambda x: round(x * FPS)
gaps = [(a["i"], b["i"]) for a, b in zip(shots, shots[1:]) if fr(a["end"]) != fr(b["start"])]
check("1a shots contiguous (no gap/overlap)", not gaps, str(gaps))
check("1b shots frame-aligned", all(abs(s["start"] * FPS - fr(s["start"])) < 0.05 and abs(s["end"] * FPS - fr(s["end"])) < 0.05 for s in shots))
check("1c shot frames add up to the video", sum(fr(s["end"]) - fr(s["start"]) for s in shots) == rep["frames"], f"{sum(fr(s['end']) - fr(s['start']) for s in shots)} vs {rep['frames']}")
over = [(s["i"], s["type"]) for s in shots if s["end"] - s["start"] > CAPS[s["type"]] + 1e-6]
check("1d v3 shot caps", not over, str(over))
# 2. order
sys.path.insert(0, str(HERE))
import plan_data as pd
script = " ".join(pd.scene_text()[k] for k in ("S1", "S2")).split()
phr = " ".join(s["phrase"] for s in shots).split()
check("2 scene order = script order (phrases tile S1 then S2)", phr == script, f"{len(phr)} vs {len(script)} words")
check("2b scenes in order S1 -> S2", [s["scene"] for s in shots] == sorted([s["scene"] for s in shots]))
# 3. assets
lib = ROOT / "library"
need = [lib / "supporting_assets" / "backgrounds" / n for n in ("Porch_background_16x9.png", "Office_background_16x9.png", "Office_parking_lot_car_16x9.png")]
need += [lib / "supporting_assets" / "characters" / "Dev_pay_stub.png", lib / "supporting_assets" / "props" / "HR_folder_page6_prop.png"]
need += [HERE / "matted" / f"{n}.png" for n in ("Ren_1_neutral", "Ren_2_hand_on_chest_talking", "Ren_3_thinking_bust", "Ren_4_pointing", "Ren_extra_thinking_full_body", "Ren_full_body_presenting", "Ren_full_body_standing")]
need += [ROOT / "assets" / "ren_library" / "ren_hold_phone.mp4", HERE / "voice" / "S1.wav", HERE / "voice" / "S2.wav", HERE / "voice" / "words_S1.json", HERE / "voice" / "words_S2.json"]
missing = [str(p.relative_to(ROOT)) for p in need if not p.exists() or p.stat().st_size == 0]
check("3a approved assets present", not missing, str(missing))
blank = [p.name for p in need if p.suffix == ".png" and p.parent.name == "matted" and p.exists() and (np.array(Image.open(p))[..., 3] > 128).mean() < 0.1]
check("3b matted Ren stills not blank", not blank, str(blank))
# 4. decode
r = subprocess.run(["ffmpeg", "-v", "error", "-xerror", "-i", str(mp4), "-f", "null", "-"], capture_output=True, text=True)
check("4a full decode, errors fatal", r.returncode == 0 and not r.stderr.strip(), r.stderr.strip()[:120])
raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(mp4), "-vf", "scale=160:90,format=gray", "-f", "rawvideo", "-"])
F = np.frombuffer(raw, np.uint8).reshape(-1, 90, 160).astype(np.float32)
check("4b decoded frame count", len(F) == rep["frames"], f"{len(F)} vs {rep['frames']}")
D = np.abs(np.diff(F, axis=0)).mean((1, 2))           # D[k] = difference between frame k and k+1
# 5. A-B-A inserts
aba = []
for k in range(1, len(F) - 1):
    d_in, d_out = D[k - 1], D[k]
    d_skip = np.abs(F[k + 1] - F[k - 1]).mean()
    if d_in > 6 and d_out > 6 and d_skip < 0.35 * min(d_in, d_out):
        aba.append((k, round(k / FPS, 3)))
check("5 no one-frame inserts (A-B-A)", not aba, str(aba))
# also two-frame inserts
aabb = []
for k in range(1, len(F) - 2):
    if D[k - 1] > 6 and D[k + 1] > 6 and D[k] < 3 and np.abs(F[k + 2] - F[k - 1]).mean() < 0.35 * min(D[k - 1], D[k + 1]):
        aabb.append((k, round(k / FPS, 3)))
check("5b no two-frame inserts", not aabb, str(aabb))
# 6. cuts on boundaries
starts = {fr(s["start"]) for s in shots[1:]}
peel_start = next(fr(s["start"]) for s in shots if s["name"] == "desk_salary") - round(0.7 * FPS)
peel_end = next(fr(s["start"]) for s in shots if s["name"] == "desk_salary")
hard = [k + 1 for k in range(len(D)) if D[k] > 12 and not (peel_start <= k + 1 <= peel_end)]       # frame index where the new picture first shows
stray = [k for k in hard if k not in starts]
check("6a every hard cut lands on a shot start (none late/early)", not stray, f"stray cuts at frames {stray}")
soft = []                                              # boundaries that should be cuts but are not visible one frame late
for s in shots[1:]:
    k = fr(s["start"])
    if peel_start <= k <= peel_end + 1:
        continue
    if k - 1 < len(D) and D[k - 1] < 1.0 and np.abs(F[min(k + 6, len(F) - 1)] - F[k - 1]).mean() > 8:
        soft.append((s["i"], k))
check("6b no boundary shows the previous shot for an extra frame", not soft, str(soft))
# the page peel ends on the incoming scene's first frame
tail = [round(float(np.abs(F[k] - F[peel_end]).mean()), 1) for k in range(peel_end - 2, peel_end + 3)]
check("6c page peel hands over to the desk shot without a stray frame", np.abs(F[peel_end] - F[peel_end + 1]).mean() < 3 and np.abs(F[peel_end - 1] - F[peel_end]).mean() < 25, f"frame diffs around the handover {tail}")
# 7. flashes
lum = F.mean((1, 2))
flash = [k for k in range(1, len(F) - 1) if abs(lum[k] - lum[k - 1]) > 12 and abs(lum[k] - lum[k + 1]) > 12 and abs(lum[k + 1] - lum[k - 1]) < 6]
check("7 no single-frame brightness flashes", not flash, str(flash))
ok = all(r[1] for r in results)
(mp4.parent / (mp4.stem + "_qa_timeline.json")).write_text(json.dumps([{"check": n, "pass": p, "detail": d} for n, p, d in results], indent=1))
print("OVERALL", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
