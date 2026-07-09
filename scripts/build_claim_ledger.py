#!/usr/bin/env python3
"""Build a public claim ledger from aggregate diagnostics."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.build_hero_signal import HeroSignals, load_signals  # noqa: E402
from ko_evidence_bench.system_matrix import load_matrix, matrix_summary  # noqa: E402


@dataclass(frozen=True)
class ClaimRow:
    claim_area: str
    status: str
    allowed_wording: str
    do_not_say: str
    next_evidence: str


def claim_rows(signals: HeroSignals) -> list[ClaimRow]:
    fallback_drop = signals.keyword_context_policy - signals.cohort_context_policy
    matrix = matrix_summary(load_matrix(ROOT / "docs" / "system_matrix.json"))
    return [
        ClaimRow(
            claim_area="Clause recovery",
            status="DIAGNOSTIC",
            allowed_wording=(
                "On the private silver qrel set, cross-text reranking improved "
                f"`clause@20` from {signals.pack_clause20} to {signals.cross_clause20} "
                f"with a paired delta of +{signals.cross_delta}p "
                f"(95% CI {signals.cross_delta_ci})."
            ),
            do_not_say="This is a final benchmark result or proof of answer quality.",
            next_evidence="Re-run after human-gold source-route labels and answer-quality audit.",
        ),
        ClaimRow(
            claim_area="Source routing",
            status="DIAGNOSTIC",
            allowed_wording=(
                "On silver route labels, a cohort-aware router improved route accuracy "
                f"from {signals.always_route} to {signals.cohort_route} versus the "
                f"always-policy baseline (+{signals.cohort_delta}p, "
                f"95% CI {signals.cohort_delta_ci})."
            ),
            do_not_say="The router is human-validated or production-safe.",
            next_evidence="Complete 300 adjudicated route labels and score the same route runs.",
        ),
        ClaimRow(
            claim_area="Unsafe policy fallback",
            status="DIAGNOSTIC",
            allowed_wording=(
                "In silver diagnostics, context-needed rows routed to policy clauses "
                f"fell from {signals.keyword_context_policy} to {signals.cohort_context_policy} "
                f"rows ({fallback_drop} fewer fallback errors)."
            ),
            do_not_say="The system safely refuses all context-dependent questions.",
            next_evidence="Human-audit context-needed rows and report abstention precision/recall.",
        ),
        ClaimRow(
            claim_area="Surface robustness",
            status="DIAGNOSTIC",
            allowed_wording=(
                f"`structural_cross_text` reached {signals.cross_clause20} overall "
                f"`clause@20`, but its worst surface slice was {signals.worst_surface_clause20}, "
                f"leaving a {signals.surface_gap} spread."
            ),
            do_not_say="The system is robust to Korean surface-form variation.",
            next_evidence="Audit intent/surface metadata and rerun surface slices with human-gold labels.",
        ),
        ClaimRow(
            claim_area="Human-gold benchmark",
            status="BLOCKED",
            allowed_wording=(
                f"The human-gold gate is not open: {signals.paired_rows}/50 paired labels, "
                f"kappa {signals.kappa}, {signals.completed_labels}/300 adjudicated labels, "
                f"and {signals.validation_errors} validation errors."
            ),
            do_not_say="The private-lab numbers are final public benchmark claims.",
            next_evidence="Double-label 50 rows, complete 300 adjudications, validate with zero errors.",
        ),
        ClaimRow(
            claim_area="Full system comparison matrix",
            status="BLOCKED",
            allowed_wording=(
                f"The system matrix is explicit and incomplete: {matrix['implemented']}/"
                f"{matrix['systems']} systems are implemented, {matrix['not_run']} are not run, "
                f"and {matrix['blocked']} {'is' if matrix['blocked'] == 1 else 'are'} blocked."
            ),
            do_not_say="The analyzer, dense, hybrid, and reranker comparison matrix is complete.",
            next_evidence="Run the missing systems or narrow the claim to the implemented diagnostics.",
        ),
        ClaimRow(
            claim_area="General Korean IR",
            status="OUT OF SCOPE",
            allowed_wording=(
                "The method is intended to transfer, but the checked-in diagnostics are "
                "from one private Korean insurance search lab."
            ),
            do_not_say="The results represent all Korean retrieval or all insurance search.",
            next_evidence="Run the same scorecard on another domain or independently built corpus.",
        ),
        ClaimRow(
            claim_area="Public data release",
            status="OUT OF SCOPE",
            allowed_wording=(
                "The public repo releases schemas, metrics, synthetic fixtures, aggregate "
                "reports, and privacy-preserving reproduction paths."
            ),
            do_not_say="Raw community crawls, messenger exports, or copyrighted corpora are included.",
            next_evidence="Add only rights-cleared public fixtures or build scripts with verified licenses.",
        ),
    ]


def render_claim_ledger(signals: HeroSignals) -> str:
    lines = [
        "# Claim Ledger",
        "",
        "Status: **diagnostic claims only; human-gold headline claims blocked**.",
        "",
        "This ledger is the public wording guard for the measurement study. It",
        "separates what the checked-in aggregate evidence supports from what still",
        "needs human labels, external replication, or rights-cleared data.",
        "",
        "| claim area | status | allowed wording | do not say | next evidence |",
        "|---|---|---|---|---|",
    ]
    for row in claim_rows(signals):
        lines.append(
            "| "
            + " | ".join(
                [
                    row.claim_area,
                    f"`{row.status}`",
                    row.allowed_wording,
                    row.do_not_say,
                    row.next_evidence,
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Use Notes",
            "",
            "- README and report prose should use the allowed wording until the",
            "  human-gold gate opens.",
            "- `DIAGNOSTIC` means useful engineering evidence, not a public benchmark",
            "  headline.",
            "- `BLOCKED` means the repo has the path and fixtures, but the private",
            "  labels are not complete enough for the claim.",
            "- `OUT OF SCOPE` means the project can discuss transferability as a",
            "  hypothesis, not as a measured result.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=ROOT / "reports" / "claim_ledger.md")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    report = render_claim_ledger(load_signals(ROOT))
    if args.check:
        current = args.out.read_text(encoding="utf-8") if args.out.exists() else ""
        if current != report:
            print("claim ledger is stale; run scripts/build_claim_ledger.py")
            return 1
        print("claim ledger is current")
        return 0

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(report, encoding="utf-8")
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
