#!/usr/bin/env bash
# Regenerate out.css only. Review it before replacing assets/tailwind-frozen.css.
set -euo pipefail

HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"

if [[ ! -x "$HERE/node_modules/.bin/tailwindcss" ]]; then
  echo "Tailwind is not installed. From this directory, run: npm ci" >&2
  exit 1
fi

python3 "$HERE/collect_tokens.py"
npm run build:css
printf '\nGenerated %s/out.css. Review the diff before copying it into assets/.\n' "$HERE"
