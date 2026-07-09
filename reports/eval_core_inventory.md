# Eval Core Inventory

Status: current private-lab inventory, summarized without raw rows.

## Available Evaluation Material

| asset | current count | status |
|---|---:|---|
| strict silver retrieval core with existing run export | 229 | scored; CI report available |
| assembled partial qrels file | 544 rows | pack-only and full cross-rerank scored; CI reports available |
| source-route silver proxy labels | 544 rows | generated from private qrel metadata; aggregate report available |
| source-route router baselines | 544 rows x 4 systems | always-policy, query-keyword, risk-aware, and cohort-aware routers scored on silver labels |
| source-route router lift gate | aggregate silver reports | cohort-aware routing lift is checked for drift before public claims |
| source-route qid-only run exports | 544 rows x 4 runs | generated privately; aggregate summary available |
| source-route silver scorecard | 544 rows x 4 runs | scored through qid-only route scorecard with per-source slices |
| source-route cohort scorecard | 544 rows x 4 runs | scored by generic private query cohort; raw source names hidden |
| query-substrate profile | 174,434 private input rows | aggregate text-shape and stress-signal profile generated without raw rows |
| intent/surface qid-only export | 544 rows | private qrels joined with route labels; aggregate summary available |
| private intent-family inventory | 544 rows | silver intent family, surface form, and trap-class slices generated |
| private route-surface scorecard | 544 rows x 4 runs | route-only surface, intent-family, and trap-class diagnostics generated |
| private runtime-surface scorecard | 544 rows x 6 runs | retrieval-hit surface, intent-family, and trap-class diagnostics generated from runtime hit booleans |
| source-route human-audit seed | 50 rows | private audit pack generated; not yet labeled |
| source-route adjudication pack | 300 rows | private audit pack generated; not yet labeled |
| source-route agreement summary | 50-row seed | generated; currently 0 paired reviewer rows |
| source-route review CSV templates | 50/50/300 rows | private reviewer CSVs generated; not yet filled |
| source-route review brief | 300-row CSV | generated; aggregate-only reviewer work summary |
| source-route priority review batch | 50-row private CSV | generated; aggregate-only batch summary checked in |
| source-route batch merge dry-run | 50-row private CSV | generated; current batch has 0 label updates |
| source-route review progress gate | 300-row CSV | generated; currently 0 complete rows |
| source-route review CSV validation | 300-row CSV and 50-row priority batch | generated; currently fails completion gate |
| source-route audit surface coverage | 300-row private audit pack | route, intent-family, surface-form, and trap-class coverage verified |
| source-route review UI | static local HTML | generated; no private data checked in |
| route-audit workflow fixture | 3 synthetic rows | end-to-end dry-run passes |
| human-gold promotion rehearsal fixture | 8 synthetic rows x 2 route runs | completed-label promotion path feeds route and route-surface scorecards |
| audit surface coverage fixture | 8 synthetic rows | coverage gate checks route, intent-family, surface-form, and trap-class axes |
| route-only scorecard fixture | 6 synthetic rows | qid-only route scoring path passes |
| route cohort scorecard fixture | 5 synthetic rows | source-map cohort slicing path passes |
| surface-form robustness fixture | 8 synthetic rows | same-intent surface variation scorecard passes |
| route-surface scorecard fixture | 8 synthetic rows x 2 runs | route-only surface, intent, and trap slicing path passes |
| layer attribution fixture | 8 synthetic rows x 2 runs | failed rows are attributed to abstention, source-route, register, surface, evidence-form, or residual evidence-hit layers |
| surface-form lift gate | aggregate synthetic report | surface-robust candidate lift and spread reduction are checked for drift |
| normalization ablation fixture | 8 synthetic rows x 2 runs | rescue/regression lift is summarized by family, surface, and trap |
| intent-family inventory fixture | 8 synthetic rows | intent families, source routes, surfaces, and trap slices are summarized |
| measurement-study readiness gate | aggregate reports | generated; currently NO-GO for headline claims |
| measurement-study draft | aggregate reports | generated from checked-in reports; diagnostic only |
| hero diagnostic signal | aggregate reports | README figure and compact signal report generated from checked-in diagnostics |
| claim wording ledger | aggregate reports | generated allowed/blocked wording guard for public claims |
| reviewer demo path | aggregate reports | generated 3-minute walkthrough for reading the repo as a measurement-study artifact |
| containerized reproduction path | repo artifacts | Dockerfile and make target rerun the public fixture demo and claim checks |
| public synthetic probe package | 13 queries / 13 qrels / 7 evidence snippets | intent-level public probe set with privacy screen |
| qualitative failure gallery | 4 synthetic examples | side-by-side route failure examples from the public probe set |
| system comparison matrix | 15 systems | implemented, not-run, and blocked systems are tracked explicitly |
| flagship alignment report | repo artifacts | generated; current overall status is NO-GO for headline claims |
| flagship scope guards | repo artifacts | dictionary framing, multi-source evidence, and real-query substrate inventory are checked |
| public-safety scan | repository-wide | Makefile target and CI workflow added |
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
silver labels. It compares `always_policy`, query-keyword, risk-aware, and
cohort-aware routers using aggregate route and abstention metrics with bootstrap
CIs. The cohort-aware router uses generic query cohorts from a private source
map, not raw source names.

