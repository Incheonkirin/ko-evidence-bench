# Public Probe System Comparison

Status: **synthetic probe systems only; not a full private benchmark matrix**.

This report runs small retrieval systems over the public synthetic
probe package. It proves that the repository can execute and compare
literal lexical, surface-normalized, semantic, hybrid, and source-route-aware
systems without publishing private queries, conversation snippets, source
names, or policy text.

## Inputs

- probe dir: `probes/ko_evidence_probe_v0`
- query rows: 13
- qrel rows: 13
- evidence rows: 7
- label status: synthetic public fixture

## Systems

| system | method |
|---|---|
| `probe_literal_lexical` | literal lexical BM25 over synthetic Korean search text |
| `probe_normalized_lexical` | surface-expanded lexical BM25 |
| `probe_semantic_centroid` | dependency-free semantic centroid scorer over concept features |
| `probe_hybrid_lexical_semantic` | lexical BM25 plus semantic concept-score fusion |
| `probe_route_aware_rerank` | hybrid scoring plus source-route-aware reranking and abstention |

## Overall Scorecard

| system | n | route_acc | suff@3 | wrong_src@3 | abst_p | abst_r | clause@3 | task_success@3 | worst_surface@3 | avg_intent_spread |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `probe_literal_lexical` | 13 | 76.9% | 100.0% | 61.5% | 0.0% | 0.0% | 100.0% | 76.9% | 50.0% | 0.0% |
| `probe_normalized_lexical` | 13 | 76.9% | 100.0% | 61.5% | 0.0% | 0.0% | 100.0% | 76.9% | 50.0% | 0.0% |
| `probe_semantic_centroid` | 13 | 84.6% | 100.0% | 53.8% | 0.0% | 0.0% | 100.0% | 84.6% | 50.0% | 0.0% |
| `probe_hybrid_lexical_semantic` | 13 | 84.6% | 100.0% | 84.6% | 0.0% | 0.0% | 100.0% | 84.6% | 50.0% | 0.0% |
| `probe_route_aware_rerank` | 13 | 100.0% | 100.0% | 0.0% | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% | 0.0% |

## Route Confusions

| system | gold route | predicted route | rows |
|---|---|---|---:|
| `probe_literal_lexical` | `human_context_needed` | `expert_answer` | 2 |
| `probe_literal_lexical` | `official_consumer_info` | `expert_answer` | 1 |
| `probe_normalized_lexical` | `human_context_needed` | `expert_answer` | 2 |
| `probe_normalized_lexical` | `official_consumer_info` | `expert_answer` | 1 |
| `probe_semantic_centroid` | `human_context_needed` | `expert_answer` | 2 |
| `probe_hybrid_lexical_semantic` | `human_context_needed` | `expert_answer` | 2 |

## Use Notes

- This is a runnable public-system comparison, not the private analyzer/dense/hybrid/reranker matrix.
- The semantic centroid is a dependency-free surrogate for exercising dense-style comparison plumbing; it is not a neural encoder.
- The hybrid system is intentionally simple; it demonstrates score fusion and source-mixing diagnostics, not a product rewrite engine.
- The route-aware system shows why source selection and abstention must be scored separately from paragraph similarity.
- Private system runs can reuse the same qid-only report shape after human labels are complete.
