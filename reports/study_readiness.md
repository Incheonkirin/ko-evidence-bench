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
| completed adjudicated route labels | 0 | needs at least 300 |
| route validation errors | 300 | must be 0 before headline use |

## Decision

Do not use the private-lab numbers as final public benchmark claims yet.
The blocking gate is human-adjudicated source-route labels: the current
checked-in validation report still has incomplete labels and validation
errors.

## Next Required Evidence

1. Complete and validate the 300-row adjudicated route-label workset.
2. Promote qid-only human labels and run the route scorecard on private route runs.
3. Re-run the retrieval scorecard with human-gold source-route slices.
4. Only then write the README/report headline around human-audited numbers.