`reports/private_router_lift_gate.md` checks that the cohort-aware router keeps
its silver diagnostic lift over the query-keyword baseline and does not regress
on the largest context-needed policy-clause fallback. It is a drift gate only;
it does not promote silver labels into human-gold claims.

`reports/private_route_run_export_summary.md` summarizes qid-only route run
files exported from private qrels for all four router variants. The exported run
files stay outside this repo because their qids can identify private source
rows.

`reports/private_route_scorecard_silver.md` scores those private qid-only route
runs against silver route labels using the same route scorecard intended for
future promoted human labels. It now includes per-gold-source route slices and
largest route-confusion pairs. It is still a diagnostic, not a headline result.

`reports/private_route_cohort_scorecard_silver.md` scores the same private
qid-only route runs by generic query cohort. The cohort names are produced by a
private source map kept outside this repo, so the report can compare query
substrates without exposing raw source names. It is still a silver diagnostic.

`reports/private_query_substrate_profile.md` profiles private query substrates
with aggregate text-shape and intent-signal features only. It compares community
post contexts, cleaned evaluation queries, and live-style conversation turns
without qids, raw queries, conversation snippets, platform identifiers,
usernames, URLs, or source file paths. This is substrate evidence for separate
cohort, surface-form, normalization, and abstention stress slices.

`reports/private_intent_surface_export_summary.md` summarizes a qid-only private
export that joins private qrels with silver route labels and adds intent family,
surface form, trap classes, route labels, and evidence ids. The qid-only export
stays outside this repo because stable ids can link back to private worksets.

`reports/private_intent_inventory_silver.md` runs the same intent-family
inventory path over that private qid-only export. It verifies that the 544-row
qrel set can now be sliced by intent family, surface form, route, and trap class
without raw text. It is still silver metadata and must be audited before public
frequency claims.

`reports/private_route_surface_scorecard_silver.md` scores private route runs
against that qid-only intent/surface export. It reports route accuracy,
abstention behavior, worst-surface accuracy, and breakdowns by surface form,
intent family, and trap class. It is route-only and does not score ranked
evidence sufficiency.

`reports/private_runtime_surface_scorecard_silver.md` joins the same qid-only
intent/surface metadata with private runtime retrieval hit booleans. It reports
`clause@20`, `answerable_clause@20`, `exact@20`, worst-surface hit rate, and
breakdowns by surface form, intent family, and trap class without publishing
qids, evidence ids, raw queries, or source names. It is still silver metadata,
not a human-gold benchmark claim.

`reports/private_route_audit_pack_summary.md` was generated from a private
50-row route audit seed. It reports only the sampling distribution. The audit
rows themselves stay outside this public repo because they may contain raw
private query text.

`reports/private_route_audit_pack_300_summary.md` was generated from a private
300-row adjudication pack. It reports only the sampling distribution. The human
labels are not filled yet.

`reports/private_route_audit_agreement_pending.md` summarizes independent
reviewer agreement on the private 50-row seed. It currently has 0 paired
reviewer rows and Cohen's kappa 0.000, so it blocks headline claims until at
least 50 paired labels exist and agreement quality is reported.

`reports/private_route_audit_validation_pending.md` validates the 300-row
adjudication pack and confirms that no adjudicated labels are complete yet.

`reports/private_route_review_csv_50_reviewer_a_summary.md`,
`reports/private_route_review_csv_50_reviewer_b_summary.md`, and
`reports/private_route_review_csv_300_adjudicated_summary.md` summarize private
CSV templates for manual labeling. The CSV files themselves stay outside this
public repo because they contain raw private query/context fields.

`reports/private_route_review_progress_300_adjudicated.md` summarizes completion
of the private 300-row adjudication CSV. It reports field fill rates and error
counts without qids, raw queries, context, or reviewer notes.

`reports/private_route_review_csv_validation_300_adjudicated.md` validates the
same private 300-row adjudication CSV before import or promotion. It confirms
that required reviewer columns exist, but all 300 rows still lack final route
labels, allowed source tiers, abstention flags, confidence, rationale codes, and
labeler ids.

