#!/usr/bin/env python3
"""Slice runtime retrieval hit results by qid-only surface metadata."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ko_evidence_bench.metrics import load_jsonl  # noqa: E402
from ko_evidence_bench.runtime_surface import (  # noqa: E402
    grouped_runtime_surface_scores,
    summarize_runtime_surface_run,
)


def pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def display_path(path: Path, *, external_label: str = "private-input") -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(ROOT))
    except ValueError:
        return external_label


def load_runtime_runs(path: Path, selected_runs: list[str]) -> dict[str, list[dict[str, Any]]]:
    result = json.loads(path.read_text(encoding="utf-8"))
    per_run = result.get("per_run")
    if not isinstance(per_run, dict):
        raise ValueError("runtime result must contain a per_run object")

    names = selected_runs or sorted(per_run)
    runs: dict[str, list[dict[str, Any]]] = {}
    for name in names:
        rows = per_run.get(name)
        if rows is None:
            raise ValueError(f"missing runtime run: {name}")
        if not isinstance(rows, list):
            raise ValueError(f"runtime run must be a list: {name}")
        runs[name] = rows
    return runs


def summary_table(
    qrels: list[dict[str, Any]],
    runs: dict[str, list[dict[str, Any]]],
    *,
    primary_metric: str,
) -> list[str]:
    lines = [
        (
            "| system | n | answerable | intent families | surfaces | {metric} | "
            "answerable_{metric} | exact@20 | avg_family_surface_spread | "
            "worst_surface_{metric} | missing hit rows | missing metadata |"
        ).format(metric=primary_metric),
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name, rows in runs.items():
        score = summarize_runtime_surface_run(qrels, rows, primary_metric=primary_metric)
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{name}`",
                    str(int(score["n"])),
                    str(int(score["answerable_n"])),
                    str(int(score["intent_family_count"])),
                    str(int(score["surface_count"])),
                    pct(score[primary_metric]),
                    pct(score[f"answerable_{primary_metric}"]),
                    pct(score["exact@20"]),
                    pct(score["avg_family_surface_spread"]),
                    pct(score[f"worst_surface_{primary_metric}"]),
                    str(int(score["missing_hit_rows"])),
                    str(int(score["missing_surface_metadata"])),
                ]
            )
            + " |"
        )
    return lines


def grouped_table(
    title: str,
    qrels: list[dict[str, Any]],
    runs: dict[str, list[dict[str, Any]]],
    *,
    key: str,
    primary_metric: str,
) -> list[str]:
    lines = [
        f"## {title}",
        "",
        (
            f"| system | slice | n | answerable | {primary_metric} | "
            f"answerable_{primary_metric} | exact@20 | missing hit rows |"
        ),
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for name, rows in runs.items():
        for item in grouped_runtime_surface_scores(
            qrels,
            rows,
            key=key,
            primary_metric=primary_metric,
        ):
            lines.append(
                "| "
                + " | ".join(
                    [
                        f"`{name}`",
                        f"`{item['value']}`",
                        str(int(item["n"])),
                        str(int(item["answerable_n"])),
                        pct(item[primary_metric]),
                        pct(item[f"answerable_{primary_metric}"]),
                        pct(item["exact@20"]),
                        str(int(item["missing_hit_rows"])),
                    ]
                )
                + " |"
            )
    return lines


def render_report(
    *,
    qrels_path: Path,
    result_path: Path,
    qrels: list[dict[str, Any]],
    runs: dict[str, list[dict[str, Any]]],
    title: str,
    label_status: str,
    primary_metric: str,
) -> str:
    lines = [
        f"# {title}",
        "",
        "This report joins qid-only intent/surface metadata with runtime",
        "retrieval hit booleans such as `clause@20` and `exact@20`. It does",
        "not include qids, raw queries, evidence ids, source names, usernames,",
        "URLs, or document text.",
        "",
        "It is a retrieval-hit surface scorecard. It does not judge answer",
        "quality or source-route correctness; pair it with route scorecards",
        "before making claims about end-to-end answerability.",
        "",
        "## Inputs",
        "",
        f"- qrels: `{display_path(qrels_path, external_label='private-surface-qrels')}`",
        f"- runtime result: `{display_path(result_path, external_label='private-runtime-result')}`",
        f"- qrel rows: {len(qrels)}",
        f"- systems: {len(runs)}",
        f"- primary metric: `{primary_metric}`",
        f"- label status: {label_status}",
        "",
        "## Runtime Surface Summary",
        "",
    ]
    lines.extend(summary_table(qrels, runs, primary_metric=primary_metric))
    lines.append("")
    lines.extend(
        grouped_table(
            "Surface Form Breakdown",
            qrels,
            runs,
            key="surface_form",
            primary_metric=primary_metric,
        )
    )
    lines.append("")
    lines.extend(
        grouped_table(
            "Intent Family Breakdown",
            qrels,
            runs,
            key="intent_family",
            primary_metric=primary_metric,
        )
    )
    lines.append("")
    lines.extend(
        grouped_table(
            "Trap-Class Breakdown",
            qrels,
            runs,
            key="trap_classes",
            primary_metric=primary_metric,
        )
    )
    lines.extend(
        [
            "",
            "## Use Notes",
            "",
            f"- `answerable_{primary_metric}` excludes rows marked as requiring human context.",
            f"- `worst_surface_{primary_metric}` is a stress signal for surface-form brittleness.",
            "- Silver metadata and hit booleans are diagnostics until human labels exist.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--qrels", type=Path, default=ROOT / "fixtures" / "surface_qrels.jsonl")
    parser.add_argument(
        "--result",
        type=Path,
        default=ROOT / "fixtures" / "runtime_results" / "surface_runtime_fixture.json",
    )
    parser.add_argument("--out", type=Path, default=ROOT / "reports" / "runtime_surface_scorecard_fixture.md")
    parser.add_argument("--run", action="append", default=[], help="Runtime run name to include. Repeatable.")
    parser.add_argument("--primary-metric", default="clause@20")
    parser.add_argument("--title", default="Runtime Surface Scorecard Fixture")
    parser.add_argument("--label-status", default="synthetic runtime hit fixture")
    args = parser.parse_args()

    qrels = load_jsonl(args.qrels)
    runs = load_runtime_runs(args.result, args.run)
    report = render_report(
        qrels_path=args.qrels,
        result_path=args.result,
        qrels=qrels,
        runs=runs,
        title=args.title,
        label_status=args.label_status,
        primary_metric=args.primary_metric,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
