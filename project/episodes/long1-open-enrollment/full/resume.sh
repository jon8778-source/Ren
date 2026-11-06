#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../../../.."
TASK_VOICE_PYTHON="${REN_VOICE_PYTHON:-/workspace/ren-voice-test-venv/bin/python}"
TASK_RENDER_PYTHON="${REN_PYTHON:-/workspace/Ren/project/.tools/venv/bin/python}"
if [ ! -x "$TASK_VOICE_PYTHON" ]; then TASK_VOICE_PYTHON=python; fi
if [ ! -x "$TASK_RENDER_PYTHON" ]; then TASK_RENDER_PYTHON=python; fi
"$TASK_VOICE_PYTHON" project/episodes/long1-open-enrollment/full/voice.py
"$TASK_RENDER_PYTHON" - <<'PY'
import json
from pathlib import Path
p=Path('project/episodes/long1-open-enrollment/full');m=json.loads((p/'manifest.json').read_text());remaining=[s['id'] for s in m['segments'] if s['status']!='complete']
if remaining:raise SystemExit('CHECKPOINT — full film is not finished. Held/remaining segments: '+', '.join(remaining)+'. See source-checks.json and checkpoint-report.json. No retry or silent gap.')
PY
"$TASK_RENDER_PYTHON" project/episodes/long1-open-enrollment/full/prepare.py
"$TASK_RENDER_PYTHON" project/episodes/long1-open-enrollment/full/render.py
"$TASK_RENDER_PYTHON" project/episodes/long1-open-enrollment/full/validate.py
