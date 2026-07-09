DOCKER_IMAGE ?= ko-evidence-bench:local

.PHONY: test check-public-safety check-study-readiness check-readme-signals check-router-lift check-surface-lift build-hero-signal check-hero-signal build-claim-ledger check-claim-ledger build-reviewer-demo check-reviewer-demo build-probe-privacy-report check-probe-privacy reproduce-probe-system-comparison check-probe-system-comparison reproduce-probe-trap-mining check-probe-trap-mining reproduce-surface-fragmentation-audit check-surface-fragmentation-audit build-qualitative-gallery check-qualitative-gallery build-system-matrix-report check-system-matrix-report build-measurement-study check-measurement-study build-alignment-report check-alignment-report verify docker-build docker-demo reproduce-table-1 reproduce-route-audit-workflow reproduce-human-gold-rehearsal reproduce-route-scorecard reproduce-route-cohort-scorecard reproduce-surface-scorecard reproduce-route-surface-scorecard reproduce-runtime-surface-scorecard reproduce-layer-attribution check-audit-surface-coverage reproduce-normalization-ablation reproduce-intent-inventory reproduce-intent-surface-export reproduce-substrate-profile summarize-private-result export-route-labels export-intent-surface-qrels export-route-runs build-route-audit-pack export-route-review-csv build-route-review-brief build-route-review-batch merge-route-review-batch check-route-review-progress validate-route-review-csv import-route-review-csv summarize-route-audit validate-route-audit promote-route-audit evaluate-route-router

test:
	python3 -m unittest discover -s tests

check-public-safety:
	python3 scripts/check_public_safety.py

check-study-readiness:
	python3 scripts/check_study_readiness.py --out reports/study_readiness.md

check-readme-signals:
	python3 scripts/sync_readme_signals.py --check

check-router-lift:
	python3 scripts/check_router_lift.py --out reports/private_router_lift_gate.md --check

check-surface-lift:
	python3 scripts/check_surface_lift.py --out reports/surface_lift_gate.md --check

build-hero-signal:
	python3 scripts/build_hero_signal.py --report-out reports/hero_signal.md --figure-out reports/figures/diagnostic_signal_heatmap.svg

check-hero-signal:
	python3 scripts/build_hero_signal.py --report-out reports/hero_signal.md --figure-out reports/figures/diagnostic_signal_heatmap.svg --check

build-claim-ledger:
	python3 scripts/build_claim_ledger.py --out reports/claim_ledger.md

check-claim-ledger:
	python3 scripts/build_claim_ledger.py --out reports/claim_ledger.md --check

build-reviewer-demo:
	python3 scripts/build_reviewer_demo.py --out reports/reviewer_demo.md

check-reviewer-demo:
	python3 scripts/build_reviewer_demo.py --out reports/reviewer_demo.md --check

build-probe-privacy-report:
	python3 scripts/check_probe_privacy.py --out reports/probe_privacy_report.md

check-probe-privacy:
	python3 scripts/check_probe_privacy.py --out reports/probe_privacy_report.md --check

reproduce-probe-system-comparison:
	python3 scripts/reproduce_probe_system_comparison.py --out reports/probe_system_comparison.md

check-probe-system-comparison:
	python3 scripts/reproduce_probe_system_comparison.py --out reports/probe_system_comparison.md --check

reproduce-probe-trap-mining:
	python3 scripts/reproduce_probe_trap_mining.py --out reports/probe_trap_mining.md

check-probe-trap-mining:
	python3 scripts/reproduce_probe_trap_mining.py --out reports/probe_trap_mining.md --check

reproduce-surface-fragmentation-audit:
	python3 scripts/reproduce_surface_fragmentation_audit.py --out reports/surface_fragmentation_audit.md

check-surface-fragmentation-audit:
	python3 scripts/reproduce_surface_fragmentation_audit.py --out reports/surface_fragmentation_audit.md --check

build-qualitative-gallery:
	python3 scripts/build_qualitative_gallery.py --out reports/qualitative_gallery.md

check-qualitative-gallery:
	python3 scripts/build_qualitative_gallery.py --out reports/qualitative_gallery.md --check

