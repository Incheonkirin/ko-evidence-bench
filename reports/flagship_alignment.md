# Flagship Alignment

Overall status: **NO-GO FOR HEADLINE CLAIMS**.

This report checks whether the repository is shaped as a measurement-study
artifact rather than a loose evaluation framework. It intentionally separates
implemented infrastructure from the human-label gate that still blocks public
headline claims.

| area | status | evidence | why it matters |
|---|---|---|---|
| Report-first artifact | `PASS` | reports/measurement_study_draft.md | The study is the product; code is the reproduction apparatus. |
| Generated finding table | `PASS` | finding candidates are generated from aggregate reports | Reviewers see numbers and claim controls before framework plumbing. |
| Claim-control gate | `PASS` | study readiness is NO-GO | The repo refuses to promote silver diagnostics as final benchmark claims. |
| README signal drift guard | `PASS` | scripts/sync_readme_signals.py --check | The first-screen numbers are generated from checked-in evidence. |
| Qid-only route scorecard path | `PASS` | private silver runs are scored through the same path as future human labels | The evaluation path is tested before human-gold labels arrive. |
| Human audit workflow | `PASS` | review UI plus synthetic audit workflow dry-run | The remaining work is label production, not missing audit plumbing. |
| Human-gold route labels | `BLOCKED` | 0/300 adjudicated labels complete; 300 validation errors | This is the required gate before public headline claims. |
| Public/private boundary | `PASS` | data statement plus public-safety scan | The private logs ground the work without leaking raw rows. |
| CI verification | `PASS` | make verify in GitHub Actions | The repo continuously checks reports, claims, fixtures, and safety. |

## Interpretation

The repo now has the public shell expected of a flagship measurement study:
generated study draft, claim-control gates, qid-only scorecards, audit
workflow, and public-safety checks. It is not headline-ready because the
source-route labels are still silver rather than human-adjudicated.

## Next Gate

Complete the 300-row adjudicated route-label workset, validate it with zero
errors, promote qid-only human labels, and rerun the route scorecard and
measurement-study draft.
