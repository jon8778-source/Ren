# When Can You Ease Off Saving for Retirement?

Working branch: `codex/retirement-ease-off-v3`, based on the current remote
approved v3 branch. Main and all approved coffee prototype originals remain
unchanged. Owner narration is approved and preserved word for word in script.md.
No additional script gate, thumbnail alternatives, Shorts or publication is part
of this task.

## Current checkpoint

See CHECKPOINT.md, manifest.json and project/GITHUB_TASK_STATUS.md. A preview
is an extract, not the complete episode. Timings in planned-shots.json are
explicitly provisional where audio is missing. Final shots.json must be derived
from completed narration. Do not copy historical coffee validation results.

## Environment

Python 3.12+, FFmpeg 6.1+ (libx264/AAC), ffprobe. From the repository root:

```bash
python3 -m venv project/episodes/retirement-ease-off/.cache/venv
project/episodes/retirement-ease-off/.cache/venv/bin/python -m pip install -r project/episodes/retirement-ease-off/requirements.txt
export REN_PILOT_PYTHON="$PWD/project/episodes/retirement-ease-off/.cache/venv/bin/python"
```

The cloud's existing /workspace/ren-voice-test-venv is also supported. Keep
HF_TOKEN in configured environment/secrets. Never paste it into a command or
commit it. resume.sh checks branch and token presence without logging values.

## Recover the recorded queue-full rejection

No automatic retry occurs. The first s004 attempt was rejected before admission:
QueueError, no event ID, no output, observed quota decrease zero. The failure
remains in manifest.json. The following explicit recovery command validates
those precise facts and allows one later attempt; it does not call Qwen itself.
Uncertain failures/timeouts and later repeat failures require separate review.

```bash
bash project/episodes/retirement-ease-off/resume.sh recover-queue-rejection
bash project/episodes/retirement-ease-off/resume.sh
```

For a normal future quota checkpoint, only the second command is needed after
the allowance resets. Existing valid WAVs are reused. Never erase inflight or
failed records to force a retry. Raw WAVs are saved and synced before validation;
the existing pilot module supplies duration, silence, corruption, clipping,
stale-input, quota, Space hardware/revision and durable publication safeguards.
The original coffee sentence's ten-second guard is retained in that module.

## Reproduce visuals and checks

Replace `python` below with the pinned virtual environment's Python:

```bash
python project/episodes/retirement-ease-off/workflow.py calculate
python project/episodes/retirement-ease-off/workflow.py verify
python project/episodes/retirement-ease-off/render.py --preview
python project/episodes/retirement-ease-off/validate.py --preview
python project/episodes/retirement-ease-off/render.py --plan-stills
python project/episodes/retirement-ease-off/validate.py --plan
```

After all narration is complete:

```bash
python project/episodes/retirement-ease-off/render.py --stills
python project/episodes/retirement-ease-off/render.py
python project/episodes/retirement-ease-off/validate.py
```

The renderer imports the actual approved v3 artwork, font, native-resolution
matting, command runner and encoded frame-count validation. Episode code extends
its shot pipeline for continuous measured narration, episode props, and reusable
per-shot encodes. Wide framing includes trainers; closer framing limits actor
scale to 1.25x native. No half-resolution decode, sharpening, mirroring, body
wobble, source audio or music. All graphics are drawn in code. No new art or
coffee-specific Alex scenes are used.

The audio master preserves natural speed and internal pauses. Only excessive
edge silence is removed; derivatives are normalized with headroom and resampled
to 48 kHz. Originals remain unchanged. Duration over 480 seconds is fatal;
propose an owner-approved minimal trim instead. The approximately 7–7½-minute
aim is secondary to exact wording and natural delivery; never pad a shorter read.

The MP4s and contact sheets are under ignored deliverables/; render caches are
ignored build/. **Do not add videos to Git history.** Audio originals and their
hashes are durable source checkpoints. A task environment without a supported
file-export mechanism must report that delivery limitation, never fabricate an
attachment/library ID or upload to an unrelated public host.

## Remaining review

No audio has been listened to. Local ASR is unavailable. Paragraph-level cut
timing is estimated within measured narration segments and needs a listening
alignment pass. Identity, accent, pronunciation and every spoken word remain
unconfirmed. See sources.md: live primary-source retrieval is blocked by current
network policy. Do not mark full validation or publication readiness complete
until these limitations and missing narration are resolved.
