"""Build videos/free_money/export/free_money_final_package.zip (local only; export/ is gitignored).

  project/.tools/venv/bin/python videos/free_money/build_package.py /output/final/free_money_final.mp4

Contents: final_video.mp4, narration/ (full audio + per-scene WAVs), script.md (the narration, unchanged), outline.md (final, with
timings), shot_plan.csv (the real shot plan), assets_used/ (only the files the renderer actually reads), contact_sheet.png (one
frame per cut), REPORT.md (validation, loudness, checks, open issues).
"""
import csv, hashlib, json, shutil, subprocess, sys, zipfile
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
mp4 = Path(sys.argv[1])
rep = json.loads((mp4.parent / (mp4.stem + "_report.json")).read_text())
shots = rep["shots"]
EXP = HERE / "export"
STAGE = EXP / "stage"
if STAGE.exists():
    shutil.rmtree(STAGE)
(STAGE / "narration" / "scenes").mkdir(parents=True)
(STAGE / "assets_used").mkdir()
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()

shutil.copy(mp4, STAGE / "final_video.mp4")
shutil.copy(ROOT / "scripts" / "Ren_Free_Money_Script.md", STAGE / "script.md")
# narration: per-scene WAVs as generated, the joined full track, and the normalised track as in the video
for sid in rep["scenes"]:
    shutil.copy(HERE / "voice" / f"{sid}.wav", STAGE / "narration" / "scenes" / f"{sid}.wav")
shutil.copy(mp4.parent / "rough_voice.wav", STAGE / "narration" / "full_narration_normalised_-16LUFS.wav")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(mp4), "-vn", "-c:a", "copy", str(STAGE / "narration" / "full_narration_as_in_video.m4a")], check=True)
# shot plan: the real one
with open(STAGE / "shot_plan.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["shot", "scene", "name", "type", "start_s", "end_s", "duration_s", "narration"])
    for s in shots:
        w.writerow([s["i"], s["scene"], s["name"], s["type"], round(s["start"], 2), round(s["end"], 2), round(s["end"] - s["start"], 2), s["phrase"]])
# assets used: only what the renderer reads
LIB = ROOT / "library"
used = ["supporting_assets/backgrounds/Porch_background_16x9.png", "supporting_assets/backgrounds/Office_background_16x9.png",
        "supporting_assets/backgrounds/Office_parking_lot_car_16x9.png", "supporting_assets/characters/Dev_pay_stub.png",
        "supporting_assets/characters/Priya_hiking_style.png", "supporting_assets/characters/Uncle_Gary.png",
        "supporting_assets/props/HR_folder_page6_prop.png"]
ren = ["Ren_1_neutral", "Ren_2_hand_on_chest_talking", "Ren_3_thinking_bust", "Ren_4_pointing", "Ren_extra_thinking_full_body",
       "Ren_full_body_presenting", "Ren_full_body_standing", "Ren_full_body_waving"]
manifest = []
for u in used:
    d = STAGE / "assets_used" / Path(u).parent.name
    d.mkdir(exist_ok=True)
    shutil.copy(LIB / u, d / Path(u).name)
    manifest.append((u, sha(LIB / u)))
(STAGE / "assets_used" / "ren_approved").mkdir()
(STAGE / "assets_used" / "ren_approved_matted").mkdir()
for n in ren:
    shutil.copy(LIB / "ren_approved" / f"{n}.jpg", STAGE / "assets_used" / "ren_approved" / f"{n}.jpg")
    shutil.copy(HERE / "matted" / f"{n}.png", STAGE / "assets_used" / "ren_approved_matted" / f"{n}.png")
    manifest.append((f"ren_approved/{n}.jpg", sha(LIB / "ren_approved" / f"{n}.jpg")))
(STAGE / "assets_used" / "ren_library_clips").mkdir()
shutil.copy(ROOT / "assets" / "ren_library" / "ren_hold_phone.mp4", STAGE / "assets_used" / "ren_library_clips" / "ren_hold_phone.mp4")
manifest.append(("ren_library/ren_hold_phone.mp4 (phone-raise clip, S2)", sha(ROOT / "assets" / "ren_library" / "ren_hold_phone.mp4")))
(STAGE / "assets_used" / "voice_reference").mkdir()
for n in ("ren_reference.wav", "ren_reference.txt"):
    shutil.copy(ROOT / "Audio" / n, STAGE / "assets_used" / "voice_reference" / n)
    manifest.append((f"Audio/{n} (voice reference)", sha(ROOT / "Audio" / n)))
(STAGE / "assets_used" / "MANIFEST_sha256.txt").write_text("\n".join(f"{h}  {n}" for n, h in manifest) + "\n")
# contact sheet: first frame of every cut
w, h, cols = 256, 144, 8
raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(mp4), "-vf", f"scale={w}:{h}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"])
F = np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3)
rows = (len(shots) + cols - 1) // cols
S = Image.new("RGB", (cols * (w + 2), rows * (h + 2)), (30, 30, 30))
for k, s in enumerate(shots):
    im = Image.fromarray(F[min(round(s["start"] * 24) + 2, len(F) - 1)])
    ImageDraw.Draw(im).text((3, 2), f"{s['i']} {s['scene']}", fill=(255, 60, 60))
    S.paste(im, ((k % cols) * (w + 2), (k // cols) * (h + 2)))
S.save(STAGE / "contact_sheet.png")
print("staged", sum(1 for _ in STAGE.rglob("*") if _.is_file()), "files")
