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
FACE = {"brow": 1.08 * 70 * o2rig / 122}  # brows tuned against the original by eye

# Glasses: scale so the lens centres match the original's (427 and 530)
g = np.array(Image.open(P / "glasses.png"))[..., 3] < 60
lab, nl = ndimage.label(g)
edge = set(np.unique(np.r_[lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
holes = sorted([i for i in range(1, nl + 1) if i not in edge], key=lambda i: -(lab == i).sum())[:2]
holes = sorted(holes, key=lambda i: np.nonzero(lab == i)[1].mean())  # Ren's right lens (screen left) first
lens = [np.c_[np.nonzero(lab == i)[1], np.nonzero(lab == i)[0]].mean(axis=0) for i in holes]
k_glasses = (530 - 427) * o2rig / (lens[1][0] - lens[0][0])
G_PIVOT, G_ATTACH = (lens[0] + lens[1]) / 2, np.array(on_head(478.5, 407))
part("glasses", "glasses", G_PIVOT, "head", G_ATTACH, k_glasses, z=80)


# Face calibration. Every eye and mouth is placed by its own visual centre (the middle of its opaque
# bounding box) on one fixed anchor, then given the largest scale that keeps all its pixels inside a target
# region: the lens opening for eyes, the face inside the jawline (and below the nose) for mouths.
def centre(n):
    ys, xs = np.nonzero(alpha(n))
    return np.array([(xs.min() + xs.max()) / 2, (ys.min() + ys.max()) / 2])


def fit(n, anchor, region, k_max):
    """Largest k <= k_max so the part, centred on anchor and scaled by k, lies inside region."""
    ys, xs = np.nonzero(alpha(n))
    pts = np.c_[xs, ys] - centre(n)
    inside = lambda k: all(0 <= y < region.shape[0] and 0 <= x < region.shape[1] and region[y, x]
                           for x, y in np.rint(anchor + pts * k).astype(int))
    lo, hi = 0.0, k_max
    if inside(hi):
        return hi
    for _ in range(30):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if inside(mid) else (lo, mid)
    return lo


# The face inside the jawline, in head px: the skin region around the face centre, bounded by the outline
hd = np.array(Image.open(P / "head.png")).astype(int)
flab, _ = ndimage.label((hd[..., 3] > 128) & (hd[..., :3].mean(-1) > 110))
face = flab == flab[1200, 781]
rows = [np.nonzero(r)[0] for r in face]
FACE_W = max(r.max() - r.min() + 1 for r in rows if len(r))  # widest point, at the cheekbones
MOUTH_W_MAX = 0.40 * FACE_W
MOUTH_Y = 1431  # where the original's closed mouth sits (head px)
mrow = rows[MOUTH_Y]
MOUTH_C = np.array([(mrow.min() + mrow.max()) / 2, MOUTH_Y])  # on the face's centre line
nose_at, nose_k = np.array(on_head(481, 469)), o2rig / k_head
NOSE_BOTTOM = nose_at[1] + (np.nonzero(alpha("nose").any(1))[0].max() - meta["nose"]["h"] / 2) * nose_k
mouth_region = ndimage.binary_erosion(face, iterations=30)  # stay 30 head px clear of the jawline
mouth_region[: int(NOSE_BOTTOM + 25)] = False                 # and clear of the nose
# Target widths as a share of the face width; fit() shrinks any that would cross the jaw or the nose
MOUTH_SHARE = {"closed": 0.34, "smile": 0.36, "wince": 0.34, "open": 0.30, "wide": 0.32, "o": 0.14}
calib = {"face_width": int(FACE_W), "mouth_anchor": [float(v) for v in MOUTH_C], "mouth": {}, "eye": {}}
for mth, share in MOUTH_SHARE.items():
    n = f"mouth-{mth}"
    w = np.ptp(np.nonzero(alpha(n).any(0))[0]) + 1
    k = fit(n, MOUTH_C, mouth_region, share * FACE_W / w)
    part(n, n, centre(n), "head", MOUTH_C, k * k_head, z=71, slot="mouth")
    calib["mouth"][n] = {"width": round(w * k), "share": round(w * k / FACE_W, 3)}
    assert w * k <= MOUTH_W_MAX, n

part("nose", "nose", (meta["nose"]["w"] / 2, meta["nose"]["h"] / 2), "head", nose_at, o2rig, z=70)

# Eyes: anchor = the centre of each lens opening; region = that opening, 3 px clear of the rim (glasses px).
# Both sides of a set share one scale (the smaller fit), so a pair always matches.
for e in ["neutral", "closed", "happy", "wide", "surprised", "angry", "sleepy"]:
    ks = []
    for side, hole in zip("rl", holes):
        region = ndimage.binary_erosion(lab == hole, iterations=3)
        ks.append(fit(f"eye-{e}-{side}", lens["rl".index(side)], region, 1.5))
    k = min(ks)
    for side in "rl":
        n = f"eye-{e}-{side}"
        anchor = G_ATTACH + (lens["rl".index(side)] - G_PIVOT) * k_glasses / k_head  # lens centre in head px
        part(n, n, centre(n), "head", anchor, k * k_glasses, z=72, slot=f"eye-{side}")
    calib["eye"][e] = round(k * k_glasses / k_head, 4)
FACE["eye"] = rig["eye-neutral-r"]["scale"]
for side, bx in {"r": 425, "l": 539}.items():
    for b in ["brow", "brow-wide", "brow-surprised", "brow-sleepy"]:
        n = f"{b}-{side}"
        part(n, n, (meta[n]["w"] / 2, meta[n]["h"] / 2), "head", on_head(bx, 366), FACE["brow"], z=74, slot=f"brow-{side}")

# Arms: shoulder sockets on the torso; joints from each limb's long axis
for side, shoulder in {"r": (30, 150), "l": (432, 150)}.items():
    ua, ub, uw = ends(f"upperarm-{side}")
    fa, fb, fw = ends(f"forearm-{side}", inset_bot=12)
    part(f"upperarm-{side}", f"upperarm-{side}", ua, "torso", shoulder, bone=ang(ub - ua), z=53, end=list(map(float, ub)), width=uw)
    part(f"forearm-{side}", f"forearm-{side}", fa, f"upperarm-{side}", ub, bone=ang(fb - fa), z=52, end=list(map(float, fb)), width=fw)

# Hands. Each hand's wrist is measured from the band of pixels at its cut end: the band's long direction
# runs across the wrist, so the hand's rest axis (bone) is perpendicular to it, pointing into the hand.
# The pivot (wrist anchor) sits on that axis, WRIST_TUCK rig units inside the cut edge. The hand is a child
# of the forearm, attached at the forearm's end with bone along the forearm's axis, so at angle 0 it
# continues the forearm's line at any arm angle; its own angle is a wrist bend on top of that.
WRIST_TUCK = 10


def wrist(n, d, depth=45):
    """Wrist anchor (at the cut edge, on the centre line), rest axis (unit, into the hand), width across."""
    ys, xs = np.nonzero(alpha(n))
    pts = np.c_[xs, ys].astype(float)
    d = np.asarray(d, float) / np.linalg.norm(d)
    pr = pts @ d
    band = pts[pr > pr.max() - depth]
    c = band.mean(axis=0)
    across = np.linalg.svd(band - c, full_matrices=False)[2][0]
    ax = np.array([-across[1], across[0]])
    if ax @ d > 0:
        ax = -ax
    edge = c + ax * ((band - c) @ ax).min()
    return edge, ax, np.ptp((band - c) @ across)


def cuff_width(n):
    ys, xs = np.nonzero(alpha(n))
    pts = np.c_[xs, ys].astype(float)
    b = np.radians(rig[n]["bone"])
    v = np.array([np.cos(b), np.sin(b)])
    band = pts[pts @ v > (pts @ v).max() - 20]
    return np.ptp(band @ np.array([-v[1], v[0]]))


CUFF = cuff_width("forearm-r")
# Sheet hands share one scale: their mean wrist width is 85% of the cuff, so each wrist tucks inside it
SHEET_HANDS = {"point": {"r": (-1, 0), "l": (1, 0)}, "thumbsup": {"r": (-1, 0), "l": (1, 0)}, "fist": {"r": (-1, 0), "l": (1, 0)},
               "open": {"r": (0, 1), "l": (0, 1)}, "hold": {"r": (-1, 1), "l": (1, 1)}}
k_hand = 0.85 * CUFF / np.mean([wrist(f"hand-{h}-{s}", d)[2] for h, ds in SHEET_HANDS.items() for s, d in ds.items()])
hands = {}


def hand(name, src, d, side, k):
    edge, ax, w = wrist(src, d)
    part(name, src, edge + ax * WRIST_TUCK / k, f"forearm-{side}", rig[f"forearm-{side}"]["end"], k, bone=ang(ax), z=51, slot=f"hand-{side}",
         wrist_width=round(float(w * k), 1))
    hands[name] = {"rest": round(ang(ax), 2), "wrist_width": round(float(w * k), 1)}


for side in "rl":
    # Relaxed hand from the body sheet (its own scale): wrist at its top, fingers straight down at rest
    hand(f"hand-relaxed-{side}", f"hand-relaxed-{side}", (0, -1), side, 1.0)
    for pose, dirs in SHEET_HANDS.items():
        hand(f"hand-{pose}-{side}", f"hand-{pose}-{side}", dirs[side], side, k_hand)
# Pointing outward: the other column's pointing hand on each arm (its finger points away from the body)
for side, other, d in (("r", "l", (1, 0)), ("l", "r", (-1, 0))):
    hand(f"hand-pointout-{side}", f"hand-point-{other}", d, side, k_hand)

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
       "colors": {"sleeve": "#363a4d", "pants": "#32363b"}, "face": calib, "hands": {"cuff_width": round(float(CUFF), 1), "parts": hands}}
(HERE / "ren" / "rig.json").write_text(json.dumps(out, indent=1) + "\n")
shutil.rmtree(PUBLIC, ignore_errors=True)
PUBLIC.mkdir(parents=True)
for f in P.glob("*.png"):
    shutil.copy(f, PUBLIC / f.name)
print(json.dumps(calib, indent=1))
print(f"{len(rig)} parts; head x{k_head:.3f}, glasses x{k_glasses:.3f}, hands x{k_hand:.3f}, eyes x{FACE['eye']:.3f}")
