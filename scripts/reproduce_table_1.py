#!/usr/bin/env python3
"""Reproduce the synthetic fixture scorecard."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ko_evidence_bench.metrics import format_scorecard, load_jsonl, score_runs


def main() -> None:
    qrels = load_jsonl(ROOT / "fixtures" / "qrels.jsonl")
    runs = {
        "always_policy": load_jsonl(ROOT / "fixtures" / "system_runs" / "always_policy.jsonl"),
        "source_routed_demo": load_jsonl(
            ROOT / "fixtures" / "system_runs" / "source_routed_demo.jsonl"
        ),
    }
    scores = score_runs(qrels, runs, k=3)
    print(format_scorecard(scores, k=3))


if __name__ == "__main__":
    main()
