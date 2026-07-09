#!/usr/bin/env python3
"""Rehearse promotion gates for full-system matrix run bundles."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ko_evidence_bench.system_matrix_promotion import (  # noqa: E402
    MatrixPromotionResult,
    evaluate_system_matrix_promotion,
)


def pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def render_report(
    result: MatrixPromotionResult,
    *,
    bundle_dir: Path,
    qrels_path: Path,
    matrix_path: Path,
    min_rows: int,
) -> str:
    if result.status == "READY":
        status = "READY for diagnostic matrix promotion"
    elif result.status == "REHEARSAL_ONLY":
        status = "BLOCKED synthetic promotion rehearsal; no matrix update"
    else:
        status = "FAIL promotion gate rehearsal"

    lines = [
        "# System Matrix Promotion Rehearsal",
        "",
        f"Status: **{status}**.",
        "",
        "This report checks whether a qid-only full-matrix run bundle is ready",
        "to promote from `not_run` to checked diagnostic evidence. It does not",
        "update `docs/system_matrix.json` and does not claim that external",
        "analyzer, dense, hybrid, or reranker systems have been run.",
        "",
        "The checked-in fixture is intentionally blocked from promotion because",
        "it is synthetic, below the private-run row threshold, and marked as not",
        "external model output.",
        "",
        "## Inputs",
        "",
        f"- bundle dir: `{display_path(bundle_dir)}`",
        f"- qrels: `{display_path(qrels_path)}`",
        f"- system matrix: `{display_path(matrix_path)}`",
        f"- minimum promotion rows: {min_rows}",
        f"- label status: {result.bundle.label_status}",
        "",
        "## Promotion Gates",
        "",
        "| gate | status | evidence | required |",
        "|---|---|---|---|",
    ]
    for gate in result.gates:
        lines.append(
            f"| `{gate.gate}` | `{gate.status}` | {gate.evidence} | {gate.required} |"
        )

    lines.extend(
        [
            "",
            "## Candidate System Scores",
            "",
            "| system | rows | complete | route_acc | suff@3 | wrong_src@3 | clause@3 | task_success@3 | worst_surface@3 |",
            "|---|---:|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for system in result.bundle.systems:
        complete = "yes" if system.complete else "no"
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{system.system_id}`",
                    str(system.rows),
                    f"`{complete}`",
                    pct(system.route_accuracy),
                    pct(system.evidence_sufficiency),
                    pct(system.wrong_source_rate),
                    pct(system.clause_recall),
                    pct(system.task_success),
                    pct(system.worst_surface),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Promotion Decision",
            "",
        ]
    )
    if result.promotion_ready:
        lines.extend(
            [
                "The bundle passes the diagnostic promotion gates. A maintainer may",
                "update the relevant `docs/system_matrix.json` rows only after",
                "checking that the referenced aggregate report is committed.",
            ]
        )
    else:
        lines.extend(
            [
                "Do not update `docs/system_matrix.json` from this fixture. The",
                "mechanical import path is rehearsed, but promotion remains blocked",
                "until a real full-matrix run bundle reaches the required scale and",
                "carries real external-run provenance.",
            ]
        )
    lines.extend(
        [
            "",
            "## Use Notes",
            "",
            "- This is a promotion gate, not a model-quality benchmark.",
            "- It is allowed for the checked-in fixture to be blocked; that is the",
            "  expected safety behavior.",
            "- Real private runs should publish only qid-only run files and aggregate",
            "  reports, never raw queries, evidence text, source names, URLs, or user",
            "  identifiers.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle-dir", type=Path, default=ROOT / "fixtures" / "system_matrix_bundle")
    parser.add_argument("--qrels", type=Path, default=ROOT / "fixtures" / "surface_qrels.jsonl")
    parser.add_argument("--matrix", type=Path, default=ROOT / "docs" / "system_matrix.json")
    parser.add_argument("--out", type=Path, default=ROOT / "reports" / "system_matrix_promotion_fixture.md")
    parser.add_argument("--min-rows", type=int, default=500)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    result = evaluate_system_matrix_promotion(
        bundle_dir=args.bundle_dir,
        qrels_path=args.qrels,
        matrix_path=args.matrix,
        min_rows=args.min_rows,
    )
    report = render_report(
        result,
        bundle_dir=args.bundle_dir,
        qrels_path=args.qrels,
        matrix_path=args.matrix,
        min_rows=args.min_rows,
    )
    if args.check:
        current = args.out.read_text(encoding="utf-8") if args.out.exists() else ""
        if current != report:
            print("system matrix promotion report is stale; run scripts/rehearse_system_matrix_promotion.py")
            return 1
        print("system matrix promotion report is current")
        return 0

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(report, encoding="utf-8")
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
