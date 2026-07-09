#!/usr/bin/env python3
"""Build the public system-comparison matrix report."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ko_evidence_bench.system_matrix import (  # noqa: E402
    load_matrix,
    matrix_summary,
    status_label,
    system_rows,
    validate_matrix,
)


def display_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(ROOT))
    except ValueError:
        return resolved.name


def render_report(matrix_path: Path, *, root: Path = ROOT) -> str:
    matrix = load_matrix(matrix_path)
    issues = validate_matrix(matrix, root=root)
    summary = matrix_summary(matrix)
    status = status_label(matrix, issues)

    lines = [
        "# System Matrix Report",
        "",
        f"Status: **{status} for full comparison matrix**.",
        "",
        str(matrix.get("status_note") or "diagnostic coverage only"),
        "",
        "This report tracks which retrieval, routing, surface, and label-gate",
        "systems are actually backed by checked-in evidence. It prevents the",
        "repo from implying that the full analyzer/dense/hybrid/reranker matrix",
        "has already been run.",
        "",
        "## Summary",
        "",
        "| item | value |",
        "|---|---:|",
        f"| matrix systems | {summary['systems']} |",
        f"| implemented systems | {summary['implemented']} |",
        f"| not-run systems | {summary['not_run']} |",
        f"| blocked systems | {summary['blocked']} |",
        f"| system families | {summary['families']} |",
        f"| implemented diagnostic rows | {summary['implemented_rows']} |",
        "",
        "## Matrix",
        "",
        "| system | family | stage | status | rows | claim scope | evidence |",
        "|---|---|---|---|---:|---|---|",
    ]
    for row in system_rows(matrix):
        evidence = str(row.get("evidence") or "")
        evidence_cell = f"`{evidence}`" if evidence else "`not yet run`"
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{row['system_id']}`",
                    f"`{row['family']}`",
                    f"`{row['stage']}`",
                    f"`{row['current_status']}`",
                    str(int(row["rows"])),
                    f"`{row['claim_scope']}`",
                    evidence_cell,
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Missing For Full Matrix",
            "",
        ]
    )
    missing = summary["missing_full_matrix"]
    if missing:
        lines.extend(f"- `{system_id}`" for system_id in missing)
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Validation",
            "",
            f"- manifest: `{display_path(matrix_path)}`",
            f"- validation issues: {len(issues)}",
        ]
    )
    if issues:
        for issue in issues:
            lines.append(f"- `{issue.system_id}` / `{issue.field}`: {issue.message}")

    lines.extend(
        [
            "",
            "## Use Notes",
            "",
            "- `implemented` means an aggregate public report exists; it does not mean",
            "  the result is human-gold or headline-ready.",
            "- `not_run` systems are explicit gaps in the full comparison matrix.",
            "- `blocked` systems depend on human labels or other external evidence.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--matrix", type=Path, default=ROOT / "docs" / "system_matrix.json")
    parser.add_argument("--out", type=Path, default=ROOT / "reports" / "system_matrix.md")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    report = render_report(args.matrix)
    if args.check:
        current = args.out.read_text(encoding="utf-8") if args.out.exists() else ""
        if current != report:
            print("system matrix report is stale; run scripts/build_system_matrix_report.py")
            return 1
        print("system matrix report is current")
        return 0

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(report, encoding="utf-8")
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
