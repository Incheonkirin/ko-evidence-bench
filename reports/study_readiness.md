# Measurement Study Readiness

Status: **NO-GO for public headline claims**.

This report is generated from aggregate-only checked-in reports. It is a
claim-control gate: it prevents the repository from presenting private-lab
diagnostics as final benchmark results before human route labels exist.

## Evidence Snapshot

| item | value | interpretation |
|---|---:|---|
| retrieval eval rows | 544 | enough for diagnostic CIs, still silver |
| best checked-in `clause@20` | 64.9% | retrieval signal, not answer quality |
| `always_policy` route accuracy | 21.5% | silver baseline only |
| query-keyword route accuracy | 31.8% | silver baseline only |
| cohort-aware route accuracy | 46.9% | silver diagnostic only |
| paired double-label rows | 0 | needs at least 50 |
| double-label raw agreement | 0.0% | audit quality signal |
| double-label Cohen's kappa | 0.000 | needs at least 0.600 |
| completed adjudicated route labels | 0 | needs at least 300 |
| route validation errors | 300 | must be 0 before headline use |
| system matrix implemented systems | 14 / 22 | diagnostic coverage only |
| system matrix not-run systems | 7 | must be 0 for full comparison claims |
| system matrix blocked systems | 1 | must be 0 for headline use |
| system matrix validation issues | 0 | must be 0 |

## Decision

Do not use the private-lab numbers as final public benchmark claims yet.
The blocking gates are human-adjudicated source-route labels and
complete system-matrix coverage: the current checked-in reports still
lack paired reviewer labels, complete adjudicated labels, or the full analyzer/dense/hybrid/reranker comparison matrix.

## Next Required Evidence

1. Double-label at least 50 route rows and report raw agreement plus Cohen's kappa.
2. Complete and validate the 300-row adjudicated route-label workset.
3. Promote qid-only human labels and run the route scorecard on private route runs.
4. Re-run the retrieval scorecard with human-gold source-route slices.
5. Run the missing analyzer, dense, hybrid, and reranker comparisons or narrow the claim.
6. Only then write the README/report headline around human-audited numbers.
