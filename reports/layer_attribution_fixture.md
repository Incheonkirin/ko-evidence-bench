# Layer Attribution Fixture

Status: **diagnostic layer attribution only; human-gold attribution blocked**.

This report attributes each failed synthetic retrieval row to one primary
diagnostic layer. It is designed to make failure mass inspectable without
publishing qids, raw queries, source names, URLs, conversation snippets,
or document text.

The attribution is ordered and diagnostic: abstention failures are counted
before route failures, route failures before evidence-hit failures, and
surface/register annotations are used only after the route is correct.

## Inputs

- qrels: `fixtures/surface_qrels.jsonl`
- runs: `fixtures/surface_runs`
- qrel rows: 8
- systems: 2
- k: 3
- label status: synthetic fixture metadata

## Layer Attribution Summary

| system | n | success rate | failure rows | dominant failure layer |
|---|---:|---:|---:|---|
| `formal_only_demo` | 8 | 37.5% | 5 | `surface_fragmentation` |
| `surface_robust_demo` | 8 | 100.0% | 0 | `success` |

## Failure Mass By Layer

| system | layer | rows | share of run | share of failures |
|---|---|---:|---:|---:|
| `formal_only_demo` | `success` | 3 | 37.5% | 0.0% |
| `formal_only_demo` | `abstention_failure` | 1 | 12.5% | 20.0% |
| `formal_only_demo` | `register_gap` | 1 | 12.5% | 20.0% |
| `formal_only_demo` | `source_route_failure` | 1 | 12.5% | 20.0% |
| `formal_only_demo` | `surface_fragmentation` | 2 | 25.0% | 40.0% |
| `surface_robust_demo` | `success` | 8 | 100.0% | 0.0% |

## Layer By Intent Family

| system | slice | n | success rate | failure rows | dominant failure layer |
|---|---|---:|---:|---:|---|
| `formal_only_demo` | `bundled_coverage` | 3 | 33.3% | 2 | `surface_fragmentation` |
| `formal_only_demo` | `refund_termination` | 3 | 33.3% | 2 | `register_gap` |
| `formal_only_demo` | `underwriting_context` | 2 | 50.0% | 1 | `abstention_failure` |
| `surface_robust_demo` | `bundled_coverage` | 3 | 100.0% | 0 | `success` |
| `surface_robust_demo` | `refund_termination` | 3 | 100.0% | 0 | `success` |
| `surface_robust_demo` | `underwriting_context` | 2 | 100.0% | 0 | `success` |

## Layer By Surface Form

| system | slice | n | success rate | failure rows | dominant failure layer |
|---|---|---:|---:|---:|---|
| `formal_only_demo` | `abbreviated` | 1 | 0.0% | 1 | `surface_fragmentation` |
| `formal_only_demo` | `colloquial` | 1 | 0.0% | 1 | `register_gap` |
| `formal_only_demo` | `formal` | 3 | 100.0% | 0 | `success` |
| `formal_only_demo` | `messenger_shorthand` | 3 | 0.0% | 3 | `surface_fragmentation` |
| `surface_robust_demo` | `abbreviated` | 1 | 100.0% | 0 | `success` |
| `surface_robust_demo` | `colloquial` | 1 | 100.0% | 0 | `success` |
| `surface_robust_demo` | `formal` | 3 | 100.0% | 0 | `success` |
| `surface_robust_demo` | `messenger_shorthand` | 3 | 100.0% | 0 | `success` |

## Layer By Trap Class

| system | slice | n | success rate | failure rows | dominant failure layer |
|---|---|---:|---:|---:|---|
| `formal_only_demo` | `abbreviation` | 1 | 0.0% | 1 | `surface_fragmentation` |
| `formal_only_demo` | `bundle_expansion` | 3 | 33.3% | 2 | `surface_fragmentation` |
| `formal_only_demo` | `messenger_shorthand` | 3 | 0.0% | 3 | `surface_fragmentation` |
| `formal_only_demo` | `needs_private_context` | 2 | 50.0% | 1 | `abstention_failure` |
| `formal_only_demo` | `product_table` | 3 | 33.3% | 2 | `register_gap` |
| `formal_only_demo` | `register_mismatch` | 2 | 0.0% | 2 | `register_gap` |
| `surface_robust_demo` | `abbreviation` | 1 | 100.0% | 0 | `success` |
| `surface_robust_demo` | `bundle_expansion` | 3 | 100.0% | 0 | `success` |
| `surface_robust_demo` | `messenger_shorthand` | 3 | 100.0% | 0 | `success` |
| `surface_robust_demo` | `needs_private_context` | 2 | 100.0% | 0 | `success` |
| `surface_robust_demo` | `product_table` | 3 | 100.0% | 0 | `success` |
| `surface_robust_demo` | `register_mismatch` | 2 | 100.0% | 0 | `success` |

## Use Notes

- This is the Table-2-style decomposition hook for the measurement study.
- The public fixture proves the attribution path, not final system behavior.
- Private runs can reuse the same qid-only path once route labels and
  intent/surface metadata are human-audited.
