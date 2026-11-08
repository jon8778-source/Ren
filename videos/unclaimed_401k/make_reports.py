"""Write shot/asset inventories and the contact sheet for the pilot.  python make_reports.py OUT_DIR/pilot.mp4 [CONTACT_DIR]"""
import csv, json, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw
HERE = Path(__file__).resolve().parent; mp4 = Path(sys.argv[1]); out = Path(sys.argv[2]) if len(sys.argv) > 2 else mp4.parent
rep = json.loads((mp4.parent / (mp4.stem + "_report.json")).read_text()); (HERE / "reports").mkdir(exist_ok=True)
MOVE = {
 "P01": ("Armchair: leaning-in settle pose -> phone raised (hard cut, Maya sits in the plate's own armchair)", "armchair sheet 1-2"),
 "P02": ("Hand-and-phone close-up: hover -> thumb press -> hover; app button state changes (code UI under the thumb)", "props hand-phone hover/tap"),
 "P03": ("Armchair: looking at phone -> small smile (3-frame cross-fade); confirmation email slides in (code)", "armchair sheet 3, 2"),
 "P04": ("Stool by the coffee table: phone -> hand lifts laptop lid (3-frame cross-fade)", "stool sheet 3-4"),
 "P05": ("Stool: leans in at laptop -> eyes widen, finger lifts; benefits alert pops (code)", "stool 5, receipt_laptop 4"),
 "P06": ("Code graphic: portal with $100 / month label popping in", "code only"),
 "P07": ("Code graphic: label swaps to $1,200 / year", "code only"),
 "P08": ("Over-the-shoulder: scrolling, head turn (cross-fades); Employer token travels along arrow into the 401(k) tile (code)", "overshoulder sheet 1-3"),
 "P09": ("Stool: finger hover over laptop -> about to press (cross-fade); Contribution % field highlights (code)", "receipt_laptop 4-5"),
 "P10": ("Stool: thinking at laptop -> sits back and exhales (hard cut); three year ticks draw (code)", "receipt_laptop 6, stool 6"),
 "P11": ("Code graphic: decorative trick icons fade, plain benefits line stays, slow zoom", "code only"),
 "P12": ("Stool: leans at laptop -> thinks, hand on chin; camera pull-back; employer line highlighted (code)", "stool 5, receipt_laptop 6"),
 "P13": ("Office: 4-pose walk cycle with coffee at constant speed -> reaches for stool -> half sits -> seated typing pose", "walk_sit 1-6, stool 1"),
 "P14": ("Stool: typing -> sips coffee -> glances at phone (cross-fades)", "stool 1-3"),
 "P15": ("Stool: leaning to type -> presses a key (hard cut); coin falls into the jar on the table (code)", "stool 5, receipt_laptop 5, coin"),
 "P16": ("Stool: reads receipt -> winces -> tucks it away (cross-fades)", "receipt_laptop 1-3"),
 "P17": ("STORY_STILL: HR desk, folder handoff; only a slow code-driven light shift", "maya_take_folder, hr_offer_folder"),
 "P18": ("Close-up: pen hand arrives, traces the tick on the 2% box (hand layer moves along the stroke; tick drawn by code)", "clipboard + hand layers"),
 "P19": ("Stool: reading form -> lowers it into the open drawer -> closes drawer -> relaxes (cross-fades)", "drawer sheet 1-5")}
with open(HERE / "reports" / "Shot_Inventory.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["shot", "type", "start_s", "end_s", "duration_s", "plate", "narration", "movement (what actually moves)", "source poses"])
    for s in rep["shots"]: w.writerow([s["id"], s["type"], round(s["start"], 3), round(s["end"], 3), round(s["end"] - s["start"], 3), s["scene"], s["phrase"], *MOVE[s["id"]]])
ASSETS = [
 ("Maya identity lock + 10 pose sheets (50 cut-outs)", "FOUND_APPROVED", "Owner approved as identity lock and source art, incl. seated poses (messages 'Yea to both', 'Approved')", "Keyframe art, not an animation rig; figures about 600 px tall"),
 ("Maya armchair poses with the baked chair removed", "FOUND_NEEDS_REVIEW", "Derived by colour segmentation (unchair.py)", "Small leftover specks near shoes"),
 ("HR character (hr_offer_folder)", "FOUND_APPROVED", "Owner 'Approved' to the HR character", "Single pose"),
 ("Plates H1 / O1 / O2 (3840x2160 upscales)", "FOUND_APPROVED", "Owner 'Approved'", "2.3x upscale of 1672x941; not perspective-calibrated; O1 mirrored with its stool removed, O2 with its stool removed (patched)"),
 ("Props: hand+phone, clipboard+pen hand, jar, coin", "FOUND_APPROVED", "From the sheets and the part-2 pack", "Pen hand and clipboard split by segmentation"),
 ("Qwen narration, pilot only (P1 31.7 s, P2 21.4 s)", "GENERATED", "Script approved by the owner for the pilot narration", "Words verified by Whisper; accent, pace and joins need listening review"),
 ("Finance UI, cards, chips, portal", "CODE_DRAWN", "Drawn in code, Fredoka, navy/sage/cream", "Style sheet and the nine UI screens were never supplied; design is new and needs review"),
 ("Ren animated clips", "NOT_USED", "Pilot is Maya-led; no Ren shots in the pilot plan", "")]
with open(HERE / "reports" / "Asset_Inventory.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["asset", "status", "basis", "limits"]); w.writerows(ASSETS)
# contact sheet
tmp = out / "_c"; tmp.mkdir(exist_ok=True); cols, W_, H_ = 4, 480, 270; n = len(rep["shots"]); rows = (n + cols - 1) // cols
sheet = Image.new("RGB", (cols * W_, rows * (H_ + 22)), (24, 28, 40)); d = ImageDraw.Draw(sheet)
for k, s in enumerate(rep["shots"]):
    t = (s["start"] + s["end"]) / 2; p = tmp / f"{s['id']}.png"
    subprocess.check_call(["ffmpeg", "-y", "-v", "error", "-ss", f"{t:.3f}", "-i", str(mp4), "-frames:v", "1", "-vf", f"scale={W_}:{H_}", str(p)])
    x, y = (k % cols) * W_, (k // cols) * (H_ + 22); sheet.paste(Image.open(p), (x, y + 22)); d.text((x + 6, y + 5), f"{s['id']}  {s['type'].replace('CHARACTER_ACTION', 'ACTION')}  {s['start']:.1f}-{s['end']:.1f}s", fill=(255, 255, 255))
    p.unlink()
tmp.rmdir(); sheet.save(out / "contact_sheet.jpg", quality=88); print("wrote reports + contact sheet")
