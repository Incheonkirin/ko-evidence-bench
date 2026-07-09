# Surface Robustness Scorecard Fixture

This report checks whether a system is robust to different surface forms
of the same intent. It uses only stable ids, source-route labels,
surface metadata, and ranked evidence ids. It does not include raw
queries, conversation snippets, source names, or platform identifiers.

A row is counted as `task_success@k` when the route decision is correct
and either sufficient evidence appears in top-k or the system correctly
abstains for rows that require human context.

## Inputs

- qrels: `fixtures/surface_qrels.jsonl`
- runs: `fixtures/surface_runs`
- label status: synthetic surface fixture labels
- k: 3

## Surface Robustness Summary

| system | n | intents | surfaces | task_success@3 | route_acc | answerable_evidence@3 | avg_intent_spread | robust_intents | worst_surface@3 | missing metadata |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `formal_only_demo` | 8 | 3 | 4 | 37.5% | 75.0% | 33.3% | 100.0% | 0.0% | 0.0% | 0 |
| `surface_robust_demo` | 8 | 3 | 4 | 100.0% | 100.0% | 100.0% | 0.0% | 100.0% | 100.0% | 0 |

## Surface Condition Breakdown

| system | surface form | n | task_success@3 | route_acc | answerable_evidence@3 |
|---|---|---:|---:|---:|---:|
| `formal_only_demo` | `abbreviated` | 1 | 0.0% | 100.0% | 0.0% |
| `formal_only_demo` | `colloquial` | 1 | 0.0% | 100.0% | 0.0% |
| `formal_only_demo` | `formal` | 3 | 100.0% | 100.0% | 100.0% |
| `formal_only_demo` | `messenger_shorthand` | 3 | 0.0% | 33.3% | 0.0% |
| `surface_robust_demo` | `abbreviated` | 1 | 100.0% | 100.0% | 100.0% |
| `surface_robust_demo` | `colloquial` | 1 | 100.0% | 100.0% | 100.0% |
| `surface_robust_demo` | `formal` | 3 | 100.0% | 100.0% | 100.0% |
| `surface_robust_demo` | `messenger_shorthand` | 3 | 100.0% | 100.0% | 100.0% |

## Intent Robustness Breakdown

| system | intent id | variants | surfaces | task_success@3 | min surface | max surface | spread |
|---|---|---:|---|---:|---:|---:|---:|
| `formal_only_demo` | `cancer_brain_heart_bundle` | 3 | `abbreviated,formal,messenger_shorthand` | 33.3% | 0.0% | 100.0% | 100.0% |
| `formal_only_demo` | `refund_termination` | 3 | `colloquial,formal,messenger_shorthand` | 33.3% | 0.0% | 100.0% | 100.0% |
| `formal_only_demo` | `underwriting_context_needed` | 2 | `formal,messenger_shorthand` | 50.0% | 0.0% | 100.0% | 100.0% |
| `surface_robust_demo` | `cancer_brain_heart_bundle` | 3 | `abbreviated,formal,messenger_shorthand` | 100.0% | 100.0% | 100.0% | 0.0% |
| `surface_robust_demo` | `refund_termination` | 3 | `colloquial,formal,messenger_shorthand` | 100.0% | 100.0% | 100.0% | 0.0% |
| `surface_robust_demo` | `underwriting_context_needed` | 2 | `formal,messenger_shorthand` | 100.0% | 100.0% | 100.0% | 0.0% |

## Fixture Inventory: Intent Id

| intent_id | rows |
|---|---:|
| `cancer_brain_heart_bundle` | 3 |
| `refund_termination` | 3 |
| `underwriting_context_needed` | 2 |

## Fixture Inventory: Surface Form

| surface_form | rows |
|---|---:|
| `formal` | 3 |
| `messenger_shorthand` | 3 |
| `abbreviated` | 1 |
| `colloquial` | 1 |

## Use Notes

- Lower `avg_intent_spread` means less performance variation across
  surface forms of the same intent.
- `worst_surface@k` is the first place to look for messenger-style,
  abbreviated, or colloquial regressions.
- Private qrels can reuse this path by adding `intent_id` and
  `surface_form` metadata while keeping raw text outside the public repo.
