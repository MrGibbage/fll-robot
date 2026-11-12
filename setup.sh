#!/usr/bin/env bash
# One-time setup: Python venv + the official LDraw parts library (downloaded, not committed).
set -euo pipefail
cd "$(dirname "$0")"
python3 -m venv .venv
.venv/bin/pip install -q -r requirements.txt
mkdir -p lib
if [ ! -d lib/ldraw ]; then
  echo "Downloading the LDraw parts library (~150 MB, CC BY 4.0, https://library.ldraw.org)…"
  curl -fSL -o lib/complete.zip https://library.ldraw.org/library/updates/complete.zip
  (cd lib && unzip -q complete.zip && rm complete.zip)
fi
echo
echo "Done. Optional but recommended: your own Stud.io parts library (has the SPIKE hub, battery and some wheels"
echo "that the official library lacks). Zip the 'ldraw' folder inside your Stud.io install and unzip it to lib/studio-ldraw"
echo "(so lib/studio-ldraw/parts, lib/studio-ldraw/UnOfficial/... exist). Then: .venv/bin/python tools/catalog.py"
