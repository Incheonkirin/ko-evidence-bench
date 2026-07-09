# Measurement Study Draft

Status: **NO-GO for public headline claims**.

## Abstract

Korean insurance questions are written in consumer language, while citable
answers often live in source-specific evidence: policy clauses, product
disclosures, official consumer guidance, claim-operation material, dispute
cases, or expert guidance. This draft measures two things separately:
whether retrieval finds citable clause evidence, and whether a source router
can tell when policy clauses are not the right evidence tier.

All numbers below are aggregate-only private-lab diagnostics. They are useful
for steering the work, but they are blocked from headline use until the
300-row human source-route adjudication workset is complete.

## Current Finding Candidates

| candidate finding | current evidence | status |
|---|---:|---|
| Cross-text reranking improves clause recovery | `clause@20` 56.4% -> 64.9%; paired delta +8.5%p | silver diagnostic |
| Always searching policy clauses is a weak source-routing baseline | `always_policy` route accuracy 21.5% | silver diagnostic |
| Query-language routing helps but misses most abstention-needed cases | route accuracy 31.8%; abstention recall 10.5% | silver diagnostic |
| Cohort-aware routing improves source routing without raw source exposure | route accuracy 46.9%; paired delta +25.4%p; abstention recall 67.0% | silver diagnostic |
| The largest silver route failure is unsafe policy-clause fallback | `human_context_needed -> policy_clause` drops from 190 to 28 rows | silver diagnostic |
| Route failures vary by private query cohort | route accuracy range 36.2% - 55.2%; context-needed policy fallback up to 54.1% | silver diagnostic |
| Real-query substrates need separate stress slices | community contexts avg 835.5 chars with 44.3% long contexts; live-style turns median 17.0 chars with 80.6% short messages; eval queries 94.5% short | substrate diagnostic |
| Private qrels now have silver intent/surface slices | 544 qid-only rows; top silver family `refund_termination` 47.1%; top surface `formal` 55.9% | silver metadata |
| Exact lexical seed counting misses same-intent surface variants | 4 exact-seed rows vs 9 qrel intent rows; undercount 2.2x | public fixture diagnostic |
| Route decisions can now be scored by surface condition | cohort-aware route-only worst surface 22.2%; missing metadata 0 | silver route diagnostic |
| Ranked retrieval hits can now be sliced by surface condition | `structural_cross_text` clause@20 64.9%; answerable clause@20 71.3%; worst surface 44.4% | silver runtime diagnostic |
| Human audit workset covers the stress axes before labeling | 300 matched rows; route 6 / 6, intent 9 / 9, surface 4 / 4, trap 10 / 10 values covered | workset diagnostic |
| Answer quality needs separate labels after retrieval | 10 synthetic completed labels; task success 60.0%; unsafe answer 20.0% | fixture rehearsal only |
| Human-gold public headline claim | 0 / 50 paired labels; 0 / 300 adjudicated labels complete | blocked |

## Retrieval Evidence

| system | metric | value | 95% CI |
|---|---|---:|---:|
| `structural_pack` | `clause@20` | 56.4% | 52.4% - 60.5% |
| `structural_cross_text` | `clause@20` | 64.9% | 60.8% - 68.8% |

Paired delta vs `structural_pack`:

| candidate | metric | delta | 95% CI |
|---|---|---:|---:|
| `structural_cross_text` | `clause@20` | +8.5%p | 5.9% - 11.2% |

Private runtime-surface diagnostics:

| system | clause@20 | answerable clause@20 | exact@20 | avg family surface spread | worst surface clause@20 | missing metadata |
|---|---:|---:|---:|---:|---:|---:|
| `structural_pack` | 56.4% | 61.9% | 46.0% | 29.2% | 44.4% | 0 |
| `structural_cross_text` | 64.9% | 71.3% | 52.4% | 29.3% | 44.4% | 0 |

This joins private runtime hit booleans with qid-only intent/surface
metadata. It does not publish raw ranked evidence ids, but it verifies
whether actual retrieval hits vary across surface conditions.

## Answer-Quality Evidence

| artifact | current evidence | status |
|---|---|---|
| `reports/answer_quality_audit_fixture.md` | 10 qid-only fixture rows; 10 completed labels; task success 60.0%; unsafe answer 20.0% | fixture only; not human-gold answer quality |
| `reports/answer_review_workflow_fixture.md` | CSV export, validation, import, qid-only validation, and promotion path passes on 10 synthetic rows | workflow rehearsal only; real reviewer labels still required |
| `reports/answer_agreement_workflow_fixture.md` | two synthetic reviewer fields validate; paired rows 10; raw agreement 80.0%; kappa 0.733 | agreement rehearsal only; not inter-annotator evidence |

This is a rehearsal for labels that judge the answer state after retrieval:
`sufficient`, `partial`, `insufficient`, `correct_abstain`, or
`unsafe_answer`. It prevents `clause@20` and other hit metrics from being
presented as answer-quality claims.

