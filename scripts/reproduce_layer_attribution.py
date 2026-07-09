#!/usr/bin/env python3
"""Attribute retrieval failures to diagnostic layers."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ko_evidence_bench.layer_attribution import (  # noqa: E402
    attribute_run,
    grouped_failure_layers,
    layer_breakdown,
    summarize_system,
    trap_failure_layers,
)
from ko_evidence_bench.metrics import load_jsonl  # noqa: E402


def pct(value: float) -> str:
    return f"{100 * value:.1f}%"


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


def summary_table(all_rows: list[dict[str, Any]], runs: dict[str, list[dict[str, Any]]]) -> list[str]:
    lines = [
        "| system | n | success rate | failure rows | dominant failure layer |",
        "|---|---:|---:|---:|---|",
    ]
    for system in sorted(runs):
        rows = [row for row in all_rows if row["system"] == system]
        summary = summarize_system(rows)
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{summary['system']}`",
                    str(int(summary["n"])),
                    pct(float(summary["success_rate"])),
                    str(int(summary["failure_rows"])),
                    f"`{summary['dominant_failure_layer']}`",
                ]
            )
            + " |"
        )
    return lines


def layer_table(all_rows: list[dict[str, Any]]) -> list[str]:
    lines = [
        "## Failure Mass By Layer",
        "",
        "| system | layer | rows | share of run | share of failures |",
        "|---|---|---:|---:|---:|",
    ]
    for row in layer_breakdown(all_rows):
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{row['system']}`",
                    f"`{row['failure_layer']}`",
                    str(int(row["rows"])),
                    pct(float(row["share_of_run"])),
                    pct(float(row["share_of_failures"])),
                ]
            )
            + " |"
        )
    return lines


def grouped_table(title: str, rows: list[dict[str, Any]]) -> list[str]:
    lines = [
        f"## {title}",
        "",
        "| system | slice | n | success rate | failure rows | dominant failure layer |",
        "|---|---|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{row['system']}`",
                    f"`{row['value']}`",
                    str(int(row["n"])),
                    pct(float(row["success_rate"])),
                    str(int(row["failure_rows"])),
                    f"`{row['dominant_failure_layer']}`",
                ]
            )
            + " |"
        )
    return lines


def render_report(
    *,
    qrels_path: Path,
    run_dir: Path,
    qrels: list[dict[str, Any]],
    runs: dict[str, list[dict[str, Any]]],
    k: int,
    title: str,
    label_status: str,
) -> str:
    all_rows: list[dict[str, Any]] = []
    for system, run_rows in runs.items():
        all_rows.extend(attribute_run(qrels, run_rows, system=system, k=k))

    lines = [
        f"# {title}",
        "",
        "Status: **diagnostic layer attribution only; human-gold attribution blocked**.",
        "",
        "This report attributes each failed synthetic retrieval row to one primary",
        "diagnostic layer. It is designed to make failure mass inspectable without",
        "publishing qids, raw queries, source names, URLs, conversation snippets,",
        "or document text.",
        "",
        "The attribution is ordered and diagnostic: abstention failures are counted",
        "before route failures, route failures before evidence-hit failures, and",
        "surface/register annotations are used only after the route is correct.",
        "",
        "## Inputs",
        "",
        f"- qrels: `{display_path(qrels_path)}`",
        f"- runs: `{display_path(run_dir)}`",
        f"- qrel rows: {len(qrels)}",
        f"- systems: {len(runs)}",
        f"- k: {k}",
        f"- label status: {label_status}",
        "",
        "## Layer Attribution Summary",
        "",
    ]
    lines.extend(summary_table(all_rows, runs))
    lines.append("")
    lines.extend(layer_table(all_rows))
    lines.append("")
    lines.extend(grouped_table("Layer By Intent Family", grouped_failure_layers(all_rows, "intent_family")))
    lines.append("")
    lines.extend(grouped_table("Layer By Surface Form", grouped_failure_layers(all_rows, "surface_form")))
    lines.append("")
    lines.extend(grouped_table("Layer By Trap Class", trap_failure_layers(all_rows)))
    lines.extend(
        [
            "",
            "## Use Notes",
            "",
            "- This is the Table-2-style decomposition hook for the measurement study.",
            "- The public fixture proves the attribution path, not final system behavior.",
            "- Private runs can reuse the same qid-only path once route labels and",
            "  intent/surface metadata are human-audited.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--qrels", type=Path, default=ROOT / "fixtures" / "surface_qrels.jsonl")
    parser.add_argument("--run-dir", type=Path, default=ROOT / "fixtures" / "surface_runs")
    parser.add_argument("--out", type=Path, default=ROOT / "reports" / "layer_attribution_fixture.md")
    parser.add_argument("--k", type=int, default=3)
    parser.add_argument("--title", default="Layer Attribution Fixture")
    parser.add_argument("--label-status", default="synthetic fixture metadata")
    args = parser.parse_args()

    qrels = load_jsonl(args.qrels)
    runs = load_runs(args.run_dir)
    report = render_report(
        qrels_path=args.qrels,
        run_dir=args.run_dir,
        qrels=qrels,
        runs=runs,
        k=args.k,
        title=args.title,
        label_status=args.label_status,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
