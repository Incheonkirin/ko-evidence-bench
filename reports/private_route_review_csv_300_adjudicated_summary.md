# Private Route Review CSV Export Summary

This report summarizes a private reviewer CSV export. The CSV may contain
raw queries and context, so it must stay outside the public repository.

- exported rows: 300
- reviewer prefix: `adjudicated`
- private csv: `route_review_v0_300_adjudicated.csv`
- existing labels in target prefix: 0

## Silver Route Distribution

| value | count | share |
|---|---:|---:|
| `human_context_needed` | 152 | 50.7% |
| `policy_clause` | 62 | 20.7% |
| `dispute_case` | 26 | 8.7% |
| `product_disclosure` | 20 | 6.7% |
| `expert_answer` | 20 | 6.7% |
| `claims_faq` | 20 | 6.7% |

## Use Notes

- Reviewers should fill `route_gold`, `allowed_source_tiers`, `should_abstain`, `confidence`, `rationale_code`, `labeler`, and `notes`.
- Use `;` to separate multiple `allowed_source_tiers` values.
- Do not copy the private CSV into the public repository.
