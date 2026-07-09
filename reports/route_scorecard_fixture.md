# Route Scorecard Fixture

This report validates the qid-only source-route scoring path on synthetic fixtures.
It is the public dry-run for promoted private human labels: no raw private query,
conversation, community, or policy text is needed to score route accuracy and
abstention behavior.

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

## Interpretation

The fixture is intentionally tiny and synthetic. Its purpose is not model quality;
it proves that qid-only route labels can be scored after the private audit gate
promotes human-adjudicated labels.
