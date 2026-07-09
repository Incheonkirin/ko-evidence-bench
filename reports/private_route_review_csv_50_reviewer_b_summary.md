# Private Route Review CSV Export Summary

This report summarizes a private reviewer CSV export. The CSV may contain
raw queries and context, so it must stay outside the public repository.

- exported rows: 50
- reviewer prefix: `reviewer_b`
- private csv: `route_review_v0_50_reviewer_b.csv`
- existing labels in target prefix: 0

## Silver Route Distribution

| value | count | share |
|---|---:|---:|
| `human_context_needed` | 25 | 50.0% |
| `policy_clause` | 9 | 18.0% |
| `dispute_case` | 4 | 8.0% |
| `claims_faq` | 4 | 8.0% |
| `expert_answer` | 4 | 8.0% |
| `product_disclosure` | 4 | 8.0% |

## Use Notes

- Reviewers should fill `route_gold`, `allowed_source_tiers`, `should_abstain`, `confidence`, `rationale_code`, `labeler`, and `notes`.
- Use `;` to separate multiple `allowed_source_tiers` values.
- Do not copy the private CSV into the public repository.
