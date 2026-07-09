#!/usr/bin/env python3
"""Export private source-route silver labels and aggregate-only reports."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ko_evidence_bench.route_labels import (  # noqa: E402
    always_policy_baseline,
    derive_route_label,
    route_floor,
    summarize_route_labels,
)


def pct(value: float) -> str:
    return f"{100 * value:.1f}%"


def load_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def table_from_counts(title: str, counts: dict[str, int]) -> list[str]:
    total = sum(counts.values())
    lines = [
        f"## {title}",
        "",
        "| value | count | share |",
        "|---|---:|---:|",
    ]
    for key, value in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
        share = value / total if total else 0.0
        lines.append(f"| `{key}` | {value} | {pct(share)} |")
    return lines


def render_report(labels: list[dict], *, source_path: Path, labels_out: Path | None) -> str:
    summary = summarize_route_labels(labels)
    always = always_policy_baseline(labels)
    majority = route_floor(labels)

    lines = [
        "# Private Source-Route Silver Label Summary",
        "",
        "This report is generated from private qrel metadata. It contains only",
        "aggregate counts and baseline rates. It does not include qids, raw",
        "queries, conversation snippets, platform identifiers, or ranked documents.",
        "",
        f"- source rows: {len(labels)}",
        f"- private qrels path: `{source_path.name}`",
        f"- private label export: `{labels_out.name if labels_out else 'not written'}`",
        "- label status: silver proxy, not human-gold",
        "",
        "## Baseline Context",
        "",
        "| baseline | metric | value |",
        "|---|---|---:|",
        f"| always_policy | route_accuracy | {pct(always['route_accuracy'])} |",
        f"| always_policy | abstention_recall | {pct(always['abstention_recall'])} |",
        f"| majority_route_floor | route_accuracy | {pct(majority['route_accuracy'])} |",
        "",
        "The majority-route floor is not a deployable system. It only shows how much",
        "label skew a real source router must beat.",
        "",
    ]
    lines.extend(table_from_counts("Route Label Counts", dict(summary["route_gold"])))
    lines.append("")
    lines.extend(table_from_counts("Abstention Counts", dict(summary["should_abstain"])))
    lines.append("")
    lines.extend(table_from_counts("Confidence Counts", dict(summary["confidence"])))
    lines.append("")
    lines.extend(table_from_counts("Rationale Counts", dict(summary["rationale_code"])))
    lines.extend(
        [
            "",
            "## Use Notes",
            "",
            "- These labels are derived from qrel metadata and must be audited before headline claims.",
            "- Public metrics may cite these counts as private-lab inventory, not as final benchmark gold.",
            "- The next gate is double-labeling at least 50 rows and adjudicating disagreements.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--qrels", type=Path, required=True)
    parser.add_argument("--labels-out", type=Path)
    parser.add_argument("--report-out", type=Path)
    args = parser.parse_args()

    rows = load_jsonl(args.qrels)
    labels = [derive_route_label(row) for row in rows]

    if args.labels_out:
        write_jsonl(args.labels_out, labels)
    report = render_report(labels, source_path=args.qrels, labels_out=args.labels_out)
    if args.report_out:
        args.report_out.parent.mkdir(parents=True, exist_ok=True)
        args.report_out.write_text(report, encoding="utf-8")
    else:
        print(report, end="")


if __name__ == "__main__":
    main()
