# Pilot revision 3: change log, QA and production readiness

**File (local only, not in git):** `/output/free_money_S1_S2_pilot_rev03.mp4`. Rev02 and the original pilot are kept beside it.
**Format:** 1280×720, 24 fps, H.264 + AAC, 51.58 s, -16.2 LUFS. **Same audio as rev02 and the pilot (bit-identical, MD5 `f927e4f3…`).** Nothing was regenerated: same art, same Qwen voice, same script and scene order.
**Status: STOP. Waiting for your written approval.** No later scenes rendered, no new artwork, no rule changes.

## Conflicts in the brief, and how I handled them
1. **"No arbitrary shot-duration limits" against the v3 caps** (Ren 5.5 s, story still 2.5 s, graphic 3.5 s). The caps are owner-approved production rules and you also asked me not to change the rules. I kept them. No shot in rev03 needed a longer hold. If you want the caps lifted for full production, that is a rule change for you to approve.
2. **"Open with the employee checking his finances" against "don't change scene order or narration".** The first 8 s of narration is the porch, the pay stub and the question. I opened on the pay stub itself and the comparison, then cut to the wide shot of Dev and Ren. No narration or scene was moved.
3. **"Compare the lease with available income".** The script has no take-home figure. The bar shows the $489 against **monthly pay before tax**, drawn to scale from the script's own $44,000 ($489 is about 13% of $3,667). No new number is printed.
4. **1080p.** Still not reliable: the library clips are native 720p and the plates are 1672 px wide. Staying at 1280×720.

## Change log
**Opening hook (first 8 s).**
- Shot 1 (0-2.3 s): a close-up of the pay stub with the glowing "Employer match: 2%" line, and a line running to a panel: *One employer's plan (example)*, You 2%, Employer 2%, and the plan's limit ghosted as "up to 4%". Without sound it says: an employer would add up to 4%, and he is getting less.
- Then the wide Dev and Ren shot, Dev's question and Ren's confusion.
- No dollar-loss figure, no flashing text, no zoom effects.
**Character interactions.**
- Kept the real phone-raise clip, the desk and laptop shot, and the pose reactions.
- **The 2% decision** now happens on a benefits screen beside Ren: the contribution slider moves to 2%, the employer's matched bar grows to 2%, and the dashed limit to 4% appears.
- **The lease trade-off** has the $489 on the phone, then a bar of $489 against monthly pay before tax, which stays on screen while Ren reacts.
- **S1's "three years"** now shows three pay stubs, each with the same 2% match and a ghosted "+2%" above it, instead of three empty circles.
**Scene composition (slide behaviour removed).**
- The repeated card behind Ren is gone: he only reacts at "felt like I'd made it".
- One age label (the "Age 25" pill) and one salary figure ("$44,000 salary").
- The porch scene was shortened to the wide reveal, so the two stub close-ups are separated by Ren's reaction shots.
**Financial graphics.**
- "Example plan" wording everywhere: "This employer's plan (example)" on the card, "401(k) enrollment | example plan" on the laptop screen, and "up to 4% of your salary (your plan may differ)".
- Employee and employer are labelled separately ("You (employee)", "Employer") and the matching rate (each $1 matched) and limit (4% of salary) are stated.
- Equations stay true on every frame (the stacks grow together).
**Transitions.** Hook to wide is a reveal cut; Dev's question to Ren is a reaction cut; the stub-to-Ren cut is the consequence; the page peel marks the time change; the phone-in-hand to phone-screen cut is a match cut. No fades, no shake, no bounce.
**Pacing.** 22 shots, average 2.3 s, no static frames. Numbers have time to read: the salary card for 4 s, the lease phone for 2.3 s, the match panel for 2.3 s, the benefits screen for 3.1 s.

## QA: pass / fail
| Check | Result | Notes |
|---|---|---|
| 1. Character consistency | **PASS** | all 44 first and middle frames of this render checked against the design lock; 100% crops of Ren's face are crisp; no new art. |
| 2. Visual clarity | **PASS** | no overlaps and nothing over faces or Ren (automatic layout check plus the contact sheets). The pay-stub paper in the two close-ups is slightly soft because the art is enlarged; the overlays on it are sharp. |
| 3. Storytelling | **PASS (my reading, not a viewer test)** | the first 8 s carries the conflict visually. I could not test it with real viewers without sound. |
| 4. Financial accuracy | **PASS** | every figure matches the script; bars drawn to scale; "example plan" wording; no unsupported claim. The "Payment due" banner is a dramatisation of the lease. |
| 5. Audio synchronisation | **PASS for timing, ear check open** | cuts and graphics follow the Whisper word times; audio unchanged. I cannot hear the audio. |
| 6. Mobile readability | **PASS with one exception** | all content text is 28 px or larger at 1280×720. The disclaimer tag is 19 px by design (v3: no large banner), which is small on a phone. |
| 7. Rendering stability | **PASS** | full decode clean with errors fatal, 1,238 frames, no black frames or audio gaps (one 0.63 s sentence-end pause that is the model's own). Rebuildable from the scripts in about 15 minutes. |

## Remaining limitations (nothing below is claimed as done)
- **No articulated animation exists.** Expressions, "looking at the laptop" and "reacting" are **simulated** with pose swaps (R1 to R3, R3 to R2), the laptop screen lighting up, and cutaways. Ren's eyes do not actually track the laptop or the phone.
- The phone raise is the only real library gesture; the lease is checked through the phone clip and a phone-screen cut, not a continuous action.
- Dev has one pose, so he is moved by camera only. The folder slides on with no hand.
- Present-day Ren and the flashback share the office plate; only the "Age 25" tag and the peel separate them.
- 1280×720 only. The mouth stays closed, per the v3 rules.
- Voice items still open: please listen to "lease" (heard as "least") and the accent.

## Production readiness: **Ready with minor limitations**
The structure, voice, art, figures and layout are stable and reproducible, and rev03 fixes the hook, the repeated labels and the match wording. What remains is not about the renderer: (1) your ear check on "lease" and the accent, (2) your decision on the v3 shot caps and on 720p against 1080p, and (3) the fact that interaction is pose-swap, not articulated, so a full six minutes will lean on the same cut-and-cover techniques.
