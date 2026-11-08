"""Ren host cutaways: genuine approved library clips (assets/ren_library/*.mp4), native 1280x720 decode and background removal, placed on
the approved sage office with ren_stage's scale standard (plate geometry OFFICE_SAGE) and a contact shadow. No generated host, no stills,
no bobbing: Ren's feet and scale are fixed for the shot and only the clip's own pixels move."""
import json, subprocess, sys
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "project" / "cliplib"))
from ren_stage import paste_smooth, contact_shadow, height_px
LIB = ROOT / "assets" / "ren_library"
FPS = 24
PK = 1920 / 1672.0                      # plate (1672x941) -> frame (1920x1080)
class PCam:
    k = PK
    def pt(self, x, y): return (x * PK, y * PK)

def cut_out(rgb):
    """RGBA Ren from one clip frame (same method as videos/postponing_life/build_pilot.cut_out): near-white connected to the frame edge plus
    enclosed pure-white pockets is background; edges softened by a pixel and the white mixed into them removed."""
    lo, hi = rgb.min(2).astype(int), rgb.max(2).astype(int)
    near = (lo > 215) & (hi - lo < 25)
    lab, _ = ndimage.label(near)
    edge = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    bg = np.isin(lab, edge[edge > 0])
    pure = (lo > 243) & (hi - lo < 12) & ~bg
    plab, n = ndimage.label(pure)
    if n:
        sizes = ndimage.sum(pure, plab, range(1, n + 1)); bg |= np.isin(plab, np.where(sizes > 150)[0] + 1)
    a = ndimage.gaussian_filter((~bg).astype(np.float32), 0.7)[..., None]
    c = rgb.astype(np.float32); c = np.where(a > 0.02, (c - (1 - a) * 255.0) / np.maximum(a, 0.02), 0)
    return np.concatenate([np.clip(c, 0, 255), a * 255], 2).astype(np.uint8)

def _decode(clip, start, n):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-ss", f"{start:.3f}", "-i", str(LIB / f"{clip}.mp4"), "-frames:v", str(n), "-vf", "fps=24,format=rgb24", "-f", "rawvideo", "-"])
    return np.frombuffer(raw, np.uint8).reshape(-1, 720, 1280, 3)

class RenClip:
    """`seconds` of `clip` starting at `start`. Anchors (feet row, centre column, standing height) come from the clip's own neutral first frame."""
    def __init__(self, clip, start, seconds, cx_plate=420, feet_plate=770):
        n = int(np.ceil(seconds * FPS - 1e-6)); self.clip, self.start = clip, start
        neutral = cut_out(_decode(clip, 0, 1)[0]); al = neutral[..., 3] > 128
        rows = np.where(al.any(1))[0]; self.top, self.feet = int(rows.min()), int(rows.max())
        leg = np.where(al[self.feet - 120:self.feet + 1].any(0))[0]; self.cx = float((leg.min() + leg.max()) / 2)
        self.h_clip = self.feet - self.top
        self.frames = [cut_out(f) for f in _decode(clip, start, n)]
        assert len(self.frames) >= n, (clip, len(self.frames), n)
        self.n = n; self.cxp, self.fp = cx_plate, feet_plate
        # crop every frame to the union of Ren's pixels so the per-frame transform stays small (positions are unchanged)
        solid = np.zeros((720, 1280), bool)
        for f in self.frames: solid |= f[..., 3] > 8
        cols, rows = np.where(solid.any(0))[0], np.where(solid.any(1))[0]
        self.box = (max(0, int(cols.min()) - 4), max(0, int(rows.min()) - 4), min(1280, int(cols.max()) + 5), min(720, int(rows.max()) + 5))
        x0, y0, x1, y1 = self.box
        self.imgs = [Image.fromarray(f[y0:y1, x0:x1], "RGBA") for f in self.frames]
        H_plate = height_px("OFFICE_SAGE", feet_plate)          # 175 cm at this floor row, in plate px
        self.scale = H_plate * PK / self.h_clip                 # clip px -> frame px
        self.fx, self.fy = cx_plate * PK, feet_plate * PK
        self.feet_rec = []

    def draw(self, frame, t):
        i = min(max(int(t * FPS + 1e-6), 0), self.n - 1)
        im = self.imgs[i]; x0, y0, _, _ = self.box; s = self.scale
        contact_shadow(frame, PCam(), self.cxp, self.fp, 150)
        left = self.fx - self.cx * s + x0 * s; top = self.fy - self.feet * s + y0 * s
        paste_smooth(frame, im, left, top, im.width * s, im.height * s)
        a = np.asarray(im)[..., 3]; ys, xs = np.where(a > 128)
        bx = (left + xs.min() * s, top + ys.min() * s, left + xs.max() * s, top + ys.max() * s)
        return bx, i
