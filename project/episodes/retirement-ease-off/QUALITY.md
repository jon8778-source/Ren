# Retirement easing-off v3 — rendered for review

The complete owner script is rendered. **This is not a claim of approved words,
voice identity, publication readiness or completed primary-source verification.**

## Delivered files prepared

- Ren_When_Can_You_Ease_Off_Saving_v3.mp4: 338.666667 seconds (5:38.67),
  1280×720, 24 fps, H.264/yuv420p and AAC mono at 48 kHz; faststart MP4.
- Ren_Retirement_Opening_v3.mp4: 55 seconds, same format.
- Ren_Retirement_Narration.wav: complete 338.665-second narration,
  48 kHz mono, 24-bit PCM. Original generated WAVs are preserved separately.
- shot-contact-sheet.jpg: all 122 encoded shot midpoints.
- script.md, shots.json, assumptions.json, calculations.json, sources.md,
  source-retrieval.json, manifest.json, validation.json and README.md.

Generated media are in ignored deliverables/, outside Git history. Source,
original WAVs, hashes and reports are on codex/retirement-ease-off-v3. Main and
the approved coffee prototype, its original assets/audio, and voice reference
have no changes. No new artwork, thumbnails, Shorts or YouTube publication.

## Office revision from owner feedback

Ren now holds one framing through each consecutive office passage; framing
changes only after a non-office cutaway. All 32 office passages obey this rule.
Office captions are wrapped into the blank wall beside Ren at (610,80)–(840,420),
clear of furniture and wall artwork. Caption bounds are validated, and every
rendered Ren frame checks the caption area against his matte silhouette.
The closer scale is now 1.15x native. All 41 office shots were re-rendered;
81 unchanged graphic shots were reused after source/shot-input equivalence checks.
The encoded narration bitstream is byte-identical to the previous version.
No new voice requests or Hugging Face allowance were used for this revision.

## Runtime and narration

Your exact script is unchanged: 980 whitespace-delimited words. Its natural
delivery is shorter than the approximately 7–7½-minute aim, but below eight
minutes. No silence padding, speed changes, stretching or added narration.
Original WAVs total 340.885 seconds; only 2.220 seconds of excessive edge silence
were removed in derivatives. Internal pauses are preserved. Segments were
normalized with headroom and properly resampled to 48 kHz. Master measurements:
−18.02 LUFS, −2.00 dBTP, 2.3 LU loudness range.

Qwen 1.7B Base, English, use_xvector_only=True, the approved reference and its
transcript hashes match the existing approved workflow. Fourteen original WAVs
passed word-count duration bounds, corruption, silence and clipping checks.
No pitch or adjacent-segment acoustic review flags were raised. These checks do
not establish speaker identity or correct words.

## Verification performed

All 122 encoded shot frame counts pass; total 8,128 frames. Longest Ren shot
5.0833 seconds; longest graphic 3.375 seconds. Full final decode with fatal
errors passes. Encoded narration correlation with the complete master is
0.9999766; audio/video timing differs by less than one frame. Each shot has only
a video stream; final audio is mapped solely from the master. No music.

All 667 calculation-source frames retained fixed correct expressions and labels.
Shared assumptions and all seven claim expressions pass the existing calculation
claims checker. Rounded outcomes are $1,066,335 and $656,242. Both use the same
$400,000 start, 25 years and zero new contributions. Rates are hypothetical real
returns after fees; the illustrative target is not a withdrawal entitlement.
Balances are in today's purchasing power, before withdrawal taxes. No realistic
market forecast or guaranteed return is presented.

The original production review inspected all 122 encoded midpoints and 78 frames
around 13 transitions. For this revision, all 41 changed encoded office midpoints
and 36 frames around all nine consecutive office boundaries were inspected;
previous review was retained for the 81 unchanged graphic encodes.
Wide/closer encoded shots were inspected at 1280×720 for face, glasses, hair,
hands, clothes and trainers. Native 1280×720 matting is retained; no sharpening,
half-resolution decode, upscaling model, mirroring or added body wobble. White
clothing and trainers remain intact in inspected frames. The four used gesture
clips were probed and sampled from 1.25 to 6.5 seconds; sampled mouths are closed.
No sampled blank frames, obscured faces/hands/furniture or major matting damage
were found. This was frame inspection, not full-motion viewing or listening.
The 17 existing voice/workflow tests pass using mocks, with no real API calls.

## Free allowance and elapsed time

15 voice endpoint attempts: 14 returned WAVs and one queue-full rejection before
admission. The rejected request had no event ID/output and zero observed quota
charge. After the correct queue-status endpoint reported an empty queue, one
explicitly documented recovery succeeded. No looping or uncertain replay.

Measured allowance decrease: **487.452565 ZeroGPU GPU-seconds**.
Instrumented request elapsed time: **572.789178 seconds**. Elapsed includes
queue/transfer/checkpoint overhead, and excludes offline waiting, diagnosis,
dependency downloads and CPU video rendering. Allowance units are not a claim
of measured physical GPU residency. Last reported remaining: 1,759.138257 of
2,400 allowance seconds; overquota_used=0. Reported reset:
2026-10-29 22:15:59 UTC. No paid endpoint, credits, hardware upgrade or other
voice service was used. See usage.json.

## Remaining blockers and limits

1. No audio has been listened to. Word accuracy, British pronunciation, delivery,
   identity and voice consistency need listening review. Optional local ASR
   weights could not be downloaded through the proxy. No substitute service used.
2. Paragraph cut alignment is estimated by word weights inside measured segments;
   it needs a listening alignment pass. The soundtrack itself is continuous and
   uses every completed segment in order.
3. Current primary US sources could not be retrieved: the network policy rejects
   IRS, SSA, Department of Labor and Investor.gov requests. sources.md records
   the claim/source checklist honestly; those pages were not verified live.
4. The owner authorized temporary public file hosting after Android could not
   open workspace links. A normal HTTPS MP4 download is supplied separately and
   checked against the original SHA-256. Such links expire after about one hour.
   No MP4 is added to Git.

Resume/rebuild with `bash project/episodes/retirement-ease-off/produce.sh`.
Completed valid audio is reused without a new voice request. Details and pinned
dependencies are in README.md.
