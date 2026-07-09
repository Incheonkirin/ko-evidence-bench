.PHONY: test reproduce-table-1 summarize-private-result

test:
	python3 -m unittest discover -s tests

reproduce-table-1:
	python3 scripts/reproduce_table_1.py

summarize-private-result:
	python3 scripts/summarize_hit_result.py --result "$(RESULT_JSON)" --baseline "$(BASELINE)" --out reports/private_aggregate_scorecard.md
