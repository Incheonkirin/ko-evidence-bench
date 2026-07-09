#!/usr/bin/env python3
"""Mine trap-class candidates from the public probe queries."""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ko_evidence_bench.metrics import load_jsonl  # noqa: E402
from ko_evidence_bench.trap_miner import compare_probe_traps, summarize_trap_rows  # noqa: E402


def pct(num: int, den: int) -> str:
    return f"{100 * (num / den if den else 0.0):.1f}%"


def display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def counter_table(title: str, counter: Counter[str]) -> list[str]:
    lines = [f"## {title}", "", "| value | rows |", "|---|---:|"]
    if not counter:
        lines.append("| none | 0 |")
        return lines
    for value, count in sorted(counter.items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"| `{value}` | {count} |")
    return lines


def nested_counter_table(title: str, nested: dict[str, Counter[str]]) -> list[str]:
    lines = [f"## {title}", "", "| slice | top detected traps |", "|---|---|"]
    for value, counter in sorted(nested.items()):
        top = ", ".join(f"`{name}:{count}`" for name, count in counter.most_common(4))
        lines.append(f"| `{value}` | {top or 'none'} |")
    return lines


def list_cell(values: list[str]) -> str:
    return ", ".join(f"`{value}`" for value in values) if values else "none"


def render_report(probe_dir: Path) -> str:
    queries = load_jsonl(probe_dir / "queries.jsonl")
    qrels = load_jsonl(probe_dir / "qrels.jsonl")
    rows = compare_probe_traps(queries, qrels)
    summary: dict[str, Any] = summarize_trap_rows(rows)

    total = int(summary["rows"])
    lines = [
        "# Public Probe Trap Mining",
        "",
        "Status: **synthetic probe diagnostics only; not analyzer-specific benchmark results**.",
        "",
        "This report mines trap-class candidates from public synthetic probe",
        "queries and compares them with the checked-in qrel annotations. It is",
        "a diagnostic dry run for failure mining, not a synonym dictionary",
        "or user-dictionary recommendation.",
        "",
        "## Inputs",
        "",
        f"- probe dir: `{display_path(probe_dir)}`",
        f"- query rows: {len(queries)}",
        f"- qrel rows: {len(qrels)}",
        "- label status: synthetic public fixture",
        "",
        "## Coverage",
        "",
        "| item | value |",
        "|---|---:|",
        f"| rows | {total} |",
        f"| rows with any detection | {summary['rows_with_any_detection']} ({pct(summary['rows_with_any_detection'], total)}) |",
        f"| rows with all expected traps detected | {summary['rows_with_full_expected_cover']} ({pct(summary['rows_with_full_expected_cover'], total)}) |",
        f"| rows with extra diagnostic traps | {summary['rows_with_extra']} ({pct(summary['rows_with_extra'], total)}) |",
        "",
    ]
    lines.extend(counter_table("Expected Trap Classes", summary["expected"]))
    lines.append("")
    lines.extend(counter_table("Detected Trap Classes", summary["detected"]))
    lines.append("")
    lines.extend(counter_table("Matched Trap Classes", summary["matched"]))
    lines.append("")
    lines.extend(counter_table("Missed Trap Classes", summary["missed"]))
    lines.append("")
    lines.extend(counter_table("Extra Diagnostic Traps", summary["extra"]))
    lines.append("")
    lines.extend(counter_table("Diagnostic Layers", summary["layers"]))
    lines.append("")
    lines.extend(nested_counter_table("Detected Traps By Surface Form", summary["by_surface"]))
    lines.append("")
    lines.extend(nested_counter_table("Detected Traps By Intent Family", summary["by_family"]))
    lines.extend(
        [
            "",
            "## Row Audit",
            "",
            "| qid | expected | detected | missed | extra | layers |",
            "|---|---|---|---|---|---|",
        ]
    )
    for row in rows:
        lines.append(
            "| "
            f"`{row['qid']}` | "
            f"{list_cell(row['expected_traps'])} | "
            f"{list_cell(row['detected_traps'])} | "
            f"{list_cell(row['missed_traps'])} | "
            f"{list_cell(row['extra_traps'])} | "
            f"{list_cell(row['diagnostic_layers'])} |"
        )

    lines.extend(
        [
            "",
            "## Use Notes",
            "",
            "- This report proves the trap-mining path on public synthetic rows only.",
            "- Extra traps are diagnostic hypotheses; they do not rewrite qrels by themselves.",
            "- Missed traps are useful regression targets for future analyzer-specific miners.",
            "- Private query logs can use the same aggregate report shape while keeping raw text outside the repository.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--probe-dir", type=Path, default=ROOT / "probes" / "ko_evidence_probe_v0")
    parser.add_argument("--out", type=Path, default=ROOT / "reports" / "probe_trap_mining.md")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    report = render_report(args.probe_dir)
    if args.check:
        current = args.out.read_text(encoding="utf-8") if args.out.exists() else ""
        if current != report:
            print("probe trap mining report is stale; run scripts/reproduce_probe_trap_mining.py")
            return 1
        print("probe trap mining report is current")
        return 0

    args.out.write_text(report, encoding="utf-8")
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
