#!/usr/bin/env python3
"""Build an aggregate-only brief for private route-review work."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


COUNT_COLUMNS = [
    "silver_route_gold",
    "silver_confidence",
    "silver_rationale_code",
    "silver_should_abstain",
    "answerability",
    "answer_structure",
    "reason_code",
    "needs_contract",
    "product_divergent",
]

LABEL_FIELDS = [
    "route_gold",
    "allowed_source_tiers",
    "should_abstain",
    "confidence",
    "rationale_code",
    "labeler",
]


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def filled(row: dict[str, str], field: str) -> bool:
    return bool((row.get(field) or "").strip())


def row_complete(row: dict[str, str]) -> bool:
    return all(filled(row, field) for field in LABEL_FIELDS)


def count_column(rows: list[dict[str, str]], column: str) -> Counter[str]:
    return Counter((row.get(column) or "").strip() or "<blank>" for row in rows)


def pct(value: float) -> str:
    return f"{100 * value:.1f}%"


def table(title: str, counts: Counter[str], *, limit: int | None = None) -> list[str]:
    total = sum(counts.values())
    lines = [f"## {title}", "", "| value | count | share |", "|---|---:|---:|"]
    rows = counts.most_common(limit)
    for key, count in rows:
        share = count / total if total else 0.0
        lines.append(f"| `{key}` | {count} | {pct(share)} |")
    return lines


def render_brief(*, csv_path: Path, rows: list[dict[str, str]]) -> str:
    n = len(rows)
    complete = sum(1 for row in rows if row_complete(row))
    low_conf = count_column(rows, "silver_confidence")["low"]
    medium_conf = count_column(rows, "silver_confidence")["medium"]
    abstain = count_column(rows, "silver_should_abstain")["true"]
    needs_contract = count_column(rows, "needs_contract")["true"]
    product_divergent = count_column(rows, "product_divergent")["true"]

    lines = [
        "# Private Route Review Brief",
        "",
        "This brief summarizes the private route-review workset without exposing",
        "qids, raw queries, context, or reviewer notes. It is meant to guide manual",
        "adjudication before import, validation, and promotion.",
        "",
        f"- private csv: `{csv_path.name}`",
        f"- rows: {n}",
        f"- currently complete rows: {complete}",
        f"- remaining rows: {n - complete}",
        "",
        "## Review Priorities",
        "",
        "| priority | count | why review carefully |",
        "|---|---:|---|",
        f"| silver `low` confidence | {low_conf} | likely label-boundary cases |",
        f"| silver `medium` confidence | {medium_conf} | useful second-pass review set |",
        f"| silver `should_abstain=true` | {abstain} | controls abstention recall and false-answer risk |",
        f"| `needs_contract=true` | {needs_contract} | should usually route to human context unless source evidence is enough |",
        f"| `product_divergent=true` | {product_divergent} | likely not answerable by one generic policy clause |",
        "",
        "## Required Per Row",
        "",
        "| field | expected content |",
        "|---|---|",
        "| `route_gold` | one source-route label |",
        "| `allowed_source_tiers` | `;`-separated source tiers supporting safe citation |",
        "| `should_abstain` | `true` or `false` |",
        "| `confidence` | `high`, `medium`, or `low` |",
        "| `rationale_code` | compact reason code for the route decision |",
        "| `labeler` | reviewer id or initials |",
        "",
    ]
    for column in COUNT_COLUMNS:
        lines.extend(table(f"Workset Distribution: `{column}`", count_column(rows, column), limit=12))
        lines.append("")
    lines.extend(
        [
            "## After Filling",
            "",
            "1. Run `scripts/check_route_review_progress.py` on the private CSV.",
            "2. Import with `scripts/import_route_review_csv.py` into a private audit pack.",
            "3. Validate with `scripts/validate_route_audit.py --require-complete`.",
            "4. Promote qid-only labels only after validation has zero errors.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--report-out", type=Path)
    args = parser.parse_args()

    report = render_brief(csv_path=args.csv, rows=load_csv(args.csv))
    if args.report_out:
        args.report_out.parent.mkdir(parents=True, exist_ok=True)
        args.report_out.write_text(report, encoding="utf-8")
    else:
        print(report)


if __name__ == "__main__":
    main()
