# Private Route Run Export Summary

This report summarizes qid-only route prediction files generated from a
private qrel source. It contains aggregate counts only and does not include
raw queries, qids, conversations, or platform identifiers.

- output dir: `route_runs_v0_silver`
- systems: 2

## Exported Runs

| system | rows | abstained |
|---|---:|---:|
| `always_policy` | 544 | 0 |
| `query_keyword_router` | 544 | 44 |

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
