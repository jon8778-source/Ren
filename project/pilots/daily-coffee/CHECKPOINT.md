# Is Your Daily Coffee Really the Problem? — checkpoint

Updated: 2026-10-28T21:09:16.667491+00:00

**This is not a completed video or a complete narration track.**

State: `quota_checkpoint`. Completed segments: 10/15.
Original audio retained: 189.609 seconds, including the reused diagnostic opening.
New original audio: 187.152 seconds. Remaining: s011, s012, s013, s014, s015.

Reported free balance: 117.85778699999997 GPU-seconds. Next-request reserve: 120 GPU-seconds; the balance is not necessarily exhausted.
Reported reset: 2026-10-29T21:01:03.789000+00:00. No paid hardware or voice fallback was used.

Observed quota decrease for this pilot batch: 269.143787 GPU-seconds.
Request elapsed time: 329.544 seconds, including queue/transfer/checkpoint overhead and any failed attempt. This is not GPU usage.

## Resume

On branch `codex/ren-coffee-pilot`, from the repository root:

```sh
bash project/pilots/daily-coffee/resume.sh
```

The launcher checks free quota before requesting anything. Completed WAVs are hash-checked and reused. It does not automatically replay failed or interrupted requests.

## Quality and limits

- Original WAVs, text, settings, reference hashes and per-attempt results are in `manifest.json`.
- Current completed originals pass duration, corruption, silence and clipping checks.
- Edge-only silence trimming and level matching affect derived files, never originals.
- ASR is unavailable locally; all spoken words, British accent, speaker identity and boundaries still require listening review. No owner approvals have been fabricated.
- Office and narrative artwork are bundled template placeholders, not approved office/Alex art.
- Continuous narration across visual cuts was functionally verified with existing test audio; no partial pilot is being delivered as finished.
- Final 285–315-second duration is enforced at assembly, without speech-speed changes or silence padding.
- Script and all completed originals are committed on this branch. Credentials, models and temporary render caches are excluded. Nothing is merged into main.

## Latest resume — 28 October 2026

Six new paragraph WAVs retained: 126.661 seconds. Observed quota decrease: 182.142213 GPU-seconds. Generation-attempt elapsed time: 223.445 seconds. One quota observation returned HTTP 503; a later read recovered the balance before generation continued. No completed segment was regenerated.

All ten saved original hashes were verified; derived edge-only trimming and level matching were exercised. Acoustic boundary flags: []. Words and voice remain pending listening review. The workflow has 22 passing unit tests; no implementation or model-setting changes were made beyond accounting for the first request after a quota reset and marking active generation accurately.
