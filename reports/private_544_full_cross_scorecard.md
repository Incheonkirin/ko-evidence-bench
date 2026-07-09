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
| minimal_cross_text | `exact@1` | 544 | 20.2% | 17.1% - 23.3% |
| minimal_cross_text | `exact@10` | 544 | 46.5% | 42.3% - 50.6% |
| minimal_cross_text | `exact@20` | 544 | 52.8% | 48.3% - 57.0% |
| minimal_cross_text | `clause@1` | 544 | 35.7% | 31.8% - 39.7% |
| minimal_cross_text | `clause@10` | 544 | 58.3% | 54.2% - 62.3% |
| minimal_cross_text | `clause@20` | 544 | 64.2% | 60.1% - 68.0% |
| minimal_cross_rrf | `exact@1` | 544 | 21.5% | 18.2% - 24.8% |
| minimal_cross_rrf | `exact@10` | 544 | 43.4% | 39.2% - 47.4% |
| minimal_cross_rrf | `exact@20` | 544 | 49.4% | 45.2% - 53.7% |
| minimal_cross_rrf | `clause@1` | 544 | 34.2% | 30.1% - 38.1% |
| minimal_cross_rrf | `clause@10` | 544 | 54.8% | 50.6% - 58.8% |
| minimal_cross_rrf | `clause@20` | 544 | 60.7% | 56.4% - 64.5% |
| structural_cross_text | `exact@1` | 544 | 19.3% | 16.2% - 22.6% |
| structural_cross_text | `exact@10` | 544 | 46.9% | 42.8% - 51.1% |
| structural_cross_text | `exact@20` | 544 | 52.4% | 48.2% - 56.4% |
| structural_cross_text | `clause@1` | 544 | 35.1% | 31.2% - 39.0% |
| structural_cross_text | `clause@10` | 544 | 60.1% | 56.1% - 64.0% |
| structural_cross_text | `clause@20` | 544 | 64.9% | 60.8% - 68.8% |
| structural_cross_rrf | `exact@1` | 544 | 20.8% | 17.5% - 23.9% |
| structural_cross_rrf | `exact@10` | 544 | 44.7% | 40.4% - 48.5% |
| structural_cross_rrf | `exact@20` | 544 | 51.1% | 46.9% - 55.3% |
| structural_cross_rrf | `clause@1` | 544 | 35.1% | 31.2% - 39.0% |
| structural_cross_rrf | `clause@10` | 544 | 56.6% | 52.4% - 60.8% |
| structural_cross_rrf | `clause@20` | 544 | 61.4% | 57.4% - 65.4% |

## Paired Delta vs `structural_pack`

| run | metric | delta | 95% CI |
|---|---|---:|---:|
| minimal_pack | `exact@1` | 1.5% | -0.7% - 3.7% |
| minimal_pack | `exact@10` | -3.3% | -5.5% - -1.1% |
| minimal_pack | `exact@20` | -4.2% | -6.1% - -2.6% |
| minimal_pack | `clause@1` | -1.8% | -4.2% - 0.7% |
| minimal_pack | `clause@10` | -3.7% | -5.9% - -1.5% |
| minimal_pack | `clause@20` | -2.9% | -4.6% - -1.3% |
| minimal_cross_text | `exact@1` | 3.1% | -0.6% - 6.6% |
| minimal_cross_text | `exact@10` | 6.6% | 3.3% - 9.9% |
| minimal_cross_text | `exact@20` | 6.8% | 4.0% - 9.6% |
| minimal_cross_text | `clause@1` | 6.2% | 2.2% - 10.5% |
| minimal_cross_text | `clause@10` | 7.5% | 4.4% - 10.8% |
| minimal_cross_text | `clause@20` | 7.7% | 5.0% - 10.7% |
| minimal_cross_rrf | `exact@1` | 4.4% | 1.5% - 7.5% |
| minimal_cross_rrf | `exact@10` | 3.5% | 0.9% - 6.1% |
| minimal_cross_rrf | `exact@20` | 3.5% | 1.1% - 5.9% |
| minimal_cross_rrf | `clause@1` | 4.8% | 1.5% - 8.3% |
| minimal_cross_rrf | `clause@10` | 4.0% | 1.3% - 7.0% |
| minimal_cross_rrf | `clause@20` | 4.2% | 1.8% - 6.8% |
| structural_cross_text | `exact@1` | 2.2% | -1.5% - 5.7% |
| structural_cross_text | `exact@10` | 7.0% | 3.9% - 10.3% |
| structural_cross_text | `exact@20` | 6.4% | 3.9% - 9.2% |
| structural_cross_text | `clause@1` | 5.7% | 1.5% - 9.9% |
| structural_cross_text | `clause@10` | 9.4% | 6.2% - 12.5% |
| structural_cross_text | `clause@20` | 8.5% | 5.9% - 11.2% |
| structural_cross_rrf | `exact@1` | 3.7% | 0.7% - 6.8% |
| structural_cross_rrf | `exact@10` | 4.8% | 2.8% - 7.0% |
| structural_cross_rrf | `exact@20` | 5.1% | 2.9% - 7.5% |
| structural_cross_rrf | `clause@1` | 5.7% | 2.6% - 9.0% |
| structural_cross_rrf | `clause@10` | 5.9% | 3.5% - 8.5% |
| structural_cross_rrf | `clause@20` | 5.0% | 2.9% - 7.0% |

## Use Notes

- Treat these as private-lab diagnostics until the evaluation core is expanded and audited.
- A CI spanning zero on paired deltas means the observed gain is not yet a stable headline claim.
