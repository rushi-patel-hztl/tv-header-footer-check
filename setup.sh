#!/usr/bin/env bash
# Installs what the cloud run needs: Python packages + headless Chromium (with OS libraries).
set -euo pipefail
cd "$(dirname "$0")"
python3 -m pip install --quiet -r requirements.txt
python3 -m playwright install --with-deps chromium
echo "Setup complete."
