#!/usr/bin/env python3
"""Score qid-only route runs by intent/surface metadata."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ko_evidence_bench.metrics import load_jsonl  # noqa: E402
from ko_evidence_bench.route_surface import (  # noqa: E402
    grouped_scores,
    route_surface_confusions,
    summarize_route_surface_run,
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


def summary_table(qrels: list[dict[str, Any]], runs: dict[str, list[dict[str, Any]]]) -> list[str]:
    lines = [
        "| system | n | intents | surfaces | route_acc | abst_p | abst_r | avg_intent_route_spread | worst_surface_route_acc | missing predictions | missing metadata |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name, rows in runs.items():
        score = summarize_route_surface_run(qrels, rows)
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{name}`",
                    str(int(score["n"])),
                    str(int(score["intent_count"])),
                    str(int(score["surface_count"])),
                    pct(score["route_accuracy"]),
                    pct(score["abstention_precision"]),
                    pct(score["abstention_recall"]),
                    pct(score["avg_intent_route_spread"]),
                    pct(score["worst_surface_route_accuracy"]),
                    str(int(score["missing_predictions"])),
                    str(int(score["missing_surface_metadata"])),
                ]
            )
            + " |"
        )
    return lines


def grouped_table(title: str, qrels: list[dict[str, Any]], runs: dict[str, list[dict[str, Any]]], *, key: str) -> list[str]:
    lines = [
        f"## {title}",
        "",
        "| system | slice | n | route_acc | abst_p | abst_r | missing predictions |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for name, rows in runs.items():
        for item in grouped_scores(qrels, rows, key=key):
            lines.append(
                "| "
                + " | ".join(
                    [
                        f"`{name}`",
                        f"`{item['value']}`",
                        str(int(item["n"])),
                        pct(item["route_accuracy"]),
                        pct(item["abstention_precision"]),
                        pct(item["abstention_recall"]),
                        str(int(item["missing_predictions"])),
                    ]
                )
                + " |"
            )
    return lines


def confusion_table(qrels: list[dict[str, Any]], runs: dict[str, list[dict[str, Any]]], *, limit: int = 12) -> list[str]:
    lines = [
        "## Largest Surface Route Confusions",
        "",
        "| system | surface form | gold route | predicted route | count | share of run |",
        "|---|---|---|---|---:|---:|",
    ]
    n = len(qrels)
    for name, rows in runs.items():
        for (surface, gold, pred), count in route_surface_confusions(qrels, rows).most_common(limit):
            lines.append(
                f"| `{name}` | `{surface}` | `{gold}` | `{pred}` | {count} | {pct(count / n if n else 0.0)} |"
            )
    return lines


def render_report(
    *,
    qrels_path: Path,
    run_dir: Path,
    qrels: list[dict[str, Any]],
    runs: dict[str, list[dict[str, Any]]],
    title: str,
    label_status: str,
) -> str:
    lines = [
        f"# {title}",
        "",
        "This report scores route and abstention behavior by qid-only intent,",
        "surface, and trap metadata. It does not include qids, raw queries,",
        "conversation snippets, source names, usernames, URLs, or document text.",
        "",
        "It is route-only: it does not evaluate whether ranked evidence passages",
        "contain sufficient answer evidence.",
        "",
        "## Inputs",
        "",
        f"- qrels: `{display_path(qrels_path)}`",
        f"- runs: `{display_path(run_dir)}`",
        f"- qrel rows: {len(qrels)}",
        f"- systems: {len(runs)}",
        f"- label status: {label_status}",
        "",
        "## Route Surface Summary",
        "",
    ]
    lines.extend(summary_table(qrels, runs))
    lines.append("")
    lines.extend(grouped_table("Surface Form Breakdown", qrels, runs, key="surface_form"))
    lines.append("")
    lines.extend(grouped_table("Intent Family Breakdown", qrels, runs, key="intent_family"))
    lines.append("")
    lines.extend(grouped_table("Trap-Class Breakdown", qrels, runs, key="trap_classes"))
    lines.append("")
    lines.extend(confusion_table(qrels, runs))
    lines.extend(
        [
            "",
            "## Use Notes",
            "",
            "- Use this report to find route and abstention regressions across surface",
            "  conditions before running heavier evidence-ranking experiments.",
            "- Treat silver-label results as diagnostics until the route labels and",
            "  intent/surface metadata are human-audited.",
            "- Pair this route-only report with the full surface robustness scorecard",
            "  once ranked evidence runs are available.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--qrels", type=Path, default=ROOT / "fixtures" / "surface_qrels.jsonl")
    parser.add_argument("--run-dir", type=Path, default=ROOT / "fixtures" / "surface_runs")
    parser.add_argument("--out", type=Path, default=ROOT / "reports" / "route_surface_scorecard_fixture.md")
    parser.add_argument("--title", default="Route Surface Scorecard Fixture")
    parser.add_argument("--label-status", default="synthetic fixture metadata")
    args = parser.parse_args()

    qrels = load_jsonl(args.qrels)
    runs = load_runs(args.run_dir)
    report = render_report(
        qrels_path=args.qrels,
        run_dir=args.run_dir,
        qrels=qrels,
        runs=runs,
        title=args.title,
        label_status=args.label_status,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