build-system-matrix-report:
	python3 scripts/build_system_matrix_report.py --out reports/system_matrix.md

check-system-matrix-report:
	python3 scripts/build_system_matrix_report.py --out reports/system_matrix.md --check

build-measurement-study:
	python3 scripts/build_measurement_study.py --out reports/measurement_study_draft.md

check-measurement-study:
	python3 scripts/build_measurement_study.py --out reports/measurement_study_draft.md --check

build-alignment-report:
	python3 scripts/build_alignment_report.py --out reports/flagship_alignment.md

check-alignment-report:
	python3 scripts/build_alignment_report.py --out reports/flagship_alignment.md --check

verify: test reproduce-table-1 reproduce-route-audit-workflow reproduce-human-gold-rehearsal reproduce-route-scorecard reproduce-route-cohort-scorecard reproduce-surface-scorecard reproduce-route-surface-scorecard reproduce-runtime-surface-scorecard reproduce-layer-attribution check-audit-surface-coverage reproduce-normalization-ablation reproduce-intent-inventory reproduce-intent-surface-export reproduce-substrate-profile check-study-readiness check-readme-signals check-router-lift check-surface-lift check-hero-signal check-claim-ledger check-reviewer-demo check-probe-privacy check-probe-system-comparison check-probe-trap-mining check-surface-fragmentation-audit check-qualitative-gallery check-system-matrix-report check-measurement-study check-alignment-report check-public-safety

docker-build:
	docker build -t $(DOCKER_IMAGE) .

docker-demo:
	docker build -t $(DOCKER_IMAGE) .
	docker run --rm $(DOCKER_IMAGE) make reproduce-table-1 reproduce-layer-attribution check-study-readiness check-hero-signal check-claim-ledger check-reviewer-demo check-probe-privacy check-probe-system-comparison check-probe-trap-mining check-surface-fragmentation-audit check-qualitative-gallery check-system-matrix-report check-measurement-study check-alignment-report check-public-safety

reproduce-table-1:
	python3 scripts/reproduce_table_1.py

reproduce-route-audit-workflow:
	python3 scripts/reproduce_route_audit_workflow.py reports/route_audit_workflow_fixture.md

reproduce-human-gold-rehearsal:
	python3 scripts/reproduce_human_gold_rehearsal.py --out reports/human_gold_rehearsal_fixture.md

reproduce-route-scorecard:
	python3 scripts/reproduce_route_scorecard.py --out reports/route_scorecard_fixture.md

reproduce-route-cohort-scorecard:
	python3 scripts/reproduce_route_cohort_scorecard.py --qrels fixtures/qrels.jsonl --labels fixtures/qrels.jsonl --run-dir fixtures/system_runs --source-map fixtures/source_cohort_map.json --out reports/route_cohort_scorecard_fixture.md --label-status "synthetic fixture labels" --fail-on-unmapped

reproduce-surface-scorecard:
	python3 scripts/reproduce_surface_scorecard.py --out reports/surface_scorecard_fixture.md

reproduce-route-surface-scorecard:
	python3 scripts/reproduce_route_surface_scorecard.py --out reports/route_surface_scorecard_fixture.md

reproduce-runtime-surface-scorecard:
	python3 scripts/reproduce_runtime_surface_scorecard.py --out reports/runtime_surface_scorecard_fixture.md

reproduce-layer-attribution:
	python3 scripts/reproduce_layer_attribution.py --out reports/layer_attribution_fixture.md

check-audit-surface-coverage:
	python3 scripts/check_audit_surface_coverage.py --out reports/audit_surface_coverage_fixture.md --require-complete

reproduce-normalization-ablation:
	python3 scripts/reproduce_normalization_ablation.py --out reports/normalization_ablation_fixture.md

reproduce-intent-inventory:
	python3 scripts/build_intent_inventory.py --out reports/intent_inventory_fixture.md

reproduce-intent-surface-export:
	python3 scripts/export_intent_surface_qrels.py --qrels fixtures/private_like_qrels.jsonl --route-labels fixtures/private_like_route_labels.jsonl --report-out reports/intent_surface_export_fixture.md

