"""Build Ren's rig definition (pivots, attach points, scales, layer order) from the cut parts.

  .tools/venv/bin/python rig/make_rig.py

Writes rig/ren/rig.json and copies the parts to remotion/public/rig/ren/. Units are body-sheet pixels.
Each part has: pivot (its own image px), parent, attach (parent image px), scale (absolute) and
bone angle (degrees in its image, 90 = pointing down; the renderer rotates it so 0 = straight down).
"""
import json
import shutil
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = Path(__file__).resolve().parent
P = HERE / "ren" / "parts"
meta = json.loads((P / "parts.json").read_text())["parts"]
PUBLIC = HERE.parent / "remotion" / "public" / "rig" / "ren"


def alpha(n):
    return np.array(Image.open(P / f"{n}.png"))[..., 3] > 128


def axis(n):
    """Centroid, unit long axis (pointing down the image), length along it and width across it."""
    m = alpha(n)
    ys, xs = np.nonzero(m)
    pts = np.c_[xs, ys].astype(float)
    c = pts.mean(axis=0)
    v = np.linalg.svd(pts - c, full_matrices=False)[2][0]
    if v[1] < 0:
        v = -v
    t = (pts - c) @ v
    w = np.abs((pts - c) @ np.array([-v[1], v[0]]))
    return c, v, t.min(), t.max(), 2 * np.percentile(w, 95)


def ends(n, inset_top=None, inset_bot=None):
    """Joint points near both ends of a limb: inset by half the width (round caps) unless told otherwise."""
    c, v, t0, t1, w = axis(n)
    a = c + v * (t0 + (w / 2 if inset_top is None else inset_top))
    b = c + v * (t1 - (w / 2 if inset_bot is None else inset_bot))
    return a, b, w


def end_centre(n, d, band=6):
    """Centre of the part's extreme edge in direction d (e.g. the wrist cut of a hand)."""
    m = alpha(n)
    ys, xs = np.nonzero(m)
    pts = np.c_[xs, ys].astype(float)
    d = np.asarray(d, float) / np.linalg.norm(d)
    proj = pts @ d
    sel = pts[proj > proj.max() - band]
    return sel.mean(axis=0), pts.mean(axis=0)


ang = lambda v: float(np.degrees(np.arctan2(v[1], v[0])))
rig = {}


def part(name, src, pivot, parent=None, attach=None, scale=1.0, bone=90.0, z=0, **kw):
    rig[name] = {"src": f"rig/ren/{src}.png", "w": meta[src]["w"], "h": meta[src]["h"], "pivot": [round(float(x), 1) for x in pivot],
                 "parent": parent, "attach": None if attach is None else [round(float(x), 1) for x in attach],
                 "scale": round(float(scale), 4), "bone": round(float(bone), 2), "z": z, **kw}


sheet = lambda n, p: np.asarray(p, float) - np.asarray(meta[n]["origin"], float)  # sheet px -> part px
to_sheet = lambda n, p: np.asarray(p, float) + np.asarray(meta[n]["origin"], float)

# Torso is the root; its pivot is the middle of the hips
tw, th = meta["torso"]["w"], meta["torso"]["h"]
part("torso", "torso", (tw / 2, th * 0.9), z=50)

# Head: blank head scaled to the body sheet's head width, pivot at the chin
HEAD_W = 1105 - 758  # the replaced sheet head's width
k_head = HEAD_W / meta["head"]["w"]
chin = meta["head"]["chin"]
part("head", "head", (meta["head"]["w"] / 2, chin), "torso", (232, 32), k_head, z=60)

# Face, placed where the original's features are. The blank head matches the original at scale 0.232, offset (304, 174)
O_S, O_X, O_Y = 0.232, 304, 174
on_head = lambda x, y: ((x - O_X) / O_S, (y - O_Y) / O_S)
o2rig = k_head / O_S  # original px -> rig units
FACE = {"eye": 1.18 * 50 * o2rig / 100, "brow": 1.08 * 70 * o2rig / 122, "mouth": 93 * o2rig / 142}  # eyes/brows tuned against the original by eye
for side, (ex, bx) in {"r": (427, 425), "l": (530, 539)}.items():
    for e in ["neutral", "closed", "happy", "wide", "surprised", "angry", "sleepy"]:
        n = f"eye-{e}-{side}"
        part(n, n, (meta[n]["w"] / 2, meta[n]["h"] / 2), "head", on_head(ex, 409), FACE["eye"], z=72, slot=f"eye-{side}")
    for b in ["brow", "brow-wide", "brow-surprised", "brow-sleepy"]:
        n = f"{b}-{side}"
        part(n, n, (meta[n]["w"] / 2, meta[n]["h"] / 2), "head", on_head(bx, 366), FACE["brow"], z=74, slot=f"brow-{side}")
part("nose", "nose", (meta["nose"]["w"] / 2, meta["nose"]["h"] / 2), "head", on_head(481, 469), o2rig, z=70)
for mth in ["closed", "smile", "wide", "o", "wince"]:
    n = f"mouth-{mth}"
    part(n, n, (meta[n]["w"] / 2, meta[n]["h"] * (0.3 if mth in ("closed", "smile") else 0.5)), "head", on_head(484, 501), FACE["mouth"], z=71, slot="mouth")
