# Is Your Daily Coffee Really the Problem? — checkpoint

Updated: 2026-10-27T22:14:54.898465+00:00

**This is not a completed video or a complete narration track.**

State: `quota_checkpoint`. Completed segments: 4/15.
Original audio retained: 62.947 seconds, including the reused diagnostic opening.
New original audio: 60.491 seconds. Remaining: s005, s006, s007, s008, s009, s010, s011, s012, s013, s014, s015.

Reported free balance: 97.63135299999999 GPU-seconds. Next-request reserve: 120 GPU-seconds; the balance is not necessarily exhausted.
Reported reset: 2026-10-28T20:40:01.231000+00:00. No paid hardware or voice fallback was used.

Observed quota decrease for this pilot batch: 87.001574 GPU-seconds.
Request elapsed time: 106.099 seconds, including queue/transfer/checkpoint overhead and any failed attempt. This is not GPU usage.

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

## Capacity estimate

The three paragraph returns used about 1.44 quota GPU-seconds per second of narration. At that observed rate, five minutes would use roughly 432 quota GPU-seconds, before accounting for the conservative unused reserve or future variation. This is a small-sample estimate, not a quota guarantee. The reused opening test was generated earlier and is excluded from the batch cost.

Validation in this task: 21 tests passed; complete planned storyboard preflight passed; continuous narration across two visual cuts was functionally rendered with existing test audio. All completed original hashes were verified. No acoustic pitch-discontinuity flags were raised, but listening remains required.
