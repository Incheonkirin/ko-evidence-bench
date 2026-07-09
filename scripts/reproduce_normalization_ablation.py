#!/usr/bin/env python3
"""Compare raw-surface and normalized/expanded retrieval runs."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ko_evidence_bench.ablation import (  # noqa: E402
    compare_runs,
    grouped_comparison,
    rescue_route_counts,
    summarize_comparison,
    trap_comparison,
)
from ko_evidence_bench.metrics import load_jsonl  # noqa: E402


def pct(value: float) -> str:
    return f"{100 * value:.1f}%"


def display_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(ROOT))
    except ValueError:
        return resolved.name


def comparison_table(title: str, rows: list[dict[str, float | str]]) -> list[str]:
    lines = [
        f"## {title}",
        "",
        "| slice | n | baseline | candidate | lift | rescued | regressed |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{row['value']}`",
                    str(int(float(row["n"]))),
                    pct(float(row["baseline_success_rate"])),
                    pct(float(row["candidate_success_rate"])),
                    pct(float(row["lift"])),
                    str(int(float(row["rescued_rows"]))),
                    str(int(float(row["regressed_rows"]))),
                ]
            )
            + " |"
        )
    return lines


def route_count_table(counts: dict[str, int]) -> list[str]:
    total = sum(counts.values())
    lines = ["## Rescued Route Distribution", "", "| route | rescued rows | share |", "|---|---:|---:|"]
    if not counts:
        lines.append("| _(none)_ | 0 | 0.0% |")
        return lines
    for route, count in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"| `{route}` | {count} | {pct(count / total if total else 0.0)} |")
    return lines


def render_report(
    *,
    qrels_path: Path,
    baseline_path: Path,
    candidate_path: Path,
    qrels: list[dict],
    baseline_rows: list[dict],
    candidate_rows: list[dict],
    baseline_name: str,
    candidate_name: str,
    k: int,
    label_status: str,
) -> str:
    rows = compare_runs(qrels, baseline_rows, candidate_rows, k=k)
    summary = summarize_comparison(rows)
    lines = [
        "# Normalization Ablation Fixture",
        "",
        "This report compares a raw-surface baseline run with a normalized or",
        "expanded candidate run. It reports aggregate rescue and regression counts",
        "only; it does not include qids, raw queries, source names, conversation",
        "snippets, or platform identifiers.",
        "",
        "The public fixture treats `surface_robust_demo` as the normalized/expanded",
        "candidate. Private experiments can replace the two run files with raw and",
        "normalized retrieval outputs over the same qrels.",
        "",
        "## Inputs",
        "",
        f"- qrels: `{display_path(qrels_path)}`",
        f"- baseline run: `{display_path(baseline_path)}`",
        f"- candidate run: `{display_path(candidate_path)}`",
        f"- baseline name: `{baseline_name}`",
        f"- candidate name: `{candidate_name}`",
        f"- label status: {label_status}",
        f"- k: {k}",
        "",
        "## Overall Lift",
        "",
        "| metric | value |",
        "|---|---:|",
        f"| rows | {int(summary['n'])} |",
        f"| baseline task success | {pct(summary['baseline_success_rate'])} |",
        f"| candidate task success | {pct(summary['candidate_success_rate'])} |",
        f"| net lift | {pct(summary['lift'])} |",
        f"| rescued rows | {int(summary['rescued_rows'])} |",
        f"| regressed rows | {int(summary['regressed_rows'])} |",
        "",
    ]
    lines.extend(comparison_table("Lift By Intent Family", grouped_comparison(rows, "intent_family")))
    lines.append("")
    lines.extend(comparison_table("Lift By Surface Form", grouped_comparison(rows, "surface_form")))
    lines.append("")
    lines.extend(comparison_table("Lift By Trap Class", trap_comparison(rows)))
    lines.append("")
    lines.extend(route_count_table(dict(rescue_route_counts(rows))))
    lines.extend(
        [
            "",
            "## Use Notes",
            "",
            "- This is an ablation report, not a query-rewrite product.",
            "- A private normalization experiment should keep raw queries outside the public repo",
            "  and publish only this aggregate report.",
            "- Per-family lift is the main signal; trap classes are diagnostic slices.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--qrels", type=Path, default=ROOT / "fixtures" / "surface_qrels.jsonl")
    parser.add_argument("--baseline-run", type=Path, default=ROOT / "fixtures" / "surface_runs" / "formal_only_demo.jsonl")
    parser.add_argument(
        "--candidate-run",
        type=Path,
        default=ROOT / "fixtures" / "surface_runs" / "surface_robust_demo.jsonl",
    )
    parser.add_argument("--baseline-name", default="formal_only_demo")
    parser.add_argument("--candidate-name", default="surface_robust_demo")
    parser.add_argument("--out", type=Path, default=ROOT / "reports" / "normalization_ablation_fixture.md")
    parser.add_argument("--k", type=int, default=3)
    parser.add_argument("--label-status", default="synthetic fixture metadata")
    args = parser.parse_args()

    qrels = load_jsonl(args.qrels)
    baseline_rows = load_jsonl(args.baseline_run)
    candidate_rows = load_jsonl(args.candidate_run)
    report = render_report(
        qrels_path=args.qrels,
        baseline_path=args.baseline_run,
        candidate_path=args.candidate_run,
        qrels=qrels,
        baseline_rows=baseline_rows,
        candidate_rows=candidate_rows,
        baseline_name=args.baseline_name,
        candidate_name=args.candidate_name,
        k=args.k,
        label_status=args.label_status,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
