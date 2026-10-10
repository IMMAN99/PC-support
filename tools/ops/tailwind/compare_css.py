#!/usr/bin/env python3
"""Summarize top-level rule changes between the frozen and generated CSS."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CURRENT = ROOT / "assets" / "tailwind-frozen.css"
GENERATED = Path(__file__).resolve().parent / "out.css"


def rules(css: str) -> set[str]:
    found: set[str] = set()
    depth = 0
    start = 0
    for index, char in enumerate(css):
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                block = css[start : index + 1].strip()
                if block:
                    found.add(block)
                start = index + 1
    tail = css[start:].strip()
    if tail:
        found.add(tail)
    return found


def selector(block: str) -> str:
    opening = block.find("{")
    return block[:opening].strip() if opening >= 0 else block[:120]


def main() -> None:
    old = rules(CURRENT.read_text(encoding="utf-8"))
    new = rules(GENERATED.read_text(encoding="utf-8"))
    removed, added = old - new, new - old
    print(f"Current rules: {len(old)}; generated rules: {len(new)}")
    print(f"Removed/changed blocks: {len(removed)}; added/changed blocks: {len(added)}")
    for label, blocks in (("Current only", removed), ("Generated only", added)):
        if not blocks:
            continue
        print(f"\n{label}:")
        for block in sorted(blocks):
            print(f"  {selector(block)[:240]}")


if __name__ == "__main__":
    main()
