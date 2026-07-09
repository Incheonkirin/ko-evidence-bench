#!/usr/bin/env python3
"""Validate a private route-review CSV without exposing row text."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ko_evidence_bench.route_audit import CONFIDENCE_LABELS, ROUTE_LABELS  # noqa: E402


REQUIRED_COLUMNS = {
    "audit_id",
    "route_gold",
    "allowed_source_tiers",
    "should_abstain",
    "confidence",
    "rationale_code",
    "labeler",
}

LABEL_COLUMNS = (
    "route_gold",
    "allowed_source_tiers",
    "should_abstain",
    "confidence",
    "rationale_code",
    "labeler",
)

ABSTAIN_ROUTES = {"human_context_needed", "out_of_scope"}


def load_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def split_allowed(value: str | None) -> list[str]:
    text = (value or "").strip()
    if not text:
        return []
    return [part.strip() for part in re.split(r"[;|,]", text) if part.strip()]


def parse_bool(value: str | None) -> bool | None:
    text = (value or "").strip().lower()
    if not text:
        return None
    if text in {"true", "t", "1", "yes", "y"}:
        return True
    if text in {"false", "f", "0", "no", "n"}:
        return False
    return None


def blank(row: dict[str, str], key: str) -> bool:
    return not (row.get(key) or "").strip()


def row_errors(row: dict[str, str], *, duplicate_audit_ids: set[str] | None = None) -> list[str]:
    errors: list[str] = []

    duplicate_audit_ids = duplicate_audit_ids or set()
    if blank(row, "audit_id"):
        errors.append("missing_audit_id")
    elif (row.get("audit_id") or "").strip() in duplicate_audit_ids:
        errors.append("duplicate_audit_id")

    route = (row.get("route_gold") or "").strip()
    route_valid = False
    if not route:
        errors.append("missing_route_gold")
    elif route not in ROUTE_LABELS:
        errors.append("invalid_route_gold")
    else:
        route_valid = True

    allowed = split_allowed(row.get("allowed_source_tiers"))
    if not allowed:
        errors.append("missing_allowed_source_tiers")
    elif any(value not in ROUTE_LABELS for value in allowed):
        errors.append("invalid_allowed_source_tiers")
    elif route_valid and route not in allowed:
        errors.append("route_gold_not_in_allowed_source_tiers")

    should_abstain = parse_bool(row.get("should_abstain"))
    if blank(row, "should_abstain"):
        errors.append("missing_should_abstain")
    elif should_abstain is None:
        errors.append("invalid_should_abstain")
    elif route_valid and should_abstain != (route in ABSTAIN_ROUTES):
        errors.append("should_abstain_route_mismatch")

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
    return lines


def summarize(columns: list[str], rows: list[dict[str, str]]) -> dict[str, object]:
    missing_columns = sorted(REQUIRED_COLUMNS - set(columns))
    duplicate_ids: Counter[str] = Counter()
    audit_ids_seen: Counter[str] = Counter()
    field_counts: Counter[str] = Counter()
    route_counts: Counter[str] = Counter()
    confidence_counts: Counter[str] = Counter()
    error_counts: Counter[str] = Counter()
    complete_rows = 0
    rows_with_errors = 0

    for row in rows:
        audit_id = (row.get("audit_id") or "").strip()
        if audit_id:
            audit_ids_seen[audit_id] += 1

    duplicate_audit_ids = {audit_id for audit_id, count in audit_ids_seen.items() if count > 1}
    if duplicate_audit_ids:
        duplicate_ids["duplicate_audit_id_groups"] = len(duplicate_audit_ids)
        duplicate_ids["duplicate_audit_id_rows"] = sum(audit_ids_seen[audit_id] for audit_id in duplicate_audit_ids)

    for row in rows:
        for field in (*LABEL_COLUMNS, "notes"):
            if not blank(row, field):
                field_counts[field] += 1

        route = (row.get("route_gold") or "").strip()
        if route in ROUTE_LABELS:
            route_counts[route] += 1
        elif route:
            route_counts["<invalid_or_unknown>"] += 1

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
        "duplicate_ids": duplicate_ids,
        "field_counts": field_counts,
        "route_counts": route_counts,
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
        "# Private Route Review CSV Validation",
        "",
        "This report validates a private route-review CSV before import or",
        "promotion. It contains aggregate counts only. It does not include qids,",
        "raw queries, context, audit ids, or reviewer notes.",
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

    duplicate_counts = summary["duplicate_ids"]
    if duplicate_counts:
        lines.extend(table("Duplicate Audit Id Summary", duplicate_counts))
        lines.append("")

    lines.extend(["## Field Fill Rates", "", "| field | filled | share |", "|---|---:|---:|"])
    for field in (*LABEL_COLUMNS, "notes"):
        count = int(field_counts[field])
        lines.append(f"| `{field}` | {count} | {pct(count / n if n else 0.0)} |")
    lines.append("")
    lines.extend(table("Valid Route Distribution", summary["route_counts"]))
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
            "- `human_context_needed` and `out_of_scope` rows should set `should_abstain=true`.",
            "- All other route labels should set `should_abstain=false`.",
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
