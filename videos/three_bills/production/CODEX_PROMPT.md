# REN | Three Bills in 30 Days | Codex production handover (script v2)

You are the Ren technical production director, animation director, financial fact-checker and technical QA lead.

The owner supplied script v2, approved the FOUR Maya poses, and in a subsequent message on 9 November 2026 explicitly stated **“Script approved.”** The v2 script is now **OWNER APPROVED FOR VOICE AND ~60-SECOND PILOT PRODUCTION**. Do not use v1. The new kitchen/dental plates are provisional and have not been approved. The full film remains BLOCKED pending explicit pilot approval.

## Source of truth

1. Read `SCRIPT.md` verbatim as the current v2 episode script. `VOICE_SCRIPT.txt` is its narration-only extraction. Never substitute v1 wording.
2. `production/assumptions.csv` is the single numerical source. Run `python production/check_numbers.py`. All displayed figures are generated in code and all calculations remain correct on every displayed frame.
3. Read `production/SCENE_PLAN.md`, `production/PRODUCTION_QA_GATE.md`, `production/ASSET_MANIFEST.json`, and `production/OWNER_DECISIONS.md`.
4. Inspect the latest Ren GitHub `video/free-money-v2` long-form baseline and any more recent approved standards: `project/REN_LONGFORM_BASELINE.md`, `project/REN_LONGFORM_CHECKLIST.md`, `project/REN_VIDEO_RULES.md`, `project/cliplib/README.md`, `project/cliplib/ren_stage.py`, real MP4 Ren animation library, approved office/car/porch plates, the coffee v3 reference, and `project/REN_LONGFORM_REFERENCE.md`. Legacy Kokoro/white-only instructions do not supersede current hybrid video rules.

## Gate A: preflight checks (script + Maya approvals already cleared)

- Verify v2 copy, claims, amount calculations, assumed calendar and timing. The 6:02 time markers are **guides**, not a measured TTS timeline; preserve natural speaking rate.
- Honour the owner's existing approval of **all four new Maya cutouts**. Do not request that same image approval again. Inspect alpha edges, consistency, staging perspective and appearance against other established artwork. If a real technical problem is found, disclose it, propose targeted correction, and request approval only for a *changed* asset, not the original unchanged images.
- Do not imply the owner approved the kitchen or dental plates; inspect and request approval for any changed/uncertain aesthetic decisions before relying on them. Their 3840x2160 nominal dimensions do not equal perspective calibration. For placed standing people calibrate `PLATE_GEOM` from real objects.
- Reuse genuine approved Ren MP4 animations for actual movement. Animated still pans do not count as Ren character animation. Render Ren by default on the left in the office, information on the right, but use meaningful story cutaways so the result is not a PowerPoint.
- Verify Qwen reference WAV, exact transcript, model, and recorded allowed voice workflow. **Script v2 has explicitly been approved; you may synthesize the approved Qwen voice for the 60-second pilot after completing preflight.**
- Record both completed owner approvals; do not request another sign-off on unchanged script v2 or Maya poses. If a provisional plate is not acceptable, use suitable existing approved repository plates or propose alternate art and obtain needed visual approval; do not stall on unapproved supplemental plates.

## Gate B: authorized now: render the ~60-second pilot after preflight

- Generate a genuine ~60-second pilot using the approved Qwen British Ren voice `Qwen/Qwen3-TTS-12Hz-1.7B-Base`, English, `use_xvector_only=True`, existing approved WAV and matching transcript; if hosted use `Qwen/Qwen3-TTS` `/generate_voice_clone`. No voice swap, music, paid fallback, speech-rate changes, time-stretch, artificial silence-padding or unapproved lip-sync.
- Cut Ren from existing actual MP4s, suppress their source audio, preserve character identity, scale and true orientation. Narration by Ren only, Maya mouth closed.
- Enforce max length 5.5s genuine Ren clip, 2.5s story still and 3.5s standalone graphic; alternate real animation / object interactions / illustrated settings, and return to Ren naturally ~30–45 seconds. No white-slide graphics stretch, footer, floating heads, decorative wobble or furniture occlusion.
- Apply grounded-foot perspective, correct contact shadows, native-resolution matte, subpixel compositing, no 1–2-frame flashes, and half-open `[start,end)` cut boundaries.
- Reconcile shot timing to measured Qwen WAVs. Preserve audio chunk hashes and caches; do not regenerate unnecessarily.
- Run financial accuracy checks and existing renderer tests, `qa_timeline.py`, `validate.py`, `jitter_check.py`, full decode with errors fatal, inspect frame transition pairs, shot midpoints and 100% crops. Record any checks that cannot be performed. Include start/end disclaimers.
- **STOP after the 60s pilot for explicit owner approval**. Full film only after pilot approval; then separate full-film QA and final approval. Never upload/publish or generate Shorts automatically.

## Deliverables at each gate

Pre-production: audit with input hashes, verified asset list, any outstanding risks, duration estimate and recommended first-minute edit. Script v2 SHA-256 `14801320664962ebd79d3ed55d0065a61d905f2dea7d7f9110bdb9d85d695636`. Pilot: playable 60-second MP4 and real QA report. Full: only after approval, complete movie with QA evidence.

All work on a new non-main branch. No merge or publication without owner authorization.