## System Matrix Evidence

| artifact | current evidence | status |
|---|---|---|
| `reports/system_matrix.md` | 14 implemented diagnostic/fixture systems; 7 not-run analyzer/dense/hybrid/reranker systems; 1 human-gold gate blocked | full comparison matrix incomplete |
| `reports/system_matrix_submission_pack_fixture.md` | qid-only submission template covers 7 missing systems and emits 9 template files | handoff template only; not external model output |
| `reports/system_matrix_bundle_fixture.md` | qid-only bundle contract covers 7 runnable missing systems with 0 validation errors | import rehearsal only; not external model output |
| `reports/system_matrix_promotion_fixture.md` | mechanical gates pass, but fixture promotion is blocked by 8 rows and fixture provenance | no matrix update from synthetic evidence |

This keeps the experiment scope honest. The current study has checked-in
retrieval, routing, surface, and fixture evidence, but it has not yet run
the full analyzer/dense/hybrid/reranker matrix needed for a stronger
public benchmark claim.

## Source-Catalog Evidence

| artifact | current evidence | status |
|---|---|---|
| `reports/source_catalog_coverage.md` | public probe covers 6 searchable source tiers plus abstention routes; 0 validation issues | fixture source-catalog gate; not private corpus-completeness proof |
| `reports/source_inventory_readiness.md` | 544 aggregate demand rows; `policy_clause` READY with 36,983 records; 4 demanded non-policy tiers BLOCKED | inventory readiness gate; not source acquisition proof |

This keeps the study from becoming policy-clause-only retrieval. The
source catalog separates policy clauses, product disclosures, official
consumer guidance, claim-operation material, dispute cases, expert
guidance, and abstention routes before route or retrieval metrics are
interpreted.
The inventory gate prevents source-routing claims from implying that
every demanded source tier has a verified private corpus.

## Source-Route Evidence

| system | route accuracy | 95% CI | abstention recall |
|---|---:|---:|---:|
| `always_policy` | 21.5% | 18.0% - 25.0% | 0.0% |
| `query_keyword_router` | 31.8% | 27.9% - 35.8% | 10.5% |
| `cohort_aware_query_router` | 46.9% | 42.6% - 50.9% | 67.0% |

Paired delta vs `always_policy`:

| candidate | metric | delta | 95% CI |
|---|---|---:|---:|
| `query_keyword_router` | `route_accuracy` | +10.3%p | 7.2% - 13.8% |
| `cohort_aware_query_router` | `route_accuracy` | +25.4%p | 19.3% - 31.2% |

Silver source-route slices:

| system | gold source tier | n | route accuracy | abstained rate | expected abstention |
|---|---|---:|---:|---:|---:|
| `query_keyword_router` | `human_context_needed` | 276 | 10.5% | 10.5% | 100.0% |

Largest silver confusion:

| system | gold source tier | predicted source tier | count | share of run |
|---|---|---|---:|---:|
| `query_keyword_router` | `human_context_needed` | `policy_clause` | 190 | 34.9% |
| `cohort_aware_query_router` | `human_context_needed` | `policy_clause` | 28 | 5.1% |

Private query-cohort diagnostics:

| system | route accuracy range across cohorts | max context-needed policy fallback |
|---|---:|---:|
| `cohort_aware_query_router` | 36.2% - 55.2% | 54.1% |

## Query Substrate Evidence

| cohort | input rows | usable rows | avg chars | median chars | short messages | long contexts | question-like |
|---|---:|---:|---:|---:|---:|---:|---:|
| `community_post_context` | 165970 | 165970 | 835.5 | 169.0 | 6.1% | 44.3% | 80.2% |
| `messenger_conversation` | 7920 | 7796 | 36.8 | 17.0 | 80.6% | 2.0% | 16.8% |
| `search_eval_query` | 544 | 544 | 23.7 | 22.0 | 94.5% | 0.0% | 41.4% |

These substrate diagnostics explain why the repo keeps separate cohort,
surface-form, normalization, and abstention slices. Long community posts,
short live-style turns, and cleaned evaluation queries are not the same
retrieval input distribution.

## Intent/Surface Metadata Evidence

| exported rows | top silver intent family | family share | top surface form | surface share | status |
|---:|---|---:|---|---:|---|
| 544 | `refund_termination` | 47.1% | `formal` | 55.9% | silver metadata; needs audit |

The qid-only metadata export lets the same private qrels be sliced by
intent family, surface form, and trap class without publishing raw text.
These slices are useful for stress-test design, but still require human
review before public frequency claims.

## Surface Fragmentation Audit

| artifact | exact-seed rows | qrel intent rows | expanded-surface rows | seed recall | undercount | status |
|---|---:|---:|---:|---:|---:|---|
| `reports/surface_fragmentation_audit.md` | 4 | 9 | 9 | 44.4% | 2.2x | public fixture; not a synonym list |

