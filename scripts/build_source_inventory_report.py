#!/usr/bin/env python3
"""Render private source inventory readiness from aggregate demand."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ko_evidence_bench.source_inventory import (  # noqa: E402
    load_source_inventory,
    source_inventory_readiness,
)


def display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def fmt_count(value: int | None) -> str:
    return "n/a" if value is None else f"{value:,}"


def render_report(*, inventory_path: Path, route_label_report_path: Path) -> str:
    inventory = load_source_inventory(inventory_path)
    route_report = route_label_report_path.read_text(encoding="utf-8")
    result = source_inventory_readiness(inventory=inventory, route_label_report=route_report)
    lines = [
        "# Source Inventory Readiness",
        "",
        f"Status: **{result.status} for private source inventory**.",
        "",
        "This report joins aggregate private route-label demand with a generic",
        "source inventory manifest. It contains no raw source names, URLs,",
        "queries, document text, or evidence ids.",
        "",
        "It is deliberately stricter than the public source catalog: a source tier",
        "can be part of the evaluation design while still being blocked for",
        "headline claims until its private inventory and rights status are audited.",
        "",
        "## Inputs",
        "",
        f"- inventory manifest: `{display_path(inventory_path)}`",
        f"- route-demand report: `{display_path(route_label_report_path)}`",
        f"- aggregate demand rows: {result.total_demand_rows}",
        f"- validation issues: {len(result.issues)}",
        f"- blocked searchable tiers: {len(result.blocked_tiers)}",
        "",
        "## Readiness By Source Tier",
        "",
        "| source tier | private route demand | inventory records | inventory status | rights status | public release | readiness |",
        "|---|---:|---:|---|---|---|---|",
    ]
    for row in result.rows:
        lines.append(
            "| "
            f"`{row.source_tier}` | "
            f"{row.demand_rows:,} | "
            f"{fmt_count(row.record_count)} | "
            f"`{row.inventory_status}` | "
            f"`{row.rights_status}` | "
            f"`{row.public_release}` | "
            f"`{row.readiness}` |"
        )

    lines.extend(
        [
            "",
            "## Blockers",
            "",
        ]
    )
    blocked = [row for row in result.rows if row.readiness == "BLOCKED"]
    if blocked:
        for row in blocked:
            lines.append(
                f"- `{row.source_tier}` has {row.demand_rows:,} silver-demand rows, "
                f"but inventory status is `{row.inventory_status}` with "
                f"{fmt_count(row.record_count)} verified records."
            )
    else:
        lines.append("- None.")

    if result.issues:
        lines.extend(["", "## Validation Issues", ""])
        for issue in result.issues:
            lines.append(f"- `{issue.source_tier}` `{issue.field}`: {issue.message}")

    lines.extend(
        [
            "",
            "## Use Notes",
            "",
            "- This is an inventory-readiness gate, not a source acquisition script.",
            "- `READY` means the tier has aggregate private inventory for diagnostics, not public redistributable data.",
            "- `BLOCKED` tiers can remain in the route taxonomy, but headline claims should name the inventory gap.",
            "- `human_context_needed` and `out_of_scope` are abstention/filtering routes, not searchable corpora.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inventory", type=Path, default=ROOT / "docs" / "source_inventory.json")
    parser.add_argument(
        "--route-label-report",
        type=Path,
        default=ROOT / "reports" / "private_route_label_summary.md",
    )
    parser.add_argument("--out", type=Path, default=ROOT / "reports" / "source_inventory_readiness.md")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    report = render_report(inventory_path=args.inventory, route_label_report_path=args.route_label_report)
    if args.check:
        current = args.out.read_text(encoding="utf-8") if args.out.exists() else ""
        if current != report:
            print("source inventory report is stale; run scripts/build_source_inventory_report.py")
            return 1
        if "Status: **INVALID" in report:
            print("source inventory report has validation issues")
            return 1
        print("source inventory report is current")
        return 0

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(report, encoding="utf-8")
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
