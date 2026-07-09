# Intent-Family Inventory Fixture

This report summarizes intent families, source-route labels, surface
conditions, and trap annotations without exposing qids, raw queries,
conversation snippets, source names, or platform identifiers.

Intent families are the organizing unit. Surface forms and trap classes
are annotations used to slice retrieval failures.

## Inputs

- qrels: `fixtures/surface_qrels.jsonl`
- rows: 8
- label status: synthetic fixture metadata

## Intent Family Summary

| intent family | rows | share | intents | surfaces | abstain rows | top routes | top surfaces | top traps |
|---|---:|---:|---:|---:|---:|---|---|---|
| `bundled_coverage` | 3 | 37.5% | 1 | 3 | 0 | `policy_clause:3` | `formal:1, abbreviated:1, messenger_shorthand:1` | `bundle_expansion:3, abbreviation:1, messenger_shorthand:1` |
| `refund_termination` | 3 | 37.5% | 1 | 3 | 0 | `product_disclosure:3` | `formal:1, colloquial:1, messenger_shorthand:1` | `product_table:3, register_mismatch:2, messenger_shorthand:1` |
| `underwriting_context` | 2 | 25.0% | 1 | 2 | 2 | `human_context_needed:2` | `formal:1, messenger_shorthand:1` | `needs_private_context:2, messenger_shorthand:1` |

## Route Distribution

| value | count | share |
|---|---:|---:|
| `policy_clause` | 3 | 37.5% |
| `product_disclosure` | 3 | 37.5% |
| `human_context_needed` | 2 | 25.0% |

## Surface Distribution

| value | count | share |
|---|---:|---:|
| `formal` | 3 | 37.5% |
| `messenger_shorthand` | 3 | 37.5% |
| `abbreviated` | 1 | 12.5% |
| `colloquial` | 1 | 12.5% |

## Trap-Class Distribution

| value | count | share |
|---|---:|---:|
| `bundle_expansion` | 3 | 21.4% |
| `messenger_shorthand` | 3 | 21.4% |
| `product_table` | 3 | 21.4% |
| `needs_private_context` | 2 | 14.3% |
| `register_mismatch` | 2 | 14.3% |
| `abbreviation` | 1 | 7.1% |

## Metadata Completeness

| field | present | missing | completeness |
|---|---:|---:|---:|
| `intent_family` | 8 | 0 | 100.0% |
| `intent_id` | 8 | 0 | 100.0% |
| `surface_form` | 8 | 0 | 100.0% |

## Use Notes

- Private qrels can reuse this report after replacing raw query text with
  stable ids and audited metadata.
- `intent_family` should be assigned before making public frequency claims.
- Trap classes are diagnostic slices; they are not the benchmark's
  organizing unit.
