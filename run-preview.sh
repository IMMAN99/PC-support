#!/usr/bin/env bash
# Local preview. Build the offline page first with:
#   python3 tools/ops/assemble_offline.py
# Use PREVIEW_HOST=0.0.0.0 only when a sandbox proxy needs external access.
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PORT="${PORT:-8899}"
PREVIEW_HOST="${PREVIEW_HOST:-127.0.0.1}"

if ! [[ "$PORT" =~ ^[0-9]{1,5}$ ]] || (( 10#$PORT < 1 || 10#$PORT > 65535 )); then
  echo "PORT must be an integer between 1 and 65535" >&2
  exit 2
fi

export PORT PREVIEW_HOST
if [[ "$PREVIEW_HOST" == "127.0.0.1" ]]; then
  echo "Serving the offline preview at http://127.0.0.1:${PORT}/ (Ctrl+C to stop)"
else
  echo "Serving the offline preview on ${PREVIEW_HOST}:${PORT} (Ctrl+C to stop)"
fi
exec python3 "$ROOT/tools/ops/preview_server.py"
