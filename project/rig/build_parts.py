"""Cut Ren's puppet-rig parts out of the source sheets into transparent PNGs.

  .tools/venv/bin/python rig/build_parts.py

Reads rig/ren/source/*.jpg and writes rig/ren/parts/<part>.png plus rig/ren/parts/parts.json
(size and source box of every part). Background is removed by flood-filling the near-white area
that touches each crop's border, so white shapes enclosed by an outline (eye whites, the T-shirt,
shoe soles) stay opaque. Hands are colour-matched to the blank head's skin tone.
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

ROOT = Path(__file__).resolve().parent / "ren"
SRC, OUT = ROOT / "source", ROOT / "parts"
OUT.mkdir(parents=True, exist_ok=True)
PAD = 8


def load(name):
    return np.array(Image.open(SRC / name).convert("RGB"))


def cut(rgb, box, keep_all=False, white=232, fill_shape=False):
    """Crop box=(x0, y0, x1, y1) with padding; transparent where near-white connects to the border."""
    x0, y0, x1, y1 = box
    h, w = rgb.shape[:2]
    x0, y0, x1, y1 = max(0, x0 - PAD), max(0, y0 - PAD), min(w, x1 + PAD), min(h, y1 + PAD)
    c = rgb[y0:y1, x0:x1]
    light = c.min(axis=2) >= white
    lab, _ = ndimage.label(light)
    edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bg = np.isin(lab, list(edge))
    fg = ~bg
    if fill_shape:  # open outlines (eye lids): close the gaps, then fill the inside
        fg |= ndimage.binary_fill_holes(ndimage.binary_closing(fg, iterations=7))
    if not keep_all:  # keep the biggest piece plus anything not touching the crop edge
        flab, n = ndimage.label(fg)
        if n > 1:
            sizes = ndimage.sum(fg, flab, range(1, n + 1))
            border = set(np.unique(np.concatenate([flab[0], flab[-1], flab[:, 0], flab[:, -1]]))) - {0}
            main = int(np.argmax(sizes)) + 1
            fg = np.isin(flab, [i for i in range(1, n + 1) if i == main or (i not in border and sizes[i - 1] > 20)])
    m = Image.fromarray((fg * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.8))
    out = Image.fromarray(c).convert("RGBA")
    out.putalpha(m)
    bb = out.getbbox()
    return out.crop(bb), (x0 + bb[0], y0 + bb[1])


parts = {}


def save(name, img, origin, sheet):
    img.save(OUT / f"{name}.png")
    parts[name] = {"w": img.width, "h": img.height, "sheet": sheet, "origin": list(origin)}


# Body sheet (head on this sheet is replaced by the blank head)
body = load("ren-body-sheet.jpg")
B = {
    "glasses": (1193, 282, 1428, 363),
    "torso": (698, 491, 1158, 1278),
    "upperarm-r": (438, 592, 634, 925), "upperarm-l": (1222, 592, 1419, 925),
    "forearm-r": (362, 941, 512, 1228), "forearm-l": (1345, 941, 1494, 1228),
    "hand-relaxed-r": (320, 1244, 455, 1463), "hand-relaxed-l": (1401, 1244, 1537, 1463),
    "shoe-r": (563, 2077, 783, 2247), "shoe-l": (1074, 2077, 1294, 2247),
}
for k, box in B.items():
    if k == "glasses":
        x0, y0, x1, y1 = box
        c = body[y0 - PAD:y1 + PAD, x0 - PAD:x1 + PAD].astype(float)
        a = np.clip((235 - c.mean(axis=2)) / 120, 0, 1)
        a = ndimage.grey_dilation(a, size=(2, 2))  # the original's frame is a little thicker
        c[a > 0.5] = np.minimum(c[a > 0.5], 60)
        img = Image.fromarray(np.dstack([c, a * 255]).astype(np.uint8), "RGBA")
        bb = img.getbbox()
        save(k, img.crop(bb), (x0 - PAD + bb[0], y0 - PAD + bb[1]), "body")
        continue
    img, o = cut(body, box)
    save(k, img, o, "body")
KNEE = 1683  # narrowest row of each leg: the knee notch
for side, (x0, x1) in {"r": (674, 867), "l": (989, 1183)}.items():
    img, o = cut(body, (x0, 1271, x1, KNEE))
    save(f"thigh-{side}", img, o, "body")
    img, o = cut(body, (x0, KNEE - 30, x1, 2044))  # shin starts a little higher, tucked behind the thigh
    save(f"shin-{side}", img, o, "body")

# Blank head, scaled later in assembly. Its neck is trimmed a little below the chin with a soft
# fade, so it overlaps the torso's neck without showing the cut line.
head = load("ren-head-blank.jpg")
img, o = cut(head, (0, 0, head.shape[1], head.shape[0]))
ha = np.array(img)
col = ha[:, ha.shape[1] // 2]
CHIN = int(next(y for y in range(int(ha.shape[0] * 0.7), ha.shape[0]) if col[y, :3].mean() < 90 and col[y, 3] > 200))
ramp = np.clip((CHIN + 130 - np.arange(ha.shape[0])) / 40, 0, 1)
ha[..., 3] = (ha[..., 3] * ramp[:, None]).astype(np.uint8)
img = Image.fromarray(ha, "RGBA")
img = img.crop(img.getbbox())
save("head", img, o, "head")
parts["head"]["chin"] = CHIN

# Face sheet: eyes and brows per expression, split left/right; mouths
face = load("ren-face-sheet.jpg")
F = {
    "brow-r": (60, 296, 186, 338), "brow-l": (250, 296, 377, 338),                 # from the neutral set
    "eye-neutral-r": (76, 344, 180, 409), "eye-neutral-l": (258, 344, 360, 409),
    "eye-closed-r": (450, 330, 560, 400), "eye-closed-l": (640, 330, 750, 400),
    "eye-happy-r": (460, 520, 560, 570), "eye-happy-l": (640, 520, 740, 570),
    "eye-wide-r": (76, 500, 180, 598), "eye-wide-l": (256, 500, 360, 598),
    "brow-wide-r": (76, 462, 180, 508), "brow-wide-l": (256, 462, 362, 508),
    "eye-surprised-r": (458, 145, 560, 212), "eye-surprised-l": (642, 145, 742, 213),
    "brow-surprised-r": (444, 82, 566, 137), "brow-surprised-l": (634, 82, 757, 137),
    "eye-angry-r": (826, 115, 963, 206), "eye-angry-l": (1005, 115, 1142, 206),
    "eye-sleepy-r": (840, 336, 950, 420), "eye-sleepy-l": (1020, 336, 1130, 420),
    "brow-sleepy-r": (832, 292, 950, 338), "brow-sleepy-l": (1019, 292, 1137, 338),
    "mouth-closed": (70, 740, 216, 800), "mouth-wide": (450, 715, 600, 805),
    "mouth-o": (664, 714, 725, 791), "mouth-smile": (790, 728, 944, 800), "mouth-wince": (989, 742, 1144, 781),
}
for k, box in F.items():
    img, o = cut(face, box, keep_all=True, white=250)
    save(k, img, o, "face")
mo = load("ren-mouth-slightly-open.jpg")
img, o = cut(mo, (680, 820, 1360, 1200))  # the clean mouth only; the smudge below it is left out
save("mouth-open", img, o, "mouth")

# Nose: none on the sheets, so take the original's nose lines (darker than the surrounding skin)
orig = load("ren-original.jpg").astype(float)
x0, y0, x1, y1 = 455, 456, 508, 488  # below the glasses rim
c = orig[y0:y1, x0:x1]
skin = np.median(c.reshape(-1, 3), axis=0)
dark = np.clip((skin.mean() - c.mean(axis=2)) / 70, 0, 1)
nose = np.dstack([c.astype(np.uint8), (dark * 255).astype(np.uint8)])
img = Image.fromarray(nose, "RGBA")
bb = img.getbbox()
save("nose", img.crop(bb), (x0 + bb[0], y0 + bb[1]), "original")

# Hands sheet: colour-matched to the head's skin, scaled to the body sheet's relaxed hands later
hands = load("ren-hands-sheet.jpg")
H = {
    "point": ((342, 120, 848, 410), (1009, 120, 1515, 410)),
    "thumbsup": ((478, 497, 819, 858), (1038, 497, 1379, 858)),
    "fist": ((452, 977, 798, 1228), (1059, 977, 1404, 1228)),
    "open": ((444, 1310, 805, 1769), (1051, 1310, 1413, 1769)),
    "hold": ((412, 1860, 774, 2217), (1083, 1860, 1445, 2217)),
}


def skin_mean(rgb):
    p = rgb.reshape(-1, 3).astype(float)
    m = (p[:, 0] > 170) & (p[:, 0] < 252) & (p[:, 0] - p[:, 2] > 25) & (p[:, 1] > 120)
    return p[m].mean(axis=0)


head_skin, hand_skin = skin_mean(head), skin_mean(hands)

# The torso's neck is a little darker than the blank head: match its skin pixels to the head
t = np.array(Image.open(OUT / "torso.png")).astype(float)
sk = (t[..., 0] > 150) & (t[..., 0] - t[..., 2] > 30) & (t[..., 1] > 110) & (t[..., 3] > 0)
neck_skin = t[sk][:, :3].mean(axis=0)
t[sk, :3] = np.clip(t[sk, :3] * (head_skin / neck_skin), 0, 255)
Image.fromarray(t.astype(np.uint8), "RGBA").save(OUT / "torso.png")
for side in "rl":  # the body sheet's relaxed hands are a shade lighter than the head too
    hp = OUT / f"hand-relaxed-{side}.png"
    t = np.array(Image.open(hp)).astype(float)
    sk = (t[..., 0] > 150) & (t[..., 0] - t[..., 2] > 30) & (t[..., 3] > 0)
    t[..., :3] = np.clip(t[..., :3] * (head_skin / t[sk][:, :3].mean(axis=0)), 0, 255)
    Image.fromarray(t.astype(np.uint8), "RGBA").save(hp)
gain = head_skin / hand_skin
for pose, (a, b) in H.items():
    for side, box in (("r", a), ("l", b)):
        img, o = cut(hands, box)
        arr = np.array(img).astype(float)
        arr[..., :3] = np.clip(arr[..., :3] * gain, 0, 255)
        save(f"hand-{pose}-{side}", Image.fromarray(arr.astype(np.uint8), "RGBA"), o, "hands")

(OUT / "parts.json").write_text(json.dumps({"skin": {"head": head_skin.round(1).tolist(), "hands_sheet": hand_skin.round(1).tolist(),
                                                     "relaxed_hands": skin_mean(body[1244:1463, 320:455]).round(1).tolist(),
                                                     "original": skin_mean(load("ren-original.jpg")).round(1).tolist()},
                                            "parts": parts}, indent=1) + "\n")
print(len(parts), "parts; skin head", head_skin.round(), "hands sheet", hand_skin.round(), "gain", gain.round(3))
