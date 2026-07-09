# Route Cohort Scorecard

This report scores qid-only route predictions by query cohort.
It contains aggregate counts only. It does not include raw source names,
qids, raw queries, conversation snippets, or platform identifiers.

## Inputs

- qrels: `qrels_v1_clean.jsonl`
- labels: `route_labels_v0_silver.jsonl`
- runs: `route_runs_v0_silver`
- source map: `source_cohort_map_v0.json`
- label status: private silver route labels
- qrel rows: 544
- label rows: 544
- matched labeled rows: 544
- unmatched label rows: 0
- unmapped source rows: 0

## Cohort Inventory

| query cohort | rows | share | human_context_needed | policy_clause |
|---|---:|---:|---:|---:|
| `professional_forum_archive` | 153 | 28.1% | 94 | 21 |
| `expert_qna_archive` | 124 | 22.8% | 71 | 32 |
| `open_forum_archive` | 115 | 21.1% | 37 | 32 |
| `general_forum_archive` | 105 | 19.3% | 57 | 18 |
| `community_cafe_archive` | 47 | 8.6% | 17 | 14 |

## Route Metrics By Query Cohort

| system | query cohort | n | route_acc | abst_p | abst_r |
|---|---|---:|---:|---:|---:|
| `always_policy` | `professional_forum_archive` | 153 | 13.7% | 0.0% | 0.0% |
| `always_policy` | `expert_qna_archive` | 124 | 25.8% | 0.0% | 0.0% |
| `always_policy` | `open_forum_archive` | 115 | 27.8% | 0.0% | 0.0% |
| `always_policy` | `general_forum_archive` | 105 | 17.1% | 0.0% | 0.0% |
| `always_policy` | `community_cafe_archive` | 47 | 29.8% | 0.0% | 0.0% |
| `query_keyword_router` | `professional_forum_archive` | 153 | 25.5% | 81.8% | 9.6% |
| `query_keyword_router` | `expert_qna_archive` | 124 | 37.9% | 76.5% | 18.3% |
| `query_keyword_router` | `open_forum_archive` | 115 | 37.4% | 42.9% | 8.1% |
| `query_keyword_router` | `general_forum_archive` | 105 | 24.8% | 42.9% | 5.3% |
| `query_keyword_router` | `community_cafe_archive` | 47 | 38.3% | 50.0% | 5.9% |

## Context-Needed Policy Fallback

This table counts cases where the gold route says human context is needed
but the system still predicts policy-clause evidence.

| system | query cohort | context-needed rows | predicted policy_clause | fallback rate |
|---|---|---:|---:|---:|
| `always_policy` | `professional_forum_archive` | 94 | 94 | 100.0% |
| `always_policy` | `expert_qna_archive` | 71 | 71 | 100.0% |
| `always_policy` | `open_forum_archive` | 37 | 37 | 100.0% |
| `always_policy` | `general_forum_archive` | 57 | 57 | 100.0% |
| `always_policy` | `community_cafe_archive` | 17 | 17 | 100.0% |
| `query_keyword_router` | `professional_forum_archive` | 94 | 61 | 64.9% |
| `query_keyword_router` | `expert_qna_archive` | 71 | 40 | 56.3% |
| `query_keyword_router` | `open_forum_archive` | 37 | 30 | 81.1% |
| `query_keyword_router` | `general_forum_archive` | 57 | 48 | 84.2% |
| `query_keyword_router` | `community_cafe_archive` | 17 | 11 | 64.7% |

## Largest Cohort Route Confusions

| system | query cohort | gold source tier | predicted source tier | count | share of cohort |
|---|---|---|---|---:|---:|
| `always_policy` | `professional_forum_archive` | `human_context_needed` | `policy_clause` | 94 | 61.4% |
| `always_policy` | `expert_qna_archive` | `human_context_needed` | `policy_clause` | 71 | 57.3% |
| `always_policy` | `general_forum_archive` | `human_context_needed` | `policy_clause` | 57 | 54.3% |
| `always_policy` | `open_forum_archive` | `human_context_needed` | `policy_clause` | 37 | 32.2% |
| `always_policy` | `community_cafe_archive` | `human_context_needed` | `policy_clause` | 17 | 36.2% |
| `always_policy` | `open_forum_archive` | `dispute_case` | `policy_clause` | 16 | 13.9% |
| `always_policy` | `professional_forum_archive` | `product_disclosure` | `policy_clause` | 16 | 10.5% |
| `always_policy` | `professional_forum_archive` | `dispute_case` | `policy_clause` | 14 | 9.2% |
| `always_policy` | `open_forum_archive` | `product_disclosure` | `policy_clause` | 13 | 11.3% |
| `always_policy` | `general_forum_archive` | `product_disclosure` | `policy_clause` | 11 | 10.5% |
| `query_keyword_router` | `professional_forum_archive` | `human_context_needed` | `policy_clause` | 61 | 39.9% |
| `query_keyword_router` | `general_forum_archive` | `human_context_needed` | `policy_clause` | 48 | 45.7% |
| `query_keyword_router` | `expert_qna_archive` | `human_context_needed` | `policy_clause` | 40 | 32.3% |
| `query_keyword_router` | `open_forum_archive` | `human_context_needed` | `policy_clause` | 30 | 26.1% |
| `query_keyword_router` | `professional_forum_archive` | `human_context_needed` | `product_disclosure` | 16 | 10.5% |
| `query_keyword_router` | `expert_qna_archive` | `human_context_needed` | `claims_faq` | 12 | 9.7% |
| `query_keyword_router` | `community_cafe_archive` | `human_context_needed` | `policy_clause` | 11 | 23.4% |
| `query_keyword_router` | `open_forum_archive` | `dispute_case` | `policy_clause` | 11 | 9.6% |
| `query_keyword_router` | `professional_forum_archive` | `dispute_case` | `policy_clause` | 11 | 7.2% |
| `query_keyword_router` | `professional_forum_archive` | `product_disclosure` | `policy_clause` | 9 | 5.9% |

## Use Notes

- Cohort names come from a source map, not from raw source names.
- Silver-label cohort results are diagnostics until human route labels exist.
- Add messenger-style cohorts through the same qrels/source-map schema before comparing live-query behavior.
