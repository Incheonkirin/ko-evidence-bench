# Private Aggregate Hit Scorecard

This report is generated from a private retrieval result export. It contains
only aggregate hit rates and bootstrap confidence intervals; it does not
include raw queries, ranked documents, or qids.

- source result n: 544
- bootstrap samples: 2000

## Hit Rates

| run | metric | n | hit rate | 95% CI |
|---|---|---:|---:|---:|
| minimal_pack | `exact@1` | 544 | 18.6% | 15.3% - 21.7% |
| minimal_pack | `exact@10` | 544 | 36.6% | 32.5% - 40.6% |
| minimal_pack | `exact@20` | 544 | 41.7% | 37.7% - 45.8% |
| minimal_pack | `clause@1` | 544 | 27.6% | 23.7% - 31.2% |
| minimal_pack | `clause@10` | 544 | 47.1% | 42.8% - 51.3% |
| minimal_pack | `clause@20` | 544 | 53.5% | 49.3% - 57.7% |
| structural_pack | `exact@1` | 544 | 17.1% | 14.0% - 20.2% |
| structural_pack | `exact@10` | 544 | 39.9% | 35.7% - 43.9% |
| structural_pack | `exact@20` | 544 | 46.0% | 41.7% - 50.0% |
| structural_pack | `clause@1` | 544 | 29.4% | 25.6% - 33.3% |
| structural_pack | `clause@10` | 544 | 50.7% | 46.5% - 54.8% |
| structural_pack | `clause@20` | 544 | 56.4% | 52.4% - 60.5% |

## Paired Delta vs `minimal_pack`

| run | metric | delta | 95% CI |
|---|---|---:|---:|
| structural_pack | `exact@1` | -1.5% | -3.7% - 0.7% |
| structural_pack | `exact@10` | 3.3% | 1.1% - 5.5% |
| structural_pack | `exact@20` | 4.2% | 2.6% - 6.1% |
| structural_pack | `clause@1` | 1.8% | -0.7% - 4.2% |
| structural_pack | `clause@10` | 3.7% | 1.5% - 5.9% |
| structural_pack | `clause@20` | 2.9% | 1.3% - 4.6% |

## Use Notes

- Treat these as private-lab diagnostics until the evaluation core is expanded and audited.
- A CI spanning zero on paired deltas means the observed gain is not yet a stable headline claim.
