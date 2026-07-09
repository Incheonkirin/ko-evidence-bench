# Private Runtime Surface Scorecard

This report joins qid-only intent/surface metadata with runtime
retrieval hit booleans such as `clause@20` and `exact@20`. It does
not include qids, raw queries, evidence ids, source names, usernames,
URLs, or document text.

It is a retrieval-hit surface scorecard. It does not judge answer
quality or source-route correctness; pair it with route scorecards
before making claims about end-to-end answerability.

## Inputs

- qrels: `private-surface-qrels`
- runtime result: `private-runtime-result`
- qrel rows: 544
- systems: 6
- primary metric: `clause@20`
- label status: silver hit booleans and silver intent/surface metadata; retrieval-hit only

## Runtime Surface Summary

| system | n | answerable | intent families | surfaces | clause@20 | answerable_clause@20 | exact@20 | avg_family_surface_spread | worst_surface_clause@20 | missing hit rows | missing metadata |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `minimal_cross_rrf` | 544 | 268 | 9 | 4 | 60.7% | 66.0% | 49.4% | 27.9% | 44.4% | 0 | 0 |
| `minimal_cross_text` | 544 | 268 | 9 | 4 | 64.2% | 68.7% | 52.8% | 28.3% | 44.4% | 0 | 0 |
| `minimal_pack` | 544 | 268 | 9 | 4 | 53.5% | 57.8% | 41.7% | 32.7% | 44.4% | 0 | 0 |
| `structural_cross_rrf` | 544 | 268 | 9 | 4 | 61.4% | 67.2% | 51.1% | 26.8% | 44.4% | 0 | 0 |
| `structural_cross_text` | 544 | 268 | 9 | 4 | 64.9% | 71.3% | 52.4% | 29.3% | 44.4% | 0 | 0 |
| `structural_pack` | 544 | 268 | 9 | 4 | 56.4% | 61.9% | 46.0% | 29.2% | 44.4% | 0 | 0 |

## Surface Form Breakdown

| system | slice | n | answerable | clause@20 | answerable_clause@20 | exact@20 | missing hit rows |
|---|---|---:|---:|---:|---:|---:|---:|
| `minimal_cross_rrf` | `abbreviated` | 67 | 33 | 70.1% | 78.8% | 55.2% | 0 |
| `minimal_cross_rrf` | `colloquial` | 9 | 5 | 44.4% | 40.0% | 33.3% | 0 |
| `minimal_cross_rrf` | `formal` | 304 | 142 | 59.5% | 65.5% | 48.7% | 0 |
| `minimal_cross_rrf` | `messenger_shorthand` | 164 | 88 | 59.8% | 63.6% | 49.4% | 0 |
| `minimal_cross_text` | `abbreviated` | 67 | 33 | 71.6% | 81.8% | 56.7% | 0 |
| `minimal_cross_text` | `colloquial` | 9 | 5 | 44.4% | 40.0% | 33.3% | 0 |
| `minimal_cross_text` | `formal` | 304 | 142 | 63.2% | 68.3% | 52.3% | 0 |
| `minimal_cross_text` | `messenger_shorthand` | 164 | 88 | 64.0% | 65.9% | 53.0% | 0 |
| `minimal_pack` | `abbreviated` | 67 | 33 | 62.7% | 66.7% | 50.7% | 0 |
| `minimal_pack` | `colloquial` | 9 | 5 | 44.4% | 40.0% | 33.3% | 0 |
| `minimal_pack` | `formal` | 304 | 142 | 51.6% | 57.0% | 38.5% | 0 |
| `minimal_pack` | `messenger_shorthand` | 164 | 88 | 53.7% | 56.8% | 44.5% | 0 |
| `structural_cross_rrf` | `abbreviated` | 67 | 33 | 70.1% | 78.8% | 58.2% | 0 |
| `structural_cross_rrf` | `colloquial` | 9 | 5 | 44.4% | 40.0% | 33.3% | 0 |
| `structural_cross_rrf` | `formal` | 304 | 142 | 60.9% | 67.6% | 50.0% | 0 |
| `structural_cross_rrf` | `messenger_shorthand` | 164 | 88 | 59.8% | 63.6% | 51.2% | 0 |
| `structural_cross_text` | `abbreviated` | 67 | 33 | 71.6% | 81.8% | 55.2% | 0 |
| `structural_cross_text` | `colloquial` | 9 | 5 | 44.4% | 40.0% | 33.3% | 0 |
| `structural_cross_text` | `formal` | 304 | 142 | 64.1% | 73.2% | 51.0% | 0 |
| `structural_cross_text` | `messenger_shorthand` | 164 | 88 | 64.6% | 65.9% | 54.9% | 0 |
| `structural_pack` | `abbreviated` | 67 | 33 | 61.2% | 66.7% | 49.3% | 0 |
| `structural_pack` | `colloquial` | 9 | 5 | 44.4% | 40.0% | 33.3% | 0 |
| `structural_pack` | `formal` | 304 | 142 | 56.2% | 63.4% | 45.1% | 0 |
| `structural_pack` | `messenger_shorthand` | 164 | 88 | 55.5% | 59.1% | 47.0% | 0 |