This public audit turns the undercounting critique into a checked
measurement path: exact lexical seeds are compared against qrel-level
intent membership across formal, abbreviated, colloquial, and
messenger-style surface forms. It does not publish or recommend a
production synonym list.

## Route Surface Evidence

| system | route accuracy | abstention recall | avg intent route spread | worst surface route accuracy | missing metadata |
|---|---:|---:|---:|---:|---:|
| `always_policy` | 21.5% | 0.0% | 0.3% | 14.9% | 0 |
| `query_keyword_router` | 31.8% | 10.5% | 1.3% | 22.4% | 0 |
| `cohort_aware_query_router` | 46.9% | 67.0% | 1.8% | 22.2% | 0 |

This is a route-only surface scorecard. It checks source-route and
abstention robustness across surface conditions. Pair it with the
runtime-surface diagnostics above to separate retrieval-hit failures
from source-route failures.

## Layer Attribution Evidence

| artifact | current evidence | status |
|---|---|---|
| `reports/layer_attribution_fixture.md` | synthetic failures are decomposed into abstention, source-route, register, surface, evidence-form, and residual evidence-hit layers | fixture path only; human-gold attribution blocked |

This is the measurement study's Table-2-style decomposition hook. It
proves that the repo can explain where failure mass accumulates, but
the public fixture does not promote layer percentages as final system
claims. Human-audited route labels and private run outputs are still
needed before this becomes a headline table.

## Human Audit Coverage

| audit rows | matched rows | route values | intent-family values | surface-form values | trap-class values | status |
|---:|---:|---:|---:|---:|---:|---|
| 300 | 300 | 6 / 6 | 9 / 9 | 4 / 4 | 10 / 10 | coverage only; labels incomplete |

This confirms the private 300-row human audit workset covers every
silver route, intent-family, surface-form, and trap-class value used by
the diagnostics. It does not remove the human-label gate: reviewers still
need to complete independent labels, agreement, adjudication, and validation.

## Claim Control

| gate | current value | required before headline use |
|---|---:|---:|
| retrieval eval rows | 544 | >= 500 |
| paired double-label rows | 0 | >= 50 |
| double-label Cohen's kappa | 0.000 | >= 0.600 |
| completed adjudicated route labels | 0 | >= 300 |
| route validation errors | 300 | 0 |
| system matrix not-run systems | 7 | 0 or narrow the claim |
| system matrix blocked systems | 1 | 0 |
| system matrix validation issues | 0 | 0 |

The retrieval rows meet the diagnostic-size threshold, but source-route labels
and the full system matrix do not yet have enough evidence: independent
agreement, adjudicated human-gold coverage, and the missing analyzer/dense/hybrid/reranker runs still block headline use. Therefore this draft should
not be presented as a final benchmark result.

## Reproduction

```bash
make reproduce-table-1
make reproduce-route-scorecard
make reproduce-route-cohort-scorecard
make reproduce-human-gold-rehearsal
make reproduce-surface-scorecard
make reproduce-route-surface-scorecard
make reproduce-runtime-surface-scorecard
make reproduce-layer-attribution
make export-probe-beir
make reproduce-probe-system-comparison
make reproduce-probe-trap-mining
make reproduce-surface-fragmentation-audit
make reproduce-answer-quality-audit
make reproduce-answer-review-workflow
make reproduce-answer-agreement-workflow
make build-system-matrix-submission-pack
make check-audit-surface-coverage
make reproduce-normalization-ablation
make reproduce-intent-inventory
make reproduce-intent-surface-export
make reproduce-substrate-profile
make check-study-readiness
make build-hero-signal
make build-claim-ledger
make build-source-catalog-report
make build-source-inventory-report
make build-probe-privacy-report
make build-qualitative-gallery
make validate-system-matrix-bundle
make rehearse-system-matrix-promotion
make build-system-matrix-report
make verify
make docker-demo
```

The public commands reproduce synthetic fixtures and regenerate aggregate
claim-control reports. The public probe package is synthetic and
screened by `reports/probe_privacy_report.md`; its BEIR-style retrieval
subset is documented at `reports/probe_beir_export.md`. Qualitative examples
are generated at `reports/qualitative_gallery.md`, and layer attribution is
generated at `reports/layer_attribution_fixture.md`. System coverage is
tracked at `reports/system_matrix.md`. `make docker-demo` runs
a short containerized reproduction path for reviewers. Private qid-only
route runs and raw qrels stay outside the public repository.

## Next Evidence

1. Double-label at least 50 source-route rows and report agreement/kappa.
2. Complete the 300-row adjudicated source-route workset.
3. Validate it with zero route-label errors.
4. Promote qid-only human labels and re-run the same route scorecard path.
5. Run the missing analyzer/dense/hybrid/reranker comparisons or narrow the claim.
6. Re-run retrieval comparisons sliced by human-gold source route.
7. Replace this draft's diagnostic claims with human-audited findings only
   if `reports/study_readiness.md` changes to GO.
