#!/usr/bin/env python3
"""Summarize private route-review CSV completion without exposing rows."""

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


def row_errors(row: dict[str, str]) -> list[str]:
    errors: list[str] = []
    route = (row.get("route_gold") or "").strip()
    if not route:
        errors.append("missing_route_gold")
        return errors
    if route not in ROUTE_LABELS:
        errors.append("invalid_route_gold")

    allowed = split_allowed(row.get("allowed_source_tiers"))
    if not allowed:
        errors.append("missing_allowed_source_tiers")
    elif any(value not in ROUTE_LABELS for value in allowed):
        errors.append("invalid_allowed_source_tiers")

    if parse_bool(row.get("should_abstain")) is None:
        errors.append("invalid_should_abstain")

    confidence = (row.get("confidence") or "").strip()
    if confidence not in CONFIDENCE_LABELS:
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


def summarize(rows: list[dict[str, str]]) -> dict[str, object]:
    error_counts: Counter[str] = Counter()
    route_counts: Counter[str] = Counter()
    confidence_counts: Counter[str] = Counter()
    field_counts: Counter[str] = Counter()
    completed = 0

    for row in rows:
        for field in ("route_gold", "allowed_source_tiers", "should_abstain", "confidence", "rationale_code", "labeler", "notes"):
            if not blank(row, field):
                field_counts[field] += 1

        route = (row.get("route_gold") or "").strip()
        if route:
            route_counts[route] += 1
        confidence = (row.get("confidence") or "").strip()
        if confidence:
            confidence_counts[confidence] += 1

        errors = row_errors(row)
        if errors:
            error_counts.update(errors)
        else:
            completed += 1

    return {
        "n": len(rows),
        "completed": completed,
        "field_counts": field_counts,
        "route_counts": route_counts,
        "confidence_counts": confidence_counts,
        "error_counts": error_counts,
    }


def render_report(*, csv_path: Path, columns: list[str], rows: list[dict[str, str]]) -> str:
    summary = summarize(rows)
    n = int(summary["n"])
    completed = int(summary["completed"])
    missing_columns = sorted(REQUIRED_COLUMNS - set(columns))
    lines = [
        "# Private Route Review Progress",
        "",
        "This report summarizes private route-review CSV completion. It contains",
        "aggregate counts only. It does not include qids, raw queries, context, or",
        "reviewer notes.",
        "",
        f"- private csv: `{csv_path.name}`",
        f"- rows: {n}",
        f"- complete rows: {completed}",
        f"- completion rate: {pct(completed / n if n else 0.0)}",
        f"- missing required columns: {len(missing_columns)}",
        "",
    ]
    if missing_columns:
        lines.extend(["## Missing Columns", "", "| column |", "|---|"])
        lines.extend(f"| `{column}` |" for column in missing_columns)
        lines.append("")

    field_counts = summary["field_counts"]
    lines.extend(["## Field Fill Rates", "", "| field | filled | share |", "|---|---:|---:|"])
    for field in ("route_gold", "allowed_source_tiers", "should_abstain", "confidence", "rationale_code", "labeler", "notes"):
        count = int(field_counts[field])
        lines.append(f"| `{field}` | {count} | {pct(count / n if n else 0.0)} |")
    lines.append("")
    lines.extend(table("Route Distribution", summary["route_counts"]))
    lines.append("")
    lines.extend(table("Confidence Distribution", summary["confidence_counts"]))
    lines.append("")
    lines.extend(table("Completion Error Counts", summary["error_counts"]))
    lines.extend(
        [
            "",
            "## Use Notes",
            "",
            "- Complete rows still need import and audit validation before promotion.",
            "- Use `scripts/import_route_review_csv.py` after labels are filled.",
            "- Keep the private CSV outside the public repository.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--report-out", type=Path)
    parser.add_argument("--fail-if-incomplete", action="store_true")
    args = parser.parse_args()

    columns, rows = load_csv(args.csv)
    report = render_report(csv_path=args.csv, columns=columns, rows=rows)
    if args.report_out:
        args.report_out.parent.mkdir(parents=True, exist_ok=True)
        args.report_out.write_text(report, encoding="utf-8")
    else:
        print(report, end="")

    summary = summarize(rows)
    if args.fail_if_incomplete and summary["completed"] != summary["n"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
