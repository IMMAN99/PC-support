#!/usr/bin/env bash
# آماده‌سازی مرورگر برای آزمون‌های خودکار.
# محیط سندباکس بین فراخوانی‌ها ریست می‌شود (پکیج pip و کتابخانه‌های سیستمی)،
# پس هر فراخوانیِ مرورگری باید اول این را اجرا کند:
#     bash tools/ops/pw_setup.sh && python3 tools/audit.py
set -e
cd /home/user
if ! python3 -c "import playwright" 2>/dev/null; then
  pip install playwright -q
fi
python3 -m playwright install chromium >/dev/null 2>&1 || true
# کتابخانه‌های سیستمی کروم (libnspr4 و…)
if ! ldconfig -p 2>/dev/null | grep -q libnspr4; then
  sudo python3 -m playwright install-deps chromium >/dev/null 2>&1
  rm -f /home/user/.sudo_as_admin_successful
fi
python3 - <<'PY'
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(); b.close()
print("✓ مرورگر آماده است")
PY
