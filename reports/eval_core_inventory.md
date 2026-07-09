# Eval Core Inventory

Status: current private-lab inventory, summarized without raw rows.

## Available Evaluation Material

| asset | current count | status |
|---|---:|---|
| strict silver retrieval core with existing run export | 229 | scored; CI report available |
| assembled partial qrels file | 544 rows | pack-only retrieval scored; CI report available |
| source-route silver proxy labels | 544 rows | generated from private qrel metadata; aggregate report available |
| target human-audited source-route labels | 300-500 rows | not yet created |

## What Is Verified Now

`reports/private_aggregate_scorecard.md` was generated from a private retrieval
result export with `n=229`. It includes bootstrap confidence intervals and
paired deltas for two system variants.

`reports/private_544_pack_only_scorecard.md` was generated from a 544-row
runtime-honest pack-only retrieval run. It verifies that the larger qrel set can
be connected to the existing retrieval stack, with aggregate CIs and paired
deltas.

`reports/private_route_label_summary.md` was generated from the 544-row private
qrel metadata file. It exports only aggregate source-route counts and baseline
context. The private qid-only label file is kept outside this public repo.

## What Is Not Yet Verified

- The 500+ qrels set has only been scored in pack-only mode. Full cross-rerank
  comparison on the same set is not yet verified.
- Source-route labels exist only as a silver proxy. They have not yet been
  double-labeled or adjudicated.
- The always-policy baseline has only been demonstrated on synthetic fixtures,
  plus route-only aggregate context on the silver source-route label set. It has
  not yet been evaluated as a full retrieval run on a human-audited route set.

## Next Gate

The next private-lab gate is:

1. Audit the 544 silver source-route labels using `docs/route_label_protocol.md`.
2. Run the full cross-rerank comparison on the 544 qrels set, or document the
   resource limit if it is too slow for the current machine.
3. Generate a source-route-aware aggregate scorecard once human-audited labels
   exist.
