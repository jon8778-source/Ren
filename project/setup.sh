#!/usr/bin/env bash
# One-time setup for the explainer pipeline. Safe to re-run.
# Installs Remotion (Node), a Python venv with the voice and QC libraries, and the Kokoro voice model.
set -euo pipefail
cd "$(dirname "$0")"
TOOLS=.tools
mkdir -p "$TOOLS"

echo "== Remotion"
(cd remotion && npm install --no-audit --no-fund >/dev/null)

echo "== Python venv ($TOOLS/venv)"
[ -x "$TOOLS/venv/bin/python" ] || python3 -m venv "$TOOLS/venv"
"$TOOLS/venv/bin/pip" install -q kokoro-onnx soundfile librosa pillow scipy numpy

echo "== Kokoro voice model"
if [ ! -f "$TOOLS/kokoro-q8.onnx" ]; then
  tmp=$(mktemp -d)
  (cd "$tmp" && npm pack -q kokoro-q8-shards@1.0.0 kokoro-js@1.2.1 >/dev/null \
     && mkdir q8 kjs && tar xzf kokoro-q8-shards-1.0.0.tgz -C q8 && tar xzf kokoro-js-1.2.1.tgz -C kjs)
  cat "$tmp"/q8/package/kokoro-q8.part{0..5}.bin > "$TOOLS/kokoro-q8.onnx"
  rm -rf "$TOOLS/voices" && cp -r "$tmp/kjs/package/voices" "$TOOLS/voices"
  rm -rf "$tmp"
fi
echo "fbae9257e1e05ffc727e951ef9b9c98418e6d79f1c9b6b13bd59f5c9028a1478  $TOOLS/kokoro-q8.onnx" | sha256sum -c -

echo "== Done. Voice: --model $TOOLS/kokoro-q8.onnx --voices $TOOLS/voices; Python: $TOOLS/venv/bin/python"
