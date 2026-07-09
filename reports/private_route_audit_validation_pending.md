# Private Route Audit Validation Summary

This report validates a private route-audit file and exposes only
aggregate counts. It does not include qids, raw queries, context, or
reviewer notes.

- audit rows: 300
- audit file: `route_audit_pack_v0_300.jsonl`
- label prefix: `adjudicated`
- require complete: true
- completed labels: 0
- completion rate: 0.0%
- rows with validation errors: 300

## Validated Route Distribution

| value | count | share |
|---|---:|---:|

## Validated Confidence Distribution

| value | count | share |
|---|---:|---:|

## Validation Error Counts

| value | count | share |
|---|---:|---:|
| `missing_route_gold` | 300 | 100.0% |

## Use Notes

- A validation report with zero row errors is required before promotion.
- This report is aggregate-only; inspect the private audit file for row-level fixes.
