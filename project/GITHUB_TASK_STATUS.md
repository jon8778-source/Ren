# Ren GitHub task status

Saved GitHub checkpoint, not the Android app's live progress indicator.
Last reviewed: 29 October 2026.

| Item | Verified state |
| --- | --- |
| Task | Ren v3 handover and character-sharpness correction |
| Branch | `codex/ren-approved-v3` |
| Publishing | Complete |
| Last verified content commit | [bb7688c](https://github.com/jon8778-source/Ren/commit/bb7688c011f31326a32484b1805db228ff981631) |
| Character correction | Decode original 1280×720 source; removed 640×360 reduction |
| Renderer | Published version matches the tested source |
| Artwork and voice | Approved originals preserved; no generation requests |
| Validation | 19 shots; 1,479 frames at 24 fps; full decode passed; equations and audio passed |
| Visual review | All shot midpoints and a same-frame close-up comparison at 100% size |
| Remaining task work | None |
| Main | Unchanged |
| Android display | Stale progress reported; client-side cause not confirmed or patched |

[Open renderer and instructions](https://github.com/jon8778-source/Ren/tree/codex/ren-approved-v3/project/prototypes/coffee-minute-v3)

[Play corrected sharp-character MP4](https://chatgpt.com/library?file_id=libfile_13029d9f00c08191982a1efc87f348c7&account_id=personal)

[Current validation evidence](prototypes/coffee-minute-v3/validation.json)

[Historical approved baseline](prototypes/coffee-minute-v3/validation-approved-baseline.json)

## Publishing safeguards

AGENTS.md directs future Ren tasks to use
[GITHUB_TASK_WORKFLOW.md](GITHUB_TASK_WORKFLOW.md): smaller writes, committed
checkpoints, remote verification and recovery from the first missing item.
These safeguards are published. They do not change the Android app or guarantee
live app sync. This page updates only when a task explicitly commits an update.
