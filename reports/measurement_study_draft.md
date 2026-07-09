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

## Claim Control

| gate | current value | required before headline use |
|---|---:|---:|
| retrieval eval rows | 544 | >= 500 |
| paired double-label rows | 0 | >= 50 |
| double-label Cohen's kappa | 0.000 | >= 0.600 |
| completed adjudicated route labels | 0 | >= 300 |
| route validation errors | 300 | 0 |

The retrieval rows meet the diagnostic-size threshold, but source-route labels
do not yet have enough independent agreement evidence or adjudicated
human-gold coverage. Therefore this draft should not be presented as a
final benchmark result.

## Reproduction

```bash
make reproduce-table-1
make reproduce-route-scorecard
make reproduce-route-cohort-scorecard
make reproduce-surface-scorecard
make reproduce-normalization-ablation
make reproduce-intent-inventory
make reproduce-substrate-profile
make check-study-readiness
make verify
```

The public commands reproduce synthetic fixtures and regenerate aggregate
claim-control reports. Private qid-only route runs and raw qrels stay outside
the public repository.

## Next Evidence

1. Double-label at least 50 source-route rows and report agreement/kappa.
2. Complete the 300-row adjudicated source-route workset.
3. Validate it with zero route-label errors.
4. Promote qid-only human labels and re-run the same route scorecard path.
5. Re-run retrieval comparisons sliced by human-gold source route.
6. Replace this draft's diagnostic claims with human-audited findings only
   if `reports/study_readiness.md` changes to GO.
