#!/usr/bin/env python3
"""Build an aggregate-only intent-family inventory report."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ko_evidence_bench.intent_inventory import aggregate_inventory, format_counter, pct  # noqa: E402
from ko_evidence_bench.metrics import load_jsonl  # noqa: E402


def display_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(ROOT))
    except ValueError:
        return resolved.name


def counter_table(title: str, counter: dict[str, int]) -> list[str]:
    total = sum(counter.values())
    lines = [f"## {title}", "", "| value | count | share |", "|---|---:|---:|"]
    for key, value in sorted(counter.items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"| `{key}` | {value} | {pct(value, total)} |")
    return lines


def completeness_table(counter: dict[str, int], *, total_rows: int) -> list[str]:
    lines = ["## Metadata Completeness", "", "| field | present | missing | completeness |", "|---|---:|---:|---:|"]
    for field in ("intent_family", "intent_id", "surface_form"):
        present = counter.get(f"present_{field}", 0)
        missing = counter.get(f"missing_{field}", 0)
        lines.append(f"| `{field}` | {present} | {missing} | {pct(present, total_rows)} |")
    return lines


def render_report(*, qrels_path: Path, qrels: list[dict], label_status: str) -> str:
    inv = aggregate_inventory(qrels)
    n = int(inv["n"])
    lines = [
        "# Intent-Family Inventory Fixture",
        "",
        "This report summarizes intent families, source-route labels, surface",
        "conditions, and trap annotations without exposing qids, raw queries,",
        "conversation snippets, source names, or platform identifiers.",
        "",
        "Intent families are the organizing unit. Surface forms and trap classes",
        "are annotations used to slice retrieval failures.",
        "",
        "## Inputs",
        "",
        f"- qrels: `{display_path(qrels_path)}`",
        f"- rows: {n}",
        f"- label status: {label_status}",
        "",
        "## Intent Family Summary",
        "",
        (
            "| intent family | rows | share | intents | surfaces | abstain rows | "
            "top routes | top surfaces | top traps |"
        ),
        "|---|---:|---:|---:|---:|---:|---|---|---|",
    ]
    for row in inv["family_rows"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{row['intent_family']}`",
                    str(row["rows"]),
                    pct(row["rows"], n),
                    str(row["intent_count"]),
                    str(row["surface_count"]),
                    str(row["abstain_rows"]),
                    f"`{format_counter(row['route_counts'])}`",
                    f"`{format_counter(row['surface_counts'])}`",
                    f"`{format_counter(row['trap_counts'])}`",
                ]
            )
            + " |"
        )
    lines.append("")
    lines.extend(counter_table("Route Distribution", inv["route_gold"]))
    lines.append("")
    lines.extend(counter_table("Surface Distribution", inv["surface_form"]))
    lines.append("")
    lines.extend(counter_table("Trap-Class Distribution", inv["trap_classes"]))
    lines.append("")
    lines.extend(completeness_table(inv["metadata_completeness"], total_rows=n))
    lines.extend(
        [
            "",
            "## Use Notes",
            "",
            "- Private qrels can reuse this report after replacing raw query text with",
            "  stable ids and audited metadata.",
            "- `intent_family` should be assigned before making public frequency claims.",
            "- Trap classes are diagnostic slices; they are not the benchmark's",
            "  organizing unit.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--qrels", type=Path, default=ROOT / "fixtures" / "surface_qrels.jsonl")
    parser.add_argument("--out", type=Path, default=ROOT / "reports" / "intent_inventory_fixture.md")
    parser.add_argument("--label-status", default="synthetic fixture metadata")
    args = parser.parse_args()

    qrels = load_jsonl(args.qrels)
    report = render_report(qrels_path=args.qrels, qrels=qrels, label_status=args.label_status)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
