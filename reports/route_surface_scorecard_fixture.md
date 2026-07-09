# Route Surface Scorecard Fixture

This report scores route and abstention behavior by qid-only intent,
surface, and trap metadata. It does not include qids, raw queries,
conversation snippets, source names, usernames, URLs, or document text.

It is route-only: it does not evaluate whether ranked evidence passages
contain sufficient answer evidence.

## Inputs

- qrels: `fixtures/surface_qrels.jsonl`
- runs: `fixtures/surface_runs`
- qrel rows: 8
- systems: 2
- label status: synthetic fixture metadata

## Route Surface Summary

| system | n | intents | surfaces | route_acc | abst_p | abst_r | avg_intent_route_spread | worst_surface_route_acc | missing predictions | missing metadata |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `formal_only_demo` | 8 | 3 | 4 | 75.0% | 100.0% | 50.0% | 66.7% | 33.3% | 0 | 0 |
| `surface_robust_demo` | 8 | 3 | 4 | 100.0% | 100.0% | 100.0% | 0.0% | 100.0% | 0 | 0 |

## Surface Form Breakdown

| system | slice | n | route_acc | abst_p | abst_r | missing predictions |
|---|---|---:|---:|---:|---:|---:|
| `formal_only_demo` | `abbreviated` | 1 | 100.0% | 0.0% | 0.0% | 0 |
| `formal_only_demo` | `colloquial` | 1 | 100.0% | 0.0% | 0.0% | 0 |
| `formal_only_demo` | `formal` | 3 | 100.0% | 100.0% | 100.0% | 0 |
| `formal_only_demo` | `messenger_shorthand` | 3 | 33.3% | 0.0% | 0.0% | 0 |
| `surface_robust_demo` | `abbreviated` | 1 | 100.0% | 0.0% | 0.0% | 0 |
| `surface_robust_demo` | `colloquial` | 1 | 100.0% | 0.0% | 0.0% | 0 |
| `surface_robust_demo` | `formal` | 3 | 100.0% | 100.0% | 100.0% | 0 |
| `surface_robust_demo` | `messenger_shorthand` | 3 | 100.0% | 100.0% | 100.0% | 0 |

## Intent Family Breakdown

| system | slice | n | route_acc | abst_p | abst_r | missing predictions |
|---|---|---:|---:|---:|---:|---:|
| `formal_only_demo` | `bundled_coverage` | 3 | 100.0% | 0.0% | 0.0% | 0 |
| `formal_only_demo` | `refund_termination` | 3 | 66.7% | 0.0% | 0.0% | 0 |
| `formal_only_demo` | `underwriting_context` | 2 | 50.0% | 100.0% | 50.0% | 0 |
| `surface_robust_demo` | `bundled_coverage` | 3 | 100.0% | 0.0% | 0.0% | 0 |
| `surface_robust_demo` | `refund_termination` | 3 | 100.0% | 0.0% | 0.0% | 0 |
| `surface_robust_demo` | `underwriting_context` | 2 | 100.0% | 100.0% | 100.0% | 0 |

## Trap-Class Breakdown

| system | slice | n | route_acc | abst_p | abst_r | missing predictions |
|---|---|---:|---:|---:|---:|---:|
| `formal_only_demo` | `abbreviation` | 1 | 100.0% | 0.0% | 0.0% | 0 |
| `formal_only_demo` | `bundle_expansion` | 3 | 100.0% | 0.0% | 0.0% | 0 |
| `formal_only_demo` | `messenger_shorthand` | 3 | 33.3% | 0.0% | 0.0% | 0 |
| `formal_only_demo` | `needs_private_context` | 2 | 50.0% | 100.0% | 50.0% | 0 |
| `formal_only_demo` | `product_table` | 3 | 66.7% | 0.0% | 0.0% | 0 |
| `formal_only_demo` | `register_mismatch` | 2 | 50.0% | 0.0% | 0.0% | 0 |
| `surface_robust_demo` | `abbreviation` | 1 | 100.0% | 0.0% | 0.0% | 0 |
| `surface_robust_demo` | `bundle_expansion` | 3 | 100.0% | 0.0% | 0.0% | 0 |
| `surface_robust_demo` | `messenger_shorthand` | 3 | 100.0% | 100.0% | 100.0% | 0 |
| `surface_robust_demo` | `needs_private_context` | 2 | 100.0% | 100.0% | 100.0% | 0 |
| `surface_robust_demo` | `product_table` | 3 | 100.0% | 0.0% | 0.0% | 0 |
| `surface_robust_demo` | `register_mismatch` | 2 | 100.0% | 0.0% | 0.0% | 0 |

## Largest Surface Route Confusions

| system | surface form | gold route | predicted route | count | share of run |
|---|---|---|---|---:|---:|
| `formal_only_demo` | `messenger_shorthand` | `product_disclosure` | `policy_clause` | 1 | 12.5% |
| `formal_only_demo` | `messenger_shorthand` | `human_context_needed` | `policy_clause` | 1 | 12.5% |

## Use Notes

- Use this report to find route and abstention regressions across surface
  conditions independently from retrieval-hit regressions.
- Treat silver-label results as diagnostics until the route labels and
  intent/surface metadata are human-audited.
- Pair this route-only report with runtime-surface or full surface
  scorecards to separate routing failures from evidence-hit failures.
