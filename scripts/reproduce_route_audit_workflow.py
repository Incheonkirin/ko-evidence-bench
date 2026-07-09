#!/usr/bin/env python3
"""Reproduce the route-audit workflow on synthetic public fixtures."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures" / "route_audit" / "audit_seed.jsonl"


LABELS_A = {
    "route-audit-0001": ("claims_faq", "claims_faq", "false", "high", "claims_ops", "reviewer-a"),
    "route-audit-0002": (
        "human_context_needed",
        "human_context_needed",
        "true",
        "high",
        "needs_private_contract",
        "reviewer-a",
    ),
    "route-audit-0003": (
        "policy_clause",
        "policy_clause",
        "false",
        "medium",
        "contract_clause_direct",
        "reviewer-a",
    ),
}

LABELS_B = {
    "route-audit-0001": ("claims_faq", "claims_faq", "false", "medium", "claims_ops", "reviewer-b"),
    "route-audit-0002": (
        "human_context_needed",
        "human_context_needed",
        "true",
        "high",
        "needs_private_contract",
        "reviewer-b",
    ),
    "route-audit-0003": (
        "product_disclosure",
        "product_disclosure",
        "false",
        "low",
        "product_table_needed",
        "reviewer-b",
    ),
}

ADJUDICATED = {
    "route-audit-0001": ("claims_faq", "claims_faq", "false", "high", "claims_ops", "adjudicator"),
    "route-audit-0002": (
        "human_context_needed",
        "human_context_needed",
        "true",
        "high",
        "needs_private_contract",
        "adjudicator",
    ),
    "route-audit-0003": (
        "policy_clause",
        "policy_clause",
        "false",
        "medium",
        "contract_clause_direct",
        "adjudicator",
    ),
}


def run(args: list[str]) -> None:
    subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def fill_csv(path: Path, labels: dict[str, tuple[str, str, str, str, str, str]]) -> None:
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
        fields = list(rows[0].keys()) if rows else []
    for row in rows:
        values = labels[row["audit_id"]]
        row.update(
            {
                "route_gold": values[0],
                "allowed_source_tiers": values[1],
                "should_abstain": values[2],
                "confidence": values[3],
                "rationale_code": values[4],
                "labeler": values[5],
                "notes": "synthetic fixture",
            }
        )
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def read_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def extract_value(report: str, prefix: str) -> str:
    for line in report.splitlines():
        if line.startswith(prefix):
            return line.split(":", 1)[1].strip()
    return ""


def workflow_report(tmp: Path) -> str:
    reviewer_a_csv = tmp / "reviewer_a.csv"
    reviewer_b_csv = tmp / "reviewer_b.csv"
    adjudicated_csv = tmp / "adjudicated.csv"
    audit_a = tmp / "audit.reviewer_a.jsonl"
    audit_ab = tmp / "audit.reviewers.jsonl"
    audit_final = tmp / "audit.adjudicated.jsonl"
    labels_out = tmp / "human_route_labels.jsonl"
    agreement_report = tmp / "agreement.md"
    validation_report = tmp / "validation.md"
    promoted_report = tmp / "promoted.md"

    run(
        [
            "scripts/export_route_review_csv.py",
            "--audit",
            str(FIXTURE),
            "--reviewer-prefix",
            "reviewer_a",
            "--csv-out",
            str(reviewer_a_csv),
        ]
    )
    fill_csv(reviewer_a_csv, LABELS_A)
    run(
        [
            "scripts/import_route_review_csv.py",
            "--audit",
            str(FIXTURE),
            "--csv",
            str(reviewer_a_csv),
            "--target-prefix",
            "reviewer_a",
            "--out",
            str(audit_a),
        ]
    )

    run(
        [
            "scripts/export_route_review_csv.py",
            "--audit",
            str(audit_a),
            "--reviewer-prefix",
            "reviewer_b",
            "--csv-out",
            str(reviewer_b_csv),
        ]
    )
    fill_csv(reviewer_b_csv, LABELS_B)
    run(
        [
            "scripts/import_route_review_csv.py",
            "--audit",
            str(audit_a),
            "--csv",
            str(reviewer_b_csv),
            "--target-prefix",
            "reviewer_b",
            "--out",
            str(audit_ab),
        ]
    )

    run(
        [
            "scripts/summarize_route_audit.py",
            "--audit",
            str(audit_ab),
            "--field-a",
            "reviewer_a.route_gold",
            "--field-b",
            "reviewer_b.route_gold",
            "--report-out",
            str(agreement_report),
        ]
    )

    run(
        [
            "scripts/export_route_review_csv.py",
            "--audit",
            str(audit_ab),
            "--reviewer-prefix",
            "adjudicated",
            "--csv-out",
            str(adjudicated_csv),
        ]
    )
    fill_csv(adjudicated_csv, ADJUDICATED)
    run(
        [
            "scripts/import_route_review_csv.py",
            "--audit",
            str(audit_ab),
            "--csv",
            str(adjudicated_csv),
            "--target-prefix",
            "adjudicated",
            "--out",
            str(audit_final),
        ]
    )

    run(
        [
            "scripts/validate_route_audit.py",
            "--audit",
            str(audit_final),
            "--label-prefix",
            "adjudicated",
            "--require-complete",
            "--report-out",
            str(validation_report),
        ]
    )
    run(
        [
            "scripts/promote_route_audit.py",
            "--audit",
            str(audit_final),
            "--label-prefix",
            "adjudicated",
            "--labels-out",
            str(labels_out),
            "--report-out",
            str(promoted_report),
        ]
    )

    agreement = agreement_report.read_text(encoding="utf-8")
    validation = validation_report.read_text(encoding="utf-8")
    promoted = promoted_report.read_text(encoding="utf-8")
    labels = read_jsonl(labels_out)
    kappa = extract_value(agreement, "- Cohen's kappa")

    lines = [
        "# Route Audit Workflow Fixture",
        "",
        "This synthetic dry-run exercises CSV export, CSV import, reviewer agreement,",
        "adjudication validation, and qid-only label promotion without private data.",
        "",
        f"- fixture audit rows: {len(read_jsonl(FIXTURE))}",
        f"- paired reviewer rows: {extract_value(agreement, '- paired completed rows')}",
        f"- reviewer raw agreement: {extract_value(agreement, '- raw agreement')}",
        f"- reviewer Cohen's kappa: {kappa}",
        f"- adjudication validation errors: {extract_value(validation, '- rows with validation errors')}",
        f"- promoted labels: {len(labels)}",
        "",
        "## Promoted Route Distribution",
        "",
        "| route | count |",
        "|---|---:|",
    ]
    counts: dict[str, int] = {}
    for label in labels:
        counts[label["route_gold"]] = counts.get(label["route_gold"], 0) + 1
    for route, count in sorted(counts.items()):
        lines.append(f"| `{route}` | {count} |")
    return "\n".join(lines) + "\n"


def main() -> None:
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    with tempfile.TemporaryDirectory() as tmp_name:
        report = workflow_report(Path(tmp_name))
    if out:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(report, encoding="utf-8")
    else:
        print(report, end="")


if __name__ == "__main__":
    main()
