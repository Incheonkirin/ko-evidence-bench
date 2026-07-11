# Generated Evidence Summary

This file is generated from checked-in synthetic or aggregate evidence by
`scripts/build_upstream_correctness_case_study.py`. It is not a general Korean
retrieval benchmark.

## Upstream Record

| Contribution | Type | Merge commit | Merged |
|---|---|---|---|
| `apache/lucene#16242` | implementation | `401c65501c0c` | 2026-06-29 |
| `elastic/elasticsearch#151157` | documentation and configuration guidance | `d666a6fc805c` | 2026-06-15 |
| `elastic/elasticsearch#152931` | implementation | `663c818c1f33` | 2026-07-10 |

## Local Boundary Observations

Runtime: Elasticsearch `8.15.3`, Lucene `9.11.1`.

| Probe | Observed result |
|---|---|
| XPN polarity | `비급여` -> `급여`; `급여` -> `급여` |
| XPN polarity | `부담보` -> `담보`; `담보` -> `담보` |
| Hangul canonical form | NFC -> `보험계약 / 보험 / 계약 / 대출 / 율`; NFD -> one jamo-sequence token |
| Graph phrase | `match`=1, `match_phrase(slop=0)`=0, `match_phrase(slop=1)`=1 |

## System-Level Polarity Stress

Metric: opposite-polarity evidence scores at or above expected evidence. The
study contains `444` counterfactual triples
derived from `37` seed evidence pairs.

| System | Wrong-polarity preferred | Seed-pair bootstrap 95% CI |
|---|---:|---:|
| Analyzer-token BM25 | 53.8% | 52.3% - 55.6% |
| Lucene-style BM25 sensitivity arm | 44.4% | 42.1% - 46.4% |
| BGE-M3 dense retrieval | 29.1% | 23.6% - 34.5% |
| BGE reranker | 48.4% | 45.9% - 50.7% |

## Scope

- No queries, passages, source names, URLs, usernames, or stable row identifiers
  are exported by this case study.
- Analyzer inputs and the phrase fixture are synthetic.
- The phrase chart records pre-fix behavior on Elasticsearch
  `8.15.3`. Post-fix behavior is supported by the merged
  upstream regression tests, not a patched local runtime in this artifact.
- The polarity rates are stress measurements, not production prevalence estimates
  or an end-to-end human-relevance benchmark.
