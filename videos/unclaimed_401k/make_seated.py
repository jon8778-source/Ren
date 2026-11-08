"""Create the armchair-seated Maya poses: the stool-sheet laptop/phone poses with the baked stool removed (art/poses/seat_*.png)."""
import sys
from pathlib import Path
from PIL import Image
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
from unchair import unstool
for k in ["stool_03", "stool_04", "stool_05", "stool_06", "receipt_laptop_04", "receipt_laptop_05", "receipt_laptop_06"]:
    o = unstool(Image.open(HERE / "art" / "poses" / f"{k}.png").convert("RGBA")); o = o.crop(o.getbbox()); o.save(HERE / "art" / "poses" / f"seat_{k}.png"); print(k, o.size)
