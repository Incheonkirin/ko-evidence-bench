# Private Silver Route Scorecard

This report validates the qid-only source-route scoring path on private silver route labels.
No raw private query, conversation, community, or policy text is needed to
score route accuracy and abstention behavior.

## Inputs

- labels: `route_labels_v0_silver.jsonl`
- runs: `route_runs_v0_silver`
- bootstrap samples: 1000

## Route Metrics

| system | n | missing | route_acc | 95% CI | abst_p | abst_r |
|---|---:|---:|---:|---:|---:|---:|
| `always_policy` | 544 | 0 | 21.5% | 18.0% - 25.0% | 0.0% | 0.0% |
| `query_keyword_router` | 544 | 0 | 31.8% | 27.9% - 35.8% | 65.9% | 10.5% |

## Paired Delta vs `always_policy`

| candidate | metric | paired delta | 95% CI |
|---|---|---:|---:|
| `query_keyword_router` | `route_accuracy` | 10.3% | 7.2% - 13.8% |

## Route Accuracy By Gold Source Tier

This slice table shows where route selection fails. The same table is
used for synthetic fixtures, silver diagnostics, and future
human-adjudicated route labels.

| system | gold source tier | n | missing | route_acc | abstained_rate | expected_abstain |
|---|---|---:|---:|---:|---:|---:|
| `always_policy` | `claims_faq` | 31 | 0 | 0.0% | 0.0% | 0.0% |
| `always_policy` | `dispute_case` | 48 | 0 | 0.0% | 0.0% | 0.0% |
| `always_policy` | `expert_answer` | 21 | 0 | 0.0% | 0.0% | 0.0% |
| `always_policy` | `human_context_needed` | 276 | 0 | 0.0% | 0.0% | 100.0% |
| `always_policy` | `policy_clause` | 117 | 0 | 100.0% | 0.0% | 0.0% |
| `always_policy` | `product_disclosure` | 51 | 0 | 0.0% | 0.0% | 0.0% |
| `query_keyword_router` | `claims_faq` | 31 | 0 | 32.3% | 6.5% | 0.0% |
| `query_keyword_router` | `dispute_case` | 48 | 0 | 12.5% | 12.5% | 0.0% |
| `query_keyword_router` | `expert_answer` | 21 | 0 | 0.0% | 4.8% | 0.0% |
| `query_keyword_router` | `human_context_needed` | 276 | 0 | 10.5% | 10.5% | 100.0% |
| `query_keyword_router` | `policy_clause` | 117 | 0 | 89.7% | 5.1% | 0.0% |
| `query_keyword_router` | `product_disclosure` | 51 | 0 | 45.1% | 0.0% | 0.0% |

## Largest Route Confusions

Rows below exclude correct gold/predicted pairs. They are aggregate
counts only and do not expose qids or row text.

| system | gold source tier | predicted source tier | count | share of run |
|---|---|---|---:|---:|
| `always_policy` | `human_context_needed` | `policy_clause` | 276 | 50.7% |
| `always_policy` | `product_disclosure` | `policy_clause` | 51 | 9.4% |
| `always_policy` | `dispute_case` | `policy_clause` | 48 | 8.8% |
| `always_policy` | `claims_faq` | `policy_clause` | 31 | 5.7% |
| `always_policy` | `expert_answer` | `policy_clause` | 21 | 3.9% |
| `query_keyword_router` | `human_context_needed` | `policy_clause` | 190 | 34.9% |
| `query_keyword_router` | `dispute_case` | `policy_clause` | 33 | 6.1% |
| `query_keyword_router` | `human_context_needed` | `product_disclosure` | 32 | 5.9% |
| `query_keyword_router` | `product_disclosure` | `policy_clause` | 27 | 5.0% |
| `query_keyword_router` | `human_context_needed` | `claims_faq` | 20 | 3.7% |
| `query_keyword_router` | `expert_answer` | `policy_clause` | 18 | 3.3% |
| `query_keyword_router` | `claims_faq` | `policy_clause` | 15 | 2.8% |
| `query_keyword_router` | `dispute_case` | `human_context_needed` | 6 | 1.1% |
| `query_keyword_router` | `policy_clause` | `human_context_needed` | 6 | 1.1% |
| `query_keyword_router` | `policy_clause` | `claims_faq` | 4 | 0.7% |
| `query_keyword_router` | `claims_faq` | `product_disclosure` | 4 | 0.7% |
| `query_keyword_router` | `human_context_needed` | `dispute_case` | 3 | 0.6% |

## Interpretation

These scores use private silver route labels. Treat them as diagnostics unless the
label file is human-adjudicated and validated. The scorecard path is the
same path intended for promoted private human labels.