## Intent Family Breakdown

| system | slice | n | answerable | clause@20 | answerable_clause@20 | exact@20 | missing hit rows |
|---|---|---:|---:|---:|---:|---:|---:|
| `minimal_cross_rrf` | `bundled_coverage` | 96 | 53 | 57.3% | 60.4% | 52.1% | 0 |
| `minimal_cross_rrf` | `claims_process` | 54 | 25 | 72.2% | 72.0% | 57.4% | 0 |
| `minimal_cross_rrf` | `coverage_terms` | 6 | 5 | 100.0% | 100.0% | 83.3% | 0 |
| `minimal_cross_rrf` | `dental_coverage` | 24 | 20 | 91.7% | 90.0% | 79.2% | 0 |
| `minimal_cross_rrf` | `dispute_complaint` | 14 | 7 | 85.7% | 100.0% | 78.6% | 0 |
| `minimal_cross_rrf` | `indemnity_noncovered` | 37 | 18 | 48.6% | 55.6% | 35.1% | 0 |
| `minimal_cross_rrf` | `product_design` | 33 | 24 | 69.7% | 79.2% | 60.6% | 0 |
| `minimal_cross_rrf` | `refund_termination` | 256 | 101 | 55.9% | 59.4% | 43.4% | 0 |
| `minimal_cross_rrf` | `underwriting_context` | 24 | 15 | 50.0% | 53.3% | 37.5% | 0 |
| `minimal_cross_text` | `bundled_coverage` | 96 | 53 | 62.5% | 64.2% | 55.2% | 0 |
| `minimal_cross_text` | `claims_process` | 54 | 25 | 70.4% | 72.0% | 53.7% | 0 |
| `minimal_cross_text` | `coverage_terms` | 6 | 5 | 100.0% | 100.0% | 100.0% | 0 |
| `minimal_cross_text` | `dental_coverage` | 24 | 20 | 91.7% | 90.0% | 75.0% | 0 |
| `minimal_cross_text` | `dispute_complaint` | 14 | 7 | 78.6% | 85.7% | 71.4% | 0 |
| `minimal_cross_text` | `indemnity_noncovered` | 37 | 18 | 54.1% | 61.1% | 35.1% | 0 |
| `minimal_cross_text` | `product_design` | 33 | 24 | 72.7% | 79.2% | 60.6% | 0 |
| `minimal_cross_text` | `refund_termination` | 256 | 101 | 60.5% | 64.4% | 49.6% | 0 |
| `minimal_cross_text` | `underwriting_context` | 24 | 15 | 54.2% | 53.3% | 45.8% | 0 |
| `minimal_pack` | `bundled_coverage` | 96 | 53 | 51.0% | 54.7% | 44.8% | 0 |
| `minimal_pack` | `claims_process` | 54 | 25 | 57.4% | 48.0% | 42.6% | 0 |
| `minimal_pack` | `coverage_terms` | 6 | 5 | 100.0% | 100.0% | 66.7% | 0 |
| `minimal_pack` | `dental_coverage` | 24 | 20 | 83.3% | 80.0% | 66.7% | 0 |
| `minimal_pack` | `dispute_complaint` | 14 | 7 | 78.6% | 85.7% | 71.4% | 0 |
| `minimal_pack` | `indemnity_noncovered` | 37 | 18 | 43.2% | 50.0% | 32.4% | 0 |
| `minimal_pack` | `product_design` | 33 | 24 | 60.6% | 70.8% | 48.5% | 0 |
| `minimal_pack` | `refund_termination` | 256 | 101 | 50.0% | 53.5% | 37.1% | 0 |
| `minimal_pack` | `underwriting_context` | 24 | 15 | 41.7% | 46.7% | 33.3% | 0 |
| `structural_cross_rrf` | `bundled_coverage` | 96 | 53 | 57.3% | 58.5% | 53.1% | 0 |
| `structural_cross_rrf` | `claims_process` | 54 | 25 | 68.5% | 68.0% | 53.7% | 0 |
| `structural_cross_rrf` | `coverage_terms` | 6 | 5 | 100.0% | 100.0% | 83.3% | 0 |
| `structural_cross_rrf` | `dental_coverage` | 24 | 20 | 91.7% | 90.0% | 83.3% | 0 |
| `structural_cross_rrf` | `dispute_complaint` | 14 | 7 | 85.7% | 100.0% | 78.6% | 0 |
| `structural_cross_rrf` | `indemnity_noncovered` | 37 | 18 | 56.8% | 66.7% | 40.5% | 0 |
| `structural_cross_rrf` | `product_design` | 33 | 24 | 69.7% | 79.2% | 60.6% | 0 |
| `structural_cross_rrf` | `refund_termination` | 256 | 101 | 57.0% | 62.4% | 45.7% | 0 |
| `structural_cross_rrf` | `underwriting_context` | 24 | 15 | 50.0% | 53.3% | 41.7% | 0 |
| `structural_cross_text` | `bundled_coverage` | 96 | 53 | 60.4% | 64.2% | 56.2% | 0 |
| `structural_cross_text` | `claims_process` | 54 | 25 | 70.4% | 72.0% | 53.7% | 0 |
| `structural_cross_text` | `coverage_terms` | 6 | 5 | 100.0% | 100.0% | 100.0% | 0 |
| `structural_cross_text` | `dental_coverage` | 24 | 20 | 91.7% | 90.0% | 75.0% | 0 |
| `structural_cross_text` | `dispute_complaint` | 14 | 7 | 78.6% | 85.7% | 71.4% | 0 |
| `structural_cross_text` | `indemnity_noncovered` | 37 | 18 | 56.8% | 61.1% | 37.8% | 0 |
| `structural_cross_text` | `product_design` | 33 | 24 | 72.7% | 79.2% | 60.6% | 0 |
| `structural_cross_text` | `refund_termination` | 256 | 101 | 62.1% | 69.3% | 48.0% | 0 |
| `structural_cross_text` | `underwriting_context` | 24 | 15 | 58.3% | 66.7% | 45.8% | 0 |
| `structural_pack` | `bundled_coverage` | 96 | 53 | 55.2% | 58.5% | 50.0% | 0 |
| `structural_pack` | `claims_process` | 54 | 25 | 59.3% | 52.0% | 46.3% | 0 |
| `structural_pack` | `coverage_terms` | 6 | 5 | 100.0% | 100.0% | 66.7% | 0 |
| `structural_pack` | `dental_coverage` | 24 | 20 | 87.5% | 85.0% | 79.2% | 0 |
| `structural_pack` | `dispute_complaint` | 14 | 7 | 85.7% | 100.0% | 78.6% | 0 |
| `structural_pack` | `indemnity_noncovered` | 37 | 18 | 48.6% | 61.1% | 32.4% | 0 |
| `structural_pack` | `product_design` | 33 | 24 | 66.7% | 75.0% | 51.5% | 0 |
| `structural_pack` | `refund_termination` | 256 | 101 | 52.0% | 56.4% | 41.0% | 0 |
| `structural_pack` | `underwriting_context` | 24 | 15 | 41.7% | 46.7% | 37.5% | 0 |

