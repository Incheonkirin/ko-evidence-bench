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
| Human-gold public headline claim | 0 / 300 adjudicated labels complete | blocked |

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

Paired delta vs `always_policy`:

| candidate | metric | delta | 95% CI |
|---|---|---:|---:|
| `query_keyword_router` | `route_accuracy` | +10.3%p | 7.2% - 13.8% |

## Claim Control

| gate | current value | required before headline use |
|---|---:|---:|
| retrieval eval rows | 544 | >= 500 |
| completed adjudicated route labels | 0 | >= 300 |
| route validation errors | 300 | 0 |

The retrieval rows meet the diagnostic-size threshold, but source-route labels
are not human-adjudicated yet. Therefore this draft should not be presented
as a final benchmark result.

## Reproduction

```bash
make reproduce-table-1
make reproduce-route-scorecard
make check-study-readiness
make verify
```

The public commands reproduce synthetic fixtures and regenerate aggregate
claim-control reports. Private qid-only route runs and raw qrels stay outside
the public repository.

## Next Evidence

1. Complete the 300-row adjudicated source-route workset.
2. Validate it with zero route-label errors.
3. Promote qid-only human labels and re-run the same route scorecard path.
4. Re-run retrieval comparisons sliced by human-gold source route.
5. Replace this draft's diagnostic claims with human-audited findings only
   if `reports/study_readiness.md` changes to GO.
