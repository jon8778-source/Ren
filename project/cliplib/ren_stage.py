"""Ren staging standard: correct scale on the floor, grounded feet, and smooth (no-shake) placement.

Reusable by any Ren video renderer (extracted from the Free Money production, November 2026). Rules are in
project/REN_VIDEO_RULES.md, section "Character scale, grounding and smooth motion".

  height_px(plate, y_feet)           how tall a standing person is, in plate pixels, at floor row y_feet
  stand(frame, cam, plate, img, x, y_feet, ...)   place a standing figure at that scale, with a contact shadow
  paste_smooth(frame, img, x, y, w, h)            composite at a FRACTIONAL position and size (no 1 px jumps)
  place_smooth(cam, frame, im, x, bottom, h_plate)   a camera's figure-placement method, sub-pixel version

`cam` is any object with .k (plate-to-frame scale) and .pt(x, y) (plate point to frame point), e.g. the Cam class in
videos/free_money/fm_rev031.py. Frames are RGBA PIL images.

Why: sizing a figure by eye (a fixed pixel height, feet on the frame edge) gives the wrong scale against desks, chairs and
cars, and resizing to whole pixels each frame while the camera moves makes the figure tremble by up to a pixel.
"""
from PIL import Image, ImageDraw, ImageFilter

# Per-plate perspective, measured from objects of known size in each approved plate:
#   office: chair 105 cm, desk 75 cm, pedestal, bookshelf, file cabinet     -> camera ~1.07 m, horizon at plate row 507
#   porch:  door 2.0 m, bench seat 45 cm                                    -> camera ~1.02 m, horizon at plate row 384
#   lot:    car tyre 63 cm, car roof 1.45 m                                 -> camera ~1.10 m, horizon at plate row 454
# (horizon row in plate pixels, camera height in cm). Each plate is a pinhole view, so for a person at floor row y:
#   height_px = cm * (y - horizon) / camera_height
PLATE_GEOM = {"OFFICE": (507, 107), "PORCH": (384, 102), "LOT": (454, 110)}
REN_CM = 175


def height_px(plate, y_feet, cm=REN_CM):
    hor, cam_cm = PLATE_GEOM[plate]
    return cm * (y_feet - hor) / cam_cm


# ---------------------------------------------------------------------------------------------
# Smooth placement. The figure is pre-scaled once per size step (sharp LANCZOS), then mapped to its exact float rectangle with
# a bicubic affine transform, so position and size change smoothly from frame to frame.
_MIP = {}
_MIP_STEP = 12


def _mip(img, h):
    key = (id(img), int(h // _MIP_STEP))
    m = _MIP.get(key)
    if m is None:
        th = int(h // _MIP_STEP) * _MIP_STEP + _MIP_STEP
        tw = max(1, round(img.width * th / img.height))
        m = img.resize((tw, th), Image.LANCZOS)
        _MIP[key] = m
    return m


def paste_smooth(frame, img, x, y, w, h):
    """Composite `img` (RGBA) onto `frame` (RGBA) filling the float rectangle (x, y, w, h)."""
    W, H = frame.size
    m = _mip(img, h)
    sx, sy = m.width / w, m.height / h
    x0, y0 = max(0, int(x // 1) - 2), max(0, int(y // 1) - 2)
    x1, y1 = min(W, int(-(-(x + w) // 1)) + 2), min(H, int(-(-(y + h) // 1)) + 2)
    if x1 <= x0 or y1 <= y0:
        return
    out = m.transform((x1 - x0, y1 - y0), Image.AFFINE, (sx, 0, (x0 - x) * sx, 0, sy, (y0 - y) * sy), Image.BICUBIC)
    frame.alpha_composite(out, (x0, y0))


def place_smooth(cam, frame, im, x, bottom, h_plate):
    """Sub-pixel version of a Cam.place(frame, im, x, bottom, h_plate): feet centred at plate point (x, bottom)."""
    h = h_plate * cam.k
    w = im.width * h / im.height
    sx, sy = cam.pt(x, bottom)
    paste_smooth(frame, im, sx - w / 2, sy - h, w, h)
    return (sx - w / 2, sy - h, sx + w / 2, sy)


# ---------------------------------------------------------------------------------------------
# Grounding: a tight contact shadow under the feet (not a soft cloud).
_SHADOW = None


def _shadow_patch():
    global _SHADOW
    if _SHADOW is None:
        pw, ph = 600, 120
        lay = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        rx, ry = 270, 46
        d.ellipse((pw / 2 - rx, ph / 2 - ry, pw / 2 + rx, ph / 2 + ry), fill=(19, 35, 63, 105))
        d.ellipse((pw / 2 - rx * 0.62, ph / 2 - ry * 0.58, pw / 2 + rx * 0.62, ph / 2 + ry * 0.58), fill=(19, 35, 63, 90))
        _SHADOW = lay.filter(ImageFilter.GaussianBlur(7))
    return _SHADOW


def contact_shadow(frame, cam, x, y, width_plate):
    sx, sy = cam.pt(x, y)
    rx = width_plate * cam.k * 0.5
    w = rx * 2 * 600 / 540
    h = w * 120 / 600
    paste_smooth(frame, _shadow_patch(), sx - w / 2, sy - h / 2, w, h)


def stand(frame, cam, plate, img, x, y_feet, boxes=None, cm=REN_CM, shadow_w=None, is_ren=True):
    """Place a standing figure with its feet at plate point (x, y_feet), at the correct perspective height, with a contact shadow.
    Returns the figure's frame box. If `boxes` is given and is_ren, sets boxes.ren and boxes.face (for layout checks)."""
    h = height_px(plate, y_feet, cm)
    w = img.width * h / img.height
    contact_shadow(frame, cam, x, y_feet, shadow_w or w * 0.95)
    r = place_smooth(cam, frame, img, x, y_feet, h)
    if boxes is not None and is_ren:
        boxes.ren = r
        boxes.face = (r[0] + 0.25 * (r[2] - r[0]), r[1], r[0] + 0.75 * (r[2] - r[0]), r[1] + 0.2 * (r[3] - r[1]))
    return r
