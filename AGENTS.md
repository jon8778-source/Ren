# Ren project instructions

For new hybrid animation prototypes, read project/REN_VIDEO_RULES.md first.
These owner-approved v3 rules supersede conflicting older prototype styling
in CLAUDE.md and project/DECISIONS.md. Continue using their existing workflow
for legacy production episodes.

For future landscape v3 office shots, use the owner-approved **Ren left,
text/illustrations right** layout from project/prototypes/ren-left-layout/.
Read its layout.json and README.md before creating a new episode renderer.
This supersedes earlier right-side Ren placement in the coffee and retirement
renderers. Keep the approved steady full-body framing; do not copy their old
placement coordinates into a new video.

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
