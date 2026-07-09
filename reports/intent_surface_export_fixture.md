# Private Intent/Surface Qrel Export Summary

This report summarizes a qid-only private export. It does not include
qids, raw queries, source names, conversation snippets, usernames, URLs,
or source file paths.

- label status: silver intent/surface metadata, not human-gold
- source qrel rows: 3
- source route-label rows: 3
- exported qid-only rows: 3
- missing route labels: 0
- answerable rows without evidence ids: 0
- private qid-only export: `not written`

## Intent Family Counts

| value | count | share |
|---|---:|---:|
| `indemnity_noncovered` | 1 | 33.3% |
| `underwriting_context` | 1 | 33.3% |
| `refund_termination` | 1 | 33.3% |

## Surface Form Counts

| value | count | share |
|---|---:|---:|
| `abbreviated` | 1 | 33.3% |
| `messenger_shorthand` | 1 | 33.3% |
| `formal` | 1 | 33.3% |

## Route Counts

| value | count | share |
|---|---:|---:|
| `policy_clause` | 1 | 33.3% |
| `human_context_needed` | 1 | 33.3% |
| `product_disclosure` | 1 | 33.3% |

## Trap-Class Counts

| value | count | share |
|---|---:|---:|
| `negation_or_exclusion` | 2 | 25.0% |
| `register_mismatch` | 2 | 25.0% |
| `source_routing` | 2 | 25.0% |
| `needs_private_context` | 1 | 12.5% |
| `product_table` | 1 | 12.5% |

## Use Notes

- This export creates benchmark metadata for slicing; it is not a claim
  that intent families are final human labels.
- Human adjudication should review route labels and metadata before any
  public headline result uses these slices.
- The qid-only export stays private because stable ids can link back to
  private worksets.
