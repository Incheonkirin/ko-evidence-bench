#!/usr/bin/env python3
"""Validate a qid-only run bundle for the missing full-system matrix."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ko_evidence_bench.system_matrix_bundle import MatrixBundleResult, validate_matrix_bundle  # noqa: E402


def pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def render_report(result: MatrixBundleResult, *, bundle_dir: Path, qrels_path: Path, matrix_path: Path) -> str:
    status = "PASS" if result.validation_errors == 0 else "FAIL"
    lines = [
        "# System Matrix Bundle Contract",
        "",
        f"Status: **{status} synthetic full-matrix run-bundle rehearsal**.",
        "",
        "This report validates the qid-only artifact shape expected from the",
        "full analyzer/dense/hybrid/reranker comparison matrix. It does not",
        "claim that those external systems have been run on the private lab.",
        "Instead, it proves that their future runs can be imported, checked for",
        "qid coverage, screened for raw-text leakage, and scored through the",
        "same route/surface metrics.",
        "",
        "The score values below are fixture-validator outputs only. They are",
        "not model-quality comparisons and must not be used as analyzer or",
        "encoder performance claims.",
        "",
        "## Inputs",
        "",
        f"- bundle dir: `{display_path(bundle_dir)}`",
        f"- qrels: `{display_path(qrels_path)}`",
        f"- system matrix: `{display_path(matrix_path)}`",
        f"- label status: {result.label_status}",
        "",
        "## Gate Summary",
        "",
        "| item | value |",
        "|---|---:|",
        f"| qrel rows | {result.qrel_rows} |",
        f"| required runnable systems | {len(result.required_systems)} |",
        f"| present systems | {len(result.present_systems)} |",
        f"| complete systems | {result.complete_systems} |",
        f"| missing systems | {len(result.missing_systems)} |",
        f"| extra systems | {len(result.extra_systems)} |",
        f"| validation errors | {result.validation_errors} |",
        "",
        "## Required Systems",
        "",
    ]
    if result.required_systems:
        lines.extend(f"- `{system_id}`" for system_id in result.required_systems)
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## System Scores",
            "",
            "| system | family | stage | rows | complete | route_acc | suff@3 | wrong_src@3 | clause@3 | task_success@3 | worst_surface@3 | avg_intent_spread |",
            "|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for system in result.systems:
        complete = "yes" if system.complete else "no"
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{system.system_id}`",
                    f"`{system.family}`",
                    f"`{system.stage}`",
                    str(system.rows),
                    f"`{complete}`",
                    pct(system.route_accuracy),
                    pct(system.evidence_sufficiency),
                    pct(system.wrong_source_rate),
                    pct(system.clause_recall),
                    pct(system.task_success),
                    pct(system.worst_surface),
                    pct(system.avg_intent_spread),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Validation Details",
            "",
        ]
    )
    if result.missing_systems:
        lines.append(f"- missing systems: `{', '.join(result.missing_systems)}`")
    if result.extra_systems:
        lines.append(f"- extra systems: `{', '.join(result.extra_systems)}`")
    for system in result.systems:
        for qid in system.missing_qids:
            lines.append(f"- `{system.system_id}` missing qid `{qid}`")
        for qid in system.extra_qids:
            lines.append(f"- `{system.system_id}` has extra qid `{qid}`")
        for qid in system.duplicate_qids:
            lines.append(f"- `{system.system_id}` has duplicate qid `{qid}`")
        for error in system.schema_errors:
            lines.append(f"- `{system.system_id}` schema: {error}")
        for error in system.raw_field_errors:
            lines.append(f"- `{system.system_id}` raw-field: {error}")
    if result.validation_errors == 0:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Use Notes",
            "",
            "- This fixture rehearses the import contract for the missing matrix systems;",
            "  it is not evidence that the private full matrix has been run.",
            "- The fixture score table exists to prove scoring compatibility, not to",
            "  compare analyzer or neural retriever quality.",
            "- Real runs should keep raw queries, source names, URLs, usernames, and",
            "  passage text outside the public repo and publish only qid-only outputs",
            "  plus aggregate reports.",
            "- Once real system runs exist, replace the fixture bundle path and rerun",
            "  this validator before changing `docs/system_matrix.json` statuses.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle-dir", type=Path, default=ROOT / "fixtures" / "system_matrix_bundle")
    parser.add_argument("--qrels", type=Path, default=ROOT / "fixtures" / "surface_qrels.jsonl")
    parser.add_argument("--matrix", type=Path, default=ROOT / "docs" / "system_matrix.json")
    parser.add_argument("--out", type=Path, default=ROOT / "reports" / "system_matrix_bundle_fixture.md")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    result = validate_matrix_bundle(bundle_dir=args.bundle_dir, qrels_path=args.qrels, matrix_path=args.matrix)
    report = render_report(result, bundle_dir=args.bundle_dir, qrels_path=args.qrels, matrix_path=args.matrix)
    if args.check:
        current = args.out.read_text(encoding="utf-8") if args.out.exists() else ""
        if current != report:
            print("system matrix bundle report is stale; run scripts/validate_system_matrix_bundle.py")
            return 1
        if result.validation_errors:
            print("system matrix bundle has validation errors")
            return 1
        print("system matrix bundle report is current")
        return 0

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(report, encoding="utf-8")
    print(report)
    return 1 if result.validation_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
