# Korean Polarity Retrieval Stress

A contrastive stress measurement over a private Korean evidence-retrieval lab.
The public artifact contains aggregate outcomes only: no queries, passages,
source names, URLs, user identifiers, or stable row ids are exported.

## Result

| system | triples | seed pairs | wrong-polarity preferred | 95% CI (seed-pair bootstrap) |
|---|---:|---:|---:|---:|
| `bm25_analyzer_tokens` | 444 | 37 | 53.8% | 52.3% - 55.6% |
| `bm25_lucene_idf_sensitivity` | 444 | 37 | 44.4% | 42.1% - 46.4% |
| `dense_bge_m3` | 444 | 37 | 29.1% | 23.6% - 34.5% |
| `cross_encoder_bge_reranker_v2_m3` | 444 | 37 | 48.4% | 45.9% - 50.7% |

The stress test asks a narrower question than recall: when the candidate
set contains expected and opposite-polarity evidence, does a system preserve
the direction of the query? Lower is better. The dense model reduces the
overall error rate relative to the lexical baselines, but the reranker remains
fragile on the same contrastive slice.

## Slice Asymmetry

| system | intent slice | triples | wrong-polarity preferred | 95% CI (seed-pair bootstrap) |
|---|---|---:|---:|---:|
| `bm25_analyzer_tokens` | `coverage` | 222 | 20.3% | 12.6% - 29.3% |
| `bm25_analyzer_tokens` | `exclusion` | 222 | 87.4% | 79.7% - 93.7% |
| `bm25_lucene_idf_sensitivity` | `coverage` | 222 | 78.4% | 70.3% - 86.0% |
| `bm25_lucene_idf_sensitivity` | `exclusion` | 222 | 10.4% | 4.5% - 18.0% |
| `dense_bge_m3` | `coverage` | 222 | 51.4% | 39.6% - 63.1% |
| `dense_bge_m3` | `exclusion` | 222 | 6.8% | 0.9% - 14.4% |
| `cross_encoder_bge_reranker_v2_m3` | `coverage` | 222 | 89.6% | 81.1% - 96.4% |
| `cross_encoder_bge_reranker_v2_m3` | `exclusion` | 222 | 7.2% | 2.3% - 14.0% |

## Measurement Contract

- contrastive triples: 444
- seed evidence pairs: 37
- intent balance: `coverage` 222, `exclusion` 222
- dense model: `BAAI/bge-m3`
- reranker model: `BAAI/bge-reranker-v2-m3`
- metric: opposite-polarity evidence scores at or above expected evidence (ties count as wrong)
- CI: percentile bootstrap clustered by seed evidence pair; 20,000 resamples; seed 13

The 444 triples are counterfactual variants derived from seed evidence
pairs, not 444 independent source documents. Intervals therefore resample
the seed pairs as clusters. This is a stress result, not an end-to-end
human-relevance benchmark or a claim of cross-domain generalization.

## Aggregate Provenance

- experiment date: 2026-07-06
- retrieval input SHA-256: `b750686050ac9ae5def37bc533b8679a27e516780844237520e565522731d9ab`
- reranker input SHA-256: `627383edc513fe08960e88bd82980a09aecf8fe570a9915be300dd8e8ca340f6`
- public output contains raw text: `false`

To regenerate locally, supply the private aggregate row exports to
`scripts/reproduce_private_polarity_stress.py`. The script projects each
input row to pair id, intent, and Boolean outcome before it creates this
report or its JSON companion.
