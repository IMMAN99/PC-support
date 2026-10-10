#!/usr/bin/env bash
# Install the Chromium browser for the current Python environment.
# Create/activate a virtual environment and install requirements-dev.txt first.
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

if ! python3 -c "import playwright" >/dev/null 2>&1; then
  echo "Playwright is not installed in the active Python environment." >&2
  echo "Create/activate a virtual environment, then run: python -m pip install -r requirements-dev.txt" >&2
  exit 1
fi

python3 -m playwright install chromium
python3 - <<'PY'
from playwright.sync_api import sync_playwright
with sync_playwright() as playwright:
    browser = playwright.chromium.launch()
    browser.close()
print("Chromium is ready.")
PY
