#!/usr/bin/env python3
"""Build the short public reviewer walkthrough."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.build_hero_signal import HeroSignals, load_signals  # noqa: E402


def render_reviewer_demo(signals: HeroSignals) -> str:
    fallback_drop = signals.keyword_context_policy - signals.cohort_context_policy
    lines = [
        "# Reviewer Demo Path",
        "",
        "Status: **3-minute diagnostic walkthrough; human-gold headline claims blocked**.",
        "",
        "This is the shortest public path through the repository. It is written for",
        "a reviewer who wants to understand the study artifact before reading code.",
        "",
        "## Three-Minute Path",
        "",
        "| step | artifact | what to check | expected read |",
        "|---:|---|---|---|",
        "| 1 | `README.md` + diagnostic figure | Start with the thesis and first-screen signals. | The repo leads with findings and claim limits, not framework features. |",
        "| 2 | `reports/hero_signal.md` | Inspect the compact evidence table behind the figure. | Clause recovery, source routing, surface spread, and the human-label gate are visible together. |",
        "| 3 | `reports/claim_ledger.md` | Compare allowed wording with blocked wording. | Diagnostic claims are separated from final benchmark claims. |",
        "| 4 | `docs/source_catalog.json` + `reports/source_catalog_coverage.md` | Check the source-tier catalog. | The evaluation is multi-source, not policy-clause-only retrieval. |",
        "| 5 | `docs/source_inventory.json` + `reports/source_inventory_readiness.md` | Check private source readiness. | Non-policy demanded source tiers remain blocked until inventory and rights review are complete. |",
        "| 6 | `probes/ko_evidence_probe_v0/` + `reports/probe_privacy_report.md` | Inspect the public probe package and screen. | The released probes are synthetic, intent-level, and privacy-screened. |",
        "| 7 | `probes/ko_evidence_probe_v0/DATASET_CARD.md` + `reports/probe_dataset_card.md` | Check the release-facing probe card. | The public probe has generated row counts, intended use, non-goals, and privacy notes. |",
        "| 8 | `reports/probe_beir_export.md` + `probes/ko_evidence_probe_v0/beir/` | Check the standard retrieval export. | The public probe can be consumed by BEIR-style tooling while route and abstention labels stay in metadata. |",
        "| 9 | `reports/probe_system_comparison.md` | Check the runnable public systems. | Lexical, semantic, hybrid, and source-route-aware retrieval are compared on the same probe. |",
        "| 10 | `reports/probe_trap_mining.md` | Inspect trap-class mining. | Analyzer and intent-fragmentation traps are mined as diagnostics, not as dictionary entries. |",
        "| 11 | `reports/surface_fragmentation_audit.md` | Check seed-counting bias. | Exact lexical seeds undercount same-intent surface variants; the output is an audit, not a synonym list. |",
        "| 12 | `reports/qualitative_gallery.md` | Read concrete side-by-side failure examples. | The route diagnostics are inspectable, not only aggregate tables. |",
        "| 13 | `reports/layer_attribution_fixture.md` | Inspect the failure-layer decomposition hook. | The study can explain where failures accumulate, not only whether a run passed. |",
        "| 14 | `reports/route_agreement_workflow_fixture.md` | Check the source-route agreement rehearsal. | Independent route labels can be validated and summarized before adjudication. |",
        "| 15 | `reports/answer_quality_audit_fixture.md` | Check the answer-quality audit rehearsal. | Retrieval hit metrics are not answer-quality claims; sufficiency and unsafe answers need separate labels. |",
        "| 16 | `reports/answer_review_workflow_fixture.md` | Check the answer-review CSV roundtrip. | The answer-quality label path can be exported, validated, imported, and promoted without publishing private rows. |",
        "| 17 | `reports/answer_agreement_workflow_fixture.md` | Check the answer-agreement rehearsal. | Two reviewer fields can be validated and summarized without exposing private rows. |",
        "| 18 | `reports/system_matrix.md` | Check which systems are actually backed by evidence. | The full analyzer/dense/hybrid/reranker matrix is explicit and incomplete. |",
        "| 19 | `reports/system_matrix_submission_pack_fixture.md` + `fixtures/system_matrix_submission_template/` | Inspect the qid-only matrix handoff template. | Missing analyzer, dense, hybrid, and reranker runs have a concrete submission shape without raw text. |",
        "| 20 | `reports/system_matrix_bundle_fixture.md` | Inspect the qid-only run-bundle contract. | Future analyzer, dense, hybrid, and reranker runs have an import and leakage-check path. |",
        "| 21 | `reports/system_matrix_promotion_fixture.md` | Check the matrix promotion rehearsal. | A validated fixture bundle is still blocked from updating the matrix without scale and real-run provenance. |",
        "| 22 | `reports/measurement_study_draft.md` | Read the aggregate-only study draft. | The report is the product; code exists to regenerate and check it. |",
        "| 23 | `reports/human_gold_rehearsal_fixture.md` | Verify the synthetic completed-label path. | Once real labels exist, the promotion and scorecard path is already rehearsed. |",
        "| 24 | `reports/study_readiness.md` | Confirm the remaining gate. | Headline claims stay blocked until human labels are complete and validated. |",
        "",
        "## One Command",
        "",
        "```bash",
        "make verify",
        "```",
        "",
        "`make verify` reruns the tests, synthetic reproductions, generated-report",
        "drift checks, readiness gate, and public-safety scan. To regenerate this",
        "walkthrough only, run:",
        "",
        "```bash",
        "make build-reviewer-demo",
        "```",
        "",
        "Containerized review path:",
        "",
        "```bash",
        "make docker-demo",
        "```",
        "",
        "`make docker-demo` builds the local image and reruns the fixture table,",
        "layer attribution, readiness gate, probe privacy screen, public probe",
        "source-catalog check, source-inventory check, dataset card, BEIR export, system comparison, trap-mining check, surface-fragmentation audit, qualitative gallery check, route-agreement workflow check, answer-quality audit check, answer-review workflow check, answer-agreement workflow check, system matrix submission-pack check, system matrix bundle check, system matrix promotion check, system matrix check,",
        "generated-report checks, and public-safety scan inside the container.",
        "",
        "## Current Diagnostic Signals",
        "",
        "| signal | value | claim status |",
        "|---|---:|---|",
        f"| retrieval eval rows | {signals.retrieval_n} | silver diagnostic |",
        f"| `clause@20` pack to cross-text | {signals.pack_clause20} -> {signals.cross_clause20} | diagnostic, not answer quality |",
        f"| route accuracy always-policy to cohort-aware | {signals.always_route} -> {signals.cohort_route} | diagnostic, not human-validated |",
        f"| context-needed policy fallback drop | {signals.keyword_context_policy} -> {signals.cohort_context_policy} ({fallback_drop} fewer rows) | diagnostic |",
        f"| worst surface `clause@20` | {signals.worst_surface_clause20} | surface robustness not solved |",
        f"| paired human-label seed | {signals.paired_rows}/50; kappa {signals.kappa} | headline blocked |",
        f"| adjudicated route labels | {signals.completed_labels}/300; {signals.validation_errors} validation errors | headline blocked |",
        "",
        "## What Not To Infer",
        "",
        "- Do not treat the silver diagnostics as final benchmark numbers.",
        "- Do not claim the result represents all Korean retrieval systems or domains.",
        "- Do not infer raw user text, source-specific platform names, or copyrighted",
        "  corpus content from the public reports.",
        "- Do not read the normalization and surface reports as a dictionary product;",
        "  they are measurement slices for retrieval behavior.",
        "",
        "## Reviewer Decision",
        "",
        "For a technical review, the current repo can be evaluated as a reproducible",
        "measurement-study shell with visible judgment about claim control. It should",
        "not yet be evaluated as a completed human-gold benchmark. The next decisive",
        "step is to complete the 50-row agreement seed and 300-row adjudicated",
        "route-label workset, then regenerate the study draft from human labels.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=ROOT / "reports" / "reviewer_demo.md")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    report = render_reviewer_demo(load_signals(ROOT))
    if args.check:
        current = args.out.read_text(encoding="utf-8") if args.out.exists() else ""
        if current != report:
            print("reviewer demo is stale; run scripts/build_reviewer_demo.py")
            return 1
        print("reviewer demo is current")
        return 0

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(report, encoding="utf-8")
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
