#!/usr/bin/env bash
# Installs Rhubarb Lip Sync 1.13.0 (phoneme-based mouth shapes) into .tools/rhubarb for the rig lab.
set -euo pipefail
cd "$(dirname "$0")/.."
[ -x .tools/rhubarb/rhubarb ] && { echo "rhubarb already installed"; exit 0; }
tmp=$(mktemp -d)
curl -sSL -o "$tmp/r.zip" https://github.com/DanielSWolf/rhubarb-lip-sync/releases/download/v1.13.0/Rhubarb-Lip-Sync-1.13.0-Linux.zip
python3 -c "import zipfile,sys; zipfile.ZipFile(sys.argv[1]).extractall(sys.argv[2])" "$tmp/r.zip" "$tmp"
rm -rf .tools/rhubarb && mv "$tmp"/Rhubarb-Lip-Sync-1.13.0-Linux .tools/rhubarb && chmod +x .tools/rhubarb/rhubarb
rm -rf "$tmp"
.tools/rhubarb/rhubarb --version
