#!/usr/bin/env bash
# Continue a saved episode checkpoint; never repeat completed voice requests.
set -euo pipefail
cd "$(git -C "$(dirname "$0")" rev-parse --show-toplevel)"
test "$(git branch --show-current)" = codex/retirement-ease-off-v3
EPISODE_PYTHON=${REN_PILOT_PYTHON:-/workspace/ren-voice-test-venv/bin/python}
EPISODE_DIR=project/episodes/retirement-ease-off
"$EPISODE_PYTHON" "$EPISODE_DIR/workflow.py" init
if ! "$EPISODE_PYTHON" -c 'import json,sys; m=json.load(open(sys.argv[1])); sys.exit(not all(s["status"]=="complete" for s in m["segments"]))' "$EPISODE_DIR/manifest.json"; then
  bash "$EPISODE_DIR/resume.sh"
fi
if ! "$EPISODE_PYTHON" -c 'import json,sys; m=json.load(open(sys.argv[1])); sys.exit(not all(s["status"]=="complete" for s in m["segments"]))' "$EPISODE_DIR/manifest.json"; then
  "$EPISODE_PYTHON" "$EPISODE_DIR/render.py" --plan-stills
  "$EPISODE_PYTHON" "$EPISODE_DIR/workflow.py" status
  echo 'Narration incomplete; planning frames preserved. No partial video labelled complete.' >&2
  exit 2
fi
"$EPISODE_PYTHON" "$EPISODE_DIR/workflow.py" calculate
"$EPISODE_PYTHON" "$EPISODE_DIR/render.py"
"$EPISODE_PYTHON" "$EPISODE_DIR/validate.py"
"$EPISODE_PYTHON" "$EPISODE_DIR/review.py"
"$EPISODE_PYTHON" "$EPISODE_DIR/render.py" --preview
"$EPISODE_PYTHON" "$EPISODE_DIR/validate.py" --preview
echo 'Technical renders complete. Check QUALITY.md for listening, sources and delivery limitations.'
