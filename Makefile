.PHONY: test reproduce-table-1

test:
	python3 -m unittest discover -s tests

reproduce-table-1:
	python3 scripts/reproduce_table_1.py
