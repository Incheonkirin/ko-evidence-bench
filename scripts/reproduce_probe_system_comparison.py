#!/usr/bin/env python3
"""Run public probe systems and render a comparison report."""

from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ko_evidence_bench.probe_systems import (  # noqa: E402
    PROBE_SYSTEM_IDS,
    build_probe_runs,
    load_probe_inputs,
    score_probe_runs,
)


SYSTEM_LABELS = {
    "probe_literal_lexical": "literal lexical BM25 over synthetic Korean search text",
    "probe_normalized_lexical": "surface-expanded lexical BM25",
    "probe_semantic_centroid": "dependency-free semantic centroid scorer over concept features",
    "probe_hybrid_lexical_semantic": "lexical BM25 plus semantic concept-score fusion",
    "probe_route_aware_rerank": "hybrid scoring plus source-route-aware reranking and abstention",
}


def pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def route_confusions(qrels: list[dict], runs: dict[str, list[dict]]) -> dict[str, dict[tuple[str, str], int]]:
    gold = {row["qid"]: row["route_gold"] for row in qrels}
    out: dict[str, dict[tuple[str, str], int]] = {}
    for system_id, run_rows in runs.items():
        counts: defaultdict[tuple[str, str], int] = defaultdict(int)
        for row in run_rows:
            pair = (gold[row["qid"]], row["route_pred"])
            if pair[0] != pair[1]:
                counts[pair] += 1
        out[system_id] = dict(counts)
    return out


def render_report(probe_dir: Path) -> str:
    inputs = load_probe_inputs(probe_dir)
    runs = build_probe_runs(inputs)
    scores = score_probe_runs(inputs, runs, k=3)
    confusions = route_confusions(inputs.qrels, runs)

    lines = [
        "# Public Probe System Comparison",
        "",
        "Status: **synthetic probe systems only; not a full private benchmark matrix**.",
        "",
        "This report runs small retrieval systems over the public synthetic",
        "probe package. It proves that the repository can execute and compare",
        "literal lexical, surface-normalized, semantic, hybrid, and source-route-aware",
        "systems without publishing private queries, conversation snippets, source",
        "names, or policy text.",
        "",
        "## Inputs",
        "",
        f"- probe dir: `{display_path(probe_dir)}`",
        f"- query rows: {len(inputs.queries)}",
        f"- qrel rows: {len(inputs.qrels)}",
        f"- evidence rows: {len(inputs.evidence)}",
        "- label status: synthetic public fixture",
        "",
        "## Systems",
        "",
        "| system | method |",
        "|---|---|",
    ]
    for system_id in PROBE_SYSTEM_IDS:
        lines.append(f"| `{system_id}` | {SYSTEM_LABELS[system_id]} |")

    lines.extend(
        [
            "",
            "## Overall Scorecard",
            "",
            "| system | n | route_acc | suff@3 | wrong_src@3 | abst_p | abst_r | clause@3 | task_success@3 | worst_surface@3 | avg_intent_spread |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in scores:
        lines.append(
            "| "
            f"`{row['system_id']}` | "
            f"{row['n']} | "
            f"{pct(row['route_accuracy'])} | "
            f"{pct(row['evidence_sufficiency@3'])} | "
            f"{pct(row['wrong_source_rate@3'])} | "
            f"{pct(row['abstention_precision'])} | "
            f"{pct(row['abstention_recall'])} | "
            f"{pct(row['clause_recall@3'])} | "
            f"{pct(row['task_success@3'])} | "
            f"{pct(row['worst_surface_task_success@3'])} | "
            f"{pct(row['avg_intent_surface_spread'])} |"
        )

    lines.extend(
        [
            "",
            "## Route Confusions",
            "",
            "| system | gold route | predicted route | rows |",
            "|---|---|---|---:|",
        ]
    )
    any_confusion = False
    for system_id in PROBE_SYSTEM_IDS:
        for (gold, pred), count in sorted(confusions[system_id].items()):
            any_confusion = True
            lines.append(f"| `{system_id}` | `{gold}` | `{pred}` | {count} |")
    if not any_confusion:
        lines.append("| all systems | none | none | 0 |")

    lines.extend(
        [
            "",
            "## Use Notes",
            "",
            "- This is a runnable public-system comparison, not the private analyzer/dense/hybrid/reranker matrix.",
            "- The semantic centroid is a dependency-free surrogate for exercising dense-style comparison plumbing; it is not a neural encoder.",
            "- The hybrid system is intentionally simple; it demonstrates score fusion and source-mixing diagnostics, not a product rewrite engine.",
            "- The route-aware system shows why source selection and abstention must be scored separately from paragraph similarity.",
            "- Private system runs can reuse the same qid-only report shape after human labels are complete.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--probe-dir", type=Path, default=ROOT / "probes" / "ko_evidence_probe_v0")
    parser.add_argument("--out", type=Path, default=ROOT / "reports" / "probe_system_comparison.md")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    report = render_report(args.probe_dir)
    if args.check:
        current = args.out.read_text(encoding="utf-8") if args.out.exists() else ""
        if current != report:
            print("probe system comparison report is stale; run scripts/reproduce_probe_system_comparison.py")
            sys.exit(1)
        print("probe system comparison report is current")
        return
    args.out.write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