reproduce-substrate-profile:
	python3 scripts/profile_query_substrates.py --source community_post:fixtures/substrates/community_posts.jsonl:jsonl:title,body --source messenger_turn:fixtures/substrates/messenger_turns.csv:csv:Message --out reports/substrate_profile_fixture.md --title "Query Substrate Profile Fixture" --label-status "synthetic query-substrate fixture"

summarize-private-result:
	python3 scripts/summarize_hit_result.py --result "$(RESULT_JSON)" --baseline "$(BASELINE)" --out reports/private_aggregate_scorecard.md

export-route-labels:
	python3 scripts/export_route_labels.py --qrels "$(QRELS_JSONL)" --labels-out "$(LABELS_OUT)" --report-out reports/private_route_label_summary.md

export-intent-surface-qrels:
	python3 scripts/export_intent_surface_qrels.py --qrels "$(QRELS_JSONL)" --route-labels "$(LABELS_JSONL)" --qrels-out "$(SURFACE_QRELS_OUT)" --report-out reports/private_intent_surface_export_summary.md

export-route-runs:
	python3 scripts/export_route_runs.py --qrels "$(QRELS_JSONL)" --out-dir "$(ROUTE_RUNS_OUT)" --report-out reports/private_route_run_export_summary.md $(ARGS)

build-route-audit-pack:
	python3 scripts/build_route_audit_pack.py --qrels "$(QRELS_JSONL)" --labels "$(LABELS_JSONL)" --audit-out "$(AUDIT_OUT)" --report-out reports/private_route_audit_pack_summary.md

export-route-review-csv:
	python3 scripts/export_route_review_csv.py --audit "$(AUDIT_JSONL)" --reviewer-prefix "$(REVIEWER_PREFIX)" --csv-out "$(CSV_OUT)" --report-out reports/private_route_review_csv_export.md

build-route-review-brief:
	python3 scripts/build_route_review_brief.py --csv "$(CSV_IN)" --report-out reports/private_route_review_brief.md

build-route-review-batch:
	python3 scripts/build_route_review_batch.py --csv "$(CSV_IN)" --out-csv "$(CSV_OUT)" --report-out reports/private_route_review_batch_summary.md

merge-route-review-batch:
	python3 scripts/merge_route_review_batch.py --full-csv "$(CSV_IN)" --batch-csv "$(BATCH_CSV)" --out-csv "$(CSV_OUT)" --report-out reports/private_route_review_batch_merge_summary.md

check-route-review-progress:
	python3 scripts/check_route_review_progress.py --csv "$(CSV_IN)" --report-out reports/private_route_review_progress.md

validate-route-review-csv:
	python3 scripts/validate_route_review_csv.py --csv "$(CSV_IN)" --report-out reports/private_route_review_csv_validation.md $(ARGS)

import-route-review-csv:
	python3 scripts/import_route_review_csv.py --audit "$(AUDIT_JSONL)" --csv "$(CSV_IN)" --target-prefix "$(TARGET_PREFIX)" --out "$(AUDIT_OUT)" --report-out reports/private_route_review_csv_import.md --skip-empty

summarize-route-audit:
	python3 scripts/summarize_route_audit.py --audit "$(AUDIT_JSONL)" --field-a "$(FIELD_A)" --field-b "$(FIELD_B)" --report-out reports/private_route_audit_agreement.md

validate-route-audit:
	python3 scripts/validate_route_audit.py --audit "$(AUDIT_JSONL)" --label-prefix "$(LABEL_PREFIX)" --require-complete --report-out reports/private_route_audit_validation.md

promote-route-audit:
	python3 scripts/promote_route_audit.py --audit "$(AUDIT_JSONL)" --label-prefix "$(LABEL_PREFIX)" --labels-out "$(LABELS_OUT)" --report-out reports/private_promoted_route_labels.md

evaluate-route-router:
	python3 scripts/evaluate_route_router.py --qrels "$(QRELS_JSONL)" --labels "$(LABELS_JSONL)" --report-out reports/private_route_router_baselines.md $(ARGS)
