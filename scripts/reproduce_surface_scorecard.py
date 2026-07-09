#!/usr/bin/env python3
"""Reproduce the surface-form robustness scorecard on synthetic fixtures."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ko_evidence_bench.metrics import load_jsonl  # noqa: E402
from ko_evidence_bench.surface import (  # noqa: E402
    intent_breakdown,
    score_surface_run,
    surface_breakdown,
    surface_inventory,
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


def summary_table(
    qrels: list[dict[str, Any]],
    runs: dict[str, list[dict[str, Any]]],
    *,
    k: int,
) -> list[str]:
    lines = [
        (
            "| system | n | intents | surfaces | task_success@{k} | route_acc | "
            "answerable_evidence@{k} | avg_intent_spread | robust_intents | "
            "worst_surface@{k} | missing metadata |"
        ).format(k=k),
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name, rows in runs.items():
        score = score_surface_run(qrels, rows, k=k)
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{name}`",
                    str(int(score["n"])),
                    str(int(score["intent_count"])),
                    str(int(score["surface_count"])),
                    pct(score[f"task_success@{k}"]),
                    pct(score["route_accuracy"]),
                    pct(score[f"answerable_evidence@{k}"]),
                    pct(score["avg_intent_surface_spread"]),
                    pct(score["robust_intent_share"]),
                    pct(score[f"worst_surface_task_success@{k}"]),
                    str(int(score["missing_surface_metadata"])),
                ]
            )
            + " |"
        )
    return lines


def surface_table(
    qrels: list[dict[str, Any]],
    runs: dict[str, list[dict[str, Any]]],
    *,
    k: int,
) -> list[str]:
    lines = [
        f"| system | surface form | n | task_success@{k} | route_acc | answerable_evidence@{k} |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for name, rows in runs.items():
        for item in surface_breakdown(qrels, rows, k=k):
            lines.append(
                "| "
                + " | ".join(
                    [
                        f"`{name}`",
                        f"`{item['surface_form']}`",
                        str(int(item["n"])),
                        pct(item[f"task_success@{k}"]),
                        pct(item["route_accuracy"]),
                        pct(item[f"answerable_evidence@{k}"]),
                    ]
                )
                + " |"
            )
    return lines


def intent_table(
    qrels: list[dict[str, Any]],
    runs: dict[str, list[dict[str, Any]]],
    *,
    k: int,
) -> list[str]:
    lines = [
        (
            f"| system | intent id | variants | surfaces | task_success@{k} | "
            "min surface | max surface | spread |"
        ),
        "|---|---|---:|---|---:|---:|---:|---:|",
    ]
    for name, rows in runs.items():
        for item in intent_breakdown(qrels, rows, k=k):
            lines.append(
                "| "
                + " | ".join(
                    [
                        f"`{name}`",
                        f"`{item['intent_id']}`",
                        str(int(item["variant_count"])),
                        f"`{item['surfaces']}`",
                        pct(item[f"task_success@{k}"]),
                        pct(item["min_surface_success"]),
                        pct(item["max_surface_success"]),
                        pct(item["surface_spread"]),
                    ]
                )
                + " |"
            )
    return lines


def inventory_table(qrels: list[dict[str, Any]], key: str) -> list[str]:
    counts = surface_inventory(qrels)[key]
    lines = [f"| {key} | rows |", "|---|---:|"]
    for value, count in counts.most_common():
        lines.append(f"| `{value}` | {count} |")
    return lines


def render_report(
    qrels: list[dict[str, Any]],
    runs: dict[str, list[dict[str, Any]]],
    *,
    qrels_path: Path,
    run_dir: Path,
    k: int,
    title: str,
    label_status: str,
) -> str:
    lines = [
        f"# {title}",
        "",
        "This report checks whether a system is robust to different surface forms",
        "of the same intent. It uses only stable ids, source-route labels,",
        "surface metadata, and ranked evidence ids. It does not include raw",
        "queries, conversation snippets, source names, or platform identifiers.",
        "",
        "A row is counted as `task_success@k` when the route decision is correct",
        "and either sufficient evidence appears in top-k or the system correctly",
        "abstains for rows that require human context.",
        "",
        "## Inputs",
        "",
        f"- qrels: `{display_path(qrels_path)}`",
        f"- runs: `{display_path(run_dir)}`",
        f"- label status: {label_status}",
        f"- k: {k}",
        "",
        "## Surface Robustness Summary",
        "",
    ]
    lines.extend(summary_table(qrels, runs, k=k))
    lines.extend(["", "## Surface Condition Breakdown", ""])
    lines.extend(surface_table(qrels, runs, k=k))
    lines.extend(["", "## Intent Robustness Breakdown", ""])
    lines.extend(intent_table(qrels, runs, k=k))
    lines.extend(["", "## Fixture Inventory: Intent Id", ""])
    lines.extend(inventory_table(qrels, "intent_id"))
    lines.extend(["", "## Fixture Inventory: Surface Form", ""])
    lines.extend(inventory_table(qrels, "surface_form"))
    lines.extend(
        [
            "",
            "## Use Notes",
            "",
            "- Lower `avg_intent_spread` means less performance variation across",
            "  surface forms of the same intent.",
            "- `worst_surface@k` is the first place to look for messenger-style,",
            "  abbreviated, or colloquial regressions.",
            "- Private qrels can reuse this path by adding `intent_id` and",
            "  `surface_form` metadata while keeping raw text outside the public repo.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--qrels", type=Path, default=ROOT / "fixtures" / "surface_qrels.jsonl")
    parser.add_argument("--run-dir", type=Path, default=ROOT / "fixtures" / "surface_runs")
    parser.add_argument("--out", type=Path, default=ROOT / "reports" / "surface_scorecard_fixture.md")
    parser.add_argument("--k", type=int, default=3)
    parser.add_argument("--title", default="Surface Robustness Scorecard Fixture")
    parser.add_argument("--label-status", default="synthetic surface fixture labels")
    args = parser.parse_args()

    qrels = load_jsonl(args.qrels)
    runs = load_runs(args.run_dir)
    report = render_report(
        qrels,
        runs,
        qrels_path=args.qrels,
        run_dir=args.run_dir,
        k=args.k,
        title=args.title,
        label_status=args.label_status,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
