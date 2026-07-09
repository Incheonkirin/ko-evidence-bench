#!/usr/bin/env python3
"""Update or check the README's generated current-signal block."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ko_evidence_bench.study_readiness import load_study_readiness, render_readme_signals  # noqa: E402


START = "<!-- BEGIN: current-verified-signals -->"
END = "<!-- END: current-verified-signals -->"


def replace_block(text: str, block: str) -> str:
    start = text.find(START)
    end = text.find(END)
    if start == -1 or end == -1 or end < start:
        raise ValueError("README is missing current-verified-signals markers")
    end += len(END)
    return text[:start] + block + text[end:]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--readme", type=Path, default=ROOT / "README.md")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    readme = args.readme.read_text(encoding="utf-8")
    block = render_readme_signals(load_study_readiness(ROOT))
    updated = replace_block(readme, block)
    if args.check:
        if updated != readme:
            print("README current verified signals are stale; run scripts/sync_readme_signals.py")
            return 1
        print("README current verified signals are current")
        return 0
    args.readme.write_text(updated, encoding="utf-8")
    print("README current verified signals updated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
