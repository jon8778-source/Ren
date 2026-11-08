"""Plates at 1920x1080 from the supplied 3840x2160 (spatially upscaled) PNGs.
O1 is mirrored so Maya (who faces right) can walk in from the left across open floor; the plate's own dark-legged
stool is replaced by a copy of the empty wall/floor beside it, so only Maya's all-wood stool is on screen."""
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter
SRC = Path("/tmp/claude-0/p1/01_Background_Plates_4K_Upscaled")
OUT = Path(__file__).resolve().parent / "art" / "plates"
def load(n): return Image.open(SRC / f"{n}_3840x2160.png").convert("RGB").resize((1920, 1080), Image.LANCZOS)
OUT.mkdir(parents=True, exist_ok=True)
load("H1_living_room_evening").save(OUT / "H1.png")
o2 = load("O2_HR_onboarding")
# remove the plate's own stool (Maya and the HR visitor bring their stools): rebuild cabinet face, wall and floor behind it
def feather(box, pad=8, blur=5):
    m = np.zeros((box[3] - box[1], box[2] - box[0]), np.float32); m[pad:-pad, pad:-pad] = 1
    return Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(blur))
a = np.asarray(o2).astype(np.float32)
wall = tuple(int(v) for v in a[560:660, 1250:1450].reshape(-1, 3).mean(0))
o2.paste(Image.new("RGB", (240, 90), wall), (1235, 668), feather((1235, 668, 1475, 758)))
o2.paste(o2.crop((1580, 672, 1670, 832)), (1470, 672), feather((1470, 672, 1560, 832), 3, 2))
bb = tuple(int(v) for v in a[770:782, 1224:1240].reshape(-1, 3).mean(0))
o2.paste(Image.new('RGB', (240, 54), bb), (1235, 752), feather((1235, 752, 1475, 806), 4, 3))
o2.paste(o2.crop((1590, 806, 1930 if False else 1920, 1065)).crop((0, 0, 330, 259)), (1235, 806), feather((1235, 806, 1565, 1065), 10, 6))
o2.save(OUT / "O2.png")
o1 = load("O1_office_day").transpose(Image.FLIP_LEFT_RIGHT)
box = (850, 595, 1100, 950)                 # mirrored stool + its floor shadow
w = box[2] - box[0]
src = o1.crop((box[0] - w - 5, box[1], box[2] - w - 5, box[3]))
mask = Image.new("L", src.size, 255).filter(ImageFilter.GaussianBlur(0.1))
m = np.zeros((src.height, src.width), np.float32); m[8:-8, 8:-8] = 1
mask = Image.fromarray((np.asarray(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(6)))).astype(np.uint8))
o1.paste(src, box[:2], mask)
o1.save(OUT / "O1.png")

# coin props from the supplied pack (white background -> transparent)
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "free_money"))
from matting import matte
P2 = Path("/tmp/claude-0/p2/02_Individual_Props")
(OUT.parent / "props").mkdir(exist_ok=True)
for n in ("coin_front_white", "coin_side_white"):
    rgba = Image.fromarray(matte(np.array(Image.open(P2 / f"{n}.png").convert("RGB"))), "RGBA")
    rgba = rgba.crop(rgba.getbbox()); rgba.save(OUT.parent / "props" / f"{n[:-6]}.png"); print(n, rgba.size)

# O1 at 3840x2160 (same mirror + stool patch at 2x) so the office can be framed closer without losing sharpness
o4 = Image.open(SRC / "O1_office_day_3840x2160.png").convert("RGB").transpose(Image.FLIP_LEFT_RIGHT)
b4 = tuple(2 * v for v in box); w4 = b4[2] - b4[0]
src4 = o4.crop((b4[0] - w4 - 10, b4[1], b4[2] - w4 - 10, b4[3]))
m4 = np.zeros((src4.height, src4.width), np.float32); m4[16:-16, 16:-16] = 1
mask4 = Image.fromarray((m4 * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(12))
o4.paste(src4, b4[:2], mask4); o4.save(OUT / "O1_4k.png")
# the approved sage office (Ren's background) at 3840x2160
Image.open(Path("/tmp/claude-0/cv3/project/prototypes/coffee-minute-v3/assets/office.png")).convert("RGB").resize((3840, 2160), Image.LANCZOS).save(OUT / "SAGE_4k.png")
Image.open(Path("/tmp/claude-0/cv3/project/prototypes/coffee-minute-v3/assets/office.png")).convert("RGB").resize((1920, 1080), Image.LANCZOS).save(OUT / "SAGE.png")
