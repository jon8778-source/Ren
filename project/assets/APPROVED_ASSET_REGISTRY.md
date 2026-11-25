# Ren — Approved Asset Registry

Created 24 November 2026, from the production audit recommendations 1–3 that the
owner (Jon) asked to progress. A machine-readable version is in
`APPROVED_ASSET_REGISTRY.json` beside this file.

**Update, 25 November 2026:** the Alex pose set (PR #12) was merged to `main`
and formally approved by the owner for production use; the Alex section below
records that approval. The same day, the owner decided Maya's canonical
design is the 401(k) episode Maya; the Maya section below records that
decision.

**How to read this registry:** it records only what the repository actually
proves — a file path, the branch it is on, a SHA-256 where one could be verified
from repo files or manifests, the approval provenance (who / when / source
document), and a status. Where the repository does not prove approval, the
status says so. Nothing in this registry creates an approval.

Source branches checked: `main` at `d48fcb697f0aed3452895ea09e28b7d2ef3e816d`
and `codex/ren-approved-v3` at `b502ac6c9017cdb5f356f8442a1984663a5aa2f7`.

---

## Ren — APPROVED, in Git

### Animation clip library (the presenter library)
- **Path:** `assets/ren_library/` — 32 MP4 clips, each listed with status
  `"ok"` in `assets/ren_library/ren_library.json` (1280×720, 24 fps, source
  audio discarded): ren_celebrate_fist_pump, ren_clipboard_tick, ren_confused,
  ren_count_fingers, ren_empty_pockets, ren_explain_hands, ren_facepalm,
  ren_hold_phone, ren_idea, ren_idle_calm, ren_idle_listen, ren_lean_in,
  ren_nod_yes, ren_open_arms, ren_point_camera, ren_point_down_right,
  ren_point_right, ren_point_up, ren_present_palm_left, ren_relieved,
  ren_rub_hands, ren_shake_no, ren_shocked, ren_shrug, ren_thinking,
  ren_thumbs_up, ren_walk_in_left, ren_walk_in_place_profile,
  ren_walk_off_right, ren_wave_bye, ren_wave_hello, ren_worried.
- **Branch:** `main` (also present on the production branches checked).
- **SHA-256:** `ren_library.json` does not carry per-clip hashes. Episode
  inventories record the first 16 characters for the clips they used, e.g.
  from `videos/three_bills/ASSET_INVENTORY.md`: ren_present_palm_left
  `4ab89972324e639b`, ren_shrug `1cacb6dd155bbec0`, ren_point_right
  `ae725bb9225f4847`, ren_thinking `5451d99e329777ff`.
- **Provenance:** `ren_library.json` per-clip status `"ok"`;
  `project/REN_VIDEO_RULES.md` (approved hybrid rules v3); the Three Bills
  inventory cites individual clips as "APPROVED animated clip".
- **Status: APPROVED — reusable presenter library, on main.**

### Locked character stills
- **Path:** `project/characters/ren/` — 8 poses (neutral, pointing, shocked,
  talking, thinking, thumbs-up, waving, worried).
- **Branch:** `main`. **Manifest:** `project/characters/manifest.json`
  (`locked: true`, Ren as `"guide"`), with full SHA-256 per pose: neutral
  `4cc68dfc839d23a02ebda55fa34adadf9eba5235f5aecdbd93861e49c5a6ee75`,
  pointing `21e97fe62038d58cf6a35c65322d11989fe443179bdb4270c5f0c75d107f307c`,
  shocked `fc773d86fd6e52a51865e38878242edd214781e57e74c697a38da400ab50118a`,
  talking `03eb06f505d36a78ee4481d66bb7650705acff74c1a85211c1c3a83d65121c95`,
  thinking `dc9bdac9a154d61ca4ed00ff94de197c9f36dcb13068bbadd0a510d802ba5241`,
  thumbs-up `fea209942a25645fa8e19098594a3643f419a0c0d881c3d383f91ef7d14e92ac`,
  waving `deb8b5eb2256fc68b8307f8fe5182ea2d77bc015b7f7b9e187ef93ba8303f6b1`,
  worried `9dd72deef5ba00fd2a58ae2990f7f730d45f61935fb76d4bda2df345b1720afc`.
- **Status: APPROVED (locked)** — legacy stills set; the hybrid rules restrict
  stills to story cutaways within limits.

### Approved stills folder
- **Path:** `library/ren_approved/` — 8 JPGs including full-body
  standing/presenting/waving. **Branch:** `main` only (absent on
  `codex/ren-approved-v3` and `codex/ren-hybrid-template`).
- **Status: PRESENT on main** — no per-file approval document was read, so no
  stronger claim is made.

### Voice reference
- **Path:** `Audio/ren_reference.wav` + `Audio/ren_reference.txt`.
  SHA-256 (first 16) `78de4bd45743554f` per the Three Bills inventory, which
  records it as "APPROVED reference (Ren Qwen clone)".
- **Configuration:** `Qwen/Qwen3-TTS-12Hz-1.7B-Base`, English, x-vector-only
  (`use_xvector_only=True` / `x_vector_only_mode=True`, `ref_text=None`
  locally) — see `project/REN_LONGFORM_BASELINE.md` and the note in
  `project/DECISIONS.md` dated 24 November 2026.
- **Status: APPROVED.**

---

## Alex — APPROVED pose set, in Git (plus approved episodic artwork)

### Reusable pose set
- **Path:** `project/characters/alex/` — README, `manifest.json`, and artwork
  stored as base64 chunks under `artwork/` (restore:
  `cat artwork/alex_neutral.png.b64.* | base64 -d`).
- **Poses (1360×1712, full-body, plain cream background):** presenting,
  neutral, thinking, thumbs-up, pointing (screen-right), waving, worried,
  shocked. SHA-256 per pose, from `project/characters/alex/manifest.json`:
  presenting `88009e40701624dc56b5dc2bc5d58b1c1509dce765e2a5afb5c49afed9bf1eef`,
  neutral `26dc51eb98a8c74e7859a42556530a2947ad61e62f743890709a7b7deaff70ff`,
  thinking `fd736937ef89735ebcfc47e50d7538f991e8abe70f47fe87cae2a499acf95d9e`,
  thumbs-up `92fdaf3d0a4f8014b3f417b5c47e99fd6f3e1b14719db46db59c14acaf50b88f`,
  pointing `d330b637b2b748205276dd181a1bfda61d9227c976c70345cfd34bb493f2cca4`,
  waving `5e74b0c2bc1802cd4479196b760e5a5105c3125adeec1aaab52cf5511345266e`,
  worried `80bd6cf05db9542abc533ab45d7d0c392cd1d79d6dfee22c57e815b930c34832`,
  shocked `b319c14ff952b95f2027830a11248e83a31e143880f7414f44585a59bdd28c4b`.
- **Provenance:** generated 24 November 2026 from the approved `alex-cafe`
  design; the owner approved the refined design and the full set in chat on
  24 November 2026, merged it via PR #12 on 25 November 2026 (merge commit
  `d48fcb6`), and formally approved it for production use on
  25 November 2026.
