#!/usr/bin/env python3
"""Summarize private route-audit labels without exposing raw rows."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ko_evidence_bench.agreement import cohens_kappa, get_path, observed_agreement, paired_labels  # noqa: E402


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def pct(value: float) -> str:
    return f"{100 * value:.1f}%"


def count_values(rows: list[dict[str, Any]], field: str) -> Counter[str]:
    counts: Counter[str] = Counter()
    for row in rows:
        value = get_path(row, field)
        if value not in (None, ""):
            counts[str(value)] += 1
    return counts


def disagreement_counts(labels_a: list[str], labels_b: list[str]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for a, b in zip(labels_a, labels_b):
        if a != b:
            counts[f"{a} -> {b}"] += 1
    return counts


def table(title: str, counts: Counter[str]) -> list[str]:
    total = sum(counts.values())
    lines = [f"## {title}", "", "| value | count | share |", "|---|---:|---:|"]
    for key, value in counts.most_common():
        share = value / total if total else 0.0
        lines.append(f"| `{key}` | {value} | {pct(share)} |")
    if not counts:
        lines.append("| `<none>` | 0 | 0.0% |")
    return lines


def render_report(rows: list[dict[str, Any]], *, audit_path: Path, field_a: str, field_b: str) -> str:
    labels_a, labels_b = paired_labels(rows, field_a, field_b)
    agreement = observed_agreement(labels_a, labels_b)
    kappa = cohens_kappa(labels_a, labels_b)
    completed_a = sum(1 for row in rows if get_path(row, field_a) not in (None, ""))
    completed_b = sum(1 for row in rows if get_path(row, field_b) not in (None, ""))
    disagreements = disagreement_counts(labels_a, labels_b)

    lines = [
        "# Private Route Audit Agreement Summary",
        "",
        "This report summarizes aggregate label agreement only. It does not include",
        "qids, raw queries, context, or reviewer notes.",
        "",
        f"- audit rows: {len(rows)}",
        f"- audit file: `{audit_path.name}`",
        f"- field A: `{field_a}`",
        f"- field B: `{field_b}`",
        f"- completed A: {completed_a}",
        f"- completed B: {completed_b}",
        f"- paired completed rows: {len(labels_a)}",
        f"- raw agreement: {pct(agreement)}",
        f"- Cohen's kappa: {kappa:.3f}",
        f"- disagreement rows: {sum(disagreements.values())}",
        "",
    ]
    lines.extend(table(f"Field A Distribution: `{field_a}`", count_values(rows, field_a)))
    lines.append("")
    lines.extend(table(f"Field B Distribution: `{field_b}`", count_values(rows, field_b)))
    lines.append("")
    lines.extend(table("Disagreement Direction Counts", disagreements))
    lines.extend(
        [
            "",
            "## Use Notes",
            "",
            "- Report agreement only after both compared fields are independently labeled.",
            "- Treat silver-vs-human agreement as calibration, not inter-annotator agreement.",
            "- Do not promote route headline claims until agreement, adjudication, and qid-only validation are complete.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--field-a", default="silver.route_gold")
    parser.add_argument("--field-b", default="human_route_gold")
    parser.add_argument("--report-out", type=Path)
    args = parser.parse_args()

    rows = load_jsonl(args.audit)
    report = render_report(rows, audit_path=args.audit, field_a=args.field_a, field_b=args.field_b)
    if args.report_out:
        args.report_out.parent.mkdir(parents=True, exist_ok=True)
        args.report_out.write_text(report, encoding="utf-8")
    else:
        print(report, end="")


if __name__ == "__main__":
    main()
