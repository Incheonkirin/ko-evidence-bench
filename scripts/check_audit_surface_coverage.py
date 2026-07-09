#!/usr/bin/env python3
"""Check whether a human-audit workset covers intent/surface stress axes."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ko_evidence_bench.audit_coverage import audit_surface_coverage  # noqa: E402
from ko_evidence_bench.metrics import load_jsonl  # noqa: E402


def pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def display_path(path: Path, *, external_label: str) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(ROOT))
    except ValueError:
        return external_label


def counter(rows: list[dict[str, Any]], key: str) -> Counter[str]:
    counts: Counter[str] = Counter()
    for row in rows:
        if key == "trap_classes":
            for value in row.get("trap_classes") or ["<none>"]:
                counts[str(value)] += 1
        else:
            counts[str(row.get(key) or "<missing>")] += 1
    return counts


def qrels_for_audit(qrels: list[dict[str, Any]], audit_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_qid = {str(row["qid"]): row for row in qrels}
    return [by_qid[str(row["qid"])] for row in audit_rows if str(row.get("qid")) in by_qid]


def count_table(title: str, rows: list[dict[str, Any]], key: str) -> list[str]:
    counts = counter(rows, key)
    total = sum(counts.values())
    lines = [f"## {title}", "", "| value | sampled rows | share |", "|---|---:|---:|"]
    for value, count in counts.most_common():
        lines.append(f"| `{value}` | {count} | {pct(count / total if total else 0.0)} |")
    return lines


def render_report(
    *,
    qrels_path: Path,
    audit_path: Path,
    qrels: list[dict[str, Any]],
    audit_rows: list[dict[str, Any]],
    title: str,
    label_status: str,
) -> str:
    coverage = audit_surface_coverage(qrels, audit_rows)
    sampled = qrels_for_audit(qrels, audit_rows)
    status = "PASS" if coverage.complete else "INCOMPLETE"
    lines = [
        f"# {title}",
        "",
        f"Status: **{status}**.",
        "",
        "This report checks whether a human-audit workset covers the same",
        "qid-only intent family, surface-form, and trap-class axes used by the",
        "retrieval diagnostics. It contains aggregate counts only and does not",
        "include qids, raw queries, context, reviewer notes, source names, URLs,",
        "or evidence ids.",
        "",
        "## Inputs",
        "",
        f"- qrels: `{display_path(qrels_path, external_label='private-surface-qrels')}`",
        f"- audit workset: `{display_path(audit_path, external_label='private-audit-workset')}`",
        f"- qrel rows: {coverage.qrel_rows}",
        f"- audit rows: {coverage.audit_rows}",
        f"- matched audit rows: {coverage.matched_rows}",
        f"- unmatched audit rows: {coverage.unmatched_audit_rows}",
        f"- label status: {label_status}",
        "",
        "## Coverage Summary",
        "",
        "| axis | full values | sampled values | missing values | min sampled rows | max sampled rows | status |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for item in coverage.slices:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{item.name}`",
                    str(item.full_values),
                    str(item.sampled_values),
                    str(len(item.missing_values)),
                    str(item.min_sampled_rows),
                    str(item.max_sampled_rows),
                    "`PASS`" if item.complete else "`MISSING`",
                ]
            )
            + " |"
        )
    lines.append("")
    lines.extend(count_table("Sampled Surface Distribution", sampled, "surface_form"))
    lines.append("")
    lines.extend(count_table("Sampled Intent-Family Distribution", sampled, "intent_family"))
    lines.append("")
    lines.extend(count_table("Sampled Trap-Class Distribution", sampled, "trap_classes"))
    lines.extend(
        [
            "",
            "## Use Notes",
            "",
            "- This is a coverage check for the audit workset, not evidence that the",
            "  labels have been completed.",
            "- Public headline claims still require completed independent labels,",
            "  agreement evidence, adjudication, and validation.",
            "- If an axis is incomplete, rebuild or supplement the private audit pack",
            "  before spending reviewer time.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--qrels", type=Path, default=ROOT / "fixtures" / "surface_qrels.jsonl")
    parser.add_argument("--audit", type=Path, default=ROOT / "fixtures" / "route_audit" / "surface_audit_seed.jsonl")
    parser.add_argument("--out", type=Path, default=ROOT / "reports" / "audit_surface_coverage_fixture.md")
    parser.add_argument("--title", default="Audit Surface Coverage Fixture")
    parser.add_argument("--label-status", default="synthetic audit coverage fixture")
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()

    qrels = load_jsonl(args.qrels)
    audit_rows = load_jsonl(args.audit)
    report = render_report(
        qrels_path=args.qrels,
        audit_path=args.audit,
        qrels=qrels,
        audit_rows=audit_rows,
        title=args.title,
        label_status=args.label_status,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(report, encoding="utf-8")
    print(report)

    if args.require_complete and not audit_surface_coverage(qrels, audit_rows).complete:
        raise SystemExit("audit surface coverage is incomplete")


if __name__ == "__main__":
    main()
