# Private Source-Route Router Baselines

This report evaluates source-route baselines against private silver labels.
It contains aggregate metrics only. It does not include raw queries, qids,
conversation snippets, or platform identifiers.

- rows: 544
- bootstrap samples: 2000
- seed: 29
- label status: silver proxy, not human-gold

## Metrics

| system | metric | value | 95% CI |
|---|---|---:|---:|
| always_policy | `route_accuracy` | 21.5% | 18.2% - 25.0% |
| always_policy | `abstention_precision` | 0.0% | 0.0% - 0.0% |
| always_policy | `abstention_recall` | 0.0% | 0.0% - 0.0% |
| query_keyword_router | `route_accuracy` | 31.8% | 27.8% - 35.7% |
| query_keyword_router | `abstention_precision` | 65.9% | 51.2% - 80.0% |
| query_keyword_router | `abstention_recall` | 10.5% | 7.1% - 14.1% |
| risk_aware_query_router | `route_accuracy` | 32.7% | 28.9% - 36.8% |
| risk_aware_query_router | `abstention_precision` | 46.0% | 38.3% - 53.7% |
| risk_aware_query_router | `abstention_recall` | 26.8% | 21.7% - 32.4% |
| cohort_aware_query_router | `route_accuracy` | 46.9% | 43.0% - 51.3% |
| cohort_aware_query_router | `abstention_precision` | 55.1% | 49.9% - 60.3% |
| cohort_aware_query_router | `abstention_recall` | 67.0% | 61.5% - 72.7% |

## Paired Delta vs `always_policy`

| system | metric | delta | 95% CI |
|---|---|---:|---:|
| query_keyword_router | `route_accuracy` | 10.3% | 7.2% - 13.4% |
| risk_aware_query_router | `route_accuracy` | 11.2% | 6.4% - 16.0% |
| cohort_aware_query_router | `route_accuracy` | 25.4% | 19.3% - 31.6% |

## Gold Route Distribution

| value | count | share |
|---|---:|---:|
| `human_context_needed` | 276 | 50.7% |
| `policy_clause` | 117 | 21.5% |
| `product_disclosure` | 51 | 9.4% |
| `dispute_case` | 48 | 8.8% |
| `claims_faq` | 31 | 5.7% |
| `expert_answer` | 21 | 3.9% |

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

## Use Notes

- These are baselines for source routing, not answer-quality claims.
- Silver-label results should be replaced by human-audited route metrics before headline use.
