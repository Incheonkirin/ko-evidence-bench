# Normalization Ablation Fixture

This report compares a raw-surface baseline run with a normalized or
expanded candidate run. It reports aggregate rescue and regression counts
only; it does not include qids, raw queries, source names, conversation
snippets, or platform identifiers.

The public fixture treats `surface_robust_demo` as the normalized/expanded
candidate. Private experiments can replace the two run files with raw and
normalized retrieval outputs over the same qrels.

## Inputs

- qrels: `fixtures/surface_qrels.jsonl`
- baseline run: `fixtures/surface_runs/formal_only_demo.jsonl`
- candidate run: `fixtures/surface_runs/surface_robust_demo.jsonl`
- baseline name: `formal_only_demo`
- candidate name: `surface_robust_demo`
- label status: synthetic fixture metadata
- k: 3

## Overall Lift

| metric | value |
|---|---:|
| rows | 8 |
| baseline task success | 37.5% |
| candidate task success | 100.0% |
| net lift | 62.5% |
| rescued rows | 5 |
| regressed rows | 0 |

## Lift By Intent Family

| slice | n | baseline | candidate | lift | rescued | regressed |
|---|---:|---:|---:|---:|---:|---:|
| `bundled_coverage` | 3 | 33.3% | 100.0% | 66.7% | 2 | 0 |
| `refund_termination` | 3 | 33.3% | 100.0% | 66.7% | 2 | 0 |
| `underwriting_context` | 2 | 50.0% | 100.0% | 50.0% | 1 | 0 |

## Lift By Surface Form

| slice | n | baseline | candidate | lift | rescued | regressed |
|---|---:|---:|---:|---:|---:|---:|
| `abbreviated` | 1 | 0.0% | 100.0% | 100.0% | 1 | 0 |
| `colloquial` | 1 | 0.0% | 100.0% | 100.0% | 1 | 0 |
| `formal` | 3 | 100.0% | 100.0% | 0.0% | 0 | 0 |
| `messenger_shorthand` | 3 | 0.0% | 100.0% | 100.0% | 3 | 0 |

## Lift By Trap Class

| slice | n | baseline | candidate | lift | rescued | regressed |
|---|---:|---:|---:|---:|---:|---:|
| `abbreviation` | 1 | 0.0% | 100.0% | 100.0% | 1 | 0 |
| `bundle_expansion` | 3 | 33.3% | 100.0% | 66.7% | 2 | 0 |
| `messenger_shorthand` | 3 | 0.0% | 100.0% | 100.0% | 3 | 0 |
| `needs_private_context` | 2 | 50.0% | 100.0% | 50.0% | 1 | 0 |
| `product_table` | 3 | 33.3% | 100.0% | 66.7% | 2 | 0 |
| `register_mismatch` | 2 | 0.0% | 100.0% | 100.0% | 2 | 0 |

## Rescued Route Distribution

| route | rescued rows | share |
|---|---:|---:|
| `policy_clause` | 2 | 40.0% |
| `product_disclosure` | 2 | 40.0% |
| `human_context_needed` | 1 | 20.0% |

## Use Notes

- This is an ablation report, not a query-rewrite product.
- A private normalization experiment should keep raw queries outside the public repo
  and publish only this aggregate report.
- Per-family lift is the main signal; trap classes are diagnostic slices.
