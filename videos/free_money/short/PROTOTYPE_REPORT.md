# 1-minute Short: 15-second prototype report (v3 Shorts gate)

**Status: STOP. Waiting for the owner's explicit approval of this prototype before the complete Short is rendered.** No approval has been recorded (`prototype-approval.json` does not exist); the launcher will refuse the full stage without it.

**File (local only, not in git):** `/output/short/free_money_short_PROTOTYPE_15s.mp4`. 1080x1920, 24 fps, H.264/yuv420p + AAC, **15.000 s (360 frames)**, -15.9 LUFS, peak -1.6 dBFS. SHA-256 `7498467423aa351c...` (bound in `prototype.qa.json`).

## What the prototype is
The first 15 s of a planned **57.5 s Short** (1,380 frames, 21 beats) made from the long video's own approved narration: 192 words, whole sentences in script order, wording unchanged, cut by `short_audio.py` (no resynthesis, no speed change, no stretching, no inserted silence).
- 0.0-3.9 s **stub close-up and example plan**: Dev's pay stub with the match line, and a panel: "One employer's plan (example)", You 2%, Employer 2%, the limit ghosted at "up to 4%". The overlooked benefit is on screen in the first seconds, with the opening disclaimer.
- 3.9-6.7 s **porch two-shot**: Ren and Dev; "Who's keeping the difference?"
- 6.7-9.7 s **tight stub line**: "Match: 2%" darkens and the frame sinks on "my stomach dropped".
- 9.7-11.4 s **three years**: Ren thinking, three pay stubs each with the same 2% match.
- 11.4-13.9 s **age 25**: Ren standing at the desk, one "Age 25" label.
- 13.9-15.0 s **salary**: Ren with one "$44,000 salary" card, and the exact end disclaimer for the last 2 s (the launcher requires it in a prototype's last two seconds; in the complete Short it sits at the end).

Six distinct compositions; full-screen environment art on the porch and office scenes; no border or letterbox; all numbers, labels and cards drawn in code.

## Launcher QA (`prototype.qa.json`): technical-pass-review-required, 0 errors, 0 warnings
Resolution and aspect, 24 fps, codecs, 360 frames, uniform frame timestamps, full fatal decode, A/V start and end (0.0 s apart), no blank frames or black bars, no frozen runs (longest identical run 1 frame), asset existence and SHA-256 (15 assets), scene timeline, unique scene and animation IDs, three or more distinct compositions, full-screen environment, 2-4 s beats (two are justified in the manifest), measured text bounds. Preflight passes.

## Measured layout (`layout.json`)
All text is inside the safe rectangle x 72-900, y 180-1560. Smallest text is 42 px (disclaimer 32 px on its own light pill). The exact disclaimer is continuous over 13.0-15.0 s. Figures are measured from the font, not guessed; interval ends are the scene ends (the opening disclaimer is actually visible 0.33-2.6 s).

## Human review: what I did and did not do
**Did:** viewed 16 frames across the whole prototype and the stills of every scene, 100% crops of faces and edges at output size, the measured text evidence, the audio level. Fixed after looking: the quote card sat over both faces on the porch (characters moved back, card made one line); the disclaimer was illegible on shirts (now on a light pill); the on-stub label was about 30 px (shortened to "Match: 2%", now 56-67 px); the "stomach dropped" beat looked like the opening shot (now a tight crop with a sinking camera).
**Did not:** listen to the audio (I cannot hear it); watch the whole prototype in motion at speed; check on a phone or other devices.

## Unresolved issues
1. **Audio joins (your ear check).** In the first 15 s the narration skips "I didn't know what he meant." (a cut at about 5.4 s) and jumps to "Twenty-five." (about 11.4 s). Joins are tight because no silence may be added. Please listen to them, the accent and the pace.
2. **Soft pay-stub paper.** The stub art is a 160 px original enlarged 3-4.7x. The paper looks soft in the close-ups; the match label on it is sharp. Faces and Ren are crisp.
3. **Landscape plates cropped to portrait.** The plates are 1672x941 and are shown 2.04x enlarged. The porch and office backgrounds look acceptable at output size; if you find them too soft, ASSET_REQUIREMENTS.md has a numbered brief for portrait-native plates (new artwork needs your approval).
4. **Ren stands at the desk,** not seated (no seated pose exists).
5. **Beats 1 and 3** both use Dev's stub; beat 3 is now a tight, sinking shot, but they are still the same prop.
6. **No captions** (not required by the rules): say if you want word-by-word captions.
7. **Not yet built:** beats 7-21 (lease, folder, match, jars, ledger, app toggle, 90 seconds, close). They are planned and in the manifest and render only after approval.
8. The Short never mentions the unverified 2027 IRS limit.

## To continue (only after you approve)
Reply with your approval, for example "prototype approved". I will record it from your message (who, when, quote, review notes, file SHA), then run the full stage for the remaining 42.5 s, QA it, and stop again for your review. Any change to the script, audio, art, layout or renderer invalidates the approval and needs a fresh prototype.
