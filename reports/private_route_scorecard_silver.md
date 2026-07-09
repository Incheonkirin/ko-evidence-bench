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

## Interpretation

These scores use private silver route labels. Treat them as diagnostics unless the
label file is human-adjudicated and validated. The scorecard path is the
same path intended for promoted private human labels.
