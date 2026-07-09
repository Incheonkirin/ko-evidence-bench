# Private Route Review Brief

This brief summarizes the private route-review workset without exposing
qids, raw queries, context, or reviewer notes. It is meant to guide manual
adjudication before import, validation, and promotion.

- private csv: `route_review_v0_300_adjudicated.csv`
- rows: 300
- currently complete rows: 0
- remaining rows: 300

## Review Priorities

| priority | count | why review carefully |
|---|---:|---|
| silver `low` confidence | 32 | likely label-boundary cases |
| silver `medium` confidence | 116 | useful second-pass review set |
| silver `should_abstain=true` | 152 | controls abstention recall and false-answer risk |
| `needs_contract=true` | 149 | should usually route to human context unless source evidence is enough |
| `product_divergent=true` | 86 | likely not answerable by one generic policy clause |

## Required Per Row

| field | expected content |
|---|---|
| `route_gold` | one source-route label |
| `allowed_source_tiers` | `;`-separated source tiers supporting safe citation |
| `should_abstain` | `true` or `false` |
| `confidence` | `high`, `medium`, or `low` |
| `rationale_code` | compact reason code for the route decision |
| `labeler` | reviewer id or initials |

## Workset Distribution: `silver_route_gold`

| value | count | share |
|---|---:|---:|
| `human_context_needed` | 152 | 50.7% |
| `policy_clause` | 62 | 20.7% |
| `dispute_case` | 26 | 8.7% |
| `product_disclosure` | 20 | 6.7% |
| `expert_answer` | 20 | 6.7% |
| `claims_faq` | 20 | 6.7% |

## Workset Distribution: `silver_confidence`

| value | count | share |
|---|---:|---:|
| `high` | 152 | 50.7% |
| `medium` | 116 | 38.7% |
| `low` | 32 | 10.7% |

## Workset Distribution: `silver_rationale_code`

| value | count | share |
|---|---:|---:|
| `needs_private_contract` | 152 | 50.7% |
| `policy_clause_direct` | 44 | 14.7% |
| `dispute_needed` | 26 | 8.7% |
| `product_table_needed` | 20 | 6.7% |
| `policy_corpus_insufficient` | 20 | 6.7% |
| `claims_ops` | 20 | 6.7% |
| `contract_table_direct` | 18 | 6.0% |

## Workset Distribution: `silver_should_abstain`

| value | count | share |
|---|---:|---:|
| `true` | 152 | 50.7% |
| `false` | 148 | 49.3% |

## Workset Distribution: `answerability`

| value | count | share |
|---|---:|---:|
| `partial` | 222 | 74.0% |
| `full` | 78 | 26.0% |

## Workset Distribution: `answer_structure`

| value | count | share |
|---|---:|---:|
| `synthesis_set` | 196 | 65.3% |
| `interchangeable_cluster` | 66 | 22.0% |
| `single_clause` | 33 | 11.0% |
| `multi_hop` | 5 | 1.7% |

## Workset Distribution: `reason_code`

| value | count | share |
|---|---:|---:|
| `needs_contract` | 81 | 27.0% |
| `not_in_corpus` | 56 | 18.7% |
| `requires_exclusion_check` | 52 | 17.3% |
| `requires_table_value` | 41 | 13.7% |
| `interchangeable` | 35 | 11.7% |
| `sequential_dependency` | 13 | 4.3% |
| `synthesis_set` | 10 | 3.3% |
| `cross_product_enumeration` | 9 | 3.0% |
| `single_sufficient` | 3 | 1.0% |

## Workset Distribution: `needs_contract`

| value | count | share |
|---|---:|---:|
| `false` | 151 | 50.3% |
| `true` | 149 | 49.7% |

## Workset Distribution: `product_divergent`

| value | count | share |
|---|---:|---:|
| `false` | 214 | 71.3% |
| `true` | 86 | 28.7% |

## After Filling

1. Run `scripts/check_route_review_progress.py` on the private CSV.
2. Import with `scripts/import_route_review_csv.py` into a private audit pack.
3. Validate with `scripts/validate_route_audit.py --require-complete`.
4. Promote qid-only labels only after validation has zero errors.
