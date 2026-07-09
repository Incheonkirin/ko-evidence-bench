#!/usr/bin/env python3
"""Render a source-tier catalog coverage report."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ko_evidence_bench.metrics import load_jsonl  # noqa: E402
from ko_evidence_bench.source_catalog import load_source_catalog, source_coverage  # noqa: E402


def display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def render_report(*, catalog_path: Path, qrels_path: Path, evidence_path: Path) -> str:
    catalog = load_source_catalog(catalog_path)
    qrels = load_jsonl(qrels_path)
    evidence = load_jsonl(evidence_path)
    coverage = source_coverage(catalog=catalog, qrels=qrels, evidence=evidence)
    status = coverage.status
    lines = [
        "# Source Catalog Coverage",
        "",
        f"Status: **{status} source-tier catalog fixture**.",
        "",
        "This report checks that the evaluation is not policy-clause-only. It",
        "joins the source-tier catalog with public probe qrels and synthetic",
        "evidence snippets, then verifies that each demanded searchable source",
        "tier has fixture evidence. It is not proof that private source corpora",
        "are complete.",
        "",
        "## Inputs",
        "",
        f"- source catalog: `{display_path(catalog_path)}`",
        f"- qrels: `{display_path(qrels_path)}`",
        f"- evidence: `{display_path(evidence_path)}`",
        f"- qrel rows: {coverage.qrel_rows}",
        f"- evidence rows: {coverage.evidence_rows}",
        f"- validation issues: {len(coverage.issues)}",
        "",
        "## Source-Tier Coverage",
        "",
        "| source tier | route-demand rows | allowed-support rows | evidence snippets | sufficient refs | public fixture | private status | headline status | gate |",
        "|---|---:|---:|---:|---:|---|---|---|---|",
    ]
    for row in coverage.rows:
        lines.append(
            "| "
            f"`{row.source_tier}` | "
            f"{row.route_demand_rows} | "
            f"{row.allowed_support_rows} | "
            f"{row.evidence_rows} | "
            f"{row.sufficient_refs} | "
            f"`{row.public_probe_status}` | "
            f"`{row.private_status}` | "
            f"`{row.headline_status}` | "
            f"`{row.gate_status}` |"
        )

    lines.extend(
        [
            "",
            "## Search Role Catalog",
            "",
            "| source tier | role | search target |",
            "|---|---|---|",
        ]
    )
    for row in coverage.rows:
        lines.append(f"| `{row.source_tier}` | {row.role} | {row.search_target} |")

    if coverage.issues:
        lines.extend(["", "## Validation Issues", ""])
        for issue in coverage.issues:
            lines.append(f"- `{issue.source_tier}` `{issue.field}`: {issue.message}")

    lines.extend(
        [
            "",
            "## Use Notes",
            "",
            "- This is a source-routing coverage gate, not a corpus acquisition claim.",
            "- `human_context_needed` and `out_of_scope` are abstention routes, not searchable corpora.",
            "- Private reports may reuse this shape with aggregate inventory counts only.",
            "- Keep raw source names, URLs, and document text outside public reports.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", type=Path, default=ROOT / "docs" / "source_catalog.json")
    parser.add_argument("--qrels", type=Path, default=ROOT / "probes" / "ko_evidence_probe_v0" / "qrels.jsonl")
    parser.add_argument("--evidence", type=Path, default=ROOT / "probes" / "ko_evidence_probe_v0" / "evidence.jsonl")
    parser.add_argument("--out", type=Path, default=ROOT / "reports" / "source_catalog_coverage.md")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    report = render_report(catalog_path=args.catalog, qrels_path=args.qrels, evidence_path=args.evidence)
    if args.check:
        current = args.out.read_text(encoding="utf-8") if args.out.exists() else ""
        if current != report:
            print("source catalog report is stale; run scripts/build_source_catalog_report.py")
            return 1
        if "Status: **PASS" not in report:
            print("source catalog report has validation issues")
            return 1
        print("source catalog report is current")
        return 0

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(report, encoding="utf-8")
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
