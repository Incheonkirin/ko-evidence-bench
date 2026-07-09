#!/usr/bin/env python3
"""Build or check the flagship alignment report."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ko_evidence_bench.alignment import load_alignment_items, render_alignment_report  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=ROOT / "reports" / "flagship_alignment.md")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    report = render_alignment_report(load_alignment_items(ROOT))
    if args.check:
        current = args.out.read_text(encoding="utf-8") if args.out.exists() else ""
        if current != report:
            print("flagship alignment report is stale; run scripts/build_alignment_report.py")
            return 1
        print("flagship alignment report is current")
        return 0

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(report, encoding="utf-8")
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
