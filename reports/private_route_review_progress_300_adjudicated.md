# Private Route Review Progress

This report summarizes private route-review CSV completion. It contains
aggregate counts only. It does not include qids, raw queries, context, or
reviewer notes.

- private csv: `route_review_v0_300_adjudicated.csv`
- rows: 300
- complete rows: 0
- completion rate: 0.0%
- missing required columns: 0

## Field Fill Rates

| field | filled | share |
|---|---:|---:|
| `route_gold` | 0 | 0.0% |
| `allowed_source_tiers` | 0 | 0.0% |
| `should_abstain` | 0 | 0.0% |
| `confidence` | 0 | 0.0% |
| `rationale_code` | 0 | 0.0% |
| `labeler` | 0 | 0.0% |
| `notes` | 0 | 0.0% |

## Route Distribution

| value | count | share |
|---|---:|---:|

## Confidence Distribution

| value | count | share |
|---|---:|---:|

## Completion Error Counts

| value | count | share |
|---|---:|---:|
| `missing_route_gold` | 300 | 100.0% |

## Use Notes

- Complete rows still need import and audit validation before promotion.
- Use `scripts/import_route_review_csv.py` after labels are filled.
- Keep the private CSV outside the public repository.
