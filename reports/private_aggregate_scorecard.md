# Private Aggregate Hit Scorecard

This report is generated from a private retrieval result export. It contains
only aggregate hit rates and bootstrap confidence intervals; it does not
include raw queries, ranked documents, or qids.

- source result n: 229
- bootstrap samples: 2000

## Hit Rates

| run | metric | n | hit rate | 95% CI |
|---|---|---:|---:|---:|
| structural_pack | `exact@1` | 229 | 15.3% | 10.9% - 20.1% |
| structural_pack | `exact@10` | 229 | 42.8% | 36.7% - 48.9% |
| structural_pack | `exact@20` | 229 | 53.3% | 46.7% - 59.4% |
| structural_pack | `clause@1` | 229 | 51.5% | 45.0% - 57.6% |
| structural_pack | `clause@10` | 229 | 76.4% | 70.7% - 81.7% |
| structural_pack | `clause@20` | 229 | 84.3% | 79.5% - 88.6% |
| structural_cross_rrf | `exact@1` | 229 | 20.1% | 14.8% - 25.3% |
| structural_cross_rrf | `exact@10` | 229 | 50.2% | 44.1% - 56.3% |
| structural_cross_rrf | `exact@20` | 229 | 60.3% | 54.1% - 66.8% |
| structural_cross_rrf | `clause@1` | 229 | 53.3% | 46.7% - 59.4% |
| structural_cross_rrf | `clause@10` | 229 | 83.4% | 78.6% - 87.8% |
| structural_cross_rrf | `clause@20` | 229 | 86.9% | 82.5% - 91.3% |

## Paired Delta vs `structural_pack`

| run | metric | delta | 95% CI |
|---|---|---:|---:|
| structural_cross_rrf | `exact@1` | 4.8% | 1.7% - 8.3% |
| structural_cross_rrf | `exact@10` | 7.4% | 3.5% - 11.4% |
| structural_cross_rrf | `exact@20` | 7.0% | 3.1% - 11.4% |
| structural_cross_rrf | `clause@1` | 1.7% | -3.1% - 7.0% |
| structural_cross_rrf | `clause@10` | 7.0% | 3.5% - 10.9% |
| structural_cross_rrf | `clause@20` | 2.6% | 0.0% - 5.2% |

## Use Notes

- Treat these as private-lab diagnostics until the evaluation core is expanded and audited.
- A CI spanning zero on paired deltas means the observed gain is not yet a stable headline claim.
