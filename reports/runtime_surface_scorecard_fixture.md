# Runtime Surface Scorecard Fixture

This report joins qid-only intent/surface metadata with runtime
retrieval hit booleans such as `clause@20` and `exact@20`. It does
not include qids, raw queries, evidence ids, source names, usernames,
URLs, or document text.

It is a retrieval-hit surface scorecard. It does not judge answer
quality or source-route correctness; pair it with route scorecards
before making claims about end-to-end answerability.

## Inputs

- qrels: `fixtures/surface_qrels.jsonl`
- runtime result: `fixtures/runtime_results/surface_runtime_fixture.json`
- qrel rows: 8
- systems: 2
- primary metric: `clause@20`
- label status: synthetic runtime hit fixture

## Runtime Surface Summary

| system | n | answerable | intent families | surfaces | clause@20 | answerable_clause@20 | exact@20 | avg_family_surface_spread | worst_surface_clause@20 | missing hit rows | missing metadata |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `raw_surface_runtime` | 8 | 6 | 3 | 4 | 25.0% | 33.3% | 25.0% | 66.7% | 0.0% | 0 | 0 |
| `surface_robust_runtime` | 8 | 6 | 3 | 4 | 75.0% | 100.0% | 75.0% | 0.0% | 66.7% | 0 | 0 |

## Surface Form Breakdown

| system | slice | n | answerable | clause@20 | answerable_clause@20 | exact@20 | missing hit rows |
|---|---|---:|---:|---:|---:|---:|---:|
| `raw_surface_runtime` | `abbreviated` | 1 | 1 | 0.0% | 0.0% | 0.0% | 0 |
| `raw_surface_runtime` | `colloquial` | 1 | 1 | 0.0% | 0.0% | 0.0% | 0 |
| `raw_surface_runtime` | `formal` | 3 | 2 | 66.7% | 100.0% | 66.7% | 0 |
| `raw_surface_runtime` | `messenger_shorthand` | 3 | 2 | 0.0% | 0.0% | 0.0% | 0 |
| `surface_robust_runtime` | `abbreviated` | 1 | 1 | 100.0% | 100.0% | 100.0% | 0 |
| `surface_robust_runtime` | `colloquial` | 1 | 1 | 100.0% | 100.0% | 100.0% | 0 |
| `surface_robust_runtime` | `formal` | 3 | 2 | 66.7% | 100.0% | 66.7% | 0 |
| `surface_robust_runtime` | `messenger_shorthand` | 3 | 2 | 66.7% | 100.0% | 66.7% | 0 |

## Intent Family Breakdown

| system | slice | n | answerable | clause@20 | answerable_clause@20 | exact@20 | missing hit rows |
|---|---|---:|---:|---:|---:|---:|---:|
| `raw_surface_runtime` | `bundled_coverage` | 3 | 3 | 33.3% | 33.3% | 33.3% | 0 |
| `raw_surface_runtime` | `refund_termination` | 3 | 3 | 33.3% | 33.3% | 33.3% | 0 |
| `raw_surface_runtime` | `underwriting_context` | 2 | 0 | 0.0% | 0.0% | 0.0% | 0 |
| `surface_robust_runtime` | `bundled_coverage` | 3 | 3 | 100.0% | 100.0% | 100.0% | 0 |
| `surface_robust_runtime` | `refund_termination` | 3 | 3 | 100.0% | 100.0% | 100.0% | 0 |
| `surface_robust_runtime` | `underwriting_context` | 2 | 0 | 0.0% | 0.0% | 0.0% | 0 |

## Trap-Class Breakdown

| system | slice | n | answerable | clause@20 | answerable_clause@20 | exact@20 | missing hit rows |
|---|---|---:|---:|---:|---:|---:|---:|
| `raw_surface_runtime` | `abbreviation` | 1 | 1 | 0.0% | 0.0% | 0.0% | 0 |
| `raw_surface_runtime` | `bundle_expansion` | 3 | 3 | 33.3% | 33.3% | 33.3% | 0 |
| `raw_surface_runtime` | `messenger_shorthand` | 3 | 2 | 0.0% | 0.0% | 0.0% | 0 |
| `raw_surface_runtime` | `needs_private_context` | 2 | 0 | 0.0% | 0.0% | 0.0% | 0 |
| `raw_surface_runtime` | `product_table` | 3 | 3 | 33.3% | 33.3% | 33.3% | 0 |
| `raw_surface_runtime` | `register_mismatch` | 2 | 2 | 0.0% | 0.0% | 0.0% | 0 |
| `surface_robust_runtime` | `abbreviation` | 1 | 1 | 100.0% | 100.0% | 100.0% | 0 |
| `surface_robust_runtime` | `bundle_expansion` | 3 | 3 | 100.0% | 100.0% | 100.0% | 0 |
| `surface_robust_runtime` | `messenger_shorthand` | 3 | 2 | 66.7% | 100.0% | 66.7% | 0 |
| `surface_robust_runtime` | `needs_private_context` | 2 | 0 | 0.0% | 0.0% | 0.0% | 0 |
| `surface_robust_runtime` | `product_table` | 3 | 3 | 100.0% | 100.0% | 100.0% | 0 |
| `surface_robust_runtime` | `register_mismatch` | 2 | 2 | 100.0% | 100.0% | 100.0% | 0 |

## Use Notes

- `answerable_clause@20` excludes rows marked as requiring human context.
- `worst_surface_clause@20` is a stress signal for surface-form brittleness.
- Silver metadata and hit booleans are diagnostics until human labels exist.
