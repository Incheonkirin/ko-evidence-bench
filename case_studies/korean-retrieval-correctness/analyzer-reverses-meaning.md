# When a Korean Analyzer Reverses Meaning

**Why `비급여` becoming `급여` is a relevance correctness failure, not ordinary stemming**

In Korean insurance search, `급여` means covered care while `비급여` means
non-covered care. Under the observed default nori part-of-speech filtering,
both queries produce the same remaining token:

```text
비급여  (non-covered)       -> 급여  (covered)
급여    (covered)           -> 급여  (covered)

부담보  (excluded coverage) -> 담보  (coverage)
담보    (coverage)          -> 담보  (coverage)
```

The distinction does not merely improve ranking. It determines which side of a
coverage statement the evidence supports.

![Observed analyzer outputs](figures/analyzer-outputs.svg)

## Minimal Reproduction

The checked-in synthetic analyzer calls were recorded on Elasticsearch `8.15.3`
with Lucene `9.11.1`:

| Input | Output tokens | Distinction preserved? |
|---|---|---|
| `비급여` | `급여` | No |
| `급여` | `급여` | Reference form |
| `부담보` | `담보` | No |
| `담보` | `담보` | Reference form |

The immediate cause is the default `XPN` entry in the
`nori_part_of_speech` stop-tag set. Nori can analyze the prefix separately, and
the filter then removes it. The downstream index receives only the lexical core.

## Broken Invariant

> A token-filtering optimization must not make contrastive domain concepts
> indistinguishable unless the product has explicitly chosen that equivalence.

Stop-word removal is normally justified when the removed token contributes little
to relevance. That assumption fails when the token controls polarity, exclusion,
renewal status, or another decision-bearing attribute.

Once `비급여` and `급여` share the same index representation, BM25 cannot recover
the original distinction. Dense retrieval or a reranker may rescue some examples
from surrounding context, but that is a system-level possibility, not restoration
of information in the lexical representation.

## Why Ordinary Metrics Can Miss It

A conventional relevance set may still assign partial relevance to documents
that discuss the same medical treatment, benefit, or clause family. Lexical
overlap is high, so aggregate Recall or nDCG can look reasonable even when the
result supports the opposite proposition.

The required test is contrastive:

```text
query expressing A
expected evidence supporting A
opposing evidence supporting not-A
```

The metric must ask whether opposing evidence is scored at or above expected
evidence. A generic topic-relevance label is not enough.

## System-Level Stress Result

The companion study evaluates 444 counterfactual triples derived from 37 seed
evidence pairs. Every tested system remained vulnerable to wrong-polarity
preference, although the aggregate rate differed substantially.

![Wrong-polarity preference by system](figures/polarity-stress.svg)

| System | Wrong-polarity preferred | Seed-pair bootstrap 95% CI |
|---|---:|---:|
| Analyzer-token BM25 | 53.8% | 52.3% - 55.6% |
| Lucene-style BM25 sensitivity arm | 44.4% | 42.1% - 46.4% |
| BGE-M3 dense retrieval | 29.1% | 23.6% - 34.5% |
| BGE reranker | 48.4% | 45.9% - 50.7% |

This is not a causal estimate of the `XPN` setting. The stress study measures
complete scoring systems over a broader polarity slice. Its role is to bridge the
unit-level analyzer counterexample to the system-level question that matters in
retrieval: which evidence is preferred after all ranking stages run?

The result also rules out a simple “use embeddings” conclusion. Dense retrieval
reduced the aggregate error, but did not eliminate it. The tested reranker raised
the error again on the same contrastive slice.

## Upstream Resolution

[Elasticsearch #151157](https://github.com/elastic/elasticsearch/pull/151157)
added an explicit warning to the official nori documentation and documented two
configuration remedies.

### 1. Preserve known compounds with a user dictionary

`user_dictionary_rules` can keep high-risk domain terms as complete noun tokens.
This is narrow and auditable, but requires a maintained inventory and regression
coverage for the terms the product depends on.

### 2. Retain `XPN` with custom stop tags

A custom `stoptags` list can omit `XPN`, preserving prefixes broadly. This avoids
silently deleting unseen prefix forms, but may add noisy prefix tokens elsewhere.

There is no universally correct global setting. Changing the default would alter
existing index semantics, so the merged contribution correctly exposes the risk
and the available controls rather than imposing one domain's decision on every
Elasticsearch user.

## Evaluation Protocol

A production regression should include at least four checks:

1. **Analyzer distinction:** contrastive terms do not collapse to identical token
   sequences without an explicit mapping.
2. **Retrieval direction:** expected evidence outranks opposing evidence for each
   polarity direction.
3. **Rescue:** the selected analyzer or dictionary improves the target slice.
4. **Regression:** broader prefix retention does not materially damage unrelated
   queries.

The fourth check matters. A dictionary that rescues known insurance terms and a
global `XPN` change have different blast radii even when both fix the minimal
example.

## Evidence And Scope

- [Synthetic analyzer observations](evidence/local-observations.json)
- [Aggregate polarity stress report](../../reports/private_polarity_stress_pilot.md)
- [Generated evidence summary](evidence/SUMMARY.md)
- [Merged upstream documentation](https://github.com/elastic/elasticsearch/pull/151157)
- [Umbrella representation-correctness case study](README.md)

The public artifact contains no source queries or passages. The 444 triples are
counterfactual variants clustered by 37 seed pairs, not 444 independent documents
and not an estimate of production prevalence.

## Takeaway

> Topic relevance is insufficient when the removed token determines whether the
> evidence supports or contradicts the query.
