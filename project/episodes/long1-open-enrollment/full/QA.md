# Full episode QA — 6 November 2026

Complete film rendered for owner review: **5:29.000**, 1280×720 landscape 16:9,
24fps, H.264 High/Level3.1/yuv420p, AAC-LC mono48k, MP4 fast-start. 7,896 frames,
107 shots. Natural narration328.978750s; video has21.25ms frame quantisation tail.
The supplied script naturally runs shorter than the approximate6–7-minute target.
No speech acceleration, time stretch, silence padding or filler was added.

## Checks performed

- Every encoded shot's exact frame count, full continuous coverage and limits:
  Ren<=5.5s, animated graphics<=3.5s; no story stills over the cap.
- Entire final movie decoded with errors fatal; all7,896 frames screened black/blank.
- All107 encoded shot midpoints and530 samples around all106 cuts inspected.
  Three1280×720 frames inspected at100% for face, glasses, hair, hands, white
  clothing/trainers, matte edges and end-card/disclaimer layout. No clipping,
  furniture obstruction, blank frame or visible edge halo found in samples.
- Native1280×720 Ren decode/matte; single0.9 composition resize. Left, steady full
  body; fitted translucent white/black-outline boxes right. No automatic mirroring,
  scaling switches, body wobble or mouth flapping. Approved narrator-led mouth closed.
- Shared math checks pass. Fixed financial regions checked over2,075 encoded frames.
  $1,440 direct cash vs$690 net value, and$2,430 contributed vs$1,830 after withdrawal
  remain distinct. Generated prop labels blank; all financial figures/equations/UI
  text in code. Completed equation totals never count up incorrectly.
- All20 original WAV hashes/settings verified. The17 already completed originals
  were reused byte-identically after owner approved the three wording replacements.
  One generation call per segment; no retries, paid fallback or overquota usage.
- Processed samples concatenate exactly in order with no inserted gaps; only
  excessive edge silence trimmed.330.678750s raw→328.978750s processed. No retiming.
  AAC/master correlation0.99997436; final loudness−18.04LUFS, true peak−1.93dBFS.
- Source-animation audio discarded; no music. Approved British Qwen1.7B Base,
  English, use_xvector_only=True, unchanged reference and transcript hashes.
-150 external SRT captions preserve exact final script text/case/punctuation and
  compounds. Timing uses local forced alignment. Decoder-only250ms context flushed
  the final phoneme of s014; that context is never in exported narration, and every
  word timing stays inside the original waveform. Forced alignment is not ASR.
- Exact educational disclaimer visible at the beginning/end. Shared clips from the
  approved opening retain its brief pilot-end disclaimer too; no persistent footer.

## Sources and approval

Owner approved removing the unverified8.2% forecast/$4,500 limit/January15 deadline.
No such date-specific claim remains in the production text/graphics. See
SOURCE_NOTES.md and wording-approval.json. Primary sites were not independently
fetched; general HSA context links are cited without claiming live verification.
Old supplier candidates/fact-check headings are retained only as historical inputs.

## Measured generation usage

Whole episode, including previously generated approved pilot:448.285260 observed
GPU-seconds,20 calls. Sum of request elapsed times518.345204s, including transfer/
queue overhead; elapsed is not GPU usage. Full production after pilot:17 new calls,
370.136345GPU-seconds,430.799039s elapsed. Latest3 approved replacements:
38.898941GPU-seconds,48.667607s elapsed. Zero paid/overquota usage, zero retries.
Historical snapshot6 Nov15:23:47UTC:1932.557652 free GPU-seconds; reported reset
7 Nov11:23:05UTC (London GMT). See quota-report.json; no live balance guarantee.

## Review limits

No actual listening, full audiovisual watch-through or physical Android test was
available. New spoken wording/pronunciation and voice continuity remain listening
review items. Coarse pitch screen flags s019→s020 (109.1→160.6Hz) for attention;
this can be inflection and is not proof of a different speaker. Same reference/
model/settings verified. No automatic rejection/regeneration for that statistic.
Technical Android-compatible codecs/fast-start confirmed; device playback untested.

No production blockers remain. This is a complete review export, not an owner
approval of final words/performance or authorisation to publish. No merge, main/
approved-branch changes, GitHub media upload, Shorts or YouTube publication.