- **Status: APPROVED — reusable character pose set, on main.**

### Episodic artwork (coffee prototype)

Alongside the pose set, Alex also has approved episodic artwork for the
coffee prototype, stored losslessly as base64 text
chunks in `project/prototypes/coffee-minute-v3/artwork/` (restored by
`unpack_artwork.py`, SHA-256 verified):

| Restored file | Chunks | SHA-256 (verified 24 Nov 2026) | Size | Original approved source |
|---|---|---|---|---|
| `alex-cafe.png` | `alex-cafe.png.b64.000`–`.023` | `83d61936e45f62b7eef7ec253f1b4a3bce3661117afe96c13ae66009029f943b` | 1,715,661 bytes | "Alex taps to pay for coffee.png" |
| `alex-home.png` | `alex-home.png.b64.000`–`.024` | `5ff172badddbe248a20996075b0a98760223a83824734a3988a361095d70ea1f` | 1,793,785 bytes | "Alex pours French press coffee.png" (corrected single mug) |

- **Branch:** `codex/ren-approved-v3` originally; on `main` via PR #11
  (merged 24 November 2026, merge commit `28f33b9`).
- **Provenance:** the prototype README's "Approved artwork" table; the coffee
  prototype v3 was approved by Jon on 29 October 2026
  (`project/REN_VIDEO_RULES.md`). Library file IDs are recorded in
  `artwork/manifest.json` and in the JSON version of this registry.
