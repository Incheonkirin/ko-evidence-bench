# Private Intent/Surface Qrel Export Summary

This report summarizes a qid-only private export. It does not include
qids, raw queries, source names, conversation snippets, usernames, URLs,
or source file paths.

- label status: silver intent/surface metadata, not human-gold
- source qrel rows: 544
- source route-label rows: 544
- exported qid-only rows: 544
- missing route labels: 0
- answerable rows without evidence ids: 20
- private qid-only export: `surface_qrels_v0_silver.jsonl`

## Intent Family Counts

| value | count | share |
|---|---:|---:|
| `refund_termination` | 256 | 47.1% |
| `bundled_coverage` | 96 | 17.6% |
| `claims_process` | 54 | 9.9% |
| `indemnity_noncovered` | 37 | 6.8% |
| `product_design` | 33 | 6.1% |
| `dental_coverage` | 24 | 4.4% |
| `underwriting_context` | 24 | 4.4% |
| `dispute_complaint` | 14 | 2.6% |
| `coverage_terms` | 6 | 1.1% |

## Surface Form Counts

| value | count | share |
|---|---:|---:|
| `formal` | 304 | 55.9% |
| `messenger_shorthand` | 164 | 30.1% |
| `abbreviated` | 67 | 12.3% |
| `colloquial` | 9 | 1.7% |

## Route Counts

| value | count | share |
|---|---:|---:|
| `human_context_needed` | 276 | 50.7% |
| `policy_clause` | 117 | 21.5% |
| `product_disclosure` | 51 | 9.4% |
| `dispute_case` | 48 | 8.8% |
| `claims_faq` | 31 | 5.7% |
| `expert_answer` | 21 | 3.9% |

## Trap-Class Counts

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

## Use Notes

- This export creates benchmark metadata for slicing; it is not a claim
  that intent families are final human labels.
- Human adjudication should review route labels and metadata before any
  public headline result uses these slices.
- The qid-only export stays private because stable ids can link back to
  private worksets.
