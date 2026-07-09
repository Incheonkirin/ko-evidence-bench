# Eval Core Inventory

Status: current private-lab inventory, summarized without raw rows.

## Available Evaluation Material

| asset | current count | status |
|---|---:|---|
| strict silver retrieval core with existing run export | 229 | scored; CI report available |
| assembled partial qrels file | 544 rows | labels exist; comparable retrieval run not yet verified |
| source-route silver proxy labels | 544 rows | generated from private qrel metadata; aggregate report available |
| target human-audited source-route labels | 300-500 rows | not yet created |

## What Is Verified Now

`reports/private_aggregate_scorecard.md` was generated from a private retrieval
result export with `n=229`. It includes bootstrap confidence intervals and
paired deltas for two system variants.

`reports/private_route_label_summary.md` was generated from the 544-row private
qrel metadata file. It exports only aggregate source-route counts and baseline
context. The private qid-only label file is kept outside this public repo.

## What Is Not Yet Verified

- The `n=229` retrieval result has not yet been expanded to the assembled
  500+ qrels set.
- Source-route labels exist only as a silver proxy. They have not yet been
  double-labeled or adjudicated.
- The always-policy baseline has only been demonstrated on synthetic fixtures,
  plus route-only aggregate context on the silver source-route label set. It has
  not yet been evaluated as a full retrieval run on a human-audited route set.

## Next Gate

The next private-lab gate is:

1. Audit the 544 silver source-route labels using `docs/route_label_protocol.md`.
2. Re-run retrieval scoring on the 500+ qrels set, or document why the existing
   run pipeline cannot yet cover it.
3. Generate a new aggregate scorecard with CIs and paired deltas.
