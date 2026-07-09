#!/usr/bin/env python3
"""Reproduce the qid-only route scorecard on synthetic fixtures."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ko_evidence_bench.metrics import load_jsonl  # noqa: E402
from ko_evidence_bench.route_score import (  # noqa: E402
    bootstrap_route_ci,
    paired_route_delta_ci,
    score_route_run,
)


def pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def display_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(ROOT))
    except ValueError:
        return resolved.name


def load_runs(run_dir: Path) -> dict[str, list[dict[str, Any]]]:
    runs: dict[str, list[dict[str, Any]]] = {}
    for path in sorted(run_dir.glob("*.jsonl")):
        runs[path.stem] = load_jsonl(path)
    if not runs:
        raise ValueError(f"no .jsonl runs found under {run_dir}")
    return runs


def route_table(
    labels: list[dict[str, Any]],
    runs: dict[str, list[dict[str, Any]]],
    *,
    samples: int,
) -> list[str]:
    lines = [
        "| system | n | missing | route_acc | 95% CI | abst_p | abst_r |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for name, rows in runs.items():
        score = score_route_run(labels, rows)
        lo, hi = bootstrap_route_ci(labels, rows, metric="route_accuracy", samples=samples)
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{name}`",
                    str(int(score["n"])),
                    str(int(score["missing_predictions"])),
                    pct(score["route_accuracy"]),
                    f"{pct(lo)} - {pct(hi)}",
                    pct(score["abstention_precision"]),
                    pct(score["abstention_recall"]),
                ]
            )
            + " |"
        )
    return lines


def delta_table(
    labels: list[dict[str, Any]],
    runs: dict[str, list[dict[str, Any]]],
    *,
    baseline: str,
    samples: int,
) -> list[str]:
    lines = [
        "| candidate | metric | paired delta | 95% CI |",
        "|---|---|---:|---:|",
    ]
    baseline_rows = runs[baseline]
    for name, rows in runs.items():
        if name == baseline:
            continue
        delta, lo, hi = paired_route_delta_ci(
            labels,
            baseline_rows,
            rows,
            metric="route_accuracy",
            samples=samples,
        )
        lines.append(f"| `{name}` | `route_accuracy` | {pct(delta)} | {pct(lo)} - {pct(hi)} |")
    if len(lines) == 2:
        lines.append("| _(none)_ | `route_accuracy` | 0.0% | 0.0% - 0.0% |")
    return lines


def render_report(
    labels: list[dict[str, Any]],
    runs: dict[str, list[dict[str, Any]]],
    *,
    labels_path: Path,
    run_dir: Path,
    baseline: str,
    samples: int,
    title: str,
    label_status: str,
) -> str:
    lines = [
        f"# {title}",
        "",
        f"This report validates the qid-only source-route scoring path on {label_status}.",
        "No raw private query, conversation, community, or policy text is needed to",
        "score route accuracy and abstention behavior.",
        "",
        "## Inputs",
        "",
        f"- labels: `{display_path(labels_path)}`",
        f"- runs: `{display_path(run_dir)}`",
        f"- bootstrap samples: {samples}",
        "",
        "## Route Metrics",
        "",
    ]
    lines.extend(route_table(labels, runs, samples=samples))
    lines.extend(
        [
            "",
            f"## Paired Delta vs `{baseline}`",
            "",
        ]
    )
    lines.extend(delta_table(labels, runs, baseline=baseline, samples=samples))
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            f"These scores use {label_status}. Treat them as diagnostics unless the",
            "label file is human-adjudicated and validated. The scorecard path is the",
            "same path intended for promoted private human labels.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--labels", type=Path, default=ROOT / "fixtures" / "route_labels.jsonl")
    parser.add_argument("--run-dir", type=Path, default=ROOT / "fixtures" / "route_runs")
    parser.add_argument("--baseline", default="always_policy")
    parser.add_argument("--out", type=Path, default=ROOT / "reports" / "route_scorecard_fixture.md")
    parser.add_argument("--samples", type=int, default=1000)
    parser.add_argument("--title", default="Route Scorecard Fixture")
    parser.add_argument("--label-status", default="synthetic fixture labels")
    args = parser.parse_args()

    labels = load_jsonl(args.labels)
    runs = load_runs(args.run_dir)
    if args.baseline not in runs:
        raise ValueError(f"baseline {args.baseline!r} not found in {args.run_dir}")

    report = render_report(
        labels,
        runs,
        labels_path=args.labels,
        run_dir=args.run_dir,
        baseline=args.baseline,
        samples=args.samples,
        title=args.title,
        label_status=args.label_status,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
