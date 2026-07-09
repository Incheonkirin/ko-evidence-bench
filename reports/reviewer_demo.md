# Reviewer Demo Path

Status: **3-minute diagnostic walkthrough; human-gold headline claims blocked**.

This is the shortest public path through the repository. It is written for
a reviewer who wants to understand the study artifact before reading code.

## Three-Minute Path

| step | artifact | what to check | expected read |
|---:|---|---|---|
| 1 | `README.md` + diagnostic figure | Start with the thesis and first-screen signals. | The repo leads with findings and claim limits, not framework features. |
| 2 | `reports/hero_signal.md` | Inspect the compact evidence table behind the figure. | Clause recovery, source routing, surface spread, and the human-label gate are visible together. |
| 3 | `reports/claim_ledger.md` | Compare allowed wording with blocked wording. | Diagnostic claims are separated from final benchmark claims. |
| 4 | `probes/ko_evidence_probe_v0/` + `reports/probe_privacy_report.md` | Inspect the public probe package and screen. | The released probes are synthetic, intent-level, and privacy-screened. |
| 5 | `probes/ko_evidence_probe_v0/DATASET_CARD.md` + `reports/probe_dataset_card.md` | Check the release-facing probe card. | The public probe has generated row counts, intended use, non-goals, and privacy notes. |
| 6 | `reports/probe_beir_export.md` + `probes/ko_evidence_probe_v0/beir/` | Check the standard retrieval export. | The public probe can be consumed by BEIR-style tooling while route and abstention labels stay in metadata. |
| 7 | `reports/probe_system_comparison.md` | Check the runnable public systems. | Lexical, semantic, hybrid, and source-route-aware retrieval are compared on the same probe. |
| 8 | `reports/probe_trap_mining.md` | Inspect trap-class mining. | Analyzer and intent-fragmentation traps are mined as diagnostics, not as dictionary entries. |
| 9 | `reports/surface_fragmentation_audit.md` | Check seed-counting bias. | Exact lexical seeds undercount same-intent surface variants; the output is an audit, not a synonym list. |
| 10 | `reports/qualitative_gallery.md` | Read concrete side-by-side failure examples. | The route diagnostics are inspectable, not only aggregate tables. |
| 11 | `reports/layer_attribution_fixture.md` | Inspect the failure-layer decomposition hook. | The study can explain where failures accumulate, not only whether a run passed. |
| 12 | `reports/system_matrix.md` | Check which systems are actually backed by evidence. | The full analyzer/dense/hybrid/reranker matrix is explicit and incomplete. |
| 13 | `reports/measurement_study_draft.md` | Read the aggregate-only study draft. | The report is the product; code exists to regenerate and check it. |
| 14 | `reports/human_gold_rehearsal_fixture.md` | Verify the synthetic completed-label path. | Once real labels exist, the promotion and scorecard path is already rehearsed. |
| 15 | `reports/study_readiness.md` | Confirm the remaining gate. | Headline claims stay blocked until human labels are complete and validated. |

## One Command

```bash
make verify
```

`make verify` reruns the tests, synthetic reproductions, generated-report
drift checks, readiness gate, and public-safety scan. To regenerate this
walkthrough only, run:

```bash
make build-reviewer-demo
```

Containerized review path:

```bash
make docker-demo
```

`make docker-demo` builds the local image and reruns the fixture table,
layer attribution, readiness gate, probe privacy screen, public probe
dataset card, BEIR export, system comparison, trap-mining check, surface-fragmentation audit, qualitative gallery check, system matrix check,
generated-report checks, and public-safety scan inside the container.

## Current Diagnostic Signals

| signal | value | claim status |
|---|---:|---|
| retrieval eval rows | 544 | silver diagnostic |
| `clause@20` pack to cross-text | 56.4% -> 64.9% | diagnostic, not answer quality |
| route accuracy always-policy to cohort-aware | 21.5% -> 46.9% | diagnostic, not human-validated |
| context-needed policy fallback drop | 190 -> 28 (162 fewer rows) | diagnostic |
| worst surface `clause@20` | 44.4% | surface robustness not solved |
| paired human-label seed | 0/50; kappa 0.000 | headline blocked |
| adjudicated route labels | 0/300; 300 validation errors | headline blocked |

## What Not To Infer

- Do not treat the silver diagnostics as final benchmark numbers.
- Do not claim the result represents all Korean retrieval systems or domains.
- Do not infer raw user text, source-specific platform names, or copyrighted
  corpus content from the public reports.
- Do not read the normalization and surface reports as a dictionary product;
  they are measurement slices for retrieval behavior.

## Reviewer Decision

For a portfolio review, the current repo can be evaluated as a reproducible
measurement-study shell with visible judgment about claim control. It should
not yet be evaluated as a completed human-gold benchmark. The next decisive
step is to complete the 50-row agreement seed and 300-row adjudicated
route-label workset, then regenerate the study draft from human labels.
