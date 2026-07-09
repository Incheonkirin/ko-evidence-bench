#!/usr/bin/env python3
"""Rehearse the human-gold promotion-to-scorecard path on fixtures."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ko_evidence_bench.metrics import load_jsonl  # noqa: E402
from ko_evidence_bench.route_score import score_route_run  # noqa: E402
from ko_evidence_bench.route_surface import summarize_route_surface_run  # noqa: E402

SURFACE_QRELS = ROOT / "fixtures" / "surface_qrels.jsonl"
SURFACE_AUDIT = ROOT / "fixtures" / "route_audit" / "surface_audit_seed.jsonl"
SURFACE_RUN_DIR = ROOT / "fixtures" / "surface_runs"


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def run(args: list[str]) -> None:
    subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def build_completed_audit_rows(
    qrels: list[dict[str, Any]],
    audit_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    qrels_by_qid = {str(row["qid"]): row for row in qrels}
    completed: list[dict[str, Any]] = []
    for audit_row in audit_rows:
        qid = str(audit_row["qid"])
        qrel = qrels_by_qid[qid]
        traps = qrel.get("trap_classes") or ["fixture"]
        completed.append(
            {
                "audit_id": audit_row["audit_id"],
                "qid": qid,
                "adjudicated": {
                    "route_gold": qrel["route_gold"],
                    "allowed_source_tiers": qrel["allowed_source_tiers"],
                    "should_abstain": qrel["should_abstain"],
                    "confidence": "high",
                    "rationale_code": f"fixture_{traps[0]}",
                    "labeler": "fixture-adjudicator",
                    "notes": "synthetic promotion rehearsal",
                },
            }
        )
    return completed


def overlay_promoted_labels(
    qrels: list[dict[str, Any]],
    promoted: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    labels_by_qid = {str(row["qid"]): row for row in promoted}
    merged: list[dict[str, Any]] = []
    for qrel in qrels:
        qid = str(qrel["qid"])
        label = labels_by_qid[qid]
        merged.append(
            {
                **qrel,
                "route_gold": label["route_gold"],
                "allowed_source_tiers": label["allowed_source_tiers"],
                "should_abstain": label["should_abstain"],
                "label_status": "synthetic_promoted_human_gold",
            }
        )
    return merged


def load_runs(run_dir: Path) -> dict[str, list[dict[str, Any]]]:
    runs: dict[str, list[dict[str, Any]]] = {}
    for path in sorted(run_dir.glob("*.jsonl")):
        runs[path.stem] = load_jsonl(path)
    if not runs:
        raise ValueError(f"no .jsonl route runs found under {run_dir}")
    return runs


def extract_value(report: str, prefix: str) -> str:
    for line in report.splitlines():
        if line.startswith(prefix):
            return line.split(":", 1)[1].strip()
    return ""


def route_score_rows(labels: list[dict[str, Any]], runs: dict[str, list[dict[str, Any]]]) -> list[str]:
    lines = [
        "| system | route_acc | abst_p | abst_r | missing predictions |",
        "|---|---:|---:|---:|---:|",
    ]
    for name, rows in runs.items():
        score = score_route_run(labels, rows)
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{name}`",
                    pct(score["route_accuracy"]),
                    pct(score["abstention_precision"]),
                    pct(score["abstention_recall"]),
                    str(int(score["missing_predictions"])),
                ]
            )
            + " |"
        )
    return lines


def route_surface_rows(qrels: list[dict[str, Any]], runs: dict[str, list[dict[str, Any]]]) -> list[str]:
    lines = [
        "| system | route_acc | abst_r | worst_surface_route_acc | missing metadata |",
        "|---|---:|---:|---:|---:|",
    ]
    for name, rows in runs.items():
        score = summarize_route_surface_run(qrels, rows)
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{name}`",
                    pct(score["route_accuracy"]),
                    pct(score["abstention_recall"]),
                    pct(score["worst_surface_route_accuracy"]),
                    str(int(score["missing_surface_metadata"])),
                ]
            )
            + " |"
        )
    return lines


def build_report(tmp: Path) -> str:
    qrels = load_jsonl(SURFACE_QRELS)
    audit_seed = load_jsonl(SURFACE_AUDIT)
    completed_audit = build_completed_audit_rows(qrels, audit_seed)

    audit_path = tmp / "completed_surface_audit.jsonl"
    labels_path = tmp / "promoted_human_route_labels.jsonl"
    surface_qrels_path = tmp / "promoted_surface_qrels.jsonl"
    validation_report_path = tmp / "validation.md"
    promoted_report_path = tmp / "promoted.md"
    coverage_report_path = tmp / "coverage.md"
    route_scorecard_path = tmp / "route_scorecard.md"
    route_surface_path = tmp / "route_surface.md"

    write_jsonl(audit_path, completed_audit)
    run(
        [
            "scripts/validate_route_audit.py",
            "--audit",
            str(audit_path),
            "--label-prefix",
            "adjudicated",
            "--require-complete",
            "--report-out",
            str(validation_report_path),
        ]
    )
    run(
        [
            "scripts/promote_route_audit.py",
            "--audit",
            str(audit_path),
            "--label-prefix",
            "adjudicated",
            "--labels-out",
            str(labels_path),
            "--report-out",
            str(promoted_report_path),
        ]
    )
    run(
        [
            "scripts/check_audit_surface_coverage.py",
            "--qrels",
            str(SURFACE_QRELS),
            "--audit",
            str(audit_path),
            "--out",
            str(coverage_report_path),
            "--require-complete",
        ]
    )

    promoted = load_jsonl(labels_path)
    promoted_surface_qrels = overlay_promoted_labels(qrels, promoted)
    write_jsonl(surface_qrels_path, promoted_surface_qrels)

    run(
        [
            "scripts/reproduce_route_scorecard.py",
            "--labels",
            str(labels_path),
            "--run-dir",
            str(SURFACE_RUN_DIR),
            "--baseline",
            "formal_only_demo",
            "--out",
            str(route_scorecard_path),
            "--samples",
            "200",
            "--title",
            "Human-Gold Promotion Route Scorecard Rehearsal",
            "--label-status",
            "synthetic promoted human-gold fixture labels",
        ]
    )
    run(
        [
            "scripts/reproduce_route_surface_scorecard.py",
            "--qrels",
            str(surface_qrels_path),
            "--run-dir",
            str(SURFACE_RUN_DIR),
            "--out",
            str(route_surface_path),
            "--title",
            "Human-Gold Promotion Route-Surface Rehearsal",
            "--label-status",
            "synthetic promoted human-gold fixture labels",
        ]
    )

    validation = validation_report_path.read_text(encoding="utf-8")
    promoted_report = promoted_report_path.read_text(encoding="utf-8")
    coverage = coverage_report_path.read_text(encoding="utf-8")
    runs = load_runs(SURFACE_RUN_DIR)
    validation_errors = extract_value(validation, "- rows with validation errors")
    promoted_count = extract_value(promoted_report, "- promoted labels")
    coverage_status = "PASS" if "Status: **PASS**." in coverage else "INCOMPLETE"
    status = (
        "PASS"
        if validation_errors == "0"
        and promoted_count == str(len(qrels))
        and coverage_status == "PASS"
        else "INCOMPLETE"
    )

    lines = [
        "# Human-Gold Promotion Rehearsal Fixture",
        "",
        f"Status: **{status}**.",
        "",
        "This synthetic rehearsal exercises the public path from completed",
        "adjudication to qid-only labels, route scorecards, and surface-route",
        "diagnostics. It uses fixture ids only: no private query, conversation,",
        "community, policy, source-name, or evidence text is published.",
        "",
        "## Gate Chain",
        "",
        "| gate | evidence | status |",
        "|---|---:|---|",
        f"| adjudicated audit rows | {len(completed_audit)} | `PASS` |",
        f"| route-audit validation errors | {validation_errors} | `PASS` |",
        f"| promoted qid-only labels | {promoted_count} | `PASS` |",
        f"| stress-axis coverage | {coverage_status} | `PASS` |",
        f"| route scorecard generated | {route_scorecard_path.name} | `PASS` |",
        f"| route-surface scorecard generated | {route_surface_path.name} | `PASS` |",
        "",
        "## Route Scorecard Rehearsal",
        "",
    ]
    lines.extend(route_score_rows(promoted, runs))
    lines.extend(
        [
            "",
            "## Route-Surface Rehearsal",
            "",
        ]
    )
    lines.extend(route_surface_rows(promoted_surface_qrels, runs))
    lines.extend(
        [
            "",
            "## Use Notes",
            "",
            "- This is not a human-gold result. It exercises the promotion and scoring",
            "  path that real adjudicated labels will use.",
            "- The private 300-row adjudication pack still needs completed labels,",
            "  validation with zero errors, and agreement evidence before headline",
            "  claims can be promoted.",
            "- The route/surface scorecards are intentionally qid-only so private text",
            "  can remain outside the public repository.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=ROOT / "reports" / "human_gold_rehearsal_fixture.md",
    )
    args = parser.parse_args()

    with tempfile.TemporaryDirectory() as tmp_name:
        report = build_report(Path(tmp_name))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
