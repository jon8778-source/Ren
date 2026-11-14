# Black Friday Short: asset requirements report (asset-first checkpoint)

Branch: `video/black-friday-30s`, created from `video/three-bills-30-days`. Reason: `main` does not contain the Shorts launcher (`project/pipeline/shorts_standards.py`), the clip library or the Qwen tooling; these live on the production branches. Rules read: AGENTS.md, CLAUDE.md, REN_VIDEO_RULES.md, REN_SHORTS_RULES.md.

## Verified
| Item | Result |
|---|---|
| E1-E4, P1, P2 SHA-256 vs manifest | all six match |
| E1-E4, P1, P2 size | 768x1344 RGB (below 1080x1920: one upscale needed, sharpness to be checked) |
| Approval status of all six | none: TEMPORARY, generated with FLUX.2-dev, not approved by the owner |
| Ren clips (6 distinct, used for 6 beats) | present in `assets/ren_library/`, 1280x720, 10.0 s; plan windows equal the windows in `ren_library.json` (all status `ok`) |
| Math | $100 x (1 - 0.30) = $70 (will be verified in code when the graphics are built) |

## Issues to decide before building
1. **Script not yet approved.** Step 4 forbids voice synthesis until you approve it. The script says 77 words; my whitespace count of the ten spoken lines is 82. At ~0.33-0.385 s/word that is ~27-32 s, so it may run over 30 s. Fallback cuts in the script file (beat 7, or shorten beat 2).
2. **Mouth-closed rule vs two clips.** Library notes: `ren_thumbs_up` has a toothy grin ~1 s at peak (beat 10); `ren_clipboard_tick` has a brief open smile (beat 3). Neither is strictly mouth-closed; I will pick sub-windows without the open smile where possible and list any that cannot be avoided, rather than substitute silently.
3. **Asset quality (visible in the contact sheet):** E1 is mostly a huge blank navy panel and a small red sign with cropped bags (reads as a shop, but the "BLACK FRIDAY" banner needs code text on a panel of unusual size); E2 is mainly a window and an empty wooden table (little kitchen identity); E3, E4 look fine. P1/P2 are on near-white with a faint grey background and need matting. None is approved art.
4. Generated environments differ in style from the approved Maya plates (soft FLUX look vs approved line art). Treat as placeholders; regeneration or approval is your call.

## Plan after approval
Matte white-background Ren clips and props at native resolution, upscale environments once, draw all text/phone/notepad/calculator/badges/captions/end card in code, Qwen British voice, 15 s prototype (beats 1-6, at least 3 compositions), preflight + QA, then STOP for your explicit approval before the full Short.

Missing poses: none. Not verified: voice, any rendering, audio listening.

## Update 14 Nov 2026 (after "Approved")
- Script approved in chat. Narration generated once with the Qwen British clone (`gen_voice.py`, seed 1114, 2 chunks): **26.84 s**, 82 words (script says 77), fits 30 s; Whisper medium.en matches the approved text except spoken numbers (rule 1/2/3, 30 %, 70, 24). Beat boundaries from `voice/beats.json`.
- Generated environments/props used as placeholders; the owner's "Approved" replied to the report that called them temporary placeholders. **Final art approval is requested at the prototype gate.** The manifest lists them as `approved` only because the launcher requires it; the evidence text states the placeholder status.
- Mouth-closed check by frame scan: `ren_clipboard_tick` (open smile at clip 3.0-3.5 s) now starts at 5.4 s and `ren_thumbs_up` (grin 2.75-4.75 s) starts at 4.9 s. Consequence: in those windows Ren holds no clipboard and the thumbs-up hand has already lowered. Other four clips: mouths closed in the windows used (sampled every 0.3 s).
- Ren clips matted at native resolution (`cut_out`), matte pulled in 1 px to remove the white fringe on dark backgrounds. Props P1/P2 matted with the same method. Environments upscaled once 768x1344 -> 1080x1920 (soft, not sharp).
