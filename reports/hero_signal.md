# Hero Diagnostic Signal

Status: **diagnostic only; human-gold headline claims blocked**.

![Diagnostic signal heatmap](figures/diagnostic_signal_heatmap.svg)

This report turns the checked-in aggregate diagnostics into a first
screen study signal: a small number of memorable findings with the
claim-control gate kept visible.

| axis | baseline | current candidate | diagnostic read |
|---|---:|---:|---|
| Clause recovery | `structural_pack` 56.4% | `structural_cross_text` 64.9% | +8.5%p paired, CI 5.9% - 11.2% |
| Source routing | `always_policy` 21.5% | `cohort_aware_query_router` 46.9% | +25.4%p paired, CI 19.3% - 31.2% |
| Unsafe policy fallback | 190 context-needed rows | 28 context-needed rows | 162 fewer silver fallback errors |
| Surface robustness | overall clause@20 64.9% | worst surface 44.4% | 20.5%p spread remains |
| Human-gold gate | 0/50 paired labels | 0/300 adjudicated labels | kappa 0.000; 300 validation errors |
| System matrix gate | 14/22 systems implemented | 7 not run; 1 blocked | full comparison matrix incomplete |

## Use Notes

- The figure and table are generated from aggregate reports only.
- These are private-lab silver diagnostics, not final benchmark claims.
- The strongest public version starts here but waits for completed
  human labels and full matrix coverage before changing the README
  language from diagnostic to headline.
