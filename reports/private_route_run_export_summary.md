# Private Route Run Export Summary

This report summarizes qid-only route prediction files generated from a
private qrel source. It contains aggregate counts only and does not include
raw queries, qids, conversations, or platform identifiers.

- output dir: `route_runs_v0_silver`
- systems: 4

## Exported Runs

| system | rows | abstained |
|---|---:|---:|
| `always_policy` | 544 | 0 |
| `query_keyword_router` | 544 | 44 |
| `risk_aware_query_router` | 544 | 161 |
| `cohort_aware_query_router` | 544 | 336 |

## Prediction Distribution: `always_policy`

| value | count | share |
|---|---:|---:|
| `policy_clause` | 544 | 100.0% |

## Prediction Distribution: `query_keyword_router`

| value | count | share |
|---|---:|---:|
| `policy_clause` | 388 | 71.3% |
| `product_disclosure` | 63 | 11.6% |
| `human_context_needed` | 44 | 8.1% |
| `claims_faq` | 35 | 6.4% |
| `dispute_case` | 10 | 1.8% |
| `expert_answer` | 4 | 0.7% |

## Prediction Distribution: `risk_aware_query_router`

| value | count | share |
|---|---:|---:|
| `policy_clause` | 257 | 47.2% |
| `human_context_needed` | 161 | 29.6% |
| `product_disclosure` | 76 | 14.0% |
| `claims_faq` | 34 | 6.2% |
| `dispute_case` | 12 | 2.2% |
| `expert_answer` | 4 | 0.7% |

## Prediction Distribution: `cohort_aware_query_router`

| value | count | share |
|---|---:|---:|
| `human_context_needed` | 336 | 61.8% |
| `policy_clause` | 82 | 15.1% |
| `product_disclosure` | 76 | 14.0% |
| `claims_faq` | 34 | 6.2% |
| `dispute_case` | 12 | 2.2% |
| `expert_answer` | 4 | 0.7% |
