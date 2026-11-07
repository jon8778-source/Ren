# Revision 6 — targeted prototype for owner review

Exactly **15.000 seconds**, 360 frames, native portrait 1080×1920, 24fps,
H.264/yuv420p video and AAC audio. Technical QA: no errors or warnings.
Video SHA-256: `d9954b4d2518a120efc8b314e686e7fa11e5d5209d3efea0130187e870b5abcb`.

## Changes

- 0–2s: renewal button visible immediately; approved palm-down right hand clicks
  the trackpad at 0.625s. Small pull-back exposes the action. Sleeve continues
  out of frame instead of ending as a rectangular cutout.
- 2–5s: four annual confirmations on successive physical calendar pages.
- 5–9s: genuine chest-up concerned Ren using the explicitly approved high-detail
  PNG, resized once from 941 to 900px. Face approximately 404px / 37.4% of frame
  width. Office upper wall fills background; no floor behind face or white papers.
- 9–15s: fixed $2,520/year revealed first; $840/year follows at 11.9167s as the
  paper unfolds. Sage contrast/underlines emphasize the comparison. “Premiums
  only” and “Care costs?” keep lower premium separate from total healthcare cost.

All earlier renderers, manifests, artwork and original MP4 preserved. No long-form
changes, no new TTS, no new artwork generation this turn, no full Short.

## Acceptance checklist

| Criterion | Result / evidence |
| --- | --- |
| Immediate opening focal point | PASS — frame zero has large renewal button; no full-body introduction |
| Click within first second | PASS — button confirmation/press at frame 15, 0.625s |
| Four-year repetition | PASS — four confirmed calendar years, starting 2.0, 2.5833, 3.1667 and 3.75s |
| Genuine reaction close-up | PASS — chest/shoulders upward, no legs/full-body source |
| Face 25–40% of width | PASS — approx. 404px / 37.4%, manual oval bounds checked on encoded screenshot |
| Visible eyes/natural concern | PASS — inspected native encoded close-up; raised inner brow, closed lips |
| Approved character identity | PASS — exact owner-approved PNG hash; no character substitution |
| Sequential premiums | PASS — Plan A at 9s; Plan B at 11.9167s, never revealed simultaneously |
| Readable figures | PASS — 178px Fredoka amounts, native screenshot inspected, measured safe bounds pass |
| No guaranteed saving implication | PASS — annual illustrative premiums; premiums-only/care-cost qualifier, no saving claim |
| No blue borders/letterboxing | PASS — full-bleed office/wood imagery; all-frame edge checks and screenshots |
| No distortion/matting damage | PASS in inspected native face/hand/shirt crops; single approved reaction asset remains stable |
| Correct figures | PASS — $2,520 and $840 derived from existing shared assumptions; no intermediate count-up |
| Audio preserved/synchronisation | PASS technically — all 705 AAC packets/timestamps and decoded PCM identical to Rev5; A/V endpoints equal |
| Narration listening/device review | NOT VERIFIED — no ear-based or physical Android playback claim |

## Checks and limits

Every encoded shot passed frame-count, geometry and fatal-decode validation
(48,72,96,60,84 frames). Full 15s fatal decode, frame timestamps, black/blank/border
screening, all-frame measured text safe areas and exact final 2s disclaimer passed.
Audio peak -2.00dBFS; no new clipping or timing edits.
Preservation-and-timing.json retains exact PCM hash and reveal timestamps.

Review evidence: three native screenshots, six sequential all-frame contact
sheets, three 4fps phone-size sequences and native face/hand/shirt crops. Visual
review used extracted frame sequences and native stills; real-time motion playback,
listening and physical Android playback remain unverified. No browser/computer-use
playback tool was exposed. Technical sync does not certify spoken delivery.

The reaction intentionally holds the single approved concerned expression for 4s;
no new acting rig, blinking, mouth movement or decorative wobble was invented.
All source animation audio is discarded; no music added.

## Approval gate

STOP. Jon approved the two artwork assets only. The actual Revision 6 MP4 awaits
explicit prototype approval before any complete 60-second production. No prototype
approval record has been created automatically. No merge or YouTube publication.

Reproduction is in ASSETS_AND_STORYBOARD.md; run validate_revision6.py after render
to rebuild screenshots and preservation evidence. Videos/caches stay outside Git.
