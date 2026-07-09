#!/usr/bin/env python3
"""Export private route-audit rows to a reviewer-editable CSV."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ko_evidence_bench.agreement import get_path  # noqa: E402


CSV_FIELDS = [
    "audit_id",
    "qid",
    "query",
    "context",
    "gate_category",
    "intent",
    "answerability",
    "answer_structure",
    "reason_code",
    "needs_contract",
    "product_divergent",
    "required_facets",
    "silver_route_gold",
    "silver_should_abstain",
    "silver_confidence",
    "silver_rationale_code",
    "route_gold",
    "allowed_source_tiers",
    "should_abstain",
    "confidence",
    "rationale_code",
    "labeler",
    "notes",
]


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def stringify(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, list):
        return ";".join(str(x) for x in value)
    return " ".join(str(value).splitlines())


def label_payload(row: dict[str, Any], prefix: str) -> dict[str, Any]:
    payload = get_path(row, prefix)
    return payload if isinstance(payload, dict) else {}


def csv_row(row: dict[str, Any], *, reviewer_prefix: str) -> dict[str, str]:
    metadata = row.get("metadata") or {}
    silver = row.get("silver") or {}
    label = label_payload(row, reviewer_prefix)
    return {
        "audit_id": stringify(row.get("audit_id")),
        "qid": stringify(row.get("qid")),
        "query": stringify(row.get("query")),
        "context": stringify(row.get("context")),
        "gate_category": stringify(metadata.get("gate_category")),
        "intent": stringify(metadata.get("intent")),
        "answerability": stringify(metadata.get("answerability")),
        "answer_structure": stringify(metadata.get("answer_structure")),
        "reason_code": stringify(metadata.get("reason_code")),
        "needs_contract": stringify(metadata.get("needs_contract")),
        "product_divergent": stringify(metadata.get("product_divergent")),
        "required_facets": stringify(metadata.get("required_facets") or []),
        "silver_route_gold": stringify(silver.get("route_gold")),
        "silver_should_abstain": stringify(silver.get("should_abstain")),
        "silver_confidence": stringify(silver.get("confidence")),
        "silver_rationale_code": stringify(silver.get("rationale_code")),
        "route_gold": stringify(label.get("route_gold")),
        "allowed_source_tiers": stringify(label.get("allowed_source_tiers") or []),
        "should_abstain": stringify(label.get("should_abstain")),
        "confidence": stringify(label.get("confidence")),
        "rationale_code": stringify(label.get("rationale_code")),
        "labeler": stringify(label.get("labeler")),
        "notes": stringify(label.get("notes")),
    }


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def pct(value: float) -> str:
    return f"{100 * value:.1f}%"


def table(title: str, counts: Counter[str]) -> list[str]:
    total = sum(counts.values())
    lines = [f"## {title}", "", "| value | count | share |", "|---|---:|---:|"]
    for key, value in counts.most_common():
        share = value / total if total else 0.0
        lines.append(f"| `{key}` | {value} | {pct(share)} |")
    return lines


def render_report(audit_rows: list[dict[str, Any]], *, reviewer_prefix: str, csv_out: Path) -> str:
    silver_counts = Counter(str((row.get("silver") or {}).get("route_gold")) for row in audit_rows)
    existing_labels = sum(1 for row in audit_rows if label_payload(row, reviewer_prefix).get("route_gold"))
    lines = [
        "# Private Route Review CSV Export Summary",
        "",
        "This report summarizes a private reviewer CSV export. The CSV may contain",
        "raw queries and context, so it must stay outside the public repository.",
        "",
        f"- exported rows: {len(audit_rows)}",
        f"- reviewer prefix: `{reviewer_prefix}`",
        f"- private csv: `{csv_out.name}`",
        f"- existing labels in target prefix: {existing_labels}",
        "",
    ]
    lines.extend(table("Silver Route Distribution", silver_counts))
    lines.extend(
        [
            "",
            "## Use Notes",
            "",
            "- Reviewers should fill `route_gold`, `allowed_source_tiers`, `should_abstain`, `confidence`, `rationale_code`, `labeler`, and `notes`.",
            "- Use `;` to separate multiple `allowed_source_tiers` values.",
            "- Do not copy the private CSV into the public repository.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--reviewer-prefix", default="reviewer_a")
    parser.add_argument("--csv-out", type=Path, required=True)
    parser.add_argument("--report-out", type=Path)
    args = parser.parse_args()

    audit_rows = load_jsonl(args.audit)
    rows = [csv_row(row, reviewer_prefix=args.reviewer_prefix) for row in audit_rows]
    write_csv(args.csv_out, rows)
    report = render_report(audit_rows, reviewer_prefix=args.reviewer_prefix, csv_out=args.csv_out)
    if args.report_out:
        args.report_out.parent.mkdir(parents=True, exist_ok=True)
        args.report_out.write_text(report, encoding="utf-8")
    else:
        print(report, end="")


if __name__ == "__main__":
    main()
