#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if command -v conda >/dev/null 2>&1; then
  echo "Conda detected. You can create an environment with:"
  echo "  conda create -n jarvis python=3.12 -y && conda activate jarvis"
fi

python3 -m pip install -r "${ROOT_DIR}/backend/requirements.txt"

cd "${ROOT_DIR}/frontend"
npm install

echo "Bootstrap complete."

