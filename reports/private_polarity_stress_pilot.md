# Polarity Stress Pilot

Status: **aggregate-only private-lab pilot; not full matrix evidence**.

This report summarizes a private counterfactual retrieval pilot without raw
queries, evidence snippets, file paths, source names, or stable row ids. Each
row pairs one query with two candidate evidence snippets: the expected evidence
and an opposite-polarity evidence snippet. The metric is whether the system
scores the opposite-polarity snippet at or above the expected snippet.

## Summary

| item | value |
|---|---:|
| contrastive triples | 444 |
| seed evidence pairs | 37 |
| unique evidence snippets embedded | 63 |
| metric | wrong-polarity evidence preferred |

## System Results

| system | rows | wrong-preferred rows | wrong-preferred rate | 95% CI | intent asymmetry |
|---|---:|---:|---:|---:|---|
| `bm25_analyzer_tokens` | 444 | 239 | 53.8% | 49.2% - 58.4% | coverage 20.3%; exclusion 87.4% |
| `bm25_lucene_idf_sensitivity` | 444 | 197 | 44.4% | 39.8% - 49.0% | coverage 78.4%; exclusion 10.4% |
| `dense_multilingual_encoder` | 444 | 129 | 29.1% | 25.0% - 33.4% | coverage 51.4%; exclusion 6.8% |
| `cross_encoder_reranker` | 444 | 215 | 48.4% | 43.8% - 53.1% | coverage 89.6%; exclusion 7.2% |

## Interpretation

The pilot checks a sharper question than ordinary clause recall: when two
snippets differ by coverage polarity, does the ranker keep the direction of the
user intent? The answer is not solved by moving from lexical retrieval to
semantic retrieval. The multilingual dense encoder reduces the overall
wrong-polarity rate, but it still prefers the wrong side for 29.1% of
contrastive triples. The cross-encoder reranker is also brittle on this pilot,
with strong intent-side asymmetry.

This is a pilot slice, not the 22-system matrix and not a human-gold benchmark.
It is useful evidence for why the benchmark keeps polarity, abstention, and
source-route metrics separate from plain top-k hit metrics.