`reports/private_audit_surface_coverage_300.md` verifies that the private
300-row human-audit workset covers every silver route, intent-family,
surface-form, and trap-class value used by the diagnostic reports. It contains
aggregate counts only and no qids or row text. This proves the workset preserves
the stress axes before review, but it does not mean labels are complete.

`reports/private_route_review_brief_300_adjudicated.md` summarizes the same
workset as a reviewer brief, including aggregate priority counts and required
fields. It is aggregate-only and contains no row text.

`reports/private_route_review_batch_priority_50_summary.md` summarizes a private
50-row priority batch selected from the 300-row adjudication CSV. The private
batch CSV stays outside this repo because it contains row text.

`reports/private_route_review_csv_validation_priority_50.md` validates that
priority batch before import. The batch currently has 0 complete rows, matching
the merge dry-run.

`reports/private_route_review_batch_merge_priority_50_summary.md` summarizes
merging the private priority batch back into the full 300-row review CSV. The
current batch is still unlabeled, so the merge updates 0 rows and skips the
empty batch rows.

`tools/route_review_ui.html` is a static local reviewer for those CSV files. It
does not include private rows and does not depend on network access.

`reports/route_audit_workflow_fixture.md` is generated from synthetic fixtures
by `make reproduce-route-audit-workflow`. It exercises CSV export/import,
reviewer agreement, adjudication validation, and qid-only label promotion.

`reports/human_gold_rehearsal_fixture.md` is generated from synthetic fixtures
by `make reproduce-human-gold-rehearsal`. It starts from completed adjudication,
validates labels with zero errors, promotes qid-only route labels, checks
stress-axis coverage, and feeds both route and route-surface scorecards. This is
the public rehearsal for the private human-gold path; it is not itself a
human-gold result.

`reports/audit_surface_coverage_fixture.md` is generated by
`make check-audit-surface-coverage`. It verifies that an audit workset can be
checked for route, intent-family, surface-form, and trap-class coverage before
review starts.

`reports/route_scorecard_fixture.md` is generated from synthetic fixtures by
`make reproduce-route-scorecard`. It proves that promoted qid-only route labels
can be scored for route accuracy, missing predictions, abstention precision, and
abstention recall without publishing private text. It also exercises the
per-source route slice and largest-confusion tables used by the private silver
scorecard.

`reports/route_cohort_scorecard_fixture.md` is generated from synthetic fixtures
by `make reproduce-route-cohort-scorecard`. It proves that source-map cohort
slicing can run without leaking raw source values.

`reports/surface_scorecard_fixture.md` is generated from synthetic fixtures by
`make reproduce-surface-scorecard`. It measures whether the same intent remains
retrievable across formal, colloquial, abbreviated, and messenger-style surface
forms using only `intent_id`, `surface_form`, route labels, and ranked evidence
ids.

`reports/runtime_surface_scorecard_fixture.md` is generated by
`make reproduce-runtime-surface-scorecard`. It proves that runtime hit booleans
can be sliced by the same intent family, surface form, and trap-class metadata
without retaining ranked evidence ids in the public repo.

`reports/layer_attribution_fixture.md` is generated by
`make reproduce-layer-attribution`. It gives the measurement study a
Table-2-style decomposition path: failed synthetic rows are assigned to one
primary diagnostic layer before any public human-gold attribution claims are
allowed.

`reports/system_matrix.md` is generated by `make build-system-matrix-report`.
It records which systems are backed by evidence and which analyzer, dense,
hybrid, reranker, or human-gold comparisons are still not run or blocked.

`reports/surface_lift_gate.md` checks that the synthetic surface-robust
candidate still improves task success, worst-surface success, and average
intent-spread over the formal-only baseline. It is a drift gate for the
demonstration, not a private benchmark claim.

`reports/normalization_ablation_fixture.md` is generated by
`make reproduce-normalization-ablation`. It compares a raw-surface baseline run
with a normalized or expanded candidate run and reports aggregate rescue and
regression counts by intent family, surface form, trap class, and route.

`reports/intent_inventory_fixture.md` is generated by
`make reproduce-intent-inventory`. It treats intent families as the organizing
unit and summarizes source routes, surface forms, and trap-class annotations
without publishing raw query text or qids.

`reports/study_readiness.md` is generated by `make check-study-readiness`. It
parses checked-in aggregate reports and records whether the measurement study is
ready for public headline claims. The current answer is NO-GO because the
adjudicated human route-label workset is still incomplete.

`reports/measurement_study_draft.md` is generated by
`make build-measurement-study`. It assembles the current finding candidates,
evidence tables, claim-control gates, and reproduction commands from aggregate
reports. It now carries the largest silver source-route failure as a diagnostic
finding candidate, the cohort-aware silver routing lift, and private
query-cohort diagnostics, while still blocking public headline claims.
`make verify` checks that the committed draft has not drifted.

