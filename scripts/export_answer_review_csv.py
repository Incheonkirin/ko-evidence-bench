#!/usr/bin/env python3
"""Export answer-quality audit rows to a reviewer-editable CSV."""

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

from ko_evidence_bench.answer_audit import label_payload  # noqa: E402


CSV_FIELDS = [
    "audit_id",
    "qid",
    "system_id",
    "intent_family",
    "surface_form",
    "trap_classes",
    "route_gold",
    "route_pred",
    "should_abstain",
    "abstained",
    "topk_evidence_ids",
    "topk_source_tiers",
    "query",
    "answer",
    "evidence_text",
    "answer_label",
    "supporting_evidence_ids",
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


def csv_row(row: dict[str, Any], *, reviewer_prefix: str) -> dict[str, str]:
    label = label_payload(row, reviewer_prefix)
    return {
        "audit_id": stringify(row.get("audit_id")),
        "qid": stringify(row.get("qid")),
        "system_id": stringify(row.get("system_id")),
        "intent_family": stringify(row.get("intent_family")),
        "surface_form": stringify(row.get("surface_form")),
        "trap_classes": stringify(row.get("trap_classes") or []),
        "route_gold": stringify(row.get("route_gold")),
        "route_pred": stringify(row.get("route_pred")),
        "should_abstain": stringify(row.get("should_abstain")),
        "abstained": stringify(row.get("abstained")),
        "topk_evidence_ids": stringify(row.get("topk_evidence_ids") or []),
        "topk_source_tiers": stringify(row.get("topk_source_tiers") or []),
        "query": stringify(row.get("query")),
        "answer": stringify(row.get("answer")),
        "evidence_text": stringify(row.get("evidence_text")),
        "answer_label": stringify(label.get("answer_label")),
        "supporting_evidence_ids": stringify(label.get("supporting_evidence_ids") or []),
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
    for key, count in counts.most_common():
        share = count / total if total else 0.0
        lines.append(f"| `{key}` | {count} | {pct(share)} |")
    if not counts:
        lines.append("| `<none>` | 0 | 0.0% |")
    return lines


def render_report(audit_rows: list[dict[str, Any]], *, reviewer_prefix: str, csv_out: Path) -> str:
    system_counts = Counter(str(row.get("system_id") or "<missing>") for row in audit_rows)
    surface_counts = Counter(str(row.get("surface_form") or "<missing>") for row in audit_rows)
    existing_labels = sum(1 for row in audit_rows if label_payload(row, reviewer_prefix).get("answer_label"))
    lines = [
        "# Private Answer Review CSV Export Summary",
        "",
        "This report summarizes an answer-quality reviewer CSV export. The CSV may",
        "contain raw query, answer, or evidence text, so it must stay outside the",
        "public repository.",
        "",
        f"- exported rows: {len(audit_rows)}",
        f"- reviewer prefix: `{reviewer_prefix}`",
        f"- private csv: `{csv_out.name}`",
        f"- existing labels in target prefix: {existing_labels}",
        "",
    ]
    lines.extend(table("System Distribution", system_counts))
    lines.append("")
    lines.extend(table("Surface Distribution", surface_counts))
    lines.extend(
        [
            "",
            "## Use Notes",
            "",
            "- Reviewers fill `answer_label`, `supporting_evidence_ids`, `confidence`, `rationale_code`, `labeler`, and `notes`.",
            "- Use `;` to separate multiple `supporting_evidence_ids` values.",
            "- Keep the private CSV outside the public repository.",
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
