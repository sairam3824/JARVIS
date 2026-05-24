#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_UVICORN="${ROOT_DIR}/backend/.venv/bin/uvicorn"

if [[ ! -x "${BACKEND_UVICORN}" ]]; then
  BACKEND_UVICORN="uvicorn"
fi

echo "Starting backend on :8000"
(cd "${ROOT_DIR}/backend" && PYTHONPATH="${ROOT_DIR}" "${BACKEND_UVICORN}" app.main:app --reload --port 8000) &
BACKEND_PID=$!

echo "Starting frontend on :5173"
(cd "${ROOT_DIR}/frontend" && npm run dev) &
FRONTEND_PID=$!

cleanup() {
  kill "${BACKEND_PID}" "${FRONTEND_PID}" >/dev/null 2>&1 || true
}

trap cleanup EXIT INT TERM
wait
