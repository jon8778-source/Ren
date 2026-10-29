#!/usr/bin/env bash
set -euo pipefail
cd "$(git -C "$(dirname "$0")" rev-parse --show-toplevel)"
test "$(git branch --show-current)" = codex/retirement-ease-off-v3
if [[ -z "${HF_TOKEN:-}" ]]; then
  echo 'HF_TOKEN missing; no generation submitted.' >&2
  exit 1
fi
EPISODE_PYTHON=${REN_PILOT_PYTHON:-/workspace/ren-voice-test-venv/bin/python}
exec "$EPISODE_PYTHON" -u project/episodes/retirement-ease-off/workflow.py "${1:-resume}"
