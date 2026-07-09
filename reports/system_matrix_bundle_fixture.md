# System Matrix Bundle Contract

Status: **PASS synthetic full-matrix run-bundle rehearsal**.

This report validates the qid-only artifact shape expected from the
full analyzer/dense/hybrid/reranker comparison matrix. It does not
claim that those external systems have been run on the private lab.
Instead, it proves that their future runs can be imported, checked for
qid coverage, screened for raw-text leakage, and scored through the
same route/surface metrics.

The score values below are fixture-validator outputs only. They are
not model-quality comparisons and must not be used as analyzer or
encoder performance claims.

## Inputs

- bundle dir: `fixtures/system_matrix_bundle`
- qrels: `fixtures/surface_qrels.jsonl`
- system matrix: `docs/system_matrix.json`
- label status: synthetic matrix bundle fixture; not external model output

## Gate Summary

| item | value |
|---|---:|
| qrel rows | 8 |
| required runnable systems | 7 |
| present systems | 7 |
| complete systems | 7 |
| missing systems | 0 |
| extra systems | 0 |
| validation errors | 0 |

## Required Systems

- `bm25_nori`
- `bm25_kiwi`
- `bm25_mecab`
- `dense_multilingual_encoder`
- `dense_korean_encoder`
- `hybrid_lexical_dense`
- `cross_encoder_reranker`

## System Scores

| system | family | stage | rows | complete | route_acc | suff@3 | wrong_src@3 | clause@3 | task_success@3 | worst_surface@3 | avg_intent_spread |
|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| `bm25_nori` | `analyzer_bm25` | `retrieval` | 8 | `yes` | 75.0% | 33.3% | 12.5% | 33.3% | 37.5% | 0.0% | 100.0% |
| `bm25_kiwi` | `analyzer_bm25` | `retrieval` | 8 | `yes` | 100.0% | 100.0% | 0.0% | 100.0% | 100.0% | 100.0% | 0.0% |
| `bm25_mecab` | `analyzer_bm25` | `retrieval` | 8 | `yes` | 75.0% | 33.3% | 12.5% | 33.3% | 37.5% | 0.0% | 100.0% |
| `dense_multilingual_encoder` | `dense_retrieval` | `retrieval` | 8 | `yes` | 75.0% | 33.3% | 12.5% | 33.3% | 37.5% | 0.0% | 100.0% |
| `dense_korean_encoder` | `dense_retrieval` | `retrieval` | 8 | `yes` | 100.0% | 100.0% | 0.0% | 100.0% | 100.0% | 100.0% | 0.0% |
| `hybrid_lexical_dense` | `hybrid_retrieval` | `retrieval` | 8 | `yes` | 100.0% | 100.0% | 0.0% | 100.0% | 100.0% | 100.0% | 0.0% |
| `cross_encoder_reranker` | `reranker` | `reranking` | 8 | `yes` | 100.0% | 100.0% | 0.0% | 100.0% | 100.0% | 100.0% | 0.0% |

## Validation Details

- none

## Use Notes

- This fixture rehearses the import contract for the missing matrix systems;
  it is not evidence that the private full matrix has been run.
- The fixture score table exists to prove scoring compatibility, not to
  compare analyzer or neural retriever quality.
- Real runs should keep raw queries, source names, URLs, usernames, and
  passage text outside the public repo and publish only qid-only outputs
  plus aggregate reports.
- Once real system runs exist, replace the fixture bundle path and rerun
  this validator before changing `docs/system_matrix.json` statuses.
