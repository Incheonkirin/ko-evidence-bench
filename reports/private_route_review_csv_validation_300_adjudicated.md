# Private Route Review CSV Validation

This report validates a private route-review CSV before import or
promotion. It contains aggregate counts only. It does not include qids,
raw queries, context, audit ids, or reviewer notes.

- private csv: `route_review_v0_300_adjudicated.csv`
- rows: 300
- complete rows: 0
- rows with validation errors: 300
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

## Valid Route Distribution

| value | count | share |
|---|---:|---:|

## Valid Confidence Distribution

| value | count | share |
|---|---:|---:|

## Validation Error Counts

| value | count | share |
|---|---:|---:|
| `missing_route_gold` | 300 | 16.7% |
| `missing_allowed_source_tiers` | 300 | 16.7% |
| `missing_should_abstain` | 300 | 16.7% |
| `missing_confidence` | 300 | 16.7% |
| `missing_rationale_code` | 300 | 16.7% |
| `missing_labeler` | 300 | 16.7% |

## Use Notes

- Run with `--require-complete` before importing labels for promotion.
- `human_context_needed` and `out_of_scope` rows should set `should_abstain=true`.
- All other route labels should set `should_abstain=false`.
- Keep the reviewed CSV outside the public repository.
