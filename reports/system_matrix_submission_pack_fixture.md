# System Matrix Submission Pack Fixture

Status: **PASS qid-only matrix submission template**.

This report checks the handoff pack for external analyzer, dense,
hybrid, and reranker runs. It is a template, not model output; it
must not be used as evidence that the full private matrix has been run.

## Inputs

- qrels: `fixtures/surface_qrels.jsonl`
- system matrix: `docs/system_matrix.json`
- pack dir: `fixtures/system_matrix_submission_template`
- qrel rows: 8
- required missing-matrix systems: 7

## Gate Summary

| gate | evidence | status |
|---|---:|---|
| qrel validation | 0 errors | `PASS` |
| required systems | 7 systems | `PASS` |
| template files | 9 / 9 present | `PASS` |
| raw-field boundary | qids plus placeholder run schema only | `PASS` |
| promotion status | template only; no external systems run | `BLOCKED` |

## Required Systems

| system | family | stage | template |
|---|---|---|---|
| `bm25_nori` | `analyzer_bm25` | `retrieval` | `fixtures/system_matrix_submission_template/runs/bm25_nori.jsonl.template` |
| `bm25_kiwi` | `analyzer_bm25` | `retrieval` | `fixtures/system_matrix_submission_template/runs/bm25_kiwi.jsonl.template` |
| `bm25_mecab` | `analyzer_bm25` | `retrieval` | `fixtures/system_matrix_submission_template/runs/bm25_mecab.jsonl.template` |
| `dense_multilingual_encoder` | `dense_retrieval` | `retrieval` | `fixtures/system_matrix_submission_template/runs/dense_multilingual_encoder.jsonl.template` |
| `dense_korean_encoder` | `dense_retrieval` | `retrieval` | `fixtures/system_matrix_submission_template/runs/dense_korean_encoder.jsonl.template` |
| `hybrid_lexical_dense` | `hybrid_retrieval` | `retrieval` | `fixtures/system_matrix_submission_template/runs/hybrid_lexical_dense.jsonl.template` |
| `cross_encoder_reranker` | `reranker` | `reranking` | `fixtures/system_matrix_submission_template/runs/cross_encoder_reranker.jsonl.template` |

## Use Notes

- This fixture turns the missing full-matrix work into a concrete handoff pack.
- Real submissions must replace `.jsonl.template` files with `.jsonl` run files.
- The submitted bundle still needs validation, provenance, scale, and promotion gates.
- Do not include raw queries, source names, URLs, answers, or evidence text in run files.
