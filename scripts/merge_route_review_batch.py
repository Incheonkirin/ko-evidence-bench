#!/usr/bin/env python3
"""Merge a private reviewed priority batch back into a full review CSV."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


MERGE_FIELDS = (
    "route_gold",
    "allowed_source_tiers",
    "should_abstain",
    "confidence",
    "rationale_code",
    "labeler",
    "notes",
)


def load_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def has_payload(row: dict[str, str]) -> bool:
    return any((row.get(field) or "").strip() for field in MERGE_FIELDS)


def index_by_audit_id(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for row in rows:
        audit_id = (row.get("audit_id") or "").strip()
        if audit_id:
            out[audit_id] = row
    return out


def merge_batch(
    full_rows: list[dict[str, str]],
    batch_rows: list[dict[str, str]],
    *,
    include_empty: bool,
) -> tuple[list[dict[str, str]], dict[str, int], Counter[str], Counter[str]]:
    batch_by_id = index_by_audit_id(batch_rows)
    stats = {
        "full_rows": len(full_rows),
        "batch_rows": len(batch_rows),
        "matched_rows": 0,
        "updated_rows": 0,
        "skipped_empty_rows": 0,
    }
    route_counts: Counter[str] = Counter()
    confidence_counts: Counter[str] = Counter()

    merged: list[dict[str, str]] = []
    for row in full_rows:
        out = dict(row)
        audit_id = (row.get("audit_id") or "").strip()
        batch_row = batch_by_id.get(audit_id)
        if batch_row is not None:
            stats["matched_rows"] += 1
            if include_empty or has_payload(batch_row):
                for field in MERGE_FIELDS:
                    out[field] = batch_row.get(field, "")
                stats["updated_rows"] += 1
                route = (out.get("route_gold") or "").strip()
                confidence = (out.get("confidence") or "").strip()
                if route:
                    route_counts[route] += 1
                if confidence:
                    confidence_counts[confidence] += 1
            else:
                stats["skipped_empty_rows"] += 1
        merged.append(out)

    stats["unmatched_batch_rows"] = max(0, len(batch_by_id) - stats["matched_rows"])
    return merged, stats, route_counts, confidence_counts


def pct(value: float) -> str:
    return f"{100 * value:.1f}%"


def table(title: str, counts: Counter[str]) -> list[str]:
    total = sum(counts.values())
    lines = [f"## {title}", "", "| value | count | share |", "|---|---:|---:|"]
    for key, count in counts.most_common():
        share = count / total if total else 0.0
        lines.append(f"| `{key}` | {count} | {pct(share)} |")
    return lines


def render_report(
    *,
    full_csv: Path,
    batch_csv: Path,
    out_csv: Path,
    include_empty: bool,
    stats: dict[str, int],
    route_counts: Counter[str],
    confidence_counts: Counter[str],
) -> str:
    lines = [
        "# Private Route Review Batch Merge Summary",
        "",
        "This report summarizes merging a private reviewed priority batch back into",
        "a full route-review CSV. It contains aggregate counts only and does not",
        "include qids, raw queries, context, or reviewer notes.",
        "",
        f"- full csv: `{full_csv.name}`",
        f"- batch csv: `{batch_csv.name}`",
        f"- private output csv: `{out_csv.name}`",
        f"- include empty batch rows: {str(include_empty).lower()}",
        "",
        "## Merge Counts",
        "",
        "| item | count |",
        "|---|---:|",
    ]
    for key in (
        "full_rows",
        "batch_rows",
        "matched_rows",
        "updated_rows",
        "skipped_empty_rows",
        "unmatched_batch_rows",
    ):
        lines.append(f"| `{key}` | {stats[key]} |")
    lines.append("")
    lines.extend(table("Merged Route Distribution", route_counts))
    lines.append("")
    lines.extend(table("Merged Confidence Distribution", confidence_counts))
    lines.extend(
        [
            "",
            "## Use Notes",
            "",
            "- Run `scripts/check_route_review_progress.py` on the merged private CSV.",
            "- Import the merged CSV only after the desired batch rows are filled.",
            "- Keep both the batch and merged CSV outside the public repository.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--full-csv", type=Path, required=True)
    parser.add_argument("--batch-csv", type=Path, required=True)
    parser.add_argument("--out-csv", type=Path, required=True)
    parser.add_argument("--report-out", type=Path)
    parser.add_argument("--include-empty", action="store_true")
    args = parser.parse_args()

    fieldnames, full_rows = load_csv(args.full_csv)
    _, batch_rows = load_csv(args.batch_csv)
    merged, stats, route_counts, confidence_counts = merge_batch(
        full_rows,
        batch_rows,
        include_empty=args.include_empty,
    )
    write_csv(args.out_csv, fieldnames, merged)
    report = render_report(
        full_csv=args.full_csv,
        batch_csv=args.batch_csv,
        out_csv=args.out_csv,
        include_empty=args.include_empty,
        stats=stats,
        route_counts=route_counts,
        confidence_counts=confidence_counts,
    )
    if args.report_out:
        args.report_out.parent.mkdir(parents=True, exist_ok=True)
        args.report_out.write_text(report, encoding="utf-8")
    else:
        print(report, end="")


if __name__ == "__main__":
    main()
