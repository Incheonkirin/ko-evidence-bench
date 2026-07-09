#!/usr/bin/env python3
"""Reproduce the public surface-fragmentation audit."""

from __future__ import annotations

import argparse
import math
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ko_evidence_bench.metrics import load_jsonl  # noqa: E402
from ko_evidence_bench.surface_fragmentation import (  # noqa: E402
    audit_surface_fragmentation,
    summarize_fragmentation_rows,
)


def pct(value: float) -> str:
    return f"{100 * value:.1f}%"


def factor(value: float) -> str:
    return "inf" if math.isinf(value) else f"{value:.1f}x"


def display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def counter_inline(counter: Counter[str]) -> str:
    if not counter:
        return "none"
    return ", ".join(f"`{key}:{value}`" for key, value in counter.most_common())


def list_cell(values: list[str]) -> str:
    return ", ".join(f"`{value}`" for value in values) if values else "none"


def render_report(*, queries_path: Path, qrels_path: Path, title: str) -> str:
    queries = load_jsonl(queries_path)
    qrels = load_jsonl(qrels_path)
    rows = audit_surface_fragmentation(queries, qrels)
    summary: dict[str, Any] = summarize_fragmentation_rows(rows)

    lines = [
        f"# {title}",
        "",
        "Status: **public fixture diagnostic; not a production synonym list**.",
        "",
        "This report tests the failure mode behind naive query-log counting:",
        "one exact lexical seed can miss other surface forms of the same intent.",
        "The checked qrels define intent membership; the surface rules only measure",
        "how much seed-only counting misses.",
        "",
        "## Inputs",
        "",
        f"- queries: `{display_path(queries_path)}`",
        f"- qrels: `{display_path(qrels_path)}`",
        f"- audited intents: {summary['intents']}",
        f"- qrel rows in audited intents: {summary['qrel_rows']}",
        "- label status: synthetic public fixture",
        "",
        "## Summary",
        "",
        "| item | value |",
        "|---|---:|",
        f"| qrel intent rows | {summary['qrel_rows']} |",
        f"| exact-seed rows | {summary['seed_rows']} |",
        f"| expanded-surface rows | {summary['expanded_rows']} |",
        f"| exact-seed recall | {pct(summary['seed_recall'])} |",
        f"| expanded-surface recall | {pct(summary['expanded_recall'])} |",
        f"| aggregate undercount factor | {factor(summary['undercount_factor'])} |",
        f"| max per-intent undercount factor | {factor(summary['max_undercount_factor'])} |",
        "",
        "## Per-Intent Audit",
        "",
        (
            "| intent | seed condition | qrel rows | seed rows | expanded rows | "
            "seed recall | undercount | missed surfaces |"
        ),
        "|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{row['intent_id']}`",
                    row["seed_description"],
                    str(row["qrel_rows"]),
                    str(row["seed_rows"]),
                    str(row["expanded_rows"]),
                    pct(row["seed_recall"]),
                    factor(row["undercount_factor"]),
                    counter_inline(row["missed_surface_counts"]),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Missed Rows By Intent",
            "",
            "| intent | missed by exact seed | missed by expanded rule |",
            "|---|---|---|",
        ]
    )
    for row in rows:
        lines.append(
            f"| `{row['intent_id']}` | {list_cell(row['missed_by_seed'])} | "
            f"{list_cell(row['missed_by_expanded'])} |"
        )

    lines.extend(
        [
            "",
            "## Surface Distribution",
            "",
            "| surface form | qrel rows | missed by exact seed |",
            "|---|---:|---:|",
        ]
    )
    all_surfaces = sorted(
        set(summary["surface_counts"]).union(set(summary["missed_surface_counts"]))
    )
    for surface in all_surfaces:
        lines.append(
            f"| `{surface}` | {summary['surface_counts'].get(surface, 0)} | "
            f"{summary['missed_surface_counts'].get(surface, 0)} |"
        )

    lines.extend(
        [
            "",
            "## Use Notes",
            "",
            "- This is an audit of counting bias, not a query rewrite system.",
            "- Expanded-surface rules are evaluated against qrels; they are not shipped as production synonyms.",
            "- Private query logs can reuse the same report shape with qid-only outputs and aggregate surface counts.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--queries", type=Path, default=ROOT / "probes" / "ko_evidence_probe_v0" / "queries.jsonl")
    parser.add_argument("--qrels", type=Path, default=ROOT / "probes" / "ko_evidence_probe_v0" / "qrels.jsonl")
    parser.add_argument("--out", type=Path, default=ROOT / "reports" / "surface_fragmentation_audit.md")
    parser.add_argument("--title", default="Surface Fragmentation Audit")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    report = render_report(queries_path=args.queries, qrels_path=args.qrels, title=args.title)
    if args.check:
        current = args.out.read_text(encoding="utf-8") if args.out.exists() else ""
        if current != report:
            print("surface fragmentation audit is stale; run scripts/reproduce_surface_fragmentation_audit.py")
            return 1
        print("surface fragmentation audit is current")
        return 0

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(report, encoding="utf-8")
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
