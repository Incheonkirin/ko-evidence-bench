# Route Cohort Scorecard

This report scores qid-only route predictions by query cohort.
It contains aggregate counts only. It does not include raw source names,
qids, raw queries, conversation snippets, or platform identifiers.

## Inputs

- qrels: `fixtures/qrels.jsonl`
- labels: `fixtures/qrels.jsonl`
- runs: `fixtures/system_runs`
- source map: `fixtures/source_cohort_map.json`
- label status: synthetic fixture labels
- qrel rows: 5
- label rows: 5
- matched labeled rows: 5
- unmatched label rows: 0
- unmapped source rows: 0

## Cohort Inventory

| query cohort | rows | share | human_context_needed | policy_clause |
|---|---:|---:|---:|---:|
| `fixture_forum` | 3 | 60.0% | 1 | 1 |
| `fixture_expert_qna` | 2 | 40.0% | 0 | 0 |

## Route Metrics By Query Cohort

| system | query cohort | n | route_acc | abst_p | abst_r |
|---|---|---:|---:|---:|---:|
| `always_policy` | `fixture_forum` | 3 | 33.3% | 0.0% | 0.0% |
| `always_policy` | `fixture_expert_qna` | 2 | 0.0% | 0.0% | 0.0% |
| `source_routed_demo` | `fixture_forum` | 3 | 100.0% | 100.0% | 100.0% |
| `source_routed_demo` | `fixture_expert_qna` | 2 | 100.0% | 0.0% | 0.0% |

## Context-Needed Policy Fallback

This table counts cases where the gold route says human context is needed
but the system still predicts policy-clause evidence.

| system | query cohort | context-needed rows | predicted policy_clause | fallback rate |
|---|---|---:|---:|---:|
| `always_policy` | `fixture_forum` | 1 | 1 | 100.0% |
| `always_policy` | `fixture_expert_qna` | 0 | 0 | 0.0% |
| `source_routed_demo` | `fixture_forum` | 1 | 0 | 0.0% |
| `source_routed_demo` | `fixture_expert_qna` | 0 | 0 | 0.0% |

## Largest Cohort Route Confusions

| system | query cohort | gold source tier | predicted source tier | count | share of cohort |
|---|---|---|---|---:|---:|
| `always_policy` | `fixture_expert_qna` | `claims_faq` | `policy_clause` | 1 | 50.0% |
| `always_policy` | `fixture_expert_qna` | `expert_answer` | `policy_clause` | 1 | 50.0% |
| `always_policy` | `fixture_forum` | `dispute_case` | `policy_clause` | 1 | 33.3% |
| `always_policy` | `fixture_forum` | `human_context_needed` | `policy_clause` | 1 | 33.3% |

## Use Notes

- Cohort names come from a source map, not from raw source names.
- Silver-label cohort results are diagnostics until human route labels exist.
- Add messenger-style cohorts through the same qrels/source-map schema before comparing live-query behavior.
