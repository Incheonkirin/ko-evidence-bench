#!/usr/bin/env python3
"""Build a private priority batch from a route-review CSV."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


PRIORITY_REASONS = [
    ("silver_low_confidence", 5),
    ("silver_medium_confidence", 2),
    ("silver_should_abstain", 3),
    ("needs_contract", 3),
    ("product_divergent", 2),
    ("not_in_corpus", 2),
    ("requires_exclusion_check", 2),
    ("requires_table_value", 1),
]

LABEL_FIELDS = ("route_gold", "allowed_source_tiers", "should_abstain", "confidence", "rationale_code", "labeler")


def load_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def filled(row: dict[str, str], field: str) -> bool:
    return bool((row.get(field) or "").strip())


def complete(row: dict[str, str]) -> bool:
    return all(filled(row, field) for field in LABEL_FIELDS)


def priority_reasons(row: dict[str, str]) -> list[str]:
    reasons: list[str] = []
    if (row.get("silver_confidence") or "").strip() == "low":
        reasons.append("silver_low_confidence")
    if (row.get("silver_confidence") or "").strip() == "medium":
        reasons.append("silver_medium_confidence")
    if (row.get("silver_should_abstain") or "").strip().lower() == "true":
        reasons.append("silver_should_abstain")
    if (row.get("needs_contract") or "").strip().lower() == "true":
        reasons.append("needs_contract")
    if (row.get("product_divergent") or "").strip().lower() == "true":
        reasons.append("product_divergent")
    reason_code = (row.get("reason_code") or "").strip()
    if reason_code in {"not_in_corpus", "requires_exclusion_check", "requires_table_value"}:
        reasons.append(reason_code)
    return reasons


def priority_score(row: dict[str, str]) -> int:
    reasons = set(priority_reasons(row))
    return sum(weight for reason, weight in PRIORITY_REASONS if reason in reasons)


def sort_key(indexed_row: tuple[int, dict[str, str]]) -> tuple[int, str, str, str, int]:
    index, row = indexed_row
    return (
        -priority_score(row),
        (row.get("silver_confidence") or ""),
        (row.get("silver_route_gold") or ""),
        (row.get("reason_code") or ""),
        index,
    )


def select_batch(rows: list[dict[str, str]], *, limit: int, include_complete: bool) -> list[dict[str, str]]:
    candidates = [(idx, row) for idx, row in enumerate(rows) if include_complete or not complete(row)]
    selected = [row for _, row in sorted(candidates, key=sort_key)[:limit]]
    return selected


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def pct(value: float) -> str:
    return f"{100 * value:.1f}%"


def count_column(rows: list[dict[str, str]], column: str) -> Counter[str]:
    return Counter((row.get(column) or "").strip() or "<blank>" for row in rows)


def table(title: str, counts: Counter[str]) -> list[str]:
    total = sum(counts.values())
    lines = [f"## {title}", "", "| value | count | share |", "|---|---:|---:|"]
    for key, count in counts.most_common():
        share = count / total if total else 0.0
        lines.append(f"| `{key}` | {count} | {pct(share)} |")
    return lines


def render_report(
    *,
    source_csv: Path,
    out_csv: Path,
    source_rows: list[dict[str, str]],
    batch_rows: list[dict[str, str]],
    limit: int,
) -> str:
    reason_counts: Counter[str] = Counter()
    for row in batch_rows:
        reason_counts.update(priority_reasons(row))

    lines = [
        "# Private Route Review Batch Summary",
        "",
        "This report summarizes a private priority batch for route adjudication.",
        "The batch CSV may contain qids, raw queries, and context, so it must stay",
        "outside the public repository. This summary is aggregate-only.",
        "",
        f"- source csv: `{source_csv.name}`",
        f"- private batch csv: `{out_csv.name}`",
        f"- source rows: {len(source_rows)}",
        f"- requested limit: {limit}",
        f"- selected rows: {len(batch_rows)}",
        f"- selected complete rows: {sum(1 for row in batch_rows if complete(row))}",
        "",
    ]
    lines.extend(table("Priority Reason Counts", reason_counts))
    lines.append("")
    for column in ("silver_route_gold", "silver_confidence", "silver_should_abstain", "reason_code", "needs_contract", "product_divergent"):
        lines.extend(table(f"Batch Distribution: `{column}`", count_column(batch_rows, column)))
        lines.append("")
    lines.extend(
        [
            "## Use Notes",
            "",
            "- Label this private batch first when starting adjudication.",
            "- After filling it, run `scripts/check_route_review_progress.py` on the batch or full CSV.",
            "- Do not copy the private batch CSV into the public repository.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--out-csv", type=Path, required=True)
    parser.add_argument("--report-out", type=Path)
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--include-complete", action="store_true")
    args = parser.parse_args()

    fieldnames, rows = load_csv(args.csv)
    batch = select_batch(rows, limit=args.limit, include_complete=args.include_complete)
    write_csv(args.out_csv, fieldnames, batch)
    report = render_report(
        source_csv=args.csv,
        out_csv=args.out_csv,
        source_rows=rows,
        batch_rows=batch,
        limit=args.limit,
    )
    if args.report_out:
        args.report_out.parent.mkdir(parents=True, exist_ok=True)
        args.report_out.write_text(report, encoding="utf-8")
    else:
        print(report)


if __name__ == "__main__":
    main()
