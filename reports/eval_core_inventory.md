# Eval Core Inventory

Status: current private-lab inventory, summarized without raw rows.

## Available Evaluation Material

| asset | current count | status |
|---|---:|---|
| strict silver retrieval core with existing run export | 229 | scored; CI report available |
| assembled partial qrels file | 544 rows | labels exist; comparable retrieval run not yet verified |
| target source-route labels | 300-500 rows | not yet created |

## What Is Verified Now

`reports/private_aggregate_scorecard.md` was generated from a private retrieval
result export with `n=229`. It includes bootstrap confidence intervals and
paired deltas for two system variants.

## What Is Not Yet Verified

- The `n=229` retrieval result has not yet been expanded to the assembled
  500+ qrels set.
- Source-route labels do not yet exist at the required 300-500 row scale.
- The always-policy baseline has only been demonstrated on synthetic fixtures,
  not on the private source-route label set.

## Next Gate

The next private-lab gate is:

1. Build source-route labels for 300-500 rows using `docs/route_label_protocol.md`.
2. Re-run retrieval scoring on the 500+ qrels set, or document why the existing
   run pipeline cannot yet cover it.
3. Generate a new aggregate scorecard with CIs and paired deltas.

