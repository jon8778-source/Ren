# I Said No to Free Money for 3 Years: final package report

**Video:** `final_video.mp4`. 3:57.3 (237.34 s), 1280x720, 24 fps, H.264 (CRF 18) + AAC mono 48 kHz, 5,696 frames, 112 shots, 47.9 MB.
**Loudness:** -16.2 LUFS integrated, true peak -1.5 dBTP. No music.
**Status:** final render complete. Nothing has been uploaded, published or merged. Waiting for the owner's phrase `approved to publish`.

## Validation (all run on the final MP4)
| Check | Result |
|---|---|
| Full decode with errors fatal (`ffmpeg -xerror`) | clean |
| Format | h264 1280x720 24 fps yuv420p, aac 48 kHz; video 237.333 s, audio 237.337 s (0.004 s apart) |
| Timeline regression checks (`qa_timeline.py`, 17 checks) | **17 of 17 pass**: shots contiguous and frame-aligned, shot frames equal video frames (5,696), v3 shot caps, scene order equals the script (732 of 732 words, S1 to S7), approved assets present, no one- or two-frame inserts, every hard cut on a shot start, both page peels (age 25, "8 years later") hand over cleanly, no flashes |
| `validate.py` | **PASS**: no layout overlaps (text clear of Ren and faces, inside the safe area), no gaps; five 0.6-0.7 s pauses, each at a sentence end |
| Placement jitter (`jitter_check.py`) | 0.06 px worst (limit 0.12); old whole-pixel placement 0.36 px |
| v3 shot caps (Ren 5.5 s, story still 2.5 s, graphic 3.5 s) | none over; 112 shots, average 2.1 s |
| Equations and figures | drawn in code; every equation true on every frame (ledger total shown only with all three amounts; match stacks grow together; jar percentages shown only when settled) |

## Narration
- Model `Qwen/Qwen3-TTS-12Hz-1.7B-Base`, run locally on CPU, English, x-vector-only voice prompt from `Audio/ren_reference.wav` (v3 rules). Fixed seeds. Each scene's chunks are joined exactly as generated: no speed change, stretching or padding. Gain only to -16 LUFS, with a limiter.
- Whisper (medium.en) matches the script in all seven scenes apart from numbers (it writes digits, e.g. "$25,500" for the spoken figure) and a few word-initial artefacts that disappear when audio is padded (checked). **I cannot hear audio.** Not assessed by ear: the accent, pronunciation, tone and pace, including "lease" (Whisper once heard "least" in S2).

## What was checked visually
The middle of all 112 shots on the final file (contact sheet, `contact_sheet.png` shows the first frame of every cut), the six scene boundaries, the page peels, 100% crops of faces and graphics, the shots with Ren standing at the desk and in the lot against the plate geometry, and the before/after of the scale and shaking fixes.

## Changes since the approved rough cut
None to the story, narration or shots. The rough cut approved at Gate 3 already included the Ren scale/grounding fix and the sub-pixel placement fix; this render is the same cut at final quality (CRF 18 instead of 23).

## IRS 2027 contribution limit (script wording not edited)
- The script says Milliman projects $25,500, up from $24,500, and that the IRS had not confirmed it at the end of October.
- **Not verified against the IRS.** `irs.gov` and `milliman.com` are outside this session's allowed network domains, so I could not read the official notice or Milliman's own page. If you want it checked, add `www.irs.gov` and `www.milliman.com` to the session's network allowlist.
- What I could find by search (secondary sources, 7 November 2026): no IRS 2027 announcement in any result; coverage says the IRS normally publishes its retirement-plan cost-of-living notice between late October and mid-November; Milliman's latest forecast (inflation data through August) is $25,500 (it was $25,000 earlier in the year), conditional on September inflation; the 2026 limit is $24,500. One outlier site says $24,000, which doesn't match any projection.
- So the script's wording agrees with what I could find, but the IRS may announce at any time, possibly right after this was checked. **Re-check before publishing.** If the IRS has announced a different figure, the S6 narration and the on-screen "2027 contribution limit" card will need a change, which needs your decision and a regenerated S6 narration.

## Open issues and limits
1. **Audio not heard by me.** Please listen to the whole video, especially the accent, the pace and "lease".
2. **Resolution:** 1280x720 (v3 baseline; native for the library clips), not 1920x1080. Not chosen otherwise.
3. **Pacing:** 2.1 s average per shot, which follows from the v3 shot caps.
4. **Ren is standing, not seated,** at the desk: no seated pose exists in the approved stills.
5. **No articulated animation.** Reactions are pose swaps and cutaways; the mouth stays closed (v3 rules). The phone clip in S2 plays as supplied and carries its source movement.
6. **"8 years later" car** is the plain parking-lot plate with a tag: the desaturated grade was not approved.
7. **Supporting characters** (Dev, Priya, Gary) have one pose each and move by camera only. Their heights against Ren (170-178 cm) are assumed. Their art is softer than Ren's; style option (b), accept as is.
8. **HR folder text** ("HR Enrollment", "Page 6", "Employee Benefits & Retirement Plan") is baked into the supplied art, accepted for this video only, with the match line drawn in code.
9. **Validation** uses the project's own scripts (`validate.py`, `qa_timeline.py`); there is no approved reference MP4 to compare against.
10. **Educational disclaimer** appears as a small tag at the start and end, as the v3 rules ask.
11. **Draft-to-final:** the rough cut was reviewed at CRF 23; the final is CRF 18, so thin lines are slightly cleaner. No other differences.
