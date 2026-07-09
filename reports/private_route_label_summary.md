# Private Source-Route Silver Label Summary

This report is generated from private qrel metadata. It contains only
aggregate counts and baseline rates. It does not include qids, raw
queries, conversation snippets, platform identifiers, or ranked documents.

- source rows: 544
- private qrels path: `qrels_v1_700_partial.jsonl`
- private label export: `route_labels_v0_silver.jsonl`
- label status: silver proxy, not human-gold

## Baseline Context

| baseline | metric | value |
|---|---|---:|
| always_policy | route_accuracy | 21.5% |
| always_policy | abstention_recall | 0.0% |
| majority_route_floor | route_accuracy | 50.7% |

The majority-route floor is not a deployable system. It only shows how much
label skew a real source router must beat.

## Route Label Counts

| value | count | share |
|---|---:|---:|
| `human_context_needed` | 276 | 50.7% |
| `policy_clause` | 117 | 21.5% |
| `product_disclosure` | 51 | 9.4% |
| `dispute_case` | 48 | 8.8% |
| `claims_faq` | 31 | 5.7% |
| `expert_answer` | 21 | 3.9% |

## Abstention Counts

| value | count | share |
|---|---:|---:|
| `True` | 276 | 50.7% |
| `False` | 268 | 49.3% |

## Confidence Counts

| value | count | share |
|---|---:|---:|
| `high` | 276 | 50.7% |
| `medium` | 226 | 41.5% |
| `low` | 42 | 7.7% |

## Rationale Counts

| value | count | share |
|---|---:|---:|
| `needs_private_contract` | 276 | 50.7% |
| `policy_clause_direct` | 86 | 15.8% |
| `product_table_needed` | 51 | 9.4% |
| `dispute_needed` | 48 | 8.8% |
| `claims_ops` | 31 | 5.7% |
| `contract_table_direct` | 31 | 5.7% |
| `policy_corpus_insufficient` | 21 | 3.9% |

## Use Notes

- These labels are derived from qrel metadata and must be audited before headline claims.
- Public metrics may cite these counts as private-lab inventory, not as final benchmark gold.
- The next gate is double-labeling at least 50 rows and adjudicating disagreements.