n = "mouth-open"
part(n, n, (meta[n]["w"] / 2, meta[n]["h"] / 2), "head", on_head(484, 506), FACE["mouth"] * 0.65 * 142 / 146, z=71, slot="mouth")

# Glasses: scale so the lens centres match the original's (427 and 530)
g = np.array(Image.open(P / "glasses.png"))[..., 3] < 60
lab, nl = ndimage.label(g)
edge = set(np.unique(np.r_[lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
holes = sorted([i for i in range(1, nl + 1) if i not in edge], key=lambda i: -(lab == i).sum())[:2]
lens = sorted([np.c_[np.nonzero(lab == i)[1], np.nonzero(lab == i)[0]].mean(axis=0) for i in holes], key=lambda p: p[0])
k_glasses = (530 - 427) * o2rig / (lens[1][0] - lens[0][0])
part("glasses", "glasses", (lens[0] + lens[1]) / 2, "head", on_head(478.5, 407), k_glasses, z=80)

# Arms: shoulder sockets on the torso; joints from each limb's long axis
for side, shoulder in {"r": (30, 150), "l": (432, 150)}.items():
    ua, ub, uw = ends(f"upperarm-{side}")
    fa, fb, fw = ends(f"forearm-{side}", inset_bot=12)
    part(f"upperarm-{side}", f"upperarm-{side}", ua, "torso", shoulder, bone=ang(ub - ua), z=53, end=list(map(float, ub)), width=uw)
    part(f"forearm-{side}", f"forearm-{side}", fa, f"upperarm-{side}", ub, bone=ang(fb - fa), z=52, end=list(map(float, fb)), width=fw)
    # Relaxed hand from the body sheet: wrist at its top
    wr, cen = end_centre(f"hand-relaxed-{side}", (0, -1))
    wr = wr + np.array([0, 10])
    part(f"hand-relaxed-{side}", f"hand-relaxed-{side}", wr, f"forearm-{side}", fb, bone=ang(cen - wr), z=51, slot=f"hand-{side}")

# Sheet hands: scaled to the relaxed hand (by hand length, wrist to fingertip), wrist pivot
rel_len = axis("hand-relaxed-r")[3] - axis("hand-relaxed-r")[2]
open_len = axis("hand-open-r")[3] - axis("hand-open-r")[2]
k_hand = rel_len / open_len
WRIST = {"point": {"r": (-1, 0), "l": (1, 0)}, "thumbsup": {"r": (-1, 0), "l": (1, 0)}, "fist": {"r": (-1, 0), "l": (1, 0)},
         "open": {"r": (0, 1), "l": (0, 1)}, "hold": {"r": (-1, 1), "l": (1, 1)}}
for pose, dirs in WRIST.items():
    for side, d in dirs.items():
        n = f"hand-{pose}-{side}"
        wr, cen = end_centre(n, d)
        wr = wr - np.asarray(d, float) / np.linalg.norm(d) * 14  # pivot a little inside the wrist end
        part(n, n, wr, f"forearm-{side}", rig[f"forearm-{side}"]["end"], k_hand, bone=ang(cen - wr), z=51, slot=f"hand-{side}")

# Legs: keep the sheet's own geometry at hip, knee and ankle
KNEE = 1683
HIPS = {"r": (160, 690), "l": (302, 690)}  # torso px, under the dark hip piece
for side in ["r", "l"]:
    th_, sh_, so = f"thigh-{side}", f"shin-{side}", f"shoe-{side}"
    tm = alpha(th_)
    xs = np.nonzero(tm[min(40, tm.shape[0] - 1)])[0]
    hip = np.array([xs.mean(), 40.0])
    part(th_, th_, hip, "torso", HIPS[side], z=30)
    sm = alpha(sh_)
    k_row = KNEE - meta[sh_]["origin"][1]
    xs = np.nonzero(sm[k_row])[0]
    knee_p = np.array([xs.mean(), k_row])
    part(sh_, sh_, knee_p, th_, sheet(th_, to_sheet(sh_, knee_p)), z=28)
    bot = sm.shape[0] - 14
    xs = np.nonzero(sm[bot])[0]
    ankle_s = to_sheet(sh_, (xs.mean(), bot))           # on the shin, sheet px
    shoe_top = meta[so]["origin"][1] + 18                 # a little into the shoe opening
    part(so, so, sheet(so, (ankle_s[0], shoe_top)), sh_, sheet(sh_, ankle_s), z=34)

layers = sorted(rig, key=lambda n: rig[n]["z"])
out = {"units": "body-sheet px", "parts": rig, "scales": {"head": k_head, "glasses": k_glasses, "hand": k_hand, **FACE},
       "colors": {"sleeve": "#363a4d", "pants": "#32363b"}}
(HERE / "ren" / "rig.json").write_text(json.dumps(out, indent=1) + "\n")
shutil.rmtree(PUBLIC, ignore_errors=True)
PUBLIC.mkdir(parents=True)
for f in P.glob("*.png"):
    shutil.copy(f, PUBLIC / f.name)
print(f"{len(rig)} parts; head x{k_head:.3f}, glasses x{k_glasses:.3f}, hands x{k_hand:.3f}, eyes x{FACE['eye']:.3f}")