## Trap-Class Breakdown

| system | slice | n | answerable | clause@20 | answerable_clause@20 | exact@20 | missing hit rows |
|---|---|---:|---:|---:|---:|---:|---:|
| `minimal_cross_rrf` | `bundle_expansion` | 190 | 88 | 59.5% | 62.5% | 46.8% | 0 |
| `minimal_cross_rrf` | `claim_ops` | 54 | 25 | 72.2% | 72.0% | 57.4% | 0 |
| `minimal_cross_rrf` | `dispute_needed` | 14 | 7 | 85.7% | 100.0% | 78.6% | 0 |
| `minimal_cross_rrf` | `needs_private_context` | 276 | 0 | 55.4% | 0.0% | 42.4% | 0 |
| `minimal_cross_rrf` | `negation_or_exclusion` | 312 | 145 | 66.7% | 73.8% | 52.2% | 0 |
| `minimal_cross_rrf` | `numeric_constraint` | 365 | 157 | 61.9% | 69.4% | 49.6% | 0 |
| `minimal_cross_rrf` | `plain_clause_recall` | 6 | 6 | 50.0% | 50.0% | 50.0% | 0 |
| `minimal_cross_rrf` | `product_table` | 306 | 132 | 60.5% | 65.2% | 47.7% | 0 |
| `minimal_cross_rrf` | `register_mismatch` | 240 | 126 | 62.1% | 66.7% | 50.4% | 0 |
| `minimal_cross_rrf` | `source_routing` | 427 | 151 | 57.1% | 60.3% | 45.2% | 0 |
| `minimal_cross_text` | `bundle_expansion` | 190 | 88 | 63.2% | 65.9% | 50.5% | 0 |
| `minimal_cross_text` | `claim_ops` | 54 | 25 | 70.4% | 72.0% | 53.7% | 0 |
| `minimal_cross_text` | `dispute_needed` | 14 | 7 | 78.6% | 85.7% | 71.4% | 0 |
| `minimal_cross_text` | `needs_private_context` | 276 | 0 | 59.8% | 0.0% | 46.7% | 0 |
| `minimal_cross_text` | `negation_or_exclusion` | 312 | 145 | 69.2% | 76.6% | 55.4% | 0 |
| `minimal_cross_text` | `numeric_constraint` | 365 | 157 | 66.8% | 73.2% | 53.4% | 0 |
| `minimal_cross_text` | `plain_clause_recall` | 6 | 6 | 50.0% | 50.0% | 50.0% | 0 |
| `minimal_cross_text` | `product_table` | 306 | 132 | 64.7% | 69.7% | 53.3% | 0 |
| `minimal_cross_text` | `register_mismatch` | 240 | 126 | 65.4% | 69.0% | 53.3% | 0 |
| `minimal_cross_text` | `source_routing` | 427 | 151 | 61.1% | 63.6% | 49.9% | 0 |
| `minimal_pack` | `bundle_expansion` | 190 | 88 | 51.1% | 54.5% | 39.5% | 0 |
| `minimal_pack` | `claim_ops` | 54 | 25 | 57.4% | 48.0% | 42.6% | 0 |
| `minimal_pack` | `dispute_needed` | 14 | 7 | 78.6% | 85.7% | 71.4% | 0 |
| `minimal_pack` | `needs_private_context` | 276 | 0 | 49.3% | 0.0% | 35.9% | 0 |
| `minimal_pack` | `negation_or_exclusion` | 312 | 145 | 58.3% | 64.1% | 43.9% | 0 |
| `minimal_pack` | `numeric_constraint` | 365 | 157 | 53.4% | 58.6% | 40.8% | 0 |
| `minimal_pack` | `plain_clause_recall` | 6 | 6 | 50.0% | 50.0% | 16.7% | 0 |
| `minimal_pack` | `product_table` | 306 | 132 | 53.9% | 58.3% | 41.2% | 0 |
| `minimal_pack` | `register_mismatch` | 240 | 126 | 55.8% | 58.7% | 45.8% | 0 |
| `minimal_pack` | `source_routing` | 427 | 151 | 50.1% | 51.7% | 38.6% | 0 |
| `structural_cross_rrf` | `bundle_expansion` | 190 | 88 | 60.5% | 64.8% | 50.5% | 0 |
| `structural_cross_rrf` | `claim_ops` | 54 | 25 | 68.5% | 68.0% | 53.7% | 0 |
| `structural_cross_rrf` | `dispute_needed` | 14 | 7 | 85.7% | 100.0% | 78.6% | 0 |
| `structural_cross_rrf` | `needs_private_context` | 276 | 0 | 55.8% | 0.0% | 43.1% | 0 |
| `structural_cross_rrf` | `negation_or_exclusion` | 312 | 145 | 68.9% | 76.6% | 54.2% | 0 |
| `structural_cross_rrf` | `numeric_constraint` | 365 | 157 | 63.8% | 71.3% | 52.1% | 0 |
| `structural_cross_rrf` | `plain_clause_recall` | 6 | 6 | 50.0% | 50.0% | 50.0% | 0 |
| `structural_cross_rrf` | `product_table` | 306 | 132 | 61.4% | 66.7% | 50.3% | 0 |
| `structural_cross_rrf` | `register_mismatch` | 240 | 126 | 62.1% | 66.7% | 52.5% | 0 |
| `structural_cross_rrf` | `source_routing` | 427 | 151 | 58.1% | 62.3% | 46.6% | 0 |
| `structural_cross_text` | `bundle_expansion` | 190 | 88 | 62.1% | 65.9% | 51.6% | 0 |
| `structural_cross_text` | `claim_ops` | 54 | 25 | 70.4% | 72.0% | 53.7% | 0 |
| `structural_cross_text` | `dispute_needed` | 14 | 7 | 78.6% | 85.7% | 71.4% | 0 |
| `structural_cross_text` | `needs_private_context` | 276 | 0 | 58.7% | 0.0% | 44.6% | 0 |
| `structural_cross_text` | `negation_or_exclusion` | 312 | 145 | 70.5% | 79.3% | 54.5% | 0 |
| `structural_cross_text` | `numeric_constraint` | 365 | 157 | 68.2% | 76.4% | 52.9% | 0 |
| `structural_cross_text` | `plain_clause_recall` | 6 | 6 | 66.7% | 66.7% | 50.0% | 0 |
| `structural_cross_text` | `product_table` | 306 | 132 | 65.7% | 72.7% | 52.0% | 0 |
| `structural_cross_text` | `register_mismatch` | 240 | 126 | 65.8% | 69.0% | 54.2% | 0 |
| `structural_cross_text` | `source_routing` | 427 | 151 | 62.1% | 68.2% | 48.9% | 0 |
| `structural_pack` | `bundle_expansion` | 190 | 88 | 54.2% | 60.2% | 42.6% | 0 |
| `structural_pack` | `claim_ops` | 54 | 25 | 59.3% | 52.0% | 46.3% | 0 |
| `structural_pack` | `dispute_needed` | 14 | 7 | 85.7% | 100.0% | 78.6% | 0 |
| `structural_pack` | `needs_private_context` | 276 | 0 | 51.1% | 0.0% | 38.8% | 0 |
| `structural_pack` | `negation_or_exclusion` | 312 | 145 | 62.8% | 69.7% | 49.0% | 0 |
| `structural_pack` | `numeric_constraint` | 365 | 157 | 57.3% | 64.3% | 46.0% | 0 |
| `structural_pack` | `plain_clause_recall` | 6 | 6 | 50.0% | 50.0% | 16.7% | 0 |
| `structural_pack` | `product_table` | 306 | 132 | 55.9% | 60.6% | 45.4% | 0 |
| `structural_pack` | `register_mismatch` | 240 | 126 | 56.7% | 60.3% | 47.1% | 0 |
| `structural_pack` | `source_routing` | 427 | 151 | 52.7% | 55.6% | 41.9% | 0 |

## Use Notes

- `answerable_clause@20` excludes rows marked as requiring human context.
- `worst_surface_clause@20` is a stress signal for surface-form brittleness.
- Silver metadata and hit booleans are diagnostics until human labels exist.