`reports/hero_signal.md` and
`reports/figures/diagnostic_signal_heatmap.svg` are generated by
`make build-hero-signal`. They compress the aggregate diagnostics into a
first-screen figure and short table for the README while keeping the
human-gold claim gate visible. The figure is a diagnostic artifact only, not a
headline benchmark result.

`reports/claim_ledger.md` is generated by `make build-claim-ledger`. It lists
which public diagnostic claims are currently allowed, which claims are blocked,
which broad claims are out of scope, and the next evidence required for each.
This is the wording guard for the README and measurement-study draft.

`reports/reviewer_demo.md` is generated by `make build-reviewer-demo`. It is the
short public walkthrough through the README figure, hero signal, claim ledger,
measurement-study draft, human-gold rehearsal, and readiness gate.

`make docker-demo` builds the local container image and reruns the public fixture
table, readiness gate, generated-report checks, and public-safety scan inside
that image. It is a reviewer convenience path, not a substitute for human-gold
labels.

`probes/ko_evidence_probe_v0/` is the public synthetic probe package. It
contains queries, intent-level qrels, and synthetic evidence snippets.
`reports/probe_privacy_report.md` is generated by `make build-probe-privacy-report`
and checks schema joins, provenance, PII patterns, private-source indicators,
and long n-gram overlap against configured reference material.

`reports/qualitative_gallery.md` is generated by `make build-qualitative-gallery`.
It turns four synthetic probe rows into side-by-side examples of policy-only
fallbacks versus source-routed candidates. The gallery is illustrative; it is
not a human-gold model result.

`reports/flagship_alignment.md` is generated by `make build-alignment-report`.
It verifies that the repo is shaped as a measurement-study artifact and names the
remaining human-label gate explicitly.
It also checks the key scope constraints that keep the project aligned with the
flagship plan: the repo is not framed as a dictionary, the evidence model spans
multiple source tiers, and the private real-query substrates are represented only
through aggregate inventory and generic cohort reports.

`make check-public-safety` scans the public repository for private-source
leakage indicators. `make verify` runs tests, reproduction commands, and that
scan. The same target is wired into GitHub Actions.

## What Is Not Yet Verified

- The 500+ qrels set has been scored with full cross-rerank, but still against
  silver qrels rather than human-audited labels.
- Source-route labels exist only as a silver proxy. They have not yet been
  double-labeled or adjudicated.
- A 50-row double-label seed and 300-row adjudication pack exist. The agreement
  report exists, but it has 0 paired reviewer rows and no usable kappa yet.
- Reviewer-editable CSV templates exist, but no completed reviewer import has
  been performed yet.
- Reviewer CSV validation exists and fails as intended on the current unfilled
  300-row adjudication CSV.
- Audit workset coverage is verified for the 300-row pack, but coverage is not
  completion: the labels still need independent review, adjudication, import,
  and validation.
- A local static review UI exists, but no reviewed CSV has been imported yet.
- The full route-audit workflow and promotion-to-scorecard path are verified
  only on synthetic fixtures; private human labels are still pending.
- The promotion gate is intentionally closed: the 300-row adjudication pack has
  0 completed labels and 300 validation errors from missing final route labels.
- The always-policy baseline has only been demonstrated on synthetic fixtures,
  plus route-only aggregate context on the silver source-route label set. The
  qid-only scorecard path exists, but it has not yet been run on human-audited
  route labels.
- Query-keyword, risk-aware, and cohort-aware routing have been evaluated only
  against silver labels, not human-audited labels.
- Query-cohort route slicing has been evaluated only against silver labels. It
  is ready for messenger/live-query cohorts once those qrels are mapped through
  the same private source-map schema.
- Surface-form evidence sufficiency is verified on synthetic fixtures with
  ranked evidence ids, and private runtime retrieval hits are now sliced by
  silver `intent_id` and `surface_form` metadata. The remaining gap is
  human-audited labels and answer-quality judgment, not the surface slicing
  plumbing.
- Normalization ablation is currently verified on synthetic fixtures. Private
  runs need paired raw-surface and normalized outputs over the same qrels before
  rescue/regression claims can be reported.
- Intent-family inventory now runs on private silver metadata. It still needs
  audited `intent_family` and `trap_classes` labels before public frequency or
  per-family claims can be reported.

## Next Gate

The next private-lab gate is:

1. Double-label the 50-row route audit seed using `docs/route_label_protocol.md`,
   then label/adjudicate the 300-row pack.
2. Promote the adjudicated qid-only route labels and run
   `scripts/reproduce_route_scorecard.py` against private route prediction runs.
3. Re-run the full cross-rerank comparison after human-audited labels are
   available.
4. Generate a source-route-aware aggregate scorecard once human-audited labels
   exist.
