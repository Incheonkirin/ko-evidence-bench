# Private Route Review Batch Merge Summary

This report summarizes merging a private reviewed priority batch back into
a full route-review CSV. It contains aggregate counts only and does not
include qids, raw queries, context, or reviewer notes.

- full csv: `route_review_v0_300_adjudicated.csv`
- batch csv: `route_review_v0_300_priority50.csv`
- private output csv: `route_review_v0_300_after_priority50.csv`
- include empty batch rows: false

## Merge Counts

| item | count |
|---|---:|
| `full_rows` | 300 |
| `batch_rows` | 50 |
| `matched_rows` | 50 |
| `updated_rows` | 0 |
| `skipped_empty_rows` | 50 |
| `unmatched_batch_rows` | 0 |

## Merged Route Distribution

| value | count | share |
|---|---:|---:|

## Merged Confidence Distribution

| value | count | share |
|---|---:|---:|

## Use Notes

- Run `scripts/check_route_review_progress.py` on the merged private CSV.
- Import the merged CSV only after the desired batch rows are filled.
- Keep both the batch and merged CSV outside the public repository.