- **Status: APPROVED as episodic artwork for the coffee prototype.** The
  reusable-character-set gap recorded in `project/DECISIONS.md`
  (27 October 2026) was closed by the pose set above.

---

## Maya — APPROVED canonical sheets, in Git (owner decision, 25 November 2026)

The owner decided on 25 November 2026 to keep the **401(k) episode's Maya**
as Maya's canonical design — the design whose sheets he approved on
8 November 2026 as "the identity lock and source art"
(`videos/unclaimed_401k/ART_AUDIT.md`). The Three Bills Maya and the
coffee-v3 lineup Maya are non-canonical variants. The canonical sheets were
supplied by the owner and committed to Git on 25 November 2026 (see below),
closing the archival gap. Like Alex, Maya has her own folder manifest
(`project/characters/maya/manifest.json`) rather than an entry in the legacy
locked-cast manifest.

### Canonical reference sheets (in Git, as chunks)
- **Path:** `project/characters/maya/` — README, `manifest.json`, and the
  sheets stored as base64 chunks under `sheets/` (restore:
  `cat sheets/<file>.b64.* | base64 -d`, then verify SHA-256).
- **Sheets (SHA-256 verified from a branch rebuild, 25 November 2026):**
  - `maya_s_seated_pose_reference_sheet.png` — `cc0a89c4bbf920d0bbe1511524f7613a9adc31ae1e694e696b95d149161e211e`
  - `maya_s_seven_pose_animation_sheet.png` — `572b33f8fb775d2cf3fface4a8253744b4bbd104fe6bfce3924c7839ab876596`
  - `maya_s_sofa_phone_sequence.png` — `fc993cf30faf24c541423982bbc890cf451f3169d57b3091409a56927b179e35`
  - `maya_s_seated_receipt_and_laptop_poses.png` — `b488f354ec8e436325707e31a6252009761cd59a5c323a66a4df4e8332485464`
  - `maya_s_laptop_pose_study.png` — `f68788d12d7e3d5703e81f03cf435aadd18bc39d4a60003fbb675e8a95328830`
  - `maya_s_walking_and_sitting_sequence.png` — `9613a80825bf1952546f8cdd0ff2d3515e47be505ea1f8c97e1cf32d6d957304`
  - `maya_s_five_step_filing_sequence.png` — `9677ec58ad889a5f319ffc0451dd6dbfb1fe5796d2094b629559d8c2e64bc8f9`
  - `image.jpg` (original cast lineup) — `f922c61ea79ba1771b8cdd43b66494ab1b389be382c35e7f8124c8336411f014`
- **Provenance:** owner approved the sheets as the identity lock and source
  art on 8 November 2026 (`videos/unclaimed_401k/ART_AUDIT.md`); owner
  confirmed the 401(k) Maya as canonical and supplied the files on
  25 November 2026. The 50 cut poses from `split_sheets.py` are not
  included; the sheets are the source art. Source figures are ~600 px tall
  in cut poses, so close-ups will be soft.
- **Status: APPROVED — canonical Maya identity lock, in Git.**

### Lineup still (in Git, as chunks)
- `supporting-cast.png` — "Centered Maya in illustrated character lineup.png"
  (Alex, revised Maya, Sam), stored as
  `project/prototypes/coffee-minute-v3/artwork/supporting-cast.png.b64.000`–`.023`
  on `codex/ren-approved-v3` (copied to `ren/production-fixes-20261124` by the
  production-fixes PR). SHA-256 (verified 24 Nov 2026)
  `07fb436f249fa2bd9c8b1d00e31e62b5e14630df2a92798753b284c57eb5833e`,
  1,710,532 bytes. Provenance: prototype README "Approved artwork" table
  ("included for reuse; this prototype uses Alex only").
