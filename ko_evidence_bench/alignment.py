"""Flagship artifact alignment checks."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .study_readiness import StudyReadiness, load_study_readiness, read


@dataclass(frozen=True)
class AlignmentItem:
    area: str
    status: str
    evidence: str
    why_it_matters: str


def has_text(path: Path, needle: str) -> bool:
    return path.exists() and needle in read(path)


def has_all_text(path: Path, needles: list[str]) -> bool:
    if not path.exists():
        return False
    text = read(path)
    return all(needle in text for needle in needles)


def load_alignment_items(root: Path) -> list[AlignmentItem]:
    readiness = load_study_readiness(root)
    return [
        AlignmentItem(
            area="Report-first artifact",
            status="PASS" if (root / "reports" / "measurement_study_draft.md").exists() else "MISSING",
            evidence="reports/measurement_study_draft.md",
            why_it_matters="The study is the product; code is the reproduction apparatus.",
        ),
        AlignmentItem(
            area="Generated finding table",
            status=(
                "PASS"
                if has_text(root / "reports" / "measurement_study_draft.md", "## Current Finding Candidates")
                else "MISSING"
            ),
            evidence="finding candidates are generated from aggregate reports",
            why_it_matters="Reviewers see numbers and claim controls before framework plumbing.",
        ),
        AlignmentItem(
            area="Hero diagnostic figure",
            status=(
                "PASS"
                if (root / "scripts" / "build_hero_signal.py").exists()
                and has_text(root / "README.md", "reports/figures/diagnostic_signal_heatmap.svg")
                and has_text(root / "reports" / "hero_signal.md", "Status: **diagnostic only")
                and has_text(root / "reports" / "figures" / "diagnostic_signal_heatmap.svg", "diagnostic signals")
                and has_text(root / "Makefile", "check-hero-signal")
                else "MISSING"
            ),
            evidence="README hero figure and report are generated from aggregate diagnostics",
            why_it_matters="The first screen leads with memorable findings while keeping the claim gate visible.",
        ),
        AlignmentItem(
            area="Claim-control gate",
            status="PASS" if (root / "reports" / "study_readiness.md").exists() else "MISSING",
            evidence=f"study readiness is {readiness.status}",
            why_it_matters="The repo refuses to promote silver diagnostics as final benchmark claims.",
        ),
        AlignmentItem(
            area="Claim wording ledger",
            status=(
                "PASS"
                if (root / "scripts" / "build_claim_ledger.py").exists()
                and has_text(root / "reports" / "claim_ledger.md", "Status: **diagnostic claims only")
                and has_text(root / "reports" / "claim_ledger.md", "do not say")
                and has_text(root / "reports" / "claim_ledger.md", "Human-gold benchmark")
                and has_text(root / "Makefile", "check-claim-ledger")
                else "MISSING"
            ),
            evidence="generated ledger separates allowed diagnostic wording from blocked claims",
            why_it_matters="The repo shows judgment about what the evidence can and cannot support.",
        ),
        AlignmentItem(
            area="Reviewer demo path",
            status=(
                "PASS"
                if (root / "scripts" / "build_reviewer_demo.py").exists()
                and has_text(root / "README.md", "reports/reviewer_demo.md")
                and has_text(root / "reports" / "reviewer_demo.md", "Status: **3-minute diagnostic walkthrough")
                and has_text(root / "reports" / "reviewer_demo.md", "What Not To Infer")
                and has_text(root / "Makefile", "check-reviewer-demo")
                else "MISSING"
            ),
            evidence="generated 3-minute walkthrough links findings, claim controls, rehearsal, and readiness",
            why_it_matters="A reviewer can understand the study artifact before reading framework code.",
        ),
        AlignmentItem(
            area="Containerized reproduction path",
            status=(
                "PASS"
                if (root / "Dockerfile").exists()
                and (root / ".dockerignore").exists()
                and has_text(root / "Makefile", "docker-demo")
                and has_text(root / "README.md", "make docker-demo")
                and has_text(root / "reports" / "reviewer_demo.md", "make docker-demo")
                else "MISSING"
            ),
            evidence="Dockerfile plus make docker-demo reruns the fixture table and claim-control checks",
            why_it_matters="A reviewer can reproduce the public demo without first configuring a Python environment.",
        ),
        AlignmentItem(
            area="Public probe set and privacy screen",
            status=(
                "PASS"
                if (root / "probes" / "ko_evidence_probe_v0" / "queries.jsonl").exists()
                and (root / "probes" / "ko_evidence_probe_v0" / "qrels.jsonl").exists()
                and (root / "probes" / "ko_evidence_probe_v0" / "evidence.jsonl").exists()
                and (root / "scripts" / "check_probe_privacy.py").exists()
                and has_text(root / "reports" / "probe_privacy_report.md", "Status: **PASS**")
                and has_text(root / "Makefile", "check-probe-privacy")
                and has_text(root / "README.md", "probes/ko_evidence_probe_v0")
                else "MISSING"
            ),
            evidence="synthetic queries, intent-level qrels, evidence snippets, and privacy-screen report",
            why_it_matters="The released instrument is a screened probe set, not a dictionary or private-data dump.",
        ),
        AlignmentItem(
            area="Public probe dataset card",
            status=(
                "PASS"
                if (root / "scripts" / "build_probe_dataset_card.py").exists()
                and (root / "probes" / "ko_evidence_probe_v0" / "DATASET_CARD.md").exists()
                and has_text(root / "probes" / "ko_evidence_probe_v0" / "DATASET_CARD.md", "synthetic public fixture")
                and has_text(root / "probes" / "ko_evidence_probe_v0" / "DATASET_CARD.md", "Not Intended Use")
                and has_text(root / "reports" / "probe_dataset_card.md", "dataset card generated from public probe files")
                and has_text(root / "Makefile", "check-probe-dataset-card")
                else "MISSING"
            ),
            evidence="generated dataset card records intended use, non-goals, distributions, and privacy notes",
            why_it_matters="The public probe is packaged like a reusable IR artifact instead of a loose fixture folder.",
        ),
        AlignmentItem(
            area="BEIR-style public probe export",
            status=(
                "PASS"
                if (root / "ko_evidence_bench" / "beir_export.py").exists()
                and (root / "scripts" / "export_probe_beir.py").exists()
                and (root / "probes" / "ko_evidence_probe_v0" / "beir" / "corpus.jsonl").exists()
                and (root / "probes" / "ko_evidence_probe_v0" / "beir" / "queries.jsonl").exists()
                and (root / "probes" / "ko_evidence_probe_v0" / "beir" / "qrels" / "test.tsv").exists()
                and has_text(root / "reports" / "probe_beir_export.md", "BEIR-style retrieval subset")
                and has_text(root / "reports" / "probe_beir_export.md", "abstention rows skipped from BEIR qrels")
                and has_text(root / "Makefile", "check-probe-beir")
                else "MISSING"
            ),
            evidence="public probe rows are exported to corpus, queries, qrels, and metadata files",
            why_it_matters="The public probe can plug into standard IR tooling without hiding route and abstention limits.",
        ),
        AlignmentItem(
            area="Runnable public probe systems",
            status=(
                "PASS"
                if (root / "ko_evidence_bench" / "probe_systems.py").exists()
                and (root / "scripts" / "reproduce_probe_system_comparison.py").exists()
                and has_text(root / "reports" / "probe_system_comparison.md", "Public Probe System Comparison")
                and has_text(root / "reports" / "probe_system_comparison.md", "probe_semantic_centroid")
                and has_text(root / "reports" / "probe_system_comparison.md", "probe_hybrid_lexical_semantic")
                and has_text(root / "reports" / "probe_system_comparison.md", "probe_route_aware_rerank")
                and has_text(root / "reports" / "system_matrix.md", "probe_route_aware_rerank")
                and has_text(root / "Makefile", "check-probe-system-comparison")
                else "MISSING"
            ),
            evidence="lexical, semantic, hybrid, and route-aware probe systems run on the same public fixture",
            why_it_matters="The public probe is executable evidence, not only a static dataset or dictionary.",
        ),
        AlignmentItem(
            area="Trap-mining diagnostic",
            status=(
                "PASS"
                if (root / "ko_evidence_bench" / "trap_miner.py").exists()
                and (root / "scripts" / "reproduce_probe_trap_mining.py").exists()
                and has_text(root / "reports" / "probe_trap_mining.md", "Public Probe Trap Mining")
                and has_text(root / "reports" / "probe_trap_mining.md", "not a synonym dictionary")
                and has_text(root / "reports" / "probe_trap_mining.md", "Extra Diagnostic Traps")
                and has_text(root / "Makefile", "check-probe-trap-mining")
                else "MISSING"
            ),
            evidence="public probe queries are mined for trap classes and compared with qrel annotations",
            why_it_matters="Analyzer and intent-fragmentation failures are measured as diagnostics, not shipped as a dictionary.",
        ),
        AlignmentItem(
            area="Surface-fragmentation undercount audit",
            status=(
                "PASS"
                if (root / "ko_evidence_bench" / "surface_fragmentation.py").exists()
                and (root / "scripts" / "reproduce_surface_fragmentation_audit.py").exists()
                and has_text(root / "reports" / "surface_fragmentation_audit.md", "Surface Fragmentation Audit")
                and has_text(root / "reports" / "surface_fragmentation_audit.md", "aggregate undercount factor")
                and has_text(root / "reports" / "surface_fragmentation_audit.md", "not a production synonym list")
                and has_text(root / "Makefile", "check-surface-fragmentation-audit")
                else "MISSING"
            ),
            evidence="public probe intents compare exact lexical seed counts with qrel-level surface variants",
            why_it_matters="The repo measures the user's undercount critique instead of turning aliases into a dictionary.",
        ),
        AlignmentItem(
            area="Qualitative failure gallery",
            status=(
                "PASS"
                if (root / "scripts" / "build_qualitative_gallery.py").exists()
                and has_text(root / "reports" / "qualitative_gallery.md", "Status: **synthetic qualitative examples only")
                and has_text(root / "reports" / "qualitative_gallery.md", "policy_only_baseline")
                and has_text(root / "reports" / "qualitative_gallery.md", "source_routed_candidate")
                and has_text(root / "Makefile", "check-qualitative-gallery")
                else "MISSING"
            ),
            evidence="synthetic side-by-side ranking examples generated from the public probe package",
            why_it_matters="Reviewers can inspect concrete failure modes instead of only aggregate metrics.",
        ),
        AlignmentItem(
            area="README signal drift guard",
            status=(
                "PASS"
                if has_text(root / "README.md", "<!-- BEGIN: current-verified-signals -->")
                else "MISSING"
            ),
            evidence="scripts/sync_readme_signals.py --check",
            why_it_matters="The first-screen numbers are generated from checked-in evidence.",
        ),
        AlignmentItem(
            area="Dictionary scope guard",
            status=(
                "PASS"
                if has_all_text(
                    root / "README.md",
                    [
                        "This is not an insurance advice system, a chatbot, or a Korean dictionary.",
                        "retrieval evaluation workbench",
                    ],
                )
                else "MISSING"
            ),
            evidence="README scope statement rejects a dictionary-first framing",
            why_it_matters="The flagship has to be a measurement artifact, not a user-dictionary repo.",
        ),
        AlignmentItem(
            area="Multi-source evidence frame",
            status=(
                "PASS"
                if has_all_text(
                    root / "docs" / "route_label_protocol.md",
                    [
                        "`policy_clause`",
                        "`product_disclosure`",
                        "`official_consumer_info`",
                        "`claims_faq`",
                        "`dispute_case`",
                        "`expert_answer`",
                        "`human_context_needed`",
                    ],
                )
                and has_text(root / "README.md", "source tier")
                and has_text(root / "reports" / "measurement_study_draft.md", "source-specific evidence")
                else "MISSING"
            ),
            evidence="route protocol and study draft model multiple citable source tiers",
            why_it_matters="The benchmark tests evidence routing, not only policy-clause recall.",
        ),
        AlignmentItem(
            area="Real-query substrate inventory",
            status=(
                "PASS"
                if has_all_text(
                    root / "README.md",
                    [
                        "derived real-user query candidates from community crawls",
                        "messenger-conversation messages",
                        "community Q&A archive rows",
                    ],
                )
                and has_text(root / "reports" / "private_route_cohort_scorecard_silver.md", "query cohort")
                else "MISSING"
            ),
            evidence="README aggregates private query substrates and cohort scorecards compare them generically",
            why_it_matters="The study is grounded in real query distributions without exposing private source names.",
        ),
        AlignmentItem(
            area="Surface-form robustness axis",
            status=(
                "PASS"
                if (root / "ko_evidence_bench" / "surface.py").exists()
                and (root / "scripts" / "reproduce_surface_scorecard.py").exists()
                and has_text(root / "reports" / "surface_scorecard_fixture.md", "avg_intent_spread")
                and has_text(root / "reports" / "surface_lift_gate.md", "Status: **PASS**")
                and has_text(root / "docs" / "schemas.md", "intent_id")
                and has_text(root / "docs" / "schemas.md", "surface_form")
                else "MISSING"
            ),
            evidence="surface-form scorecard and lift gate measure same-intent robustness across phrasing conditions",
            why_it_matters="This implements the intent-fragmentation axis, not token dictionaries.",
        ),
        AlignmentItem(
            area="Route-surface diagnostic axis",
            status=(
                "PASS"
                if (root / "ko_evidence_bench" / "route_surface.py").exists()
                and (root / "scripts" / "reproduce_route_surface_scorecard.py").exists()
                and has_text(root / "reports" / "route_surface_scorecard_fixture.md", "Route Surface Summary")
                and has_text(root / "reports" / "private_route_surface_scorecard_silver.md", "Private Route Surface Scorecard")
                and has_text(root / "reports" / "measurement_study_draft.md", "Route Surface Evidence")
                else "MISSING"
            ),
            evidence="route-only scorecard slices source-route and abstention behavior by surface, intent family, and trap class",
            why_it_matters="The study can separate surface-conditioned routing failures from retrieval-hit failures.",
        ),
        AlignmentItem(
            area="Runtime-surface retrieval-hit axis",
            status=(
                "PASS"
                if (root / "ko_evidence_bench" / "runtime_surface.py").exists()
                and (root / "scripts" / "reproduce_runtime_surface_scorecard.py").exists()
                and has_text(root / "reports" / "runtime_surface_scorecard_fixture.md", "Runtime Surface Summary")
                and has_text(
                    root / "reports" / "private_runtime_surface_scorecard_silver.md",
                    "Private Runtime Surface Scorecard",
                )
                and has_text(root / "reports" / "measurement_study_draft.md", "Private runtime-surface diagnostics")
                else "MISSING"
            ),
            evidence="runtime hit booleans are sliced by surface form, intent family, and trap class without raw evidence ids",
            why_it_matters="This moves surface robustness from fixture-only demos into actual retrieval-hit diagnostics.",
        ),
        AlignmentItem(
            area="Layer attribution axis",
            status=(
                "PASS"
                if (root / "ko_evidence_bench" / "layer_attribution.py").exists()
                and (root / "scripts" / "reproduce_layer_attribution.py").exists()
                and has_text(root / "reports" / "layer_attribution_fixture.md", "Failure Mass By Layer")
                and has_text(root / "reports" / "layer_attribution_fixture.md", "surface_fragmentation")
                and has_text(root / "reports" / "measurement_study_draft.md", "Layer Attribution Evidence")
                and has_text(root / "Makefile", "reproduce-layer-attribution")
                else "MISSING"
            ),
            evidence="failed synthetic rows are decomposed into primary diagnostic layers",
            why_it_matters="The study can explain where failures accumulate instead of only reporting aggregate scores.",
        ),
        AlignmentItem(
            area="Answer-quality audit rehearsal",
            status=(
                "PASS"
                if (root / "ko_evidence_bench" / "answer_audit.py").exists()
                and (root / "scripts" / "reproduce_answer_quality_audit.py").exists()
                and has_text(root / "reports" / "answer_quality_audit_fixture.md", "PASS synthetic answer-quality audit rehearsal")
                and has_text(root / "reports" / "answer_quality_audit_fixture.md", "not human-gold answer-quality evidence")
                and has_text(root / "reports" / "answer_quality_audit_fixture.md", "not a final benchmark claim")
                and has_text(root / "Makefile", "check-answer-quality-audit")
                else "MISSING"
            ),
            evidence="synthetic qid-only labels validate answer sufficiency, correct abstention, and unsafe answers",
            why_it_matters="Retrieval-hit metrics are not final answer-quality claims; the audit path keeps that boundary explicit.",
        ),
        AlignmentItem(
            area="System comparison matrix guard",
            status=(
                "PASS"
                if (root / "ko_evidence_bench" / "system_matrix.py").exists()
                and (root / "docs" / "system_matrix.json").exists()
                and (root / "scripts" / "build_system_matrix_report.py").exists()
                and has_text(root / "reports" / "system_matrix.md", "INCOMPLETE for full comparison matrix")
                and has_text(root / "reports" / "system_matrix.md", "dense_multilingual_encoder")
                and has_text(root / "reports" / "system_matrix.md", "hybrid_lexical_dense")
                and has_text(root / "Makefile", "check-system-matrix-report")
                else "MISSING"
            ),
            evidence="system matrix report separates implemented diagnostics from not-run and blocked comparisons",
            why_it_matters="The repo must not imply the full analyzer/dense/hybrid/reranker matrix has already been run.",
        ),
        AlignmentItem(
            area="Full-matrix run-bundle contract",
            status=(
                "PASS"
                if (root / "ko_evidence_bench" / "system_matrix_bundle.py").exists()
                and (root / "scripts" / "validate_system_matrix_bundle.py").exists()
                and (root / "fixtures" / "system_matrix_bundle" / "manifest.json").exists()
                and has_text(root / "reports" / "system_matrix_bundle_fixture.md", "PASS synthetic full-matrix run-bundle rehearsal")
                and has_text(root / "reports" / "system_matrix_bundle_fixture.md", "required runnable systems | 7")
                and has_text(root / "reports" / "system_matrix_bundle_fixture.md", "validation errors | 0")
                and has_text(root / "Makefile", "check-system-matrix-bundle")
                else "MISSING"
            ),
            evidence="synthetic qid-only bundle validates import, coverage, leakage, and scoring for the missing systems",
            why_it_matters="The missing full matrix now has a checked artifact contract instead of an undefined handoff.",
        ),
        AlignmentItem(
            area="Full-matrix promotion gate",
            status=(
                "PASS"
                if (root / "ko_evidence_bench" / "system_matrix_promotion.py").exists()
                and (root / "scripts" / "rehearse_system_matrix_promotion.py").exists()
                and has_text(
                    root / "reports" / "system_matrix_promotion_fixture.md",
                    "BLOCKED synthetic promotion rehearsal; no matrix update",
                )
                and has_text(
                    root / "reports" / "system_matrix_promotion_fixture.md",
                    "Do not update `docs/system_matrix.json` from this fixture.",
                )
                and has_text(root / "Makefile", "check-system-matrix-promotion")
                else "MISSING"
            ),
            evidence="promotion gates reject the synthetic bundle until scale and real-run provenance exist",
            why_it_matters="The repo can accept future full-matrix runs without pretending fixture outputs are model evidence.",
        ),
        AlignmentItem(
            area="Intent-family inventory axis",
            status=(
                "PASS"
                if (root / "ko_evidence_bench" / "intent_inventory.py").exists()
                and (root / "scripts" / "build_intent_inventory.py").exists()
                and has_text(root / "reports" / "intent_inventory_fixture.md", "Intent Family Summary")
                and has_text(root / "reports" / "intent_inventory_fixture.md", "Trap-Class Distribution")
                and has_text(root / "docs" / "schemas.md", "intent_family")
                and has_text(root / "docs" / "schemas.md", "trap_classes")
                and has_text(root / "reports" / "private_intent_inventory_silver.md", "Private Intent-Family Inventory")
                and has_text(root / "reports" / "private_intent_surface_export_summary.md", "exported qid-only rows: 544")
                else "MISSING"
            ),
            evidence="fixture and private silver inventories treat intent families, surface forms, and trap classes as aggregate slices",
            why_it_matters="This moves the flagship design from synthetic slices into the private qid-only qrel path.",
        ),
        AlignmentItem(
            area="Normalization ablation axis",
            status=(
                "PASS"
                if (root / "ko_evidence_bench" / "ablation.py").exists()
                and (root / "scripts" / "reproduce_normalization_ablation.py").exists()
                and has_text(root / "reports" / "normalization_ablation_fixture.md", "Lift By Intent Family")
                and has_text(root / "reports" / "normalization_ablation_fixture.md", "rescued rows | 5")
                and has_text(root / "reports" / "normalization_ablation_fixture.md", "not a query-rewrite product")
                else "MISSING"
            ),
            evidence="normalization ablation reports aggregate rescue/regression by intent family and surface",
            why_it_matters="This validates normalization as measured lift, not a standalone dictionary artifact.",
        ),
        AlignmentItem(
            area="Qid-only route scorecard path",
            status=(
                "PASS"
                if (root / "reports" / "private_route_scorecard_silver.md").exists()
                and (root / "scripts" / "export_route_runs.py").exists()
                else "MISSING"
            ),
            evidence="private silver runs are scored through the same path as future human labels",
            why_it_matters="The evaluation path is tested before human-gold labels arrive.",
        ),
        AlignmentItem(
            area="Per-source route failure slices",
            status=(
                "PASS"
                if has_text(root / "reports" / "route_scorecard_fixture.md", "## Route Accuracy By Gold Source Tier")
                and has_text(root / "reports" / "route_scorecard_fixture.md", "## Largest Route Confusions")
                and has_text(root / "reports" / "private_route_scorecard_silver.md", "## Route Accuracy By Gold Source Tier")
                and has_text(root / "reports" / "measurement_study_draft.md", "Largest silver confusion")
                else "MISSING"
            ),
            evidence="route scorecards expose source-tier slices and largest route confusions",
            why_it_matters="The study can explain where routing fails, not just report one aggregate number.",
        ),
        AlignmentItem(
            area="Query-cohort route slices",
            status=(
                "PASS"
                if (root / "scripts" / "reproduce_route_cohort_scorecard.py").exists()
                and (root / "fixtures" / "source_cohort_map.json").exists()
                and has_text(root / "reports" / "route_cohort_scorecard_fixture.md", "## Route Metrics By Query Cohort")
                and has_text(root / "reports" / "private_route_cohort_scorecard_silver.md", "unmapped source rows: 0")
                and has_text(root / "reports" / "measurement_study_draft.md", "Private query-cohort diagnostics")
                else "MISSING"
            ),
            evidence="source-map cohort scorecards compare query substrates without raw source names",
            why_it_matters="The study can test whether failures differ across real query cohorts.",
        ),
        AlignmentItem(
            area="Query-substrate profile",
            status=(
                "PASS"
                if (root / "scripts" / "profile_query_substrates.py").exists()
                and (root / "reports" / "substrate_profile_fixture.md").exists()
                and (root / "reports" / "private_query_substrate_profile.md").exists()
                and has_text(root / "reports" / "measurement_study_draft.md", "Query Substrate Evidence")
                else "MISSING"
            ),
            evidence="aggregate shape profile compares community post contexts, cleaned eval queries, and live-style conversation turns",
            why_it_matters="The study shows why query cohorts need different stress slices instead of treating all text as one corpus.",
        ),
        AlignmentItem(
            area="Cohort-aware routing baseline",
            status=(
                "PASS"
                if has_text(root / "ko_evidence_bench" / "route_router.py", "cohort_aware_query_route")
                and has_text(root / "reports" / "private_route_router_baselines.md", "cohort_aware_query_router")
                and has_text(root / "reports" / "private_router_lift_gate.md", "Status: **PASS**")
                and has_text(root / "reports" / "measurement_study_draft.md", "+25.4%p")
                and has_text(root / "reports" / "private_route_run_export_summary.md", "systems: 4")
                else "MISSING"
            ),
            evidence="cohort-aware router is exported, scored, and guarded by a silver lift gate",
            why_it_matters="The repo shows a measured routing improvement, not only an evaluation shell.",
        ),
        AlignmentItem(
            area="Human audit workflow",
            status=(
                "PASS"
                if (root / "tools" / "route_review_ui.html").exists()
                and (root / "reports" / "route_audit_workflow_fixture.md").exists()
                else "MISSING"
            ),
            evidence="review UI plus synthetic audit workflow dry-run",
            why_it_matters="The remaining work is label production, not missing audit plumbing.",
        ),
        AlignmentItem(
            area="Human-label progress gate",
            status=(
                "PASS"
                if (root / "scripts" / "check_route_review_progress.py").exists()
                and (root / "scripts" / "validate_route_review_csv.py").exists()
                and (root / "scripts" / "build_route_review_brief.py").exists()
                and (root / "scripts" / "build_route_review_batch.py").exists()
                and (root / "scripts" / "merge_route_review_batch.py").exists()
                and (root / "reports" / "private_route_review_brief_300_adjudicated.md").exists()
                and (root / "reports" / "private_route_review_batch_priority_50_summary.md").exists()
                and (root / "reports" / "private_route_review_batch_merge_priority_50_summary.md").exists()
                and (root / "reports" / "private_route_review_progress_300_adjudicated.md").exists()
                and (root / "reports" / "private_route_review_csv_validation_300_adjudicated.md").exists()
                else "MISSING"
            ),
            evidence="300-row brief, priority batch, merge dry-run, progress, and CSV validation are summarized without raw rows",
            why_it_matters="The remaining human task can be prioritized, started, merged, and tracked before import.",
        ),
        AlignmentItem(
            area="Human-audit coverage gate",
            status=(
                "PASS"
                if (root / "ko_evidence_bench" / "audit_coverage.py").exists()
                and (root / "scripts" / "check_audit_surface_coverage.py").exists()
                and has_text(root / "reports" / "audit_surface_coverage_fixture.md", "Status: **PASS**")
                and has_text(root / "reports" / "private_audit_surface_coverage_300.md", "Status: **PASS**")
                and has_text(root / "reports" / "measurement_study_draft.md", "Human Audit Coverage")
                else "MISSING"
            ),
            evidence="300-row private audit workset covers route, intent-family, surface-form, and trap-class axes",
            why_it_matters="The human-gold workset must preserve the surface/intent design before reviewers spend time.",
        ),
        AlignmentItem(
            area="Human-gold promotion rehearsal",
            status=(
                "PASS"
                if (root / "scripts" / "reproduce_human_gold_rehearsal.py").exists()
                and has_text(root / "Makefile", "reproduce-human-gold-rehearsal")
                and has_text(root / "reports" / "human_gold_rehearsal_fixture.md", "Status: **PASS**")
                and has_text(root / "reports" / "human_gold_rehearsal_fixture.md", "promoted qid-only labels")
                and has_text(root / "reports" / "human_gold_rehearsal_fixture.md", "Route-Surface Rehearsal")
                else "MISSING"
            ),
            evidence="synthetic completed labels validate, promote, and feed route plus route-surface scorecards",
            why_it_matters="Once real labels are finished, the remaining path to measurement-study scorecards is already rehearsed.",
        ),
        AlignmentItem(
            area="Human-gold route labels",
            status="PASS" if readiness.headline_ready else "BLOCKED",
            evidence=(
                f"{readiness.agreement_paired_rows}/50 paired labels; "
                f"kappa {readiness.agreement_kappa:.3f}; "
                f"{readiness.completed_route_labels}/300 adjudicated labels complete; "
                f"{readiness.route_validation_errors} validation errors"
            ),
            why_it_matters="Agreement quality and adjudicated coverage are required before public headline claims.",
        ),
        AlignmentItem(
            area="Public/private boundary",
            status=(
                "PASS"
                if (root / "docs" / "data_statement.md").exists()
                and (root / "scripts" / "check_public_safety.py").exists()
                else "MISSING"
            ),
            evidence="data statement plus public-safety scan",
            why_it_matters="The private logs ground the work without leaking raw rows.",
        ),
        AlignmentItem(
            area="CI verification",
            status=(
                "PASS"
                if has_text(root / "Makefile", "check-measurement-study")
                and has_text(root / "Makefile", "check-readme-signals")
                and has_text(root / ".github" / "workflows" / "ci.yml", "make verify")
                else "MISSING"
            ),
            evidence="make verify in GitHub Actions",
            why_it_matters="The repo continuously checks reports, claims, fixtures, and safety.",
        ),
    ]


def overall_status(items: list[AlignmentItem]) -> str:
    if any(item.status == "MISSING" for item in items):
        return "INCOMPLETE"
    if any(item.status == "BLOCKED" for item in items):
        return "NO-GO FOR HEADLINE CLAIMS"
    return "GO FOR HEADLINE CLAIM REVIEW"


def render_alignment_report(items: list[AlignmentItem]) -> str:
    lines = [
        "# Flagship Alignment",
        "",
        f"Overall status: **{overall_status(items)}**.",
        "",
        "This report checks whether the repository is shaped as a measurement-study",
        "artifact rather than a loose evaluation framework. It intentionally separates",
        "implemented infrastructure from the human-label gate that still blocks public",
        "headline claims.",
        "",
        "| area | status | evidence | why it matters |",
        "|---|---|---|---|",
    ]
    for item in items:
        lines.append(
            f"| {item.area} | `{item.status}` | {item.evidence} | {item.why_it_matters} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The repo now has the public shell expected of a flagship measurement study:",
            "generated study draft, claim-control gates, reviewer walkthrough,",
            "containerized reproduction, screened public probes, dataset card,",
            "qualitative examples, layer attribution, system matrix guard,",
            "answer-quality audit rehearsal, full-matrix run-bundle contract,",
            "full-matrix promotion gate, qid-only scorecards, audit workflow,",
            "and public-safety checks. It is not headline-ready",
            "because source-route labels still lack independent agreement",
            "evidence and human-adjudicated coverage, and the full comparison",
            "matrix still has not-run or blocked systems.",
            "",
            "## Next Gate",
            "",
            "Double-label at least 50 route rows, report agreement and kappa, complete",
            "the 300-row adjudicated route-label workset, validate it with zero errors,",
            "run the missing system comparisons or narrow the claim, promote qid-only",
            "human labels, and rerun the route scorecard and measurement-study draft.",
            "",
        ]
    )
    return "\n".join(lines)
