#!/usr/bin/env python3
"""Collect literal Tailwind class tokens from the editable HTML source."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "پشتیبان_رایانه.html"
OUTPUT = Path(__file__).resolve().parent / "tokens.txt"


def main() -> None:
    html = SOURCE.read_text(encoding="utf-8")
    # Avoid treating CSS declarations and commented examples as Tailwind classes.
    html = re.sub(r"<style\b[^>]*>.*?</style\s*>", "", html, flags=re.IGNORECASE | re.DOTALL)
    html = re.sub(r"<!--.*?-->", "", html, flags=re.DOTALL)
    tokens: set[str] = set()

    for match in re.finditer(r'class="([^"]*)"', html):
        tokens.update(match.group(1).split())
    for match in re.finditer(
        r"classList\.(?:add|remove|toggle|contains)\(\s*['\"]([^'\"]+)['\"]",
        html,
    ):
        tokens.update(match.group(1).split())
    for match in re.finditer(r"\.className\s*=\s*['\"`]([^'\"`]+)['\"`]", html):
        tokens.update(match.group(1).split())
    for match in re.finditer(r'const\s+\w*[Cc]lass\s*=\s*"([^"]*)"', html):
        tokens.update(match.group(1).split())

    ordered = sorted(token for token in tokens if token)
    OUTPUT.write_text("\n".join(ordered) + "\n", encoding="utf-8")
    print(f"Collected {len(ordered)} Tailwind tokens from {SOURCE.name} -> {OUTPUT.name}")


if __name__ == "__main__":
    main()
