# Is Your Daily Coffee Really the Problem? — checkpoint

Updated: 2026-10-28T22:35:31.931346+00:00

**Complete pilot rendered for review; voice/words still await owner listening confirmation.**

State: `pilot_rendered_review_pending`. Completed segments: 15/15.
Original audio retained: 297.093 seconds, including the reused diagnostic opening.
New original audio: 294.636 seconds. Remaining: none.

Reported free balance: 2246.590822 GPU-seconds. Next-request reserve: 120 GPU-seconds; the balance is not necessarily exhausted.
Reported reset: 2026-10-29T22:15:59.575000+00:00. No paid hardware or voice fallback was used.

Observed quota decrease for this pilot batch: 422.552965 GPU-seconds.
Request elapsed time: 506.983 seconds, including queue/transfer/checkpoint overhead and any failed attempt. This is not GPU usage.

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
