# Measurement Study v0: Citable Korean Evidence Retrieval

## Question

When users ask insurance questions in consumer language, can a retrieval stack
recover the evidence needed to support an answer, preserve semantic direction,
and expose cases that need more context rather than a plausible-looking clause?

This repository is the public measurement layer for that question. It does not
publish raw user text or the underlying evidence corpus. It publishes aggregate
results, scorecard code, synthetic probes, and run contracts.

## Substrate

| asset | measured size | role in the study |
|---|---:|---|
| clause evidence corpus | 36,983 passages from 111 products | retrieval and reranking target |
| community-derived query candidates | 165,970 | demand distribution and qrel-candidate source |
| meaningful messenger messages | 7,324 | short-turn and context-loss stress source |
| community Q&A archive | 56,293 | expert-language and source-routing analysis |
| evaluated retrieval qrels | 544 silver rows | aggregate retrieval diagnostics |

The community and messenger collections are not interchangeable. Community
posts are often long contexts that need query extraction; messenger turns are
short and underspecified. The [aggregate substrate profile](private_query_substrate_profile.md)
shows the distribution shift without exposing a row of source text.

## Finding 1: Cross-Text Reranking Has a Measurable Retrieval Lift

On the same `n=544` silver retrieval set, `structural_cross_text` improves
`clause@20` over `structural_pack` by `+8.5` percentage points. The paired
bootstrap interval excludes zero.

| system | `clause@20` | 95% CI | paired delta vs. pack | paired 95% CI |
|---|---:|---:|---:|---:|
| `structural_pack` | 56.4% | 52.4% - 60.5% | - | - |
| `structural_cross_text` | 64.9% | 60.8% - 68.8% | +8.5%p | +5.9%p - +11.2%p |

This is a systems result: a candidate-pack-only path is not the same as a
cross-text reranked path. The worst observed surface slice reaches `44.4%`, so
the aggregate lift is not a robustness guarantee.

Sources: [aggregate scorecard](private_544_full_cross_scorecard.md) and
[runtime surface scorecard](private_runtime_surface_scorecard_silver.md).

## Finding 2: Semantic Direction Is a Separate Failure Mode

The polarity experiment gives a query an expected evidence snippet and an
opposite-polarity snippet. It measures whether the wrong side scores at or
above the expected side. The `444` counterfactual triples come from `37` seed
evidence pairs, so confidence intervals resample seed pairs rather than
pretending every derived triple is independent.

| system | wrong-polarity preferred | seed-pair bootstrap 95% CI |
|---|---:|---:|
| analyzer-token BM25 | 53.8% | 52.3% - 55.6% |
| Lucene-style BM25 sensitivity arm | 44.4% | 42.1% - 46.4% |
| `BAAI/bge-m3` | 29.1% | 23.6% - 34.5% |
| `BAAI/bge-reranker-v2-m3` | 48.4% | 45.9% - 50.7% |

Dense retrieval reduces the overall error rate in this slice, but neither dense
retrieval nor reranking makes polarity safe by default. This is why the project
uses contrastive stress probes in addition to `clause@k`.

Sources: [polarity stress report](private_polarity_stress_pilot.md) and
[aggregate JSON](private_polarity_stress_pilot.json).

## Finding 3: Input Shape Changes the Evaluation Problem

| cohort | usable rows | median characters | short messages | long contexts |
|---|---:|---:|---:|---:|
| community post context | 165,970 | 169.0 | 6.1% | 44.3% |
| messenger conversation | 7,796 | 17.0 | 80.6% | 2.0% |
| cleaned search evaluation query | 544 | 22.0 | 94.5% | 0.0% |

A long post, a short messenger turn, and a cleaned retrieval query have
different failure modes. The study therefore organizes evaluation by
information need and surface condition, not by one undifferentiated corpus.

## Implementation Contribution

The public code makes the measurements executable rather than reporting them
as static prose:

- `score_run()` separates any evidence hit, required-evidence coverage, and
  true multi-evidence sufficiency.
- `clustered_bootstrap_hit_ci()` preserves seed-pair dependence for
  counterfactual stress grids.
- `reproduce_private_polarity_stress.py` projects private row exports into
  aggregate-only reports and does not serialize raw-text fields.
- Qid-only system bundles retain runner, corpus, qrel, engine, and model
  provenance without shipping private inputs.
- Synthetic public probes exercise the same metric and schema behavior in a
  clean-room environment.

## Scope

This is a deep single-corpus study, not a claim about every Korean retrieval
system. The 544-row retrieval labels are silver; they establish a measured
retrieval and stress-testing baseline, not human-validated answer quality.
Source routing and answer sufficiency have their own evaluation contracts and
will only be promoted with independently reviewed labels and a populated
multi-source corpus.

## Reproduce

```bash
make test
make reproduce-table-1
make reproduce-surface-scorecard
make verify
```

The public commands use synthetic fixtures. A private operator can reproduce
the polarity aggregate from local row exports with
`scripts/reproduce_private_polarity_stress.py`, then validate external system
runs through `scripts/validate_system_matrix_bundle.py` before publishing a
qid-only aggregate result.
