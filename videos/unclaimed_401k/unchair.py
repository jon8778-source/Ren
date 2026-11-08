"""Remove Maya's baked-in armchair from the armchair poses so she can sit in the H1 plate's own chair.
Chair pixels = low-saturation taupe/beige fabric, its brown legs and outline lines that touch only chair."""
import numpy as np
from PIL import Image
from scipy import ndimage
import colorsys

def hsv(a):
    r, g, b = [a[..., i].astype(np.float32) / 255 for i in range(3)]
    mx, mn = np.maximum(np.maximum(r, g), b), np.minimum(np.minimum(r, g), b)
    d = mx - mn
    s = np.where(mx > 0, d / np.maximum(mx, 1e-6), 0)
    h = np.zeros_like(mx)
    m = d > 1e-6
    hr = np.where(mx == r, ((g - b) / np.maximum(d, 1e-6)) % 6, np.where(mx == g, (b - r) / np.maximum(d, 1e-6) + 2, (r - g) / np.maximum(d, 1e-6) + 4))
    h = np.where(m, hr * 60, 0)
    return h, s, mx

def unchair(im, dbg=False):
    a = np.array(im.convert("RGBA")); al = a[..., 3] > 40
    h, s, v = hsv(a[..., :3])
    # fabric: warm grey (h 20-50, sat .05-.22, value .55-.9)  ; legs: brown dark (h 15-35, sat .35-.7, v .2-.45)
    fabric = al & (h > 15) & (h < 55) & (s > 0.04) & (s < 0.25) & (v > 0.5) & (v < 0.92)
    legs = al & (h > 10) & (h < 40) & (s > 0.3) & (v > 0.15) & (v < 0.45)
    chair = fabric | legs
    chair = ndimage.binary_closing(chair, iterations=2)
    # body-colour evidence: sweater (rust), navy, skin, hair, phone, shoes (near-white), earring
    rust = (h > 5) & (h < 22) & (s > 0.5) & (v > 0.4)
    navy = (h > 200) & (h < 250) & (s > 0.4) & (v < 0.5)
    skin = (h > 12) & (h < 35) & (s > 0.18) & (s < 0.55) & (v > 0.8)
    white = (s < 0.09) & (v > 0.9)
    body = al & ~chair & (rust | navy | skin | white)
    body = ndimage.binary_opening(body, iterations=1)
    # keep hair/phone/outlines that are dark & close to body evidence
    dark = al & ~chair & (v < 0.35)
    near = ndimage.binary_dilation(body, iterations=7)
    # dark pixels belong to body if their dark component touches the body mask dilated, but not if they only touch chair
    lab, n = ndimage.label(dark)
    keep = np.zeros_like(al)
    touch_body = ndimage.binary_dilation(body, iterations=3)
    touch_chair = ndimage.binary_dilation(chair, iterations=3)
    for i in range(1, n + 1):
        c = lab == i
        tb, tc = (c & touch_body).sum(), (c & touch_chair).sum()
        if tb > 0 and tb >= 0.15 * tc: keep |= c
    out = (body | keep)
    out = ndimage.binary_closing(out, iterations=3)
    out = ndimage.binary_fill_holes(out)
    core = ndimage.binary_opening(out, iterations=5)      # thin leftover chair outlines are not part of the core
    out &= ndimage.binary_dilation(core, iterations=9)
    # drop small specks
    lab, n = ndimage.label(out)
    sz = ndimage.sum(out, lab, range(1, n + 1))
    out = np.isin(lab, 1 + np.where(sz > 800)[0])
    # big leftover chair-fabric patches (enclosed between the legs) are removed; small ones are shoe shading
    fab = ndimage.binary_opening(out & fabric, iterations=1)
    fl, fn = ndimage.label(fab)
    fs = ndimage.sum(fab, fl, range(1, fn + 1))
    out &= ~ndimage.binary_dilation(np.isin(fl, 1 + np.where(fs > 700)[0]), iterations=2)
    # chair-coloured pixels INSIDE the body silhouette (e.g. hair highlights) stay
    res = a.copy(); res[..., 3] = np.where(out, a[..., 3], 0)
    return Image.fromarray(res, "RGBA")

if __name__ == "__main__":
    import sys
    for i in (1, 2, 3):
        im = Image.open(f"art/poses/armchair_{i:02d}.png"); o = unchair(im)
        o = o.crop(o.getbbox()); o.save(f"art/poses/maya_nochair_{i:02d}.png")
        bg = Image.new("RGBA", o.size, (60, 90, 60, 255)); bg.alpha_composite(o); bg.convert("RGB").save(f"/tmp/claude-0/nochair_{i}.png")
        print(i, im.size, o.size)
