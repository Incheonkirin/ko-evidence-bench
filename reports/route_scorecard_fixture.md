# Route Scorecard Fixture

This report validates the qid-only source-route scoring path on synthetic fixture labels.
No raw private query, conversation, community, or policy text is needed to
score route accuracy and abstention behavior.

## Inputs

- labels: `fixtures/route_labels.jsonl`
- runs: `fixtures/route_runs`
- bootstrap samples: 1000

## Route Metrics

| system | n | missing | route_acc | 95% CI | abst_p | abst_r |
|---|---:|---:|---:|---:|---:|---:|
| `always_policy` | 6 | 0 | 16.7% | 0.0% - 50.0% | 0.0% | 0.0% |
| `source_routed_demo` | 6 | 0 | 100.0% | 100.0% - 100.0% | 100.0% | 100.0% |

## Paired Delta vs `always_policy`

| candidate | metric | paired delta | 95% CI |
|---|---|---:|---:|
| `source_routed_demo` | `route_accuracy` | 83.3% | 50.0% - 100.0% |

## Route Accuracy By Gold Source Tier

This slice table shows where route selection fails. The same table is
used for synthetic fixtures, silver diagnostics, and future
human-adjudicated route labels.

| system | gold source tier | n | missing | route_acc | abstained_rate | expected_abstain |
|---|---|---:|---:|---:|---:|---:|
| `always_policy` | `claims_faq` | 1 | 0 | 0.0% | 0.0% | 0.0% |
| `always_policy` | `expert_answer` | 1 | 0 | 0.0% | 0.0% | 0.0% |
| `always_policy` | `human_context_needed` | 1 | 0 | 0.0% | 0.0% | 100.0% |
| `always_policy` | `official_consumer_info` | 1 | 0 | 0.0% | 0.0% | 0.0% |
| `always_policy` | `policy_clause` | 1 | 0 | 100.0% | 0.0% | 0.0% |
| `always_policy` | `product_disclosure` | 1 | 0 | 0.0% | 0.0% | 0.0% |
| `source_routed_demo` | `claims_faq` | 1 | 0 | 100.0% | 0.0% | 0.0% |
| `source_routed_demo` | `expert_answer` | 1 | 0 | 100.0% | 0.0% | 0.0% |
| `source_routed_demo` | `human_context_needed` | 1 | 0 | 100.0% | 100.0% | 100.0% |
| `source_routed_demo` | `official_consumer_info` | 1 | 0 | 100.0% | 0.0% | 0.0% |
| `source_routed_demo` | `policy_clause` | 1 | 0 | 100.0% | 0.0% | 0.0% |
| `source_routed_demo` | `product_disclosure` | 1 | 0 | 100.0% | 0.0% | 0.0% |

## Largest Route Confusions

Rows below exclude correct gold/predicted pairs. They are aggregate
counts only and do not expose qids or row text.

| system | gold source tier | predicted source tier | count | share of run |
|---|---|---|---:|---:|
| `always_policy` | `claims_faq` | `policy_clause` | 1 | 16.7% |
| `always_policy` | `human_context_needed` | `policy_clause` | 1 | 16.7% |
| `always_policy` | `product_disclosure` | `policy_clause` | 1 | 16.7% |
| `always_policy` | `official_consumer_info` | `policy_clause` | 1 | 16.7% |
| `always_policy` | `expert_answer` | `policy_clause` | 1 | 16.7% |

## Interpretation

These scores use synthetic fixture labels. Treat them as diagnostics unless the
label file is human-adjudicated and validated. The scorecard path is the
same path intended for promoted private human labels.
