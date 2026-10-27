#!/usr/bin/env bash
# Resume only this checkpoint, with no token values in arguments or logs.
set -euo pipefail
PILOT_ROOT=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
cd "$PILOT_ROOT"
if [[ -z "${HF_TOKEN:-}" ]]; then
  echo 'HF_TOKEN missing; no generation submitted.' >&2
  exit 1
fi
if [[ $(git branch --show-current) != codex/ren-coffee-pilot ]]; then
  echo 'Use the codex/ren-coffee-pilot checkout; no branch changes were made.' >&2
  exit 1
fi
PILOT_PYTHON=${REN_PILOT_PYTHON:-/workspace/ren-voice-test-venv/bin/python}
if [[ ! -x "$PILOT_PYTHON" ]]; then
  PILOT_PYTHON="$PILOT_ROOT/project/pilots/daily-coffee/.cache/venv/bin/python"
  if [[ ! -x "$PILOT_PYTHON" ]]; then
    python3 -m venv "${PILOT_PYTHON%/bin/python}"
    "$PILOT_PYTHON" -m pip install --no-cache-dir -r project/pilots/daily-coffee/requirements.txt
  fi
fi
exec "$PILOT_PYTHON" -u project/cliplib/pilot.py resume --publish-checkpoints "$@"
