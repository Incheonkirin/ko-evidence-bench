# Route Audit Workflow Fixture

This synthetic dry-run exercises CSV export, CSV import, reviewer agreement,
adjudication validation, and qid-only label promotion without private data.

- fixture audit rows: 3
- paired reviewer rows: 3
- reviewer raw agreement: 66.7%
- reviewer Cohen's kappa: 0.571
- adjudication validation errors: 0
- promoted labels: 3

## Promoted Route Distribution

| route | count |
|---|---:|
| `claims_faq` | 1 |
| `human_context_needed` | 1 |
| `policy_clause` | 1 |
