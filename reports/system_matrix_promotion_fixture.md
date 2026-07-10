# System Matrix Promotion Rehearsal

Status: **BLOCKED synthetic promotion rehearsal; no matrix update**.

This report checks whether a qid-only full-matrix run bundle is ready
to promote from `not_run` to checked diagnostic evidence. It does not
update `docs/system_matrix.json` and does not claim that external
analyzer, dense, hybrid, or reranker systems have been run.

The checked-in fixture is intentionally blocked from promotion because
it is synthetic, below the private-run row threshold, and marked as not
external model output.

## Inputs

- bundle dir: `fixtures/system_matrix_bundle`
- qrels: `fixtures/surface_qrels.jsonl`
- system matrix: `docs/system_matrix.json`
- minimum promotion rows: 500
- label status: synthetic matrix bundle fixture; not external model output

## Promotion Gates

| gate | status | evidence | required |
|---|---|---|---|
| `validation` | `PASS` | 0 validation errors | 0 validation errors |
| `required_systems` | `PASS` | 7 present / 7 required | all and only matrix not-run systems are present |
| `run_completeness` | `PASS` | 7 complete systems | every system covers every qid exactly once |
| `qid_only_screen` | `PASS` | 0 raw-field errors | no raw query, answer, source, url, username, or passage fields |
| `scale` | `BLOCKED` | 8 qrel rows | >= 500 qrel rows for private full-matrix promotion |
| `run_provenance` | `BLOCKED` | 0 private external / 7 required systems | every submitted system declares private_external_run provenance |

## Candidate System Scores

| system | rows | complete | route_acc | suff@3 | wrong_src@3 | clause@3 | task_success@3 | worst_surface@3 |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| `bm25_nori` | 8 | `yes` | 75.0% | 33.3% | 12.5% | 33.3% | 37.5% | 0.0% |
| `bm25_kiwi` | 8 | `yes` | 100.0% | 100.0% | 0.0% | 100.0% | 100.0% | 100.0% |
| `bm25_mecab` | 8 | `yes` | 75.0% | 33.3% | 12.5% | 33.3% | 37.5% | 0.0% |
| `dense_multilingual_encoder` | 8 | `yes` | 75.0% | 33.3% | 12.5% | 33.3% | 37.5% | 0.0% |
| `dense_korean_encoder` | 8 | `yes` | 100.0% | 100.0% | 0.0% | 100.0% | 100.0% | 100.0% |
| `hybrid_lexical_dense` | 8 | `yes` | 100.0% | 100.0% | 0.0% | 100.0% | 100.0% | 100.0% |
| `cross_encoder_reranker` | 8 | `yes` | 100.0% | 100.0% | 0.0% | 100.0% | 100.0% | 100.0% |

## Promotion Decision

Do not update `docs/system_matrix.json` from this fixture. The
mechanical import path is rehearsed, but promotion remains blocked
until a real full-matrix run bundle reaches the required scale and
carries real external-run provenance.

## Use Notes

- This is a promotion gate, not a model-quality benchmark.
- It is allowed for the checked-in fixture to be blocked; that is the
  expected safety behavior.
- Real private runs should publish only qid-only run files and aggregate
  reports, never raw queries, evidence text, source names, URLs, or user
  identifiers.
