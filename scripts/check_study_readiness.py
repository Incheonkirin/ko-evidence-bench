#!/usr/bin/env python3
"""Generate the measurement-study readiness report."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ko_evidence_bench.study_readiness import load_study_readiness, render_study_readiness  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--out", type=Path, default=ROOT / "reports" / "study_readiness.md")
    parser.add_argument(
        "--require-headline-ready",
        action="store_true",
        help="fail if the current reports do not prove headline readiness",
    )
    args = parser.parse_args()

    readiness = load_study_readiness(args.root)
    report = render_study_readiness(readiness)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(report, encoding="utf-8")
    print(report)
    if args.require_headline_ready and not readiness.headline_ready:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
