"""Asset inventory for the Three Bills pilot: path, SHA-256, provenance, approval status and where it is used. -> ASSET_INVENTORY.csv / .md"""
import csv, hashlib, json
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
man = {a["path"]: a for a in json.loads((HERE / "production" / "ASSET_MANIFEST.json").read_text())["assets"]}
rows = []
def add(kind, path, status, provenance, used, note=""):
    p = ROOT / path if not Path(path).is_absolute() else Path(path)
    rows.append([kind, str(path), sha(p)[:16] if p.exists() else "MISSING", status, provenance, used, note])
add("script", "videos/three_bills/script/SCRIPT.md", "OWNER APPROVED (per pack record)", "Pack OWNER_DECISIONS.md: owner 'Script approved' 9 Nov 2026 after supplying v2; SHA-256 verified = 14801320...", "all narration", "I did not see the approval message live; the pack records it")
add("script", "videos/three_bills/script/VOICE_SCRIPT.txt", "OWNER APPROVED (per pack record)", "Voice-only extraction, SHA-256 verified = efa04724...", "voice synthesis (paragraphs 1-9 for the pilot)")
for n, used in (("maya_01_neutral", "S02 (start), S09 (start), S13"), ("maya_02_surprised_envelope", "S02 (after 0.9 s), S15, S16 (start)"), ("maya_03_worried_phone", "S04, S07, S08 (start), S09, S10, S16"), ("maya_04_relief_phone", "S08")):
    m = man[f"assets/cast/{n}.png"]; add("character (Maya)", f"videos/three_bills/art/cast/{n}.png", "OWNER APPROVED 9 Nov 2026 (per pack record)", "Pack assets/cast; hash = manifest hash; image_gen + cutout", used, "alpha edges inspected at 100% on dark and sage backgrounds; NOT the same design as the 401(k) episode's Maya")
for n, status, used in (("Office_parking_lot_car_16x9", "APPROVED (Free Money pack, PLATE_GEOM LOT calibrated)", "S02, S15, S16"), ("Porch_background_16x9", "APPROVED (Free Money pack, PLATE_GEOM PORCH calibrated)", "S04, S07, S08, S12 veil"), ("Office_background_16x9", "APPROVED (Free Money pack, PLATE_GEOM OFFICE calibrated)", "S09, S10, S13, S14 veil")):
    add("environment", f"library/supporting_assets/backgrounds/{n}.png", status, "library/supporting_assets (owner's asset pack, 'style lock approved' 7 Nov 2026 for the Free Money episode)", used, "reuse for this episode is allowed by the pack; no new approval implied beyond that")
add("environment", "videos/unclaimed_401k/art/plates/SAGE.png", "APPROVED (Ren's sage home office, REN_VIDEO_RULES.md)", "office.png restored from branch codex/ren-approved-v3 (hash-checked there)", "S01, S05 veil, S06, S11, S17 (Ren shots)", "plate geometry OFFICE_SAGE fitted by eye in the 401(k) episode")
for n, used in (("car_key", "S02"), ("leaking_pipe", "S05")):
    m = man[f"assets/props/{n}.png"]; add("prop", f"videos/three_bills/art/props/{n}.png", "kit asset (not individually approved)", "Pack assets/props, simple vector prop, no text", used)
for n in ("blank_invoice", "blank_phone", "savings_envelope"):
    add("prop", f"videos/three_bills/art/props/{n}.png", "kit asset, UNUSED in the pilot", "Pack", "-", "invoice and phone are drawn in code in the pilot so figures stay editable")
for n in ("kitchen_sink_plate_16x9", "dental_waiting_plate_16x9"):
    add("environment", f"videos/three_bills/art/plates/{n}.png", "PROVISIONAL, NOT USED", "Pack: schematic flat vector, not perspective-calibrated, style does not match the painterly approved plates", "-", "needs owner approval before any use")
for clip, used in (("ren_present_palm_left", "S01 (mirrored)"), ("ren_shrug", "S06"), ("ren_point_right", "S11"), ("ren_thinking", "S17")):
    add("character (Ren)", f"assets/ren_library/{clip}.mp4", "APPROVED animated clip (ren_library.json status ok)", "assets/ren_library; used in the approved 401(k) episode", used, "mouth-closed window; source audio discarded")
add("voice", "Audio/ren_reference.wav", "APPROVED reference (Ren Qwen clone)", "Audio/ren_reference.txt is its transcript (not used in x-vector-only mode)", "voice/H.wav, voice/L.wav")
add("production", "videos/three_bills/production/assumptions.csv", "single numeric source", "Pack; check_numbers.py prints MATHS OK", "every on-screen figure (tb_ui.A)")
with open(HERE / "ASSET_INVENTORY.csv", "w", newline="") as f: w = csv.writer(f); w.writerow(["kind", "path", "sha256_16", "status", "provenance", "used_in_pilot", "note"]); w.writerows(rows)
md = ["# Asset inventory: Three Bills pilot", "", "| Kind | Path | SHA-256 (16) | Status | Used in pilot | Note |", "|---|---|---|---|---|---|"]
for r in rows: md.append(f"| {r[0]} | `{r[1]}` | {r[2]} | {r[3]} | {r[5]} | {r[6]} |")
(HERE / "ASSET_INVENTORY.md").write_text("\n".join(md) + "\n"); print(len(rows), "rows")
