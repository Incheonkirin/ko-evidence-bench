#!/usr/bin/env python3
"""Build or check the aggregate-only measurement-study draft."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ko_evidence_bench.study_report import load_study_report_signals, render_measurement_study  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=ROOT / "reports" / "measurement_study_draft.md")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    report = render_measurement_study(load_study_report_signals(ROOT))
    if args.check:
        current = args.out.read_text(encoding="utf-8") if args.out.exists() else ""
        if current != report:
            print("measurement study draft is stale; run scripts/build_measurement_study.py")
            return 1
        print("measurement study draft is current")
        return 0

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(report, encoding="utf-8")
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
