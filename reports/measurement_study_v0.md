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
- Use `scripts/summarize_hit_result.py` to publish aggregate hit rates from
  private retrieval exports without qids or raw text.
- Use `scripts/export_route_labels.py` to generate qid-only private route-label
  worksets and aggregate route inventories without raw text.
- Follow `docs/route_label_protocol.md` before claiming source-route accuracy.

## Current Private-Lab Signals

- Retrieval CI report: `n=229`, aggregate-only.
- Larger runtime-honest pack-only report: `n=544`, aggregate-only.
- Source-route silver proxy: `n=544`, aggregate-only.
- Source-route audit seed: `n=50`, private rows plus aggregate-only summary.
- Source-route adjudication workset: `n=300`, private rows plus aggregate-only
  summary.
- Source-route reviewer CSV templates: `n=50` reviewer A, `n=50` reviewer B,
  and `n=300` adjudication templates.
- Source-route review UI: static local CSV editor, no private rows checked in.
- Source-route adjudication validation: `0/300` complete, promotion blocked
  until final labels are filled.
- Structural pack-only `clause@20`: 56.4% with 95% CI 52.4%-60.5%.
- Structural cross-text `clause@20`: 64.9% with 95% CI 60.8%-68.8%.
- Structural cross-text paired lift over structural pack-only on `clause@20`:
  +8.5 percentage points with 95% CI +5.9 to +11.2.
- Naive always-policy route accuracy on the silver proxy: 21.5%.
- Query-only keyword router route accuracy on the silver proxy: 31.8%, a
  +10.3 percentage-point paired lift over always-policy.

These are useful steering signals, not final benchmark claims.

## Table 1

Run:

```bash
make reproduce-table-1
```

This table is synthetic. It validates metric behavior, not model quality.
