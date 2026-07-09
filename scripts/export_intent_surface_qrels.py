#!/usr/bin/env python3
"""Export qid-only intent/surface qrels from private qrels and route labels."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ko_evidence_bench.intent_surface_export import export_surface_qrels, summarize_export  # noqa: E402
from ko_evidence_bench.intent_inventory import pct  # noqa: E402


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def counter_table(title: str, counter: Counter[str]) -> list[str]:
    total = sum(counter.values())
    lines = [f"## {title}", "", "| value | count | share |", "|---|---:|---:|"]
    for key, value in counter.most_common():
        lines.append(f"| `{key}` | {value} | {pct(value, total)} |")
    return lines


def render_report(records: list[dict[str, Any]], stats: dict[str, int], *, qrels_out: Path | None) -> str:
    summary = summarize_export(records, stats)
    lines = [
        "# Private Intent/Surface Qrel Export Summary",
        "",
        "This report summarizes a qid-only private export. It does not include",
        "qids, raw queries, source names, conversation snippets, usernames, URLs,",
        "or source file paths.",
        "",
        "- label status: silver intent/surface metadata, not human-gold",
        f"- source qrel rows: {summary['qrel_rows']}",
        f"- source route-label rows: {summary['route_label_rows']}",
        f"- exported qid-only rows: {summary['exported_rows']}",
        f"- missing route labels: {summary.get('missing_route_label', 0)}",
        f"- answerable rows without evidence ids: {summary.get('answerable_without_evidence_ids', 0)}",
        f"- private qid-only export: `{qrels_out.name if qrels_out else 'not written'}`",
        "",
    ]
    lines.extend(counter_table("Intent Family Counts", summary["intent_family"]))  # type: ignore[arg-type]
    lines.append("")
    lines.extend(counter_table("Surface Form Counts", summary["surface_form"]))  # type: ignore[arg-type]
    lines.append("")
    lines.extend(counter_table("Route Counts", summary["route_gold"]))  # type: ignore[arg-type]
    lines.append("")
    lines.extend(counter_table("Trap-Class Counts", summary["trap_classes"]))  # type: ignore[arg-type]
    lines.extend(
        [
            "",
            "## Use Notes",
            "",
            "- This export creates benchmark metadata for slicing; it is not a claim",
            "  that intent families are final human labels.",
            "- Human adjudication should review route labels and metadata before any",
            "  public headline result uses these slices.",
            "- The qid-only export stays private because stable ids can link back to",
            "  private worksets.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--qrels", type=Path, required=True)
    parser.add_argument("--route-labels", type=Path, required=True)
    parser.add_argument("--qrels-out", type=Path)
    parser.add_argument("--report-out", type=Path, required=True)
    args = parser.parse_args()

    qrels = load_jsonl(args.qrels)
    route_labels = load_jsonl(args.route_labels)
    records, stats = export_surface_qrels(qrels, route_labels)

    if args.qrels_out:
        write_jsonl(args.qrels_out, records)

    report = render_report(records, stats, qrels_out=args.qrels_out)
    args.report_out.parent.mkdir(parents=True, exist_ok=True)
    args.report_out.write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
