# Private Intent-Family Inventory

This report summarizes intent families, source-route labels, surface
conditions, and trap annotations without exposing qids, raw queries,
conversation snippets, source names, or platform identifiers.

Intent families are the organizing unit. Surface forms and trap classes
are annotations used to slice retrieval failures.

## Inputs

- qrels: `surface_qrels_v0_silver.jsonl`
- rows: 544
- label status: silver intent/surface metadata; not human-gold

## Intent Family Summary

| intent family | rows | share | intents | surfaces | abstain rows | top routes | top surfaces | top traps |
|---|---:|---:|---:|---:|---:|---|---|---|
| `bundled_coverage` | 96 | 17.6% | 88 | 4 | 43 | `policy_clause:43, human_context_needed:43, expert_answer:9` | `formal:51, messenger_shorthand:35, abbreviated:5` | `bundle_expansion:82, numeric_constraint:60, source_routing:53` |
| `claims_process` | 54 | 9.9% | 47 | 4 | 29 | `human_context_needed:29, claims_faq:17, dispute_case:5` | `messenger_shorthand:24, formal:23, abbreviated:6` | `claim_ops:54, source_routing:51, register_mismatch:31` |
| `coverage_terms` | 6 | 1.1% | 6 | 2 | 1 | `policy_clause:5, human_context_needed:1` | `messenger_shorthand:3, formal:3` | `negation_or_exclusion:4, numeric_constraint:3, register_mismatch:3` |
| `dental_coverage` | 24 | 4.4% | 23 | 2 | 4 | `policy_clause:19, human_context_needed:4, dispute_case:1` | `formal:20, messenger_shorthand:4` | `negation_or_exclusion:20, numeric_constraint:16, product_table:8` |
| `dispute_complaint` | 14 | 2.6% | 14 | 3 | 7 | `human_context_needed:7, dispute_case:6, policy_clause:1` | `formal:9, messenger_shorthand:4, abbreviated:1` | `dispute_needed:14, source_routing:13, negation_or_exclusion:12` |
| `indemnity_noncovered` | 37 | 6.8% | 37 | 3 | 19 | `human_context_needed:19, policy_clause:11, dispute_case:4` | `formal:20, messenger_shorthand:9, abbreviated:8` | `numeric_constraint:28, source_routing:26, negation_or_exclusion:23` |
| `product_design` | 33 | 6.1% | 33 | 3 | 9 | `policy_clause:19, human_context_needed:9, expert_answer:4` | `formal:19, messenger_shorthand:8, abbreviated:6` | `numeric_constraint:15, register_mismatch:14, source_routing:14` |
| `refund_termination` | 256 | 47.1% | 213 | 4 | 155 | `human_context_needed:155, product_disclosure:51, dispute_case:23` | `formal:146, messenger_shorthand:71, abbreviated:36` | `product_table:256, source_routing:246, numeric_constraint:192` |
| `underwriting_context` | 24 | 4.4% | 19 | 3 | 9 | `human_context_needed:9, dispute_case:7, policy_clause:6` | `formal:13, messenger_shorthand:6, abbreviated:5` | `source_routing:18, numeric_constraint:13, register_mismatch:11` |

## Route Distribution

| value | count | share |
|---|---:|---:|
| `human_context_needed` | 276 | 50.7% |
| `policy_clause` | 117 | 21.5% |
| `product_disclosure` | 51 | 9.4% |
| `dispute_case` | 48 | 8.8% |
| `claims_faq` | 31 | 5.7% |
| `expert_answer` | 21 | 3.9% |

## Surface Distribution

| value | count | share |
|---|---:|---:|
| `formal` | 304 | 55.9% |
| `messenger_shorthand` | 164 | 30.1% |
| `abbreviated` | 67 | 12.3% |
| `colloquial` | 9 | 1.7% |

## Trap-Class Distribution

| value | count | share |
|---|---:|---:|
| `source_routing` | 427 | 19.5% |
| `numeric_constraint` | 365 | 16.7% |
| `negation_or_exclusion` | 312 | 14.2% |
| `product_table` | 306 | 14.0% |
| `needs_private_context` | 276 | 12.6% |
| `register_mismatch` | 240 | 11.0% |
| `bundle_expansion` | 190 | 8.7% |
| `claim_ops` | 54 | 2.5% |
| `dispute_needed` | 14 | 0.6% |
| `plain_clause_recall` | 6 | 0.3% |

## Metadata Completeness

| field | present | missing | completeness |
|---|---:|---:|---:|
| `intent_family` | 544 | 0 | 100.0% |
| `intent_id` | 544 | 0 | 100.0% |
| `surface_form` | 544 | 0 | 100.0% |

## Use Notes

- Private qrels can reuse this report after replacing raw query text with
  stable ids and audited metadata.
- `intent_family` should be assigned before making public frequency claims.
- Trap classes are diagnostic slices; they are not the benchmark's
  organizing unit.