- **Status: APPROVED prototype artwork — a lineup still, not a Maya pose set
  and not an identity lock. The lineup Maya is NOT the canonical design
  (owner decision, 25 November 2026).**

### Three Bills poses (NOT in Git)
Recorded in `videos/three_bills/ASSET_INVENTORY.md` at
`videos/three_bills/art/cast/` — a tree that does **not** exist in the Git
listing on `main` or on `video/three-bills-30-days` (local/gitignored
episode art):

| File | SHA-256 (first 16, per inventory) | Inventory status |
|---|---|---|
| `maya_01_neutral.png` | `6b140a9c8a70ccb4` | OWNER APPROVED 9 Nov 2026 (per pack record) |
| `maya_02_surprised_envelope.png` | `ba173f462624ec19` | OWNER APPROVED 9 Nov 2026 (per pack record) |
| `maya_03_worried_phone.png` | `e8770c7e9cef2a4e` | OWNER APPROVED 9 Nov 2026 (per pack record) |
| `maya_04_relief_phone.png` | `f123ada071ee7cb3` | OWNER APPROVED 9 Nov 2026 (per pack record) |

- **Provenance caveat:** the inventory's approval for the script is recorded
  as "per pack record — I did not see the approval message live", and the
  Maya rows carry the same "(per pack record)" basis: **second-hand
  provenance**, weaker than a recorded explicit approval.
- The same inventory states this Maya is **NOT the same design as the
  401(k) episode's Maya**. The 401(k) episode's Maya art
  (`videos/unclaimed_401k/art/`) is likewise local-only and not in Git.
- **Status: NON-CANONICAL VARIANT (owner decision, 25 November 2026) — the
  Three Bills Maya is not Maya's canonical design; she remains that
  episode's episodic artwork only. Files absent from Git; the approval
  provenance stays second-hand as recorded above.**

---

## Environments (for completeness)

- `office.png` (coffee prototype) — chunks
  `office.png.b64.000`–`.026` in
  `project/prototypes/coffee-minute-v3/artwork/`, SHA-256 (verified)
  `b428d9b93631c05f2832a2dbaff94cc17370329dad1a4cd82600fbb40019bd36`,
  1,897,116 bytes, source "Welcoming sage-accented home office.png".
  Status: APPROVED for the coffee prototype.
- Background plates on `main`: `library/supporting_assets/backgrounds/`
  — `Office_background_16x9.png` (SHA-256 first 16 `bfc7066bc8253ac3`),
  `Office_parking_lot_car_16x9.png` (`0dc0b4d6e623f571`),
  `Porch_background_16x9.png` (`b6732b5526d5bbc8`), recorded in the Three
  Bills inventory as "APPROVED (Free Money pack, PLATE_GEOM calibrated)".

---

## To close these gaps — what Jon needs to supply / approve

1. **Maya files: CLOSED (25 November 2026)** — the canonical 401(k) sheets
   were supplied by the owner and committed to Git
   (`project/characters/maya/`, PR #15) with full SHA-256 hashes recorded
   above and in `project/characters/maya/manifest.json`.
2. **Maya identity: CLOSED (25 November 2026)** — the owner decided the
   401(k) Maya is canonical; the Three Bills and lineup Mayas are
   non-canonical variants.
3. **Maya approval:** the 9 November 2026 second-hand approval concerned
   the now-non-canonical Three Bills variant; the canonical 401(k)
   approval is recorded first-hand in the episode's `ART_AUDIT.md`
   (8 November 2026). No further confirmation needed.
4. **Alex: CLOSED (25 November 2026)** — reusable pose set approved by the
   owner and recorded above (`project/characters/alex/`, PR #12).
5. **Ren (optional tidy-up):** add full per-clip SHA-256 hashes to
   `assets/ren_library/ren_library.json` so every clip is hash-verifiable,
   not only the four cited by episode inventories.
