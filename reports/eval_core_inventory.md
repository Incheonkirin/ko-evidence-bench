# Eval Core Inventory

Status: current private-lab inventory, summarized without raw rows.

## Available Evaluation Material

| asset | current count | status |
|---|---:|---|
| strict silver retrieval core with existing run export | 229 | scored; CI report available |
| assembled partial qrels file | 544 rows | pack-only and full cross-rerank scored; CI reports available |
| source-route silver proxy labels | 544 rows | generated from private qrel metadata; aggregate report available |
| source-route router baselines | 544 rows | always-policy and query-only router scored on silver labels |
| source-route human-audit seed | 50 rows | private audit pack generated; not yet labeled |
| source-route adjudication pack | 300 rows | private audit pack generated; not yet labeled |
| source-route review CSV templates | 50/50/300 rows | private reviewer CSVs generated; not yet filled |
| source-route adjudication validation | 300 rows | 0 completed; validation gate pending |
| target human-audited source-route labels | 300-500 rows | workset exists; labels not yet created |

## What Is Verified Now

`reports/private_aggregate_scorecard.md` was generated from a private retrieval
result export with `n=229`. It includes bootstrap confidence intervals and
paired deltas for two system variants.

`reports/private_544_pack_only_scorecard.md` was generated from a 544-row
runtime-honest pack-only retrieval run. It verifies that the larger qrel set can
be connected to the existing retrieval stack, with aggregate CIs and paired
deltas.

`reports/private_544_full_cross_scorecard.md` was generated from a 544-row
runtime-honest full cross-rerank run. It compares pack-only, cross-text, and
cross-RRF variants with aggregate CIs and paired deltas.

`reports/private_route_label_summary.md` was generated from the 544-row private
qrel metadata file. It exports only aggregate source-route counts and baseline
context. The private qid-only label file is kept outside this public repo.

`reports/private_route_router_baselines.md` was generated from the same 544-row
silver labels. It compares `always_policy` against a query-only keyword router
using aggregate route and abstention metrics with bootstrap CIs.

`reports/private_route_audit_pack_summary.md` was generated from a private
50-row route audit seed. It reports only the sampling distribution. The audit
rows themselves stay outside this public repo because they may contain raw
private query text.

`reports/private_route_audit_pack_300_summary.md` was generated from a private
300-row adjudication pack. It reports only the sampling distribution. The human
labels are not filled yet.

`reports/private_route_audit_validation_pending.md` validates the 300-row
adjudication pack and confirms that no adjudicated labels are complete yet.

`reports/private_route_review_csv_50_reviewer_a_summary.md`,
`reports/private_route_review_csv_50_reviewer_b_summary.md`, and
`reports/private_route_review_csv_300_adjudicated_summary.md` summarize private
CSV templates for manual labeling. The CSV files themselves stay outside this
public repo because they contain raw private query/context fields.

## What Is Not Yet Verified

- The 500+ qrels set has been scored with full cross-rerank, but still against
  silver qrels rather than human-audited labels.
- Source-route labels exist only as a silver proxy. They have not yet been
  double-labeled or adjudicated.
- A 50-row double-label seed and 300-row adjudication pack exist, but no human
  agreement metric exists yet.
- Reviewer-editable CSV templates exist, but no completed reviewer import has
  been performed yet.
- The promotion gate is intentionally closed: the 300-row adjudication pack has
  0 completed labels and 300 validation errors from missing final route labels.
- The always-policy baseline has only been demonstrated on synthetic fixtures,
  plus route-only aggregate context on the silver source-route label set. It has
  not yet been evaluated as a full retrieval run on a human-audited route set.
- Query-only routing has been evaluated only against silver labels, not
  human-audited labels.

## Next Gate

The next private-lab gate is:

1. Double-label the 50-row route audit seed using `docs/route_label_protocol.md`,
   then label/adjudicate the 300-row pack.
2. Re-run the full cross-rerank comparison after human-audited labels are
   available.
3. Generate a source-route-aware aggregate scorecard once human-audited labels
   exist.
