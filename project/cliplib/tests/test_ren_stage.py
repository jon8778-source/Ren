"""Tests for the Ren staging standard (project/cliplib/ren_stage.py). Uses a synthetic figure, so no artwork is needed."""
import importlib.util
import unittest
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

MODULE = Path(__file__).resolve().parents[1] / 'ren_stage.py'
spec = importlib.util.spec_from_file_location('ren_stage', MODULE)
rs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rs)


class FakeCam:
    """Plate-to-frame mapping with a slow push, like the real Cam."""
    def __init__(self, zoom=1.0, cx=800.0, cy=470.0, w=1280, h=720, plate_w=1672):
        self.k = (w / (plate_w / zoom))
        self.x0, self.y0 = cx - (plate_w / zoom) / 2, cy - (plate_w / zoom) * h / w / 2

    def pt(self, x, y):
        return ((x - self.x0) * self.k, (y - self.y0) * self.k)


def figure():
    im = Image.new('RGBA', (300, 900), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((90, 20, 210, 160), fill=(20, 20, 30, 255))
    d.rounded_rectangle((60, 170, 240, 600), 40, fill=(40, 50, 90, 255))
    d.rectangle((90, 600, 210, 880), fill=(30, 30, 30, 255))
    return im


class HeightTests(unittest.TestCase):
    def test_office_height_matches_the_measured_chair_depth(self):
        # a 175 cm person at the office chair's floor row (about 880) is about 610 plate pixels tall
        self.assertAlmostEqual(rs.height_px('OFFICE', 880), 610, delta=15)

    def test_height_grows_toward_the_camera(self):
        for plate in rs.PLATE_GEOM:
            self.assertLess(rs.height_px(plate, 700), rs.height_px(plate, 800))

    def test_height_scales_with_real_height(self):
        self.assertAlmostEqual(rs.height_px('PORCH', 760, 87.5) * 2, rs.height_px('PORCH', 760, 175), places=6)

    def test_feet_must_stand_below_the_horizon(self):
        for plate, (horizon, _) in rs.PLATE_GEOM.items():
            self.assertLess(rs.height_px(plate, horizon - 1), 0)


class SmoothPlacementTests(unittest.TestCase):
    def centroid(self, frame):
        a = np.asarray(frame)[..., 3].astype(float) / 255
        yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
        return (a * xx).sum() / a.sum(), (a * yy).sum() / a.sum()

    def run_path(self, place):
        im = figure()
        a = np.asarray(im)[..., 3].astype(float) / 255
        sy, sx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
        fx, fy = (a * sx).sum() / a.sum() / im.width, (a * sy).sum() / a.sum() / im.height
        ex, ey, n = [], [], 60
        for i in range(n):
            t = i / (n - 1)
            h = 480 + 120 * t
            w = im.width * h / im.height
            x, y = 300 + 40.37 * t, 90 + 13.9 * t
            frame = Image.new('RGBA', (1280, 720), (0, 0, 0, 0))
            place(frame, im, x, y, w, h)
            cx, cy = self.centroid(frame)
            ex.append(cx - (x + fx * w))
            ey.append(cy - (y + fy * h))
        t = np.arange(n)
        return max(float(np.std(np.array(v) - np.polyval(np.polyfit(t, v, 3), t))) for v in (ex, ey))

    @staticmethod
    def whole_pixel(frame, im, x, y, w, h):
        frame.alpha_composite(im.resize((round(w), round(h)), Image.LANCZOS), (int(round(x)), int(round(y))))

    def test_smooth_placement_does_not_tremble(self):
        smooth = self.run_path(rs.paste_smooth)
        old = self.run_path(self.whole_pixel)
        self.assertLess(smooth, 0.12)
        self.assertGreater(old, 2 * smooth)          # the whole-pixel method is clearly worse

    def test_partly_or_fully_off_frame_is_safe(self):
        frame = Image.new('RGBA', (1280, 720), (0, 0, 0, 0))
        rs.paste_smooth(frame, figure(), -80.5, -20.25, 200.0, 600.0)
        rs.paste_smooth(frame, figure(), 1200.75, 400.5, 200.0, 600.0)
        rs.paste_smooth(frame, figure(), 5000.0, 5000.0, 200.0, 600.0)     # nothing to draw, no error
        self.assertGreater(np.asarray(frame)[..., 3].max(), 0)


class StandTests(unittest.TestCase):
    class Boxes:
        ren = face = None

    def test_feet_land_on_the_requested_floor_point(self):
        cam = FakeCam(zoom=1.1)
        frame = Image.new('RGBA', (1280, 720), (0, 0, 0, 0))
        boxes = self.Boxes()
        box = rs.stand(frame, cam, 'OFFICE', figure(), 800, 880, boxes)
        fx, fy = cam.pt(800, 880)
        self.assertAlmostEqual(box[3], fy, places=6)
        self.assertAlmostEqual((box[0] + box[2]) / 2, fx, places=6)
        self.assertEqual(boxes.ren, box)
        self.assertLess(boxes.face[3], box[3])                 # the head box is above the feet

    def test_height_follows_the_floor_row(self):
        cam = FakeCam()
        near = rs.stand(Image.new('RGBA', (1280, 720)), cam, 'OFFICE', figure(), 800, 900)
        far = rs.stand(Image.new('RGBA', (1280, 720)), cam, 'OFFICE', figure(), 800, 760)
        self.assertGreater(near[3] - near[1], far[3] - far[1])

    def test_contact_shadow_is_under_the_feet(self):
        cam = FakeCam()
        frame = Image.new('RGBA', (1280, 720), (0, 0, 0, 0))
        rs.stand(frame, cam, 'OFFICE', Image.new('RGBA', (300, 900), (0, 0, 0, 0)), 800, 880)      # an invisible figure: only the shadow draws
        a = np.asarray(frame)[..., 3]
        ys, xs = np.nonzero(a > 10)
        fx, fy = cam.pt(800, 880)
        self.assertLess(abs(ys.mean() - fy), 3)
        self.assertLess(abs(xs.mean() - fx), 3)


    def test_mip_cache_never_returns_another_images_pixels(self):
        # regression: the cache was keyed on id(img); a new image that reused a freed image's id got the old one's pre-scaled copy
        red = Image.new('RGBA', (300, 600), (255, 0, 0, 255))
        f1 = Image.new('RGBA', (400, 700), (0, 0, 0, 0))
        rs.paste_smooth(f1, red, 50, 50, 150, 300)
        key = (id(red), red.size, int(300 // rs._MIP_STEP))
        stale = rs._MIP[key]
        blue = Image.new('RGBA', (500, 600), (0, 0, 255, 255))            # different size and colour
        rs._MIP[(id(blue), blue.size, int(300 // rs._MIP_STEP))] = stale   # simulate an id collision with a different image object
        f2 = Image.new('RGBA', (400, 700), (0, 0, 0, 0))
        rs.paste_smooth(f2, blue, 50, 50, 250, 300)
        px = np.asarray(f2)[200, 150]
        self.assertEqual(tuple(px[:3]), (0, 0, 255))


if __name__ == '__main__':
    unittest.main()
