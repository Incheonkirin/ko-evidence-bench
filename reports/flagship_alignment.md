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
| Dictionary scope guard | `PASS` | README scope statement rejects a dictionary-first framing | The flagship has to be a measurement artifact, not a user-dictionary repo. |
| Multi-source evidence frame | `PASS` | route protocol and study draft model multiple citable source tiers | The benchmark tests evidence routing, not only policy-clause recall. |
| Real-query substrate inventory | `PASS` | README aggregates private query substrates and cohort scorecards compare them generically | The study is grounded in real query distributions without exposing private source names. |
| Surface-form robustness axis | `PASS` | surface-form scorecard and lift gate measure same-intent robustness across phrasing conditions | This implements the Fable axis about intent fragmentation, not token dictionaries. |
| Route-surface diagnostic axis | `PASS` | route-only scorecard slices source-route and abstention behavior by surface, intent family, and trap class | The study can separate surface-conditioned routing failures from retrieval-hit failures. |
| Runtime-surface retrieval-hit axis | `PASS` | runtime hit booleans are sliced by surface form, intent family, and trap class without raw evidence ids | This moves surface robustness from fixture-only demos into actual retrieval-hit diagnostics. |
| Intent-family inventory axis | `PASS` | fixture and private silver inventories treat intent families, surface forms, and trap classes as aggregate slices | This moves the flagship design from synthetic slices into the private qid-only qrel path. |
| Normalization ablation axis | `PASS` | normalization ablation reports aggregate rescue/regression by intent family and surface | This validates normalization as measured lift, not a standalone dictionary artifact. |
| Qid-only route scorecard path | `PASS` | private silver runs are scored through the same path as future human labels | The evaluation path is tested before human-gold labels arrive. |
| Per-source route failure slices | `PASS` | route scorecards expose source-tier slices and largest route confusions | The study can explain where routing fails, not just report one aggregate number. |
| Query-cohort route slices | `PASS` | source-map cohort scorecards compare query substrates without raw source names | The study can test whether failures differ across real query cohorts. |
| Query-substrate profile | `PASS` | aggregate shape profile compares community post contexts, cleaned eval queries, and live-style conversation turns | The study shows why query cohorts need different stress slices instead of treating all text as one corpus. |
| Cohort-aware routing baseline | `PASS` | cohort-aware router is exported, scored, and guarded by a silver lift gate | The repo shows a measured routing improvement, not only an evaluation shell. |
| Human audit workflow | `PASS` | review UI plus synthetic audit workflow dry-run | The remaining work is label production, not missing audit plumbing. |
| Human-label progress gate | `PASS` | 300-row brief, priority batch, merge dry-run, progress, and CSV validation are summarized without raw rows | The remaining human task can be prioritized, started, merged, and tracked before import. |
| Human-gold route labels | `BLOCKED` | 0/50 paired labels; kappa 0.000; 0/300 adjudicated labels complete; 300 validation errors | Agreement quality and adjudicated coverage are required before public headline claims. |
| Public/private boundary | `PASS` | data statement plus public-safety scan | The private logs ground the work without leaking raw rows. |
| CI verification | `PASS` | make verify in GitHub Actions | The repo continuously checks reports, claims, fixtures, and safety. |

## Interpretation

The repo now has the public shell expected of a flagship measurement study:
generated study draft, claim-control gates, qid-only scorecards, audit
workflow, and public-safety checks. It is not headline-ready because the
source-route labels still lack independent agreement evidence and
human-adjudicated coverage.

## Next Gate

Double-label at least 50 route rows, report agreement and kappa, complete
the 300-row adjudicated route-label workset, validate it with zero errors,
promote qid-only human labels, and rerun the route scorecard and
measurement-study draft.
