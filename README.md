# ko-evidence-bench

**Do Korean retrieval systems find citable evidence, or only plausible text?**

Real insurance questions are written in consumer language, while answerable
evidence lives in clause language, official guidance, and product-specific
documents. `ko-evidence-bench` measures the gap: clause recovery, semantic
polarity preservation, surface-form robustness, evidence sufficiency, source
routing, and abstention.

The project is a public measurement companion to a private retrieval lab. The
lab holds raw crawls and copyrighted documents; this repository publishes the
evaluation code, synthetic probes, qid-only run contracts, and aggregate-only
results.

<!-- BEGIN: current-verified-signals -->
## Measured v0.1 Signals

| Finding | Measured result |
|---|---:|
| Clause retrieval | 544 silver qrels; best checked-in `clause@20` 64.9% with bootstrap CIs |
| Polarity preservation | 444 contrastive triples; dense wrong-polarity 29.1%; reranker wrong-polarity 48.4% |
| Scope | Retrieval and polarity are aggregate silver studies; human-validated source routing and answer quality are deliberately reported separately |

The result reports state exactly what each number measures and retain the
public/private boundary; they do not release user text or copyrighted evidence.
<!-- END: current-verified-signals -->

## Upstream Correctness: Where Retrieval Fails Before Ranking

Three merged Apache Lucene and Elasticsearch contributions trace Korean search
failures across the full lexical representation path:

