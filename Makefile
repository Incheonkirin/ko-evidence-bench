.PHONY: test check-public-safety check-study-readiness check-readme-signals build-measurement-study check-measurement-study build-alignment-report check-alignment-report verify reproduce-table-1 reproduce-route-audit-workflow reproduce-route-scorecard summarize-private-result export-route-labels export-route-runs build-route-audit-pack export-route-review-csv import-route-review-csv summarize-route-audit validate-route-audit promote-route-audit evaluate-route-router

test:
	python3 -m unittest discover -s tests

check-public-safety:
	python3 scripts/check_public_safety.py

check-study-readiness:
	python3 scripts/check_study_readiness.py --out reports/study_readiness.md

check-readme-signals:
	python3 scripts/sync_readme_signals.py --check

build-measurement-study:
	python3 scripts/build_measurement_study.py --out reports/measurement_study_draft.md

check-measurement-study:
	python3 scripts/build_measurement_study.py --out reports/measurement_study_draft.md --check

build-alignment-report:
	python3 scripts/build_alignment_report.py --out reports/flagship_alignment.md

check-alignment-report:
	python3 scripts/build_alignment_report.py --out reports/flagship_alignment.md --check

verify: test reproduce-table-1 reproduce-route-audit-workflow reproduce-route-scorecard check-study-readiness check-readme-signals check-measurement-study check-alignment-report check-public-safety

reproduce-table-1:
	python3 scripts/reproduce_table_1.py

reproduce-route-audit-workflow:
	python3 scripts/reproduce_route_audit_workflow.py reports/route_audit_workflow_fixture.md

reproduce-route-scorecard:
	python3 scripts/reproduce_route_scorecard.py --out reports/route_scorecard_fixture.md

summarize-private-result:
	python3 scripts/summarize_hit_result.py --result "$(RESULT_JSON)" --baseline "$(BASELINE)" --out reports/private_aggregate_scorecard.md

export-route-labels:
	python3 scripts/export_route_labels.py --qrels "$(QRELS_JSONL)" --labels-out "$(LABELS_OUT)" --report-out reports/private_route_label_summary.md

export-route-runs:
	python3 scripts/export_route_runs.py --qrels "$(QRELS_JSONL)" --out-dir "$(ROUTE_RUNS_OUT)" --report-out reports/private_route_run_export_summary.md

build-route-audit-pack:
	python3 scripts/build_route_audit_pack.py --qrels "$(QRELS_JSONL)" --labels "$(LABELS_JSONL)" --audit-out "$(AUDIT_OUT)" --report-out reports/private_route_audit_pack_summary.md

export-route-review-csv:
	python3 scripts/export_route_review_csv.py --audit "$(AUDIT_JSONL)" --reviewer-prefix "$(REVIEWER_PREFIX)" --csv-out "$(CSV_OUT)" --report-out reports/private_route_review_csv_export.md

import-route-review-csv:
	python3 scripts/import_route_review_csv.py --audit "$(AUDIT_JSONL)" --csv "$(CSV_IN)" --target-prefix "$(TARGET_PREFIX)" --out "$(AUDIT_OUT)" --report-out reports/private_route_review_csv_import.md --skip-empty

summarize-route-audit:
	python3 scripts/summarize_route_audit.py --audit "$(AUDIT_JSONL)" --field-a "$(FIELD_A)" --field-b "$(FIELD_B)" --report-out reports/private_route_audit_agreement.md

validate-route-audit:
	python3 scripts/validate_route_audit.py --audit "$(AUDIT_JSONL)" --label-prefix "$(LABEL_PREFIX)" --require-complete --report-out reports/private_route_audit_validation.md

promote-route-audit:
	python3 scripts/promote_route_audit.py --audit "$(AUDIT_JSONL)" --label-prefix "$(LABEL_PREFIX)" --labels-out "$(LABELS_OUT)" --report-out reports/private_promoted_route_labels.md

evaluate-route-router:
	python3 scripts/evaluate_route_router.py --qrels "$(QRELS_JSONL)" --labels "$(LABELS_JSONL)" --report-out reports/private_route_router_baselines.md
