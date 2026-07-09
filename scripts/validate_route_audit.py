#!/usr/bin/env python3
"""Validate private route-audit labels and write an aggregate report."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ko_evidence_bench.route_audit import validate_audit_rows  # noqa: E402


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def pct(value: float) -> str:
    return f"{100 * value:.1f}%"


def table(title: str, counts: Counter[str]) -> list[str]:
    total = sum(counts.values())
    lines = [f"## {title}", "", "| value | count | share |", "|---|---:|---:|"]
    for key, value in counts.most_common():
        share = value / total if total else 0.0
        lines.append(f"| `{key}` | {value} | {pct(share)} |")
    return lines


def error_table(errors: list[dict[str, Any]]) -> list[str]:
    counts: Counter[str] = Counter()
    for item in errors:
        counts.update(item["errors"])
    return table("Validation Error Counts", counts)


def render_report(
    result: dict[str, Any],
    *,
    audit_path: Path,
    label_prefix: str,
    require_complete: bool,
) -> str:
    n = result["n"]
    completed = result["completed"]
    lines = [
        "# Private Route Audit Validation Summary",
        "",
        "This report validates a private route-audit file and exposes only",
        "aggregate counts. It does not include qids, raw queries, context, or",
        "reviewer notes.",
        "",
        f"- audit rows: {n}",
        f"- audit file: `{audit_path.name}`",
        f"- label prefix: `{label_prefix}`",
        f"- require complete: {str(require_complete).lower()}",
        f"- completed labels: {completed}",
        f"- completion rate: {pct(completed / n if n else 0.0)}",
        f"- rows with validation errors: {result['error_count']}",
        "",
    ]
    lines.extend(table("Validated Route Distribution", result["route_counts"]))
    lines.append("")
    lines.extend(table("Validated Confidence Distribution", result["confidence_counts"]))
    if result["row_errors"]:
        lines.append("")
        lines.extend(error_table(result["row_errors"]))
    lines.extend(
        [
            "",
            "## Use Notes",
            "",
            "- A validation report with zero row errors is required before promotion.",
            "- This report is aggregate-only; inspect the private audit file for row-level fixes.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--label-prefix", default="adjudicated")
    parser.add_argument("--require-complete", action="store_true")
    parser.add_argument("--report-out", type=Path)
    args = parser.parse_args()

    rows = load_jsonl(args.audit)
    result = validate_audit_rows(
        rows,
        label_prefix=args.label_prefix,
        require_complete=args.require_complete,
    )
    report = render_report(
        result,
        audit_path=args.audit,
        label_prefix=args.label_prefix,
        require_complete=args.require_complete,
    )
    if args.report_out:
        args.report_out.parent.mkdir(parents=True, exist_ok=True)
        args.report_out.write_text(report, encoding="utf-8")
    else:
        print(report, end="")


if __name__ == "__main__":
    main()
