import importlib.util
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / 'render_hybrid.py'
spec = importlib.util.spec_from_file_location('hybrid', MODULE)
hybrid = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hybrid)


class HybridTests(unittest.TestCase):
    def test_rejects_long_still(self):
        with self.assertRaisesRegex(ValueError, 'duration'):
            hybrid.validate({'shots': [{'kind': 'story', 'duration': 7}]}, Path('.'))

    def test_rejects_outdated_clip_window(self):
        with self.assertRaisesRegex(ValueError, 'window'):
            hybrid.validate({'shots': [{'kind': 'ren', 'duration': 5, 'clip': 'ren_point_camera', 'in_s': 999}]}, Path('.'))

    def test_rejects_unapproved_mirroring(self):
        with self.assertRaisesRegex(ValueError, 'mirrored'):
            hybrid.validate({'shots': [{'kind': 'ren', 'duration': 1, 'clip': 'ren_shake_no', 'mirror': True}]}, Path('.'))

    def test_countup_changes_pixels(self):
        shot = {'kind': 'graphic', 'duration': 2, 'title': 'Example', 'value': 730}
        a = hybrid.picture(shot, 0, Path('.'))
        b = hybrid.picture(shot, 47, Path('.'))
        self.assertNotEqual(a.tobytes(), b.tobytes())

    def test_rejects_infinite_duration(self):
        with self.assertRaisesRegex(ValueError, 'duration'):
            hybrid.validate({'shots': [{'kind': 'graphic', 'duration': float('inf')}]}, Path('.'))


if __name__ == '__main__':
    unittest.main()
