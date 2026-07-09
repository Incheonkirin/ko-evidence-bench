#!/usr/bin/env python3
"""Summarize private retrieval hit exports without exposing qids or text."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ko_evidence_bench.metrics import bootstrap_hit_ci, paired_delta_ci, summarize_hit_rows


DEFAULT_METRICS = ["exact@1", "exact@10", "exact@20", "clause@1", "clause@10", "clause@20"]


def pct(value: float) -> str:
    return f"{100 * value:.1f}%"


def load_result(path: Path) -> dict:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict) or "per_run" not in obj:
        raise ValueError("expected a result JSON with a per_run object")
    return obj


def render_markdown(
    result: dict,
    *,
    metrics: list[str],
    runs: list[str],
    baseline: str | None,
    samples: int,
) -> str:
    per_run = result["per_run"]
    for run in runs:
        if run not in per_run:
            raise ValueError(f"run not found in result: {run}")
    if baseline and baseline not in per_run:
        raise ValueError(f"baseline run not found in result: {baseline}")

    lines = [
        "# Private Aggregate Hit Scorecard",
        "",
        "This report is generated from a private retrieval result export. It contains",
        "only aggregate hit rates and bootstrap confidence intervals; it does not",
        "include raw queries, ranked documents, or qids.",
        "",
        f"- source result n: {result.get('n') or len(per_run[runs[0]])}",
        f"- bootstrap samples: {samples}",
        "",
        "## Hit Rates",
        "",
        "| run | metric | n | hit rate | 95% CI |",
        "|---|---|---:|---:|---:|",
    ]

    for run in runs:
        rows = per_run[run]
        for metric in metrics:
            summary = summarize_hit_rows(rows, metric)
            lo, hi = bootstrap_hit_ci(rows, metric, samples=samples)
            lines.append(
                f"| {run} | `{metric}` | {int(summary['n'])} | {pct(summary['rate'])} | {pct(lo)} - {pct(hi)} |"
            )

    if baseline:
        lines += [
            "",
            f"## Paired Delta vs `{baseline}`",
            "",
            "| run | metric | delta | 95% CI |",
            "|---|---|---:|---:|",
        ]
        base_rows = per_run[baseline]
        for run in runs:
            if run == baseline:
                continue
            rows = per_run[run]
            for metric in metrics:
                delta, lo, hi = paired_delta_ci(base_rows, rows, metric, samples=samples)
                lines.append(f"| {run} | `{metric}` | {pct(delta)} | {pct(lo)} - {pct(hi)} |")

    lines += [
        "",
        "## Use Notes",
        "",
        "- Treat these as private-lab diagnostics until the evaluation core is expanded and audited.",
        "- A CI spanning zero on paired deltas means the observed gain is not yet a stable headline claim.",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--run", action="append", dest="runs", help="Run to include. Repeatable.")
    parser.add_argument("--metric", action="append", dest="metrics", help="Metric to include. Repeatable.")
    parser.add_argument("--baseline")
    parser.add_argument("--samples", type=int, default=2000)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    result = load_result(args.result)
    runs = args.runs or list(result["per_run"].keys())
    metrics = args.metrics or DEFAULT_METRICS
    report = render_markdown(
        result,
        metrics=metrics,
        runs=runs,
        baseline=args.baseline,
        samples=args.samples,
    )
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(report, encoding="utf-8")
    else:
        print(report, end="")


if __name__ == "__main__":
    main()
