# Public Probe Trap Mining

Status: **synthetic probe diagnostics only; not analyzer-specific benchmark results**.

This report mines trap-class candidates from public synthetic probe
queries and compares them with the checked-in qrel annotations. It is
a diagnostic dry run for failure mining, not a synonym dictionary
or user-dictionary recommendation.

## Inputs

- probe dir: `probes/ko_evidence_probe_v0`
- query rows: 13
- qrel rows: 13
- label status: synthetic public fixture

## Coverage

| item | value |
|---|---:|
| rows | 13 |
| rows with any detection | 13 (100.0%) |
| rows with all expected traps detected | 13 (100.0%) |
| rows with extra diagnostic traps | 3 (23.1%) |

## Expected Trap Classes

| value | rows |
|---|---:|
| `bundle_expansion` | 3 |
| `messenger_shorthand` | 3 |
| `source_routing` | 3 |
| `needs_private_context` | 2 |
| `negation_or_exclusion` | 2 |
| `product_table` | 2 |
| `register_mismatch` | 2 |
| `abbreviation` | 1 |

## Detected Trap Classes

| value | rows |
|---|---:|
| `source_routing` | 4 |
| `bundle_expansion` | 3 |
| `messenger_shorthand` | 3 |
| `negation_or_exclusion` | 3 |
| `abbreviation` | 2 |
| `needs_private_context` | 2 |
| `product_table` | 2 |
| `register_mismatch` | 2 |

## Matched Trap Classes

| value | rows |
|---|---:|
| `bundle_expansion` | 3 |
| `messenger_shorthand` | 3 |
| `source_routing` | 3 |
| `needs_private_context` | 2 |
| `negation_or_exclusion` | 2 |
| `product_table` | 2 |
| `register_mismatch` | 2 |
| `abbreviation` | 1 |

## Missed Trap Classes

| value | rows |
|---|---:|
| none | 0 |

## Extra Diagnostic Traps

| value | rows |
|---|---:|
| `abbreviation` | 1 |
| `negation_or_exclusion` | 1 |
| `source_routing` | 1 |

## Diagnostic Layers

| value | rows |
|---|---:|
| `surface_fragmentation` | 6 |
| `source_route` | 4 |
| `semantic_contrast` | 3 |
| `abstention` | 2 |
| `evidence_form` | 2 |
| `register_gap` | 2 |

## Detected Traps By Surface Form

| slice | top detected traps |
|---|---|
| `abbreviated` | `bundle_expansion:1`, `abbreviation:1` |
| `colloquial` | `abbreviation:1`, `negation_or_exclusion:1`, `register_mismatch:1`, `needs_private_context:1` |
| `formal` | `source_routing:4`, `negation_or_exclusion:2`, `bundle_expansion:1`, `product_table:1` |
| `messenger_shorthand` | `messenger_shorthand:3`, `bundle_expansion:1`, `product_table:1`, `needs_private_context:1` |

## Detected Traps By Intent Family

| slice | top detected traps |
|---|---|
| `bundled_coverage` | `bundle_expansion:3`, `abbreviation:1`, `messenger_shorthand:1` |
| `claims_process` | `source_routing:1` |
| `dispute_complaint` | `negation_or_exclusion:1`, `source_routing:1` |
| `indemnity_noncovered` | `negation_or_exclusion:2`, `abbreviation:1`, `register_mismatch:1` |
| `product_design` | `source_routing:1` |
| `refund_termination` | `product_table:2`, `messenger_shorthand:1` |
| `underwriting_context` | `needs_private_context:2`, `messenger_shorthand:1`, `register_mismatch:1`, `source_routing:1` |

## Row Audit

| qid | expected | detected | missed | extra | layers |
|---|---|---|---|---|---|
| `probe-bundle-formal` | `bundle_expansion` | `bundle_expansion` | none | none | `surface_fragmentation` |
| `probe-bundle-abbrev` | `bundle_expansion`, `abbreviation` | `bundle_expansion`, `abbreviation` | none | none | `surface_fragmentation` |
| `probe-bundle-messenger` | `bundle_expansion`, `messenger_shorthand` | `bundle_expansion`, `messenger_shorthand` | none | none | `surface_fragmentation` |
| `probe-indemnity-formal` | `negation_or_exclusion` | `negation_or_exclusion` | none | none | `semantic_contrast` |
| `probe-indemnity-colloquial` | `negation_or_exclusion`, `register_mismatch` | `abbreviation`, `negation_or_exclusion`, `register_mismatch` | none | `abbreviation` | `register_gap`, `semantic_contrast`, `surface_fragmentation` |
| `probe-refund-formal` | `product_table` | `product_table` | none | none | `evidence_form` |
| `probe-refund-messenger` | `product_table`, `messenger_shorthand` | `messenger_shorthand`, `product_table` | none | none | `evidence_form`, `surface_fragmentation` |
| `probe-underwriting-context` | `needs_private_context` | `needs_private_context` | none | none | `abstention` |
| `probe-underwriting-messenger` | `needs_private_context`, `messenger_shorthand` | `messenger_shorthand`, `needs_private_context` | none | none | `abstention`, `surface_fragmentation` |
| `probe-claims-docs` | `source_routing` | `source_routing` | none | none | `source_route` |
| `probe-dispute-denial` | `source_routing` | `negation_or_exclusion`, `source_routing` | none | `negation_or_exclusion` | `semantic_contrast`, `source_route` |
| `probe-product-disclosure` | `source_routing` | `source_routing` | none | none | `source_route` |
| `probe-expert-explain` | `register_mismatch` | `register_mismatch`, `source_routing` | none | `source_routing` | `register_gap`, `source_route` |

## Use Notes

- This report proves the trap-mining path on public synthetic rows only.
- Extra traps are diagnostic hypotheses; they do not rewrite qrels by themselves.
- Missed traps are useful regression targets for future analyzer-specific miners.
- Private query logs can use the same aggregate report shape while keeping raw text outside the repository.
