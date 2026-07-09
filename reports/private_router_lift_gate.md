# Private Router Lift Gate

Status: **PASS**.

This gate checks the checked-in silver diagnostic reports. It contains
aggregate values only and does not include qids, raw queries, source names,
conversation snippets, or platform identifiers.

- baseline: `query_keyword_router`
- candidate: `cohort_aware_query_router`
- label status: silver proxy, not human-gold

## Gate Checks

| check | current value | threshold | status |
|---|---:|---:|---|
| route accuracy lift vs `query_keyword_router` | 15.1%p | >= 10.0%p | `PASS` |
| abstention recall lift vs `query_keyword_router` | 56.5%p | >= 30.0%p | `PASS` |
| `human_context_needed -> policy_clause` fallback rows | 28 | <= 50 | `PASS` |

## Signal Snapshot

| signal | value |
|---|---:|
| `query_keyword_router` route accuracy | 31.8% |
| `cohort_aware_query_router` route accuracy | 46.9% |
| `query_keyword_router` abstention recall | 10.5% |
| `cohort_aware_query_router` abstention recall | 67.0% |
| `cohort_aware_query_router` paired delta vs `always_policy` | 25.4%p |

## Use Notes

- A passing gate means the silver diagnostic lift has not regressed.
- It does not turn silver labels into human-gold headline claims.
- If this fails, inspect router changes before updating public-facing diagnostics.
