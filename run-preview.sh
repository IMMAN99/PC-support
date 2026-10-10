#!/usr/bin/env bash
# اجرای پیش‌نمایش سایت — یک دستور، بدون هیچ تنظیمی
#   bash run-preview.sh
# اگر پورت ۸۸۹۹ گرفتارِ یک اجرای قبلی بود، همان را نشان می‌دهد و اجرای دوباره نمی‌سازد.
set -u
cd "$(dirname "$0")"

PORT=8899

if command -v ss >/dev/null 2>&1 && ss -ltn 2>/dev/null | grep -q ":$PORT"; then
  echo "پیش‌نمایش همین حالا روشن است →  http://localhost:$PORT"
  exit 0
fi

echo "پیش‌نمایش را روی پورت $PORT بالا می‌آورم…  (برای توقف: Ctrl+C)"
exec python3 tools/ops/preview_server.py
