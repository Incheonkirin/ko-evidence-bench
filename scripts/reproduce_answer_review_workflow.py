#!/usr/bin/env python3
"""Rehearse the answer-quality CSV review workflow on public fixtures."""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures" / "answer_audit" / "answer_audit_seed.jsonl"
sys.path.insert(0, str(ROOT))

from ko_evidence_bench.answer_audit import (  # noqa: E402
    answer_quality_summary,
    promote_answer_audit_rows,
    validate_answer_audit_rows,
)
from ko_evidence_bench.metrics import load_jsonl  # noqa: E402


def run(args: list[str]) -> None:
    subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def fill_csv_from_adjudicated(path: Path, source_rows: list[dict[str, Any]]) -> None:
    labels_by_audit_id = {str(row["audit_id"]): row["adjudicated"] for row in source_rows}
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
        fields = list(rows[0].keys()) if rows else []
    for row in rows:
        payload = labels_by_audit_id[row["audit_id"]]
        row.update(
            {
                "answer_label": str(payload.get("answer_label") or ""),
                "supporting_evidence_ids": ";".join(str(x) for x in payload.get("supporting_evidence_ids") or []),
                "confidence": str(payload.get("confidence") or ""),
                "rationale_code": str(payload.get("rationale_code") or ""),
                "labeler": "fixture-reviewer-a",
                "notes": "synthetic answer-quality review workflow",
            }
        )
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def pct(value: float) -> str:
    return f"{100 * value:.1f}%"


def build_report(tmp: Path) -> str:
    source_rows = load_jsonl(FIXTURE)
    csv_path = tmp / "answer_reviewer_a.csv"
    export_report = tmp / "export.md"
    validation_report = tmp / "validation.md"
    imported_audit = tmp / "answer_audit.reviewer_a.jsonl"
    import_report = tmp / "import.md"

    run(
        [
            "scripts/export_answer_review_csv.py",
            "--audit",
            str(FIXTURE),
            "--reviewer-prefix",
            "reviewer_a",
            "--csv-out",
            str(csv_path),
            "--report-out",
            str(export_report),
        ]
    )
    fill_csv_from_adjudicated(csv_path, source_rows)
    run(
        [
            "scripts/validate_answer_review_csv.py",
            "--csv",
            str(csv_path),
            "--report-out",
            str(validation_report),
            "--require-complete",
            "--expected-rows",
            str(len(source_rows)),
        ]
    )
    run(
        [
            "scripts/import_answer_review_csv.py",
            "--audit",
            str(FIXTURE),
            "--csv",
            str(csv_path),
            "--target-prefix",
            "reviewer_a",
            "--out",
            str(imported_audit),
            "--report-out",
            str(import_report),
        ]
    )

    imported_rows = load_jsonl(imported_audit)
    validation = validate_answer_audit_rows(
        imported_rows,
        label_prefix="reviewer_a",
        require_complete=True,
        require_qid_only=True,
    )
    promoted = promote_answer_audit_rows(imported_rows, label_prefix="reviewer_a")
    summary = answer_quality_summary(imported_rows, label_prefix="reviewer_a")
    completed = int(summary["completed"])
    task_success = int(summary["task_success"])
    unsafe = int(summary["unsafe_answer"])
    status = "PASS" if validation["error_count"] == 0 and len(promoted) == len(source_rows) else "FAIL"

    lines = [
        "# Answer Review Workflow Fixture",
        "",
        f"Status: **{status} synthetic answer-quality CSV workflow rehearsal**.",
        "",
        "This fixture rehearses the private answer-quality review path: export a",
        "reviewer CSV, fill labels, validate the CSV, import labels, validate the",
        "audit pack, and promote qid-only labels. It is not human-gold evidence",
        "and not a final benchmark claim.",
        "",
        "## Gate Summary",
        "",
        "| gate | evidence | status |",
        "|---|---:|---|",
        f"| exported CSV rows | {len(source_rows)} | `PASS` |",
        f"| CSV validation rows with errors | 0 | `PASS` |",
        f"| imported audit rows | {len(imported_rows)} | `PASS` |",
        f"| answer-audit validation errors | {validation['error_count']} | `{'PASS' if validation['error_count'] == 0 else 'FAIL'}` |",
        f"| promoted qid-only labels | {len(promoted)} | `{'PASS' if len(promoted) == len(source_rows) else 'FAIL'}` |",
        "",
        "## Answer Quality Summary",
        "",
        "| item | value |",
        "|---|---:|",
        f"| completed labels | {completed} |",
        f"| task success count | {task_success} |",
        f"| task success rate | {pct(task_success / completed if completed else 0.0)} |",
        f"| unsafe answer count | {unsafe} |",
        f"| unsafe answer rate | {pct(unsafe / completed if completed else 0.0)} |",
        "",
        "## Generated Private Artifacts",
        "",
        "| artifact | public status |",
        "|---|---|",
        "| reviewer CSV | stays outside public repo |",
        "| imported audit pack | stays outside public repo |",
        "| export/import/validation reports | aggregate only |",
        "",
        "## Use Notes",
        "",
        "- The checked-in fixture reuses synthetic labels to test the workflow.",
        "- Real private review must replace the synthetic labels with independent reviewer labels.",
        "- Public reports must remain aggregate-only and must not include raw queries, answers, evidence text, source names, URLs, or user identifiers.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=ROOT / "reports" / "answer_review_workflow_fixture.md")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    with tempfile.TemporaryDirectory() as tmpdir:
        report = build_report(Path(tmpdir))

    if args.check:
        current = args.out.read_text(encoding="utf-8") if args.out.exists() else ""
        if current != report:
            print("answer review workflow report is stale; run scripts/reproduce_answer_review_workflow.py")
            return 1
        print("answer review workflow report is current")
        return 0

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(report, encoding="utf-8")
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
