#!/usr/bin/env python3
"""Rehearse source-route agreement reporting on public fixtures."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures" / "route_audit" / "audit_seed.jsonl"
sys.path.insert(0, str(ROOT))

from ko_evidence_bench.agreement import cohens_kappa, observed_agreement, paired_labels  # noqa: E402
from ko_evidence_bench.metrics import load_jsonl  # noqa: E402
from ko_evidence_bench.route_audit import validate_audit_rows  # noqa: E402


REVIEWER_B_OVERRIDES = {
    "route-audit-0003": {
        "route_gold": "product_disclosure",
        "allowed_source_tiers": ["product_disclosure"],
        "should_abstain": False,
        "confidence": "low",
        "rationale_code": "fixture_product_table_needed",
    }
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
    silver = row["silver"]
    return {
        "route_gold": silver["route_gold"],
        "allowed_source_tiers": list(silver["allowed_source_tiers"]),
        "should_abstain": silver["should_abstain"],
        "confidence": silver["confidence"],
        "rationale_code": silver["rationale_code"],
        "labeler": reviewer,
        "notes": "synthetic route agreement rehearsal",
    }


def build_double_labeled_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in rows:
        merged = dict(row)
        reviewer_a = reviewer_payload(row, reviewer="fixture-route-reviewer-a")
        reviewer_b = reviewer_payload(row, reviewer="fixture-route-reviewer-b")
        override = REVIEWER_B_OVERRIDES.get(str(row["audit_id"]))
        if override:
            reviewer_b.update(override)
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
    audit_path = tmp / "route_audit.double_labeled.jsonl"
    agreement_report_path = tmp / "route_agreement.md"
    write_jsonl(audit_path, rows)

    validation_a = validate_audit_rows(rows, label_prefix="reviewer_a", require_complete=True)
    validation_b = validate_audit_rows(rows, label_prefix="reviewer_b", require_complete=True)
    labels_a, labels_b = paired_labels(rows, "reviewer_a.route_gold", "reviewer_b.route_gold")
    agreement = observed_agreement(labels_a, labels_b)
    kappa = cohens_kappa(labels_a, labels_b)
    run(
        [
            "scripts/summarize_route_audit.py",
            "--audit",
            str(audit_path),
            "--field-a",
            "reviewer_a.route_gold",
            "--field-b",
            "reviewer_b.route_gold",
            "--report-out",
            str(agreement_report_path),
        ]
    )
    agreement_report = agreement_report_path.read_text(encoding="utf-8")
    paired = extract_value(agreement_report, "- paired completed rows")
    disagreements = extract_value(agreement_report, "- disagreement rows")
    status = "PASS" if validation_a["error_count"] == 0 and validation_b["error_count"] == 0 else "FAIL"

    lines = [
        "# Route Agreement Workflow Fixture",
        "",
        f"Status: **{status} synthetic source-route agreement rehearsal**.",
        "",
        "This fixture rehearses independent source-route label agreement on",
        "synthetic rows. It validates two reviewer payloads and summarizes raw",
        "agreement plus Cohen's kappa without exposing qids, raw queries, context,",
        "source names, audit ids, or reviewer notes. It is not human-gold evidence.",
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
        "- The checked-in fixture intentionally includes a synthetic source-route disagreement.",
        "- Real private review must use independent reviewer labels before reporting inter-annotator agreement.",
        "- Agreement is necessary but not sufficient; adjudication and qid-only promotion still gate headline claims.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=ROOT / "reports" / "route_agreement_workflow_fixture.md")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    with tempfile.TemporaryDirectory() as tmpdir:
        report = build_report(Path(tmpdir))

    if args.check:
        current = args.out.read_text(encoding="utf-8") if args.out.exists() else ""
        if current != report:
            print("route agreement workflow report is stale; run scripts/reproduce_route_agreement_workflow.py")
            return 1
        print("route agreement workflow report is current")
        return 0

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(report, encoding="utf-8")
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
