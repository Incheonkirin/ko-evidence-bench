#!/usr/bin/env python3
"""Validate an answer-quality review CSV without exposing row text."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ko_evidence_bench.answer_audit import ANSWER_LABELS, CONFIDENCE_LABELS  # noqa: E402


REQUIRED_COLUMNS = {
    "audit_id",
    "answer_label",
    "supporting_evidence_ids",
    "confidence",
    "rationale_code",
    "labeler",
}
LABEL_COLUMNS = (
    "answer_label",
    "supporting_evidence_ids",
    "confidence",
    "rationale_code",
    "labeler",
)
SUPPORT_REQUIRED = {"sufficient", "partial"}


def load_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def split_list(value: str | None) -> list[str]:
    text = (value or "").strip()
    if not text:
        return []
    return [part.strip() for part in re.split(r"[;|,]", text) if part.strip()]


def blank(row: dict[str, str], key: str) -> bool:
    return not (row.get(key) or "").strip()


def row_errors(row: dict[str, str], *, duplicate_audit_ids: set[str] | None = None) -> list[str]:
    errors: list[str] = []
    duplicate_audit_ids = duplicate_audit_ids or set()
    audit_id = (row.get("audit_id") or "").strip()
    if not audit_id:
        errors.append("missing_audit_id")
    elif audit_id in duplicate_audit_ids:
        errors.append("duplicate_audit_id")

    label = (row.get("answer_label") or "").strip()
    if not label:
        errors.append("missing_answer_label")
    elif label not in ANSWER_LABELS:
        errors.append("invalid_answer_label")

    supporting = split_list(row.get("supporting_evidence_ids"))
    if label in SUPPORT_REQUIRED and not supporting:
        errors.append("missing_supporting_evidence_ids")

    confidence = (row.get("confidence") or "").strip()
    if not confidence:
        errors.append("missing_confidence")
    elif confidence not in CONFIDENCE_LABELS:
        errors.append("invalid_confidence")

    if blank(row, "rationale_code"):
        errors.append("missing_rationale_code")
    if blank(row, "labeler"):
        errors.append("missing_labeler")

    return errors


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


def summarize(columns: list[str], rows: list[dict[str, str]]) -> dict[str, object]:
    missing_columns = sorted(REQUIRED_COLUMNS - set(columns))
    field_counts: Counter[str] = Counter()
    label_counts: Counter[str] = Counter()
    confidence_counts: Counter[str] = Counter()
    error_counts: Counter[str] = Counter()
    audit_ids_seen: Counter[str] = Counter()
    complete_rows = 0
    rows_with_errors = 0

    for row in rows:
        audit_id = (row.get("audit_id") or "").strip()
        if audit_id:
            audit_ids_seen[audit_id] += 1
    duplicate_audit_ids = {audit_id for audit_id, count in audit_ids_seen.items() if count > 1}

    for row in rows:
        for field in (*LABEL_COLUMNS, "notes"):
            if not blank(row, field):
                field_counts[field] += 1
        label = (row.get("answer_label") or "").strip()
        if label in ANSWER_LABELS:
            label_counts[label] += 1
        elif label:
            label_counts["<invalid_or_unknown>"] += 1
        confidence = (row.get("confidence") or "").strip()
        if confidence in CONFIDENCE_LABELS:
            confidence_counts[confidence] += 1
        elif confidence:
            confidence_counts["<invalid_or_unknown>"] += 1

        errors = row_errors(row, duplicate_audit_ids=duplicate_audit_ids)
        if errors:
            rows_with_errors += 1
            error_counts.update(errors)
        else:
            complete_rows += 1

    for column in missing_columns:
        error_counts[f"missing_column:{column}"] += 1
    if missing_columns:
        complete_rows = 0

    return {
        "n": len(rows),
        "complete_rows": complete_rows,
        "rows_with_errors": rows_with_errors,
        "missing_columns": missing_columns,
        "field_counts": field_counts,
        "label_counts": label_counts,
        "confidence_counts": confidence_counts,
        "error_counts": error_counts,
    }


def render_report(*, csv_path: Path, columns: list[str], rows: list[dict[str, str]]) -> str:
    summary = summarize(columns, rows)
    n = int(summary["n"])
    complete_rows = int(summary["complete_rows"])
    rows_with_errors = int(summary["rows_with_errors"])
    missing_columns = summary["missing_columns"]
    field_counts = summary["field_counts"]
    lines = [
        "# Private Answer Review CSV Validation",
        "",
        "This report validates a private answer-quality review CSV before import.",
        "It contains aggregate counts only. It does not include qids, raw queries,",
        "answers, evidence text, audit ids, or reviewer notes.",
        "",
        f"- private csv: `{csv_path.name}`",
        f"- rows: {n}",
        f"- complete rows: {complete_rows}",
        f"- rows with validation errors: {rows_with_errors}",
        f"- completion rate: {pct(complete_rows / n if n else 0.0)}",
        f"- missing required columns: {len(missing_columns)}",
        "",
    ]
    if missing_columns:
        lines.extend(["## Missing Required Columns", "", "| column |", "|---|"])
        lines.extend(f"| `{column}` |" for column in missing_columns)
        lines.append("")
    lines.extend(["## Field Fill Rates", "", "| field | filled | share |", "|---|---:|---:|"])
    for field in (*LABEL_COLUMNS, "notes"):
        count = int(field_counts[field])
        lines.append(f"| `{field}` | {count} | {pct(count / n if n else 0.0)} |")
    lines.append("")
    lines.extend(table("Valid Answer Label Distribution", summary["label_counts"]))
    lines.append("")
    lines.extend(table("Valid Confidence Distribution", summary["confidence_counts"]))
    lines.append("")
    lines.extend(table("Validation Error Counts", summary["error_counts"]))
    lines.extend(
        [
            "",
            "## Use Notes",
            "",
            "- Run with `--require-complete` before importing labels for promotion.",
            "- `sufficient` and `partial` rows should include at least one supporting evidence id.",
            "- Keep the reviewed CSV outside the public repository.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--report-out", type=Path)
    parser.add_argument("--require-complete", action="store_true")
    parser.add_argument("--expected-rows", type=int)
    args = parser.parse_args()

    columns, rows = load_csv(args.csv)
    report = render_report(csv_path=args.csv, columns=columns, rows=rows)
    if args.report_out:
        args.report_out.parent.mkdir(parents=True, exist_ok=True)
        args.report_out.write_text(report, encoding="utf-8")
    else:
        print(report, end="")

    summary = summarize(columns, rows)
    has_errors = bool(summary["missing_columns"]) or bool(summary["error_counts"])
    complete = summary["complete_rows"] == summary["n"]
    expected_ok = args.expected_rows is None or summary["n"] == args.expected_rows
    if args.require_complete and (has_errors or not complete or not expected_ok):
        return 1
    if args.expected_rows is not None and not expected_ok:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
