# System Matrix Report

Status: **INCOMPLETE for full comparison matrix**.

diagnostic coverage only; full analyzer/dense/hybrid/reranker matrix incomplete

This report tracks which retrieval, routing, surface, and label-gate
systems are actually backed by checked-in evidence. It prevents the
repo from implying that the full analyzer/dense/hybrid/reranker matrix
has already been run.

## Summary

| item | value |
|---|---:|
| matrix systems | 15 |
| implemented systems | 7 |
| not-run systems | 7 |
| blocked systems | 1 |
| system families | 9 |
| implemented diagnostic rows | 2736 |

## Matrix

| system | family | stage | status | rows | claim scope | evidence |
|---|---|---|---|---:|---|---|
| `structural_pack` | `lexical_retrieval` | `retrieval` | `implemented` | 544 | `diagnostic` | `reports/private_544_pack_only_scorecard.md` |
| `structural_cross_text` | `reranked_retrieval` | `retrieval` | `implemented` | 544 | `diagnostic` | `reports/private_544_full_cross_scorecard.md` |
| `always_policy` | `source_routing` | `routing` | `implemented` | 544 | `diagnostic` | `reports/private_route_scorecard_silver.md` |
| `query_keyword_router` | `source_routing` | `routing` | `implemented` | 544 | `diagnostic` | `reports/private_route_router_baselines.md` |
| `cohort_aware_query_router` | `source_routing` | `routing` | `implemented` | 544 | `diagnostic` | `reports/private_route_scorecard_silver.md` |
| `formal_only_demo` | `surface_fixture` | `fixture` | `implemented` | 8 | `fixture` | `reports/surface_scorecard_fixture.md` |
| `surface_robust_demo` | `surface_fixture` | `fixture` | `implemented` | 8 | `fixture` | `reports/surface_scorecard_fixture.md` |
| `bm25_nori` | `analyzer_bm25` | `retrieval` | `not_run` | 0 | `missing_for_full_matrix` | `not yet run` |
| `bm25_kiwi` | `analyzer_bm25` | `retrieval` | `not_run` | 0 | `missing_for_full_matrix` | `not yet run` |
| `bm25_mecab` | `analyzer_bm25` | `retrieval` | `not_run` | 0 | `missing_for_full_matrix` | `not yet run` |
| `dense_multilingual_encoder` | `dense_retrieval` | `retrieval` | `not_run` | 0 | `missing_for_full_matrix` | `not yet run` |
| `dense_korean_encoder` | `dense_retrieval` | `retrieval` | `not_run` | 0 | `missing_for_full_matrix` | `not yet run` |
| `hybrid_lexical_dense` | `hybrid_retrieval` | `retrieval` | `not_run` | 0 | `missing_for_full_matrix` | `not yet run` |
| `cross_encoder_reranker` | `reranker` | `reranking` | `not_run` | 0 | `missing_for_full_matrix` | `not yet run` |
| `human_gold_route_scorecard` | `human_gold_gate` | `label_gate` | `blocked` | 0 | `required_for_headline` | `reports/study_readiness.md` |

## Missing For Full Matrix

- `bm25_nori`
- `bm25_kiwi`
- `bm25_mecab`
- `dense_multilingual_encoder`
- `dense_korean_encoder`
- `hybrid_lexical_dense`
- `cross_encoder_reranker`
- `human_gold_route_scorecard`

## Validation

- manifest: `docs/system_matrix.json`
- validation issues: 0

## Use Notes

- `implemented` means an aggregate public report exists; it does not mean
  the result is human-gold or headline-ready.
- `not_run` systems are explicit gaps in the full comparison matrix.
- `blocked` systems depend on human labels or other external evidence.
