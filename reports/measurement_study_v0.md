# Measurement Study v0

Status: fixture-only draft.

## Finding to Validate

The working claim is simple: Korean insurance retrieval fails not only because
terms differ, but because the required source tier changes. A good system should
retrieve the right kind of evidence and abstain when citation is not possible.

## Private Substrate

| Asset | Count | Public Use |
|---|---:|---|
| Insurer policy clause passages | 36,983 | aggregate metrics only |
| Derived community query candidates | 165,970 | aggregate distribution only |
| Messenger conversation messages | 7,324 | synthetic live-stress fixtures only |
| Community Q&A archive rows | 56,293 | aggregate/expert-language analysis only |

## Before Headline Claims

- Expand strict silver core toward at least 500 queries.
- Add bootstrap confidence intervals over query ids.
- Build source-route gold labels for 300-500 queries.
- Compare against `always_policy` and simple rule baselines.
- Audit whether silver labels are circular with systems under test.

## Table 1

Run:

```bash
make reproduce-table-1
```

This table is synthetic. It validates metric behavior, not model quality.
