# Audit Surface Coverage Fixture

Status: **PASS**.

This report checks whether a human-audit workset covers the same
qid-only intent family, surface-form, and trap-class axes used by the
retrieval diagnostics. It contains aggregate counts only and does not
include qids, raw queries, context, reviewer notes, source names, URLs,
or evidence ids.

## Inputs

- qrels: `fixtures/surface_qrels.jsonl`
- audit workset: `fixtures/route_audit/surface_audit_seed.jsonl`
- qrel rows: 8
- audit rows: 8
- matched audit rows: 8
- unmatched audit rows: 0
- label status: synthetic audit coverage fixture

## Coverage Summary

| axis | full values | sampled values | missing values | min sampled rows | max sampled rows | status |
|---|---:|---:|---:|---:|---:|---|
| `route_gold` | 3 | 3 | 0 | 2 | 3 | `PASS` |
| `intent_family` | 3 | 3 | 0 | 2 | 3 | `PASS` |
| `surface_form` | 4 | 4 | 0 | 1 | 3 | `PASS` |
| `trap_classes` | 6 | 6 | 0 | 1 | 3 | `PASS` |

## Sampled Surface Distribution

| value | sampled rows | share |
|---|---:|---:|
| `formal` | 3 | 37.5% |
| `messenger_shorthand` | 3 | 37.5% |
| `abbreviated` | 1 | 12.5% |
| `colloquial` | 1 | 12.5% |

## Sampled Intent-Family Distribution

| value | sampled rows | share |
|---|---:|---:|
| `bundled_coverage` | 3 | 37.5% |
| `refund_termination` | 3 | 37.5% |
| `underwriting_context` | 2 | 25.0% |

## Sampled Trap-Class Distribution

| value | sampled rows | share |
|---|---:|---:|
| `bundle_expansion` | 3 | 21.4% |
| `messenger_shorthand` | 3 | 21.4% |
| `product_table` | 3 | 21.4% |
| `register_mismatch` | 2 | 14.3% |
| `needs_private_context` | 2 | 14.3% |
| `abbreviation` | 1 | 7.1% |

## Use Notes

- This is a coverage check for the audit workset, not evidence that the
  labels have been completed.
- Public headline claims still require completed independent labels,
  agreement evidence, adjudication, and validation.
- If an axis is incomplete, rebuild or supplement the private audit pack
  before spending reviewer time.
