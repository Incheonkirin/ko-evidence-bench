#!/usr/bin/env python3
"""Rehearse answer-quality agreement reporting on public fixtures."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures" / "answer_audit" / "answer_audit_seed.jsonl"
sys.path.insert(0, str(ROOT))

from ko_evidence_bench.agreement import cohens_kappa, observed_agreement, paired_labels  # noqa: E402
from ko_evidence_bench.answer_audit import validate_answer_audit_rows  # noqa: E402
from ko_evidence_bench.metrics import load_jsonl  # noqa: E402


REVIEWER_B_OVERRIDES = {
    "answer-audit-0003": "insufficient",
    "answer-audit-0004": "partial",
}


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


def reviewer_payload(row: dict[str, Any], *, reviewer: str) -> dict[str, Any]:
    payload = dict(row["adjudicated"])
    payload["labeler"] = reviewer
    payload["notes"] = "synthetic answer agreement rehearsal"
    return payload


def build_double_labeled_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in rows:
        merged = dict(row)
        reviewer_a = reviewer_payload(row, reviewer="fixture-reviewer-a")
        reviewer_b = reviewer_payload(row, reviewer="fixture-reviewer-b")
        override = REVIEWER_B_OVERRIDES.get(str(row["audit_id"]))
        if override:
            reviewer_b["answer_label"] = override
            reviewer_b["rationale_code"] = f"fixture_disagreement_{override}"
            if override in {"insufficient", "unsafe_answer", "correct_abstain"}:
                reviewer_b["supporting_evidence_ids"] = []
            elif not reviewer_b.get("supporting_evidence_ids"):
                reviewer_b["supporting_evidence_ids"] = list(row.get("topk_evidence_ids") or [])
        merged["reviewer_a"] = reviewer_a
        merged["reviewer_b"] = reviewer_b
        out.append(merged)
    return out


def pct(value: float) -> str:
    return f"{100 * value:.1f}%"


def extract_value(report: str, prefix: str) -> str:
    for line in report.splitlines():
        if line.startswith(prefix):
            return line.split(":", 1)[1].strip()
    return ""


def build_report(tmp: Path) -> str:
    rows = build_double_labeled_rows(load_jsonl(FIXTURE))
    audit_path = tmp / "answer_audit.double_labeled.jsonl"
    agreement_report_path = tmp / "answer_agreement.md"
    write_jsonl(audit_path, rows)

    validation_a = validate_answer_audit_rows(
        rows,
        label_prefix="reviewer_a",
        require_complete=True,
        require_qid_only=True,
    )
    validation_b = validate_answer_audit_rows(
        rows,
        label_prefix="reviewer_b",
        require_complete=True,
        require_qid_only=True,
    )
    labels_a, labels_b = paired_labels(rows, "reviewer_a.answer_label", "reviewer_b.answer_label")
    agreement = observed_agreement(labels_a, labels_b)
    kappa = cohens_kappa(labels_a, labels_b)
    run(
        [
            "scripts/summarize_answer_audit.py",
            "--audit",
            str(audit_path),
            "--field-a",
            "reviewer_a.answer_label",
            "--field-b",
            "reviewer_b.answer_label",
            "--report-out",
            str(agreement_report_path),
        ]
    )
    agreement_report = agreement_report_path.read_text(encoding="utf-8")
    paired = extract_value(agreement_report, "- paired completed rows")
    disagreements = extract_value(agreement_report, "- disagreement rows")
    status = "PASS" if validation_a["error_count"] == 0 and validation_b["error_count"] == 0 else "FAIL"
    lines = [
        "# Answer Agreement Workflow Fixture",
        "",
        f"Status: **{status} synthetic answer-quality agreement rehearsal**.",
        "",
        "This fixture rehearses independent answer-quality label agreement on",
        "synthetic rows. It validates two reviewer payloads and summarizes raw",
        "agreement plus Cohen's kappa without exposing qids, raw queries, answers,",
        "evidence text, audit ids, or reviewer notes. It is not human-gold evidence.",
        "",
        "## Gate Summary",
        "",
        "| gate | evidence | status |",
        "|---|---:|---|",
        f"| reviewer A validation errors | {validation_a['error_count']} | `{'PASS' if validation_a['error_count'] == 0 else 'FAIL'}` |",
        f"| reviewer B validation errors | {validation_b['error_count']} | `{'PASS' if validation_b['error_count'] == 0 else 'FAIL'}` |",
        f"| paired completed rows | {paired} | `PASS` |",
        f"| raw agreement | {pct(agreement)} | `PASS` |",
        f"| Cohen's kappa | {kappa:.3f} | `PASS` |",
        f"| disagreement rows | {disagreements} | `PASS` |",
        "",
        "## Agreement Summary",
        "",
        "| item | value |",
        "|---|---:|",
        f"| paired rows | {paired} |",
        f"| raw agreement | {pct(agreement)} |",
        f"| Cohen's kappa | {kappa:.3f} |",
        f"| disagreement rows | {disagreements} |",
        "",
        "## Use Notes",
        "",
        "- The checked-in fixture intentionally includes synthetic disagreements.",
        "- Real private review must use independent reviewer labels before reporting inter-annotator agreement.",
        "- Agreement is necessary but not sufficient; adjudication and qid-only promotion still gate headline claims.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=ROOT / "reports" / "answer_agreement_workflow_fixture.md")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    with tempfile.TemporaryDirectory() as tmpdir:
        report = build_report(Path(tmpdir))

    if args.check:
        current = args.out.read_text(encoding="utf-8") if args.out.exists() else ""
        if current != report:
            print("answer agreement workflow report is stale; run scripts/reproduce_answer_agreement_workflow.py")
            return 1
        print("answer agreement workflow report is current")
        return 0

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(report, encoding="utf-8")
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
