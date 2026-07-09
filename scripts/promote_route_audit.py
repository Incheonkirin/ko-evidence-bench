#!/usr/bin/env python3
"""Promote adjudicated private route-audit rows into qid-only labels."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ko_evidence_bench.route_audit import promote_audit_rows, validate_audit_rows  # noqa: E402


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def pct(value: float) -> str:
    return f"{100 * value:.1f}%"


def table(title: str, counts: Counter[str]) -> list[str]:
    total = sum(counts.values())
    lines = [f"## {title}", "", "| value | count | share |", "|---|---:|---:|"]
    for key, value in counts.most_common():
        share = value / total if total else 0.0
        lines.append(f"| `{key}` | {value} | {pct(share)} |")
    return lines


def render_report(
    *,
    audit_path: Path,
    labels_out: Path,
    label_prefix: str,
    validation: dict[str, Any],
    promoted: list[dict[str, Any]],
) -> str:
    route_counts = Counter(row["route_gold"] for row in promoted)
    abstention_counts = Counter(str(row["should_abstain"]) for row in promoted)
    confidence_counts = Counter(row["confidence"] for row in promoted)
    lines = [
        "# Private Promoted Route Label Summary",
        "",
        "This report summarizes a qid-only private route label export. It contains",
        "aggregate counts only. It does not include raw queries, context, qids, or",
        "reviewer notes.",
        "",
        f"- audit rows: {validation['n']}",
        f"- audit file: `{audit_path.name}`",
        f"- label prefix: `{label_prefix}`",
        f"- promoted labels: {len(promoted)}",
        f"- labels export: `{labels_out.name}`",
        f"- validation errors: {validation['error_count']}",
        "",
    ]
    lines.extend(table("Promoted Route Distribution", route_counts))
    lines.append("")
    lines.extend(table("Promoted Abstention Distribution", abstention_counts))
    lines.append("")
    lines.extend(table("Promoted Confidence Distribution", confidence_counts))
    lines.extend(
        [
            "",
            "## Use Notes",
            "",
            "- Promote only adjudicated labels for headline metrics.",
            "- Keep the qid-only export outside this public repository unless qids are explicitly safe to publish.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--label-prefix", default="adjudicated")
    parser.add_argument("--labels-out", type=Path, required=True)
    parser.add_argument("--report-out", type=Path)
    parser.add_argument(
        "--allow-errors",
        action="store_true",
        help="Write valid completed rows even if some audit rows are invalid.",
    )
    args = parser.parse_args()

    rows = load_jsonl(args.audit)
    validation = validate_audit_rows(rows, label_prefix=args.label_prefix, require_complete=True)
    if validation["error_count"] and not args.allow_errors:
        raise SystemExit(
            f"cannot promote: {validation['error_count']} rows have validation errors; "
            "use --allow-errors to export only valid completed rows"
        )
    promoted = promote_audit_rows(rows, label_prefix=args.label_prefix)
    write_jsonl(args.labels_out, promoted)
    report = render_report(
        audit_path=args.audit,
        labels_out=args.labels_out,
        label_prefix=args.label_prefix,
        validation=validation,
        promoted=promoted,
    )
    if args.report_out:
        args.report_out.parent.mkdir(parents=True, exist_ok=True)
        args.report_out.write_text(report, encoding="utf-8")
    else:
        print(report, end="")


if __name__ == "__main__":
    main()
