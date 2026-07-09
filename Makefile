.PHONY: test reproduce-table-1 summarize-private-result export-route-labels build-route-audit-pack summarize-route-audit

test:
	python3 -m unittest discover -s tests

reproduce-table-1:
	python3 scripts/reproduce_table_1.py

summarize-private-result:
	python3 scripts/summarize_hit_result.py --result "$(RESULT_JSON)" --baseline "$(BASELINE)" --out reports/private_aggregate_scorecard.md

export-route-labels:
	python3 scripts/export_route_labels.py --qrels "$(QRELS_JSONL)" --labels-out "$(LABELS_OUT)" --report-out reports/private_route_label_summary.md

build-route-audit-pack:
	python3 scripts/build_route_audit_pack.py --qrels "$(QRELS_JSONL)" --labels "$(LABELS_JSONL)" --audit-out "$(AUDIT_OUT)" --report-out reports/private_route_audit_pack_summary.md

summarize-route-audit:
	python3 scripts/summarize_route_audit.py --audit "$(AUDIT_JSONL)" --field-a "$(FIELD_A)" --field-b "$(FIELD_B)" --report-out reports/private_route_audit_agreement.md
