# Private Audit Surface Coverage

Status: **PASS**.

This report checks whether a human-audit workset covers the same
qid-only intent family, surface-form, and trap-class axes used by the
retrieval diagnostics. It contains aggregate counts only and does not
include qids, raw queries, context, reviewer notes, source names, URLs,
or evidence ids.

## Inputs

- qrels: `private-surface-qrels`
- audit workset: `private-audit-workset`
- qrel rows: 544
- audit rows: 300
- matched audit rows: 300
- unmatched audit rows: 0
- label status: 300-row private audit workset over silver intent/surface metadata

## Coverage Summary

| axis | full values | sampled values | missing values | min sampled rows | max sampled rows | status |
|---|---:|---:|---:|---:|---:|---|
| `route_gold` | 6 | 6 | 0 | 20 | 152 | `PASS` |
| `intent_family` | 9 | 9 | 0 | 4 | 133 | `PASS` |
| `surface_form` | 4 | 4 | 0 | 4 | 167 | `PASS` |
| `trap_classes` | 10 | 10 | 0 | 4 | 238 | `PASS` |

## Sampled Surface Distribution

| value | sampled rows | share |
|---|---:|---:|
| `formal` | 167 | 55.7% |
| `messenger_shorthand` | 92 | 30.7% |
| `abbreviated` | 37 | 12.3% |
| `colloquial` | 4 | 1.3% |

## Sampled Intent-Family Distribution

| value | sampled rows | share |
|---|---:|---:|
| `refund_termination` | 133 | 44.3% |
| `bundled_coverage` | 55 | 18.3% |
| `claims_process` | 32 | 10.7% |
| `product_design` | 22 | 7.3% |
| `indemnity_noncovered` | 19 | 6.3% |
| `underwriting_context` | 17 | 5.7% |
| `dental_coverage` | 14 | 4.7% |
| `coverage_terms` | 4 | 1.3% |
| `dispute_complaint` | 4 | 1.3% |

## Sampled Trap-Class Distribution

| value | sampled rows | share |
|---|---:|---:|
| `source_routing` | 238 | 19.9% |
| `numeric_constraint` | 195 | 16.3% |
| `product_table` | 163 | 13.6% |
| `negation_or_exclusion` | 160 | 13.4% |
| `needs_private_context` | 152 | 12.7% |
| `register_mismatch` | 133 | 11.1% |
| `bundle_expansion` | 114 | 9.5% |
| `claim_ops` | 32 | 2.7% |
| `plain_clause_recall` | 6 | 0.5% |
| `dispute_needed` | 4 | 0.3% |

## Use Notes

- This is a coverage check for the audit workset, not evidence that the
  labels have been completed.
- Public headline claims still require completed independent labels,
  agreement evidence, adjudication, and validation.
- If an axis is incomplete, rebuild or supplement the private audit pack
  before spending reviewer time.
