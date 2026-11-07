# Ren project instructions

For new hybrid animation prototypes, read project/REN_VIDEO_RULES.md first.
These owner-approved v3 rules supersede conflicting older prototype styling
in CLAUDE.md and project/DECISIONS.md. Continue using their existing workflow
for legacy production episodes.

The approved v3 renderer, all four original artworks, pinned dependencies,
run instructions and validation results are published under
project/prototypes/coffee-minute-v3/. Artwork is stored losslessly in the
artwork/ chunks and restored automatically by render.py (or unpack_artwork.py);
SHA-256 checks prevent substitution or corruption. See README.md and
validation.json for fresh-checkout verification. Keep prototype work separate
from main and preserve approved narration. No new voice requests are needed.

## Character sharpness and GitHub task recovery

Decode Ren clips at their native 1280×720 resolution before matting and the
final composition resize. Do not downsample them to 640×360. Check the face,
glasses, hair, hands and clothing at 100% output size in wide and close shots;
resolution/frame-count checks alone do not establish visual sharpness.
For GitHub publishing, follow project/GITHUB_TASK_WORKFLOW.md and maintain
project/GITHUB_TASK_STATUS.md with remotely verified checkpoints. These are
publishing safeguards, not an Android client-sync fix. Resume from the remote
branch after an interruption; do not regenerate approved art or narration.

## Shorts production

For any vertical Ren YouTube Short, read both `project/REN_VIDEO_RULES.md` and `project/REN_SHORTS_RULES.md` before planning, asset generation, narration or rendering. The Shorts rules add story-first creative direction and a 15-second owner-approval prototype gate; the general video rules continue to govern approved character identity, Qwen voice, technical integrity and financial accuracy. If the two documents conflict on Shorts-specific composition or storytelling, prefer `REN_SHORTS_RULES.md` while preserving the general rules' voice, character and accuracy safeguards. For long-form videos, read `REN_VIDEO_RULES.md` and `REN_LONGFORM_RULES.md` without imposing Shorts-specific rules. Do not assume an owner's reference MP4 is available locally; verify assets before using them.

## Long-form production

For every new long-form Ren video, read `project/REN_VIDEO_RULES.md` and `project/REN_LONGFORM_RULES.md` before scripting, asset planning, narration or rendering. Follow the story-first narrative and supporting-character guidance, perform the asset inventory, and STOP after the mandatory approximately 60-second pilot for owner approval before rendering the full video. Preserve the approved Qwen voice, character art, maths and technical safeguards in the general video rules. Do not apply Shorts-specific 9:16 requirements or the 15-second prototype gate to long-form work. Only use a shorter preview for targeted edits when explicitly authorised by the owner.
