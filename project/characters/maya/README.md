# Maya — canonical reference sheets (identity lock)

Status: APPROVED. These sheets are Maya's identity lock and source art,
approved by the owner on 8 November 2026 for the 401(k) episode
(`videos/unclaimed_401k/ART_AUDIT.md`). On 25 November 2026 the owner
confirmed the 401(k) Maya as Maya's canonical design; the Three Bills Maya
is a non-canonical variant. The owner supplied these files on
25 November 2026 and they were committed to Git the same day.

## Design

Long wavy dark hair, rust-orange sweater, navy trousers, white trainers,
small gold earrings. `sheets/image.jpg` is the original cast lineup
(Alex, Maya centre, Sam) — the same Maya design as these sheets and as the
coffee-v3 supporting-cast lineup.

## Files

Each sheet is stored as base64 chunks, following the repo convention:
`sheets/<file>.b64.000`, `.001`, ...

Restore a sheet with:

    cat sheets/maya_s_seven_pose_animation_sheet.png.b64.* | base64 -d > maya_s_seven_pose_animation_sheet.png

Verify against the SHA-256 in `manifest.json` after restoring.

## Sheets

- `maya_s_seated_pose_reference_sheet.png` — stool poses
- `maya_s_seven_pose_animation_sheet.png` — standing poses (neutral, phone, surprise, point, exhale, card-in-pocket, walk with coffee)
- `maya_s_sofa_phone_sequence.png` — armchair/sofa phone sequence
- `maya_s_seated_receipt_and_laptop_poses.png` — receipt and laptop poses
- `maya_s_laptop_pose_study.png` — laptop pose study
- `maya_s_walking_and_sitting_sequence.png` — walk-in and sit sequence
- `maya_s_five_step_filing_sequence.png` — filing/drawer sequence
- `image.jpg` — original cast lineup

The 50 cut poses produced by the episode's `split_sheets.py` are not
included; these sheets are the source art the poses are cut from.
