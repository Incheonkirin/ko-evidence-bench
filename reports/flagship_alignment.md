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
| Hero diagnostic figure | `PASS` | README hero figure and report are generated from aggregate diagnostics | The first screen leads with memorable findings while keeping the claim gate visible. |
| Claim-control gate | `PASS` | study readiness is NO-GO | The repo refuses to promote silver diagnostics as final benchmark claims. |
| Claim wording ledger | `PASS` | generated ledger separates allowed diagnostic wording from blocked claims | The repo shows judgment about what the evidence can and cannot support. |
| Reviewer demo path | `PASS` | generated 3-minute walkthrough links findings, claim controls, rehearsal, and readiness | A reviewer can understand the study artifact before reading framework code. |
| Containerized reproduction path | `PASS` | Dockerfile plus make docker-demo reruns the fixture table and claim-control checks | A reviewer can reproduce the public demo without first configuring a Python environment. |
| Public probe set and privacy screen | `PASS` | synthetic queries, intent-level qrels, evidence snippets, and privacy-screen report | The released instrument is a screened probe set, not a dictionary or private-data dump. |
| Public probe dataset card | `PASS` | generated dataset card records intended use, non-goals, distributions, and privacy notes | The public probe is packaged like a reusable IR artifact instead of a loose fixture folder. |
| BEIR-style public probe export | `PASS` | public probe rows are exported to corpus, queries, qrels, and metadata files | The public probe can plug into standard IR tooling without hiding route and abstention limits. |
| Runnable public probe systems | `PASS` | lexical, semantic, hybrid, and route-aware probe systems run on the same public fixture | The public probe is executable evidence, not only a static dataset or dictionary. |
| Trap-mining diagnostic | `PASS` | public probe queries are mined for trap classes and compared with qrel annotations | Analyzer and intent-fragmentation failures are measured as diagnostics, not shipped as a dictionary. |
| Surface-fragmentation undercount audit | `PASS` | public probe intents compare exact lexical seed counts with qrel-level surface variants | The repo measures the user's undercount critique instead of turning aliases into a dictionary. |
| Qualitative failure gallery | `PASS` | synthetic side-by-side ranking examples generated from the public probe package | Reviewers can inspect concrete failure modes instead of only aggregate metrics. |
| README signal drift guard | `PASS` | scripts/sync_readme_signals.py --check | The first-screen numbers are generated from checked-in evidence. |
| Dictionary scope guard | `PASS` | README scope statement rejects a dictionary-first framing | The flagship has to be a measurement artifact, not a user-dictionary repo. |
| Multi-source evidence frame | `PASS` | route protocol and study draft model multiple citable source tiers | The benchmark tests evidence routing, not only policy-clause recall. |
| Real-query substrate inventory | `PASS` | README aggregates private query substrates and cohort scorecards compare them generically | The study is grounded in real query distributions without exposing private source names. |
| Surface-form robustness axis | `PASS` | surface-form scorecard and lift gate measure same-intent robustness across phrasing conditions | This implements the intent-fragmentation axis, not token dictionaries. |
| Route-surface diagnostic axis | `PASS` | route-only scorecard slices source-route and abstention behavior by surface, intent family, and trap class | The study can separate surface-conditioned routing failures from retrieval-hit failures. |
| Runtime-surface retrieval-hit axis | `PASS` | runtime hit booleans are sliced by surface form, intent family, and trap class without raw evidence ids | This moves surface robustness from fixture-only demos into actual retrieval-hit diagnostics. |
| Layer attribution axis | `PASS` | failed synthetic rows are decomposed into primary diagnostic layers | The study can explain where failures accumulate instead of only reporting aggregate scores. |
| System comparison matrix guard | `PASS` | system matrix report separates implemented diagnostics from not-run and blocked comparisons | The repo must not imply the full analyzer/dense/hybrid/reranker matrix has already been run. |
| Full-matrix run-bundle contract | `PASS` | synthetic qid-only bundle validates import, coverage, leakage, and scoring for the missing systems | The missing full matrix now has a checked artifact contract instead of an undefined handoff. |
| Intent-family inventory axis | `PASS` | fixture and private silver inventories treat intent families, surface forms, and trap classes as aggregate slices | This moves the flagship design from synthetic slices into the private qid-only qrel path. |
| Normalization ablation axis | `PASS` | normalization ablation reports aggregate rescue/regression by intent family and surface | This validates normalization as measured lift, not a standalone dictionary artifact. |
| Qid-only route scorecard path | `PASS` | private silver runs are scored through the same path as future human labels | The evaluation path is tested before human-gold labels arrive. |
| Per-source route failure slices | `PASS` | route scorecards expose source-tier slices and largest route confusions | The study can explain where routing fails, not just report one aggregate number. |
| Query-cohort route slices | `PASS` | source-map cohort scorecards compare query substrates without raw source names | The study can test whether failures differ across real query cohorts. |
| Query-substrate profile | `PASS` | aggregate shape profile compares community post contexts, cleaned eval queries, and live-style conversation turns | The study shows why query cohorts need different stress slices instead of treating all text as one corpus. |
| Cohort-aware routing baseline | `PASS` | cohort-aware router is exported, scored, and guarded by a silver lift gate | The repo shows a measured routing improvement, not only an evaluation shell. |
| Human audit workflow | `PASS` | review UI plus synthetic audit workflow dry-run | The remaining work is label production, not missing audit plumbing. |
| Human-label progress gate | `PASS` | 300-row brief, priority batch, merge dry-run, progress, and CSV validation are summarized without raw rows | The remaining human task can be prioritized, started, merged, and tracked before import. |
| Human-audit coverage gate | `PASS` | 300-row private audit workset covers route, intent-family, surface-form, and trap-class axes | The human-gold workset must preserve the surface/intent design before reviewers spend time. |
| Human-gold promotion rehearsal | `PASS` | synthetic completed labels validate, promote, and feed route plus route-surface scorecards | Once real labels are finished, the remaining path to measurement-study scorecards is already rehearsed. |
| Human-gold route labels | `BLOCKED` | 0/50 paired labels; kappa 0.000; 0/300 adjudicated labels complete; 300 validation errors | Agreement quality and adjudicated coverage are required before public headline claims. |
| Public/private boundary | `PASS` | data statement plus public-safety scan | The private logs ground the work without leaking raw rows. |
| CI verification | `PASS` | make verify in GitHub Actions | The repo continuously checks reports, claims, fixtures, and safety. |

## Interpretation

The repo now has the public shell expected of a flagship measurement study:
generated study draft, claim-control gates, reviewer walkthrough,
containerized reproduction, screened public probes, dataset card,
qualitative examples, layer attribution, system matrix guard,
full-matrix run-bundle contract, qid-only scorecards, audit workflow,
and public-safety checks. It is not headline-ready
because source-route labels still lack independent agreement
evidence and human-adjudicated coverage, and the full comparison
matrix still has not-run or blocked systems.

## Next Gate

Double-label at least 50 route rows, report agreement and kappa, complete
the 300-row adjudicated route-label workset, validate it with zero errors,
run the missing system comparisons or narrow the claim, promote qid-only
human labels, and rerun the route scorecard and measurement-study draft.
