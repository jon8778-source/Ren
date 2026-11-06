# Ren Long 1 visual-asset manifest

## Generated editable-code visual comps

| Asset | Intended scene | Production status |
|---|---|---|
| `assets/scenes/01_open_enrollment.png` | Hook email/click | Concept only, rebuild in approved renderer |
| `assets/scenes/02_four_seconds_payoff.png` | 4 sec vs 40 min and $1,980 hook | Concept |
| `assets/scenes/03_payment_audit.png` | Car/backstory/payment audit | Concept |
| `assets/scenes/04_three_questions.png` | Dev's three-question reveal | Concept |
| `assets/scenes/05_bad_year_comparison.png` | Worst-year PPO/HDHP comparison | Concept |
| `assets/scenes/06_real_year_comparison.png` | Normal-year net comparison | Concept |
| `assets/scenes/07_hsa_contributions.png` | Funding the HSA | Concept |
| `assets/scenes/08_hsa_balance.png` | HSA contributions vs withdrawals | Concept |
| `assets/scenes/09_not_always_cheaper.png` | PPO might be better for some people | Concept |
| `assets/scenes/10_three_question_close.png` | Final CTA and disclaimer | Concept |
| `assets/thumbnail_concept.png` | Working YouTube thumbnail | Concept, not approved for publishing |
| `assets/storyboard_contact_sheet.png` | 10-scene layout overview | Review only |

## Reference artwork used

User-uploaded Ren portrait images are provided as JPGs in `assets/source_references/`. Simple near-white exterior matte versions are available in `assets/character_cutouts/`. These are visual layout references, **not approved GitHub renderer frames**. Do not substitute them for the approved v3 native-resolution animation. Cutouts may have edge artefacts; validate white shirt, glasses and arms if shown.

## Assets deliberately NOT invented

- Dev portrait or mouth animation: no user-approved character design yet. Use Dev's voice-free dialogue as cards or an establishing porch/sedan graphic.
- Priya portrait: use phone text overlay or seek separate art approval.
- Danny/Uncle Gary portraits: communicate via phone messages until approved designs exist.
- New Ren animations, voice, backgrounds: use the approved v3 assets and source repository rather than substituting new images.
- Neither of the two Shorts: user intends a separate Codex brief.

## Regeneration

`generate_graphics.py` generates the PNGs from the included user-supplied portraits, PIL and scipy. It preserves financial values in code so producers can re-check them rather than copying data from a visually generated picture. Final Ren motion graphics should reproduce these as code-generated text/graphics with the correct repo Fredoka font.
