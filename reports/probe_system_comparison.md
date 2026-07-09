# Public Probe System Comparison

Status: **synthetic probe systems only; not a full private benchmark matrix**.

This report runs three small retrieval systems over the public synthetic
probe package. It proves that the repository can execute and compare
surface-fragile, surface-normalized, and source-route-aware systems without
publishing private queries, conversation snippets, source names, or policy
text.

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
| `probe_route_aware_rerank` | surface expansion plus source-route-aware reranking and abstention |

## Overall Scorecard

| system | n | route_acc | suff@3 | wrong_src@3 | abst_p | abst_r | clause@3 | task_success@3 | worst_surface@3 | avg_intent_spread |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `probe_literal_lexical` | 13 | 76.9% | 100.0% | 61.5% | 0.0% | 0.0% | 100.0% | 76.9% | 50.0% | 0.0% |
| `probe_normalized_lexical` | 13 | 76.9% | 100.0% | 61.5% | 0.0% | 0.0% | 100.0% | 76.9% | 50.0% | 0.0% |
| `probe_route_aware_rerank` | 13 | 100.0% | 100.0% | 0.0% | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% | 0.0% |

## Route Confusions

| system | gold route | predicted route | rows |
|---|---|---|---:|
| `probe_literal_lexical` | `human_context_needed` | `expert_answer` | 2 |
| `probe_literal_lexical` | `official_consumer_info` | `expert_answer` | 1 |
| `probe_normalized_lexical` | `human_context_needed` | `expert_answer` | 2 |
| `probe_normalized_lexical` | `official_consumer_info` | `expert_answer` | 1 |

## Use Notes

- This is a runnable public-system comparison, not the private analyzer/dense/hybrid/reranker matrix.
- The surface-expanded system is intentionally simple; it demonstrates the evaluation path, not a product rewrite engine.
- The route-aware system shows why source selection and abstention must be scored separately from paragraph similarity.
- Private system runs can reuse the same qid-only report shape after human labels are complete.
