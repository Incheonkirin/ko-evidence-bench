# Private Route Review Batch Summary

This report summarizes a private priority batch for route adjudication.
The batch CSV may contain qids, raw queries, and context, so it must stay
outside the public repository. This summary is aggregate-only.

- source csv: `route_review_v0_300_adjudicated.csv`
- private batch csv: `route_review_v0_300_priority50.csv`
- source rows: 300
- requested limit: 50
- selected rows: 50
- selected complete rows: 0

## Priority Reason Counts

| value | count | share |
|---|---:|---:|
| `product_divergent` | 50 | 28.9% |
| `silver_should_abstain` | 47 | 27.2% |
| `needs_contract` | 47 | 27.2% |
| `requires_table_value` | 12 | 6.9% |
| `not_in_corpus` | 9 | 5.2% |
| `requires_exclusion_check` | 5 | 2.9% |
| `silver_low_confidence` | 3 | 1.7% |

## Batch Distribution: `silver_route_gold`

| value | count | share |
|---|---:|---:|
| `human_context_needed` | 47 | 94.0% |
| `policy_clause` | 2 | 4.0% |
| `expert_answer` | 1 | 2.0% |

## Batch Distribution: `silver_confidence`

| value | count | share |
|---|---:|---:|
| `high` | 47 | 94.0% |
| `low` | 3 | 6.0% |

## Batch Distribution: `silver_should_abstain`

| value | count | share |
|---|---:|---:|
| `true` | 47 | 94.0% |
| `false` | 3 | 6.0% |

## Batch Distribution: `reason_code`

| value | count | share |
|---|---:|---:|
| `needs_contract` | 20 | 40.0% |
| `requires_table_value` | 12 | 24.0% |
| `not_in_corpus` | 9 | 18.0% |
| `requires_exclusion_check` | 5 | 10.0% |
| `cross_product_enumeration` | 3 | 6.0% |
| `interchangeable` | 1 | 2.0% |

## Batch Distribution: `needs_contract`

| value | count | share |
|---|---:|---:|
| `true` | 47 | 94.0% |
| `false` | 3 | 6.0% |

## Batch Distribution: `product_divergent`

| value | count | share |
|---|---:|---:|
| `true` | 50 | 100.0% |

## Use Notes

- Label this private batch first when starting adjudication.
- After filling it, run `scripts/check_route_review_progress.py` on the batch or full CSV.
- Do not copy the private batch CSV into the public repository.