| Boundary | Merged contribution | Failure made observable |
|---|---|---|
| Unicode -> tokenizer | [Lucene #16242](https://github.com/apache/lucene/pull/16242) | Canonically equivalent NFD/NFC Hangul received different Korean analysis. |
| Morphology -> filtered tokens | [Elasticsearch #151157](https://github.com/elastic/elasticsearch/pull/151157) | The default `XPN` stop tag could collapse `비급여` into `급여`. |
| Token graph -> phrase query | [Elasticsearch #152931](https://github.com/elastic/elasticsearch/pull/152931) | An exact Korean source phrase returned zero hits at `slop=0`. |

The [full correctness case study](case_studies/korean-retrieval-correctness/README.md)
connects each upstream invariant and regression to the 444-triple system-level
polarity stress measurement. Its summary, PR manifest, observations, and SVGs are
generated from checked-in synthetic or aggregate evidence.

## Results

### 1. Cross-reranking improves clause recovery, but it does not solve robustness

On `n=544` private silver qrels, cross-text reranking raised `clause@20` from
`56.4%` to `64.9%` (`+8.5` percentage points; paired bootstrap 95% CI
`+5.9` to `+11.2`). The worst surface slice still reached only `44.4%`.

| system | `clause@20` | 95% CI |
|---|---:|---:|
| `structural_pack` | 56.4% | 52.4% - 60.5% |
| `structural_cross_text` | 64.9% | 60.8% - 68.8% |

See [the aggregate retrieval scorecard](reports/private_544_full_cross_scorecard.md)
and [the surface breakdown](reports/private_runtime_surface_scorecard_silver.md).

### 2. Better semantic retrieval can still reverse the answer

The polarity stress study uses `444` counterfactual triples derived from `37`
seed evidence pairs. It asks whether a system scores opposite-polarity evidence
at or above the expected evidence. Lower is better.

| system | wrong-polarity preferred | seed-pair bootstrap 95% CI |
|---|---:|---:|
| analyzer-token BM25 | 53.8% | 52.3% - 55.6% |
| Lucene-style BM25 sensitivity arm | 44.4% | 42.1% - 46.4% |
| `BAAI/bge-m3` | 29.1% | 23.6% - 34.5% |
| `BAAI/bge-reranker-v2-m3` | 48.4% | 45.9% - 50.7% |

The result is intentionally more specific than generic retrieval recall: a
model can retrieve relevant-looking text and still prefer the opposite claim.
Read [the stress report](reports/private_polarity_stress_pilot.md) and inspect
[the aggregate-only regeneration script](scripts/reproduce_private_polarity_stress.py).

### 3. Community posts and live chat are different retrieval inputs

| private substrate | usable rows | median characters | short messages | long contexts |
|---|---:|---:|---:|---:|
| community post context | 165,970 | 169.0 | 6.1% | 44.3% |
| messenger conversation | 7,796 | 17.0 | 80.6% | 2.0% |
| cleaned search evaluation query | 544 | 22.0 | 94.5% | 0.0% |

Community data maps demand and supplies qrel candidates. Messenger turns are a
separate live-query stress condition: short, fragmented, and often dependent on
missing context. The [substrate profile](reports/private_query_substrate_profile.md)
keeps those roles distinct rather than treating every text record as a search
query.

## What The Scorecard Measures

| metric | question |
|---|---|
| `clause@k`, `exact@k` | Did the run recover the expected evidence unit? |
| `evidence_hit@k` | Did top-k find any acceptable evidence? |
| `evidence_coverage@k` | How much of the required evidence set did top-k recover? |
| `evidence_sufficiency@k` | Did top-k recover every required evidence unit? |
| `wrong_source_rate@k` | Did the run surface evidence from a disallowed tier? |
| abstention precision / recall | Did the system stop when the available evidence was insufficient? |
| surface spread | Does the same intent behave differently across formal, colloquial, abbreviated, and messenger-style queries? |

The evidence schema distinguishes a plausible single hit from a sufficient set
of evidence. For example, a coverage clause alone should not pass a question
that also needs a limit or exclusion. See [the schema](docs/schemas.md).

## Run It

The checked-in public probe is synthetic and privacy-screened. It exercises the
same scorecard semantics without pretending to reproduce private model quality.

```bash
make test
make reproduce-table-1
make reproduce-surface-scorecard
```

For a clean-room verification path:

```bash
make verify
```

### Containerized demo

```bash
make docker-demo
```

`make docker-demo` builds the local image and runs tests, public fixtures,
generated-report checks, and the public-safety scan without requiring private
data or external services.

## Private-Run Contract

Real analyzer, dense, hybrid, and reranker runs enter through a qid-only bundle.
Each external run records the runner commit, corpus fingerprint, qrel fingerprint,
engine, model revision, and timestamp; the public artifact contains no queries,
passages, source names, URLs, or user identifiers.

```bash
python3 scripts/validate_system_matrix_bundle.py \
  --bundle-dir /path/to/private_bundle \
  --qrels /path/to/private_qrels.jsonl \
  --matrix docs/system_matrix.json \
  --out reports/private_system_matrix_bundle.md
```

The [run-bundle contract](reports/system_matrix_bundle_fixture.md) and
[submission template](fixtures/system_matrix_submission_template/README.md)
show the exact shape. A fixture is explicitly tagged as a fixture; it cannot be
mistaken for a model run.

## Repository Map

```text
ko_evidence_bench/   reference metrics, schemas, surface and run-bundle validation
scripts/             result reproduction, aggregate export, and safety checks
probes/              synthetic public probe set and BEIR-style export
fixtures/            executable public examples
reports/             aggregate study results and reproducible diagnostic reports
case_studies/        upstream investigations connected to system-level evaluation
docs/                metric, schema, privacy, and data-boundary notes
```

The core public artifact is [the v0 measurement study](reports/measurement_study_v0.md).
The [data statement](docs/data_statement.md) describes the public/private
boundary and the one-corpus scope.

## Scope

The measured retrieval results come from one private Korean insurance evidence
corpus. The aggregate qrels are silver diagnostics, not a claim of human-gold
answer quality or universal Korean retrieval performance. Human-validated source
routing and answer-quality evaluation remain separate workstreams. That scope is
why the repository reports retrieval lift and polarity failure directly while it
does not inflate them into a generic chatbot or dictionary claim.

## Contributing

Contributions are welcome for metric definitions, query-variant probes, run
adapters, and reproducible retrieval diagnostics. Do not submit raw user text,
copyrighted evidence, source-specific platform identifiers, or a term dictionary.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the contribution boundary.
