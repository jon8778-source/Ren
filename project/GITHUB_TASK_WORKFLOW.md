# GitHub publishing and recovery

These instructions apply to Ren repository tasks. They improve publishing and
recovery independently of the ChatGPT Android progress display. They are not an
Android client patch, a live monitor, or a guarantee of background execution.

## Before writing

- Read AGENTS.md and the applicable project rules. Confirm the authorized branch.
- Read project/GITHUB_TASK_STATUS.md and inspect the current remote branch.
  Treat that file as a recorded checkpoint; later commits may supersede it.
- Compare remote files with the requested deliverables. Reuse completed work.
- Test write access using a necessary small source/document update. If CLI push
  lacks credentials, use the connected GitHub app; do not ask the Android user
  to install a CLI or paste a token into chat.

## Keep writes bounded

- Use normal binary upload only when supported and completing successfully.
  After an interrupted or uncertain write, check its resulting object or branch
  before retrying. Do not loop on the same stalled method.
- For the approved artwork pack, retain its existing lossless format and
  checksums. If another large binary needs this fallback, limit each text chunk
  to 96,000 characters and each create-tree request to at most three such chunks.
  Verify the reconstructed original bytes before using them.
- Never print full binary/base64 payloads into user-visible progress or tool
  summaries. Pass them as data, with short metadata as the visible result.
- Publish a checkpoint after each coherent asset or at most five successful
  upload requests, whichever comes first. Commit the partial state and status
  together on the task branch; mark incomplete deliverables explicitly.
- Update the branch using its expected head SHA. Do not force away concurrent
  changes. Read the new head after a lease mismatch.
- After a checkpoint, verify the remote files and return a short status with a
  direct commit link. Report successful requests, not an invented percentage.

## Status record

Keep project/GITHUB_TASK_STATUS.md concise. Record the task, branch, stage,
completed deliverables, remaining actions/blockers, the last verified content
commit, validation evidence and result links. Mark complete only after required
files are reachable on the branch and all requested validation passes.
This file changes only when a task explicitly commits an update; it is not live.

## Resume after an app interruption

1. Read the status page and branch head using the GitHub connector.
2. Check the expected paths and hashes at that commit. A created blob/tree is
   not published until a branch references the commit.
3. Inspect ambiguous writes before retrying. Continue from the first missing
   item. Preserve approved artwork and narration.
4. Re-run checks only when the source changed, a prior check failed, or results
   were not retained.
5. Finish with the confirmed commit/folder links, requested deliverables,
   validation summary and anything incomplete. Do not imply work continues
   after a final response unless an actual background task was created.

## Observed incident: 29 October 2026

The conversation recorded a CLI push failing for missing HTTPS credentials,
interrupted large connector uploads, and older progress text in the Android
app. The completed handover was independently verified on GitHub at
e3cf0438564ff5cae41017123713e25d63031a00. Smaller lossless artwork uploads
succeeded. These facts do not establish the cause of the Android crash or stale
display; Android client logs and service telemetry were not available.
