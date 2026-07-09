# Ko Evidence Probe v0 Dataset Card

Status: **synthetic public fixture; not a private benchmark release**.

## Summary

Ko Evidence Probe v0 is a small Korean evidence-retrieval probe for
source routing, abstention, and surface-form robustness. It is designed
to make the evaluation protocol reusable without releasing private
community crawls, messenger exports, community Q&A rows, or copyrighted
policy corpora.

The probe is intentionally small. Its job is to exercise the public
schema, privacy screen, BEIR-style export, and diagnostic scorecards.
It should not be cited as a production benchmark or as evidence about
all Korean retrieval systems.

## Files

- probe directory: `probes/ko_evidence_probe_v0`
- `queries.jsonl`: synthetic Korean query variants with intent and surface metadata.
- `qrels.jsonl`: source-route labels, abstention labels, and sufficient evidence ids.
- `evidence.jsonl`: synthetic evidence snippets by source tier.
- `beir/`: answerable-only BEIR-style subset at `probes/ko_evidence_probe_v0/beir`.

## Size

| item | count |
|---|---:|
| queries | 13 |
| qrels | 13 |
| evidence snippets | 7 |
| answerable qrels | 11 |
| abstention qrels | 2 |
| sufficient query-evidence pairs | 11 |
| intent families | 7 |
| intent ids | 8 |
| surface forms | 4 |

## Intended Use

- Regression-test source-aware retrieval metrics.
- Check whether one intent remains retrievable across formal, colloquial,
  abbreviated, and messenger-style surface forms.
- Exercise BEIR-style retrieval tooling on answerable rows while keeping
  route and abstention metadata available for richer diagnostics.
- Demonstrate privacy-preserving release mechanics for a larger private
  Korean search-lab workflow.

## Not Intended Use

- Do not treat this as a human-gold benchmark.
- Do not use it to claim broad Korean IR model quality.
- Do not use it as an insurance advice dataset.
- Do not read the surface metadata as a synonym dictionary or rewrite product.

## Labels

Each query has an `intent_family`, `intent_id`, `surface_form`, and
`trap_classes` annotation. Qrels add `route_gold`,
`allowed_source_tiers`, `should_abstain`, and
`sufficient_evidence_ids`. BEIR qrels contain answerable rows only;
abstention, route, surface, and trap metadata remain in
`query_metadata.jsonl` and the original qrels.

## Intent-Family Distribution

| value | rows |
|---|---:|
| `bundled_coverage` | 3 |
| `underwriting_context` | 3 |
| `indemnity_noncovered` | 2 |
| `refund_termination` | 2 |
| `claims_process` | 1 |
| `dispute_complaint` | 1 |
| `product_design` | 1 |

## Surface-Form Distribution

| value | rows |
|---|---:|
| `formal` | 7 |
| `messenger_shorthand` | 3 |
| `colloquial` | 2 |
| `abbreviated` | 1 |

## Route Distribution

| value | rows |
|---|---:|
| `policy_clause` | 5 |
| `human_context_needed` | 2 |
| `product_disclosure` | 2 |
| `claims_faq` | 1 |
| `dispute_case` | 1 |
| `expert_answer` | 1 |
| `official_consumer_info` | 1 |

## Trap-Class Distribution

| value | rows |
|---|---:|
| `bundle_expansion` | 3 |
| `messenger_shorthand` | 3 |
| `source_routing` | 3 |
| `needs_private_context` | 2 |
| `negation_or_exclusion` | 2 |
| `product_table` | 2 |
| `register_mismatch` | 2 |
| `abbreviation` | 1 |

## Privacy And Provenance

All rows use `provenance = synthetic_public_fixture`. The probe is built
from synthetic Korean examples and synthetic evidence snippets. It is
screened by `make check-probe-privacy` for schema joins, source-tier
validity, PII-like patterns, private-source indicators, and long
n-gram overlap against configured reference material.

## Evaluation Hooks

- `make reproduce-probe-system-comparison` runs lexical, surface-expanded,
  semantic-centroid, hybrid, and source-route-aware systems.
- `make reproduce-probe-trap-mining` checks diagnostic trap mining.
- `make reproduce-surface-fragmentation-audit` measures lexical seed
  undercounting across surface variants.
- `make export-probe-beir` regenerates the BEIR-style retrieval subset.

## Release Notes

- License: repository license.
- Language: Korean query text with English synthetic evidence summaries.
- Domain: insurance evidence retrieval as a first testbed.
- Claim status: fixture only; human-gold headline claims remain blocked
  until independent labels and the full comparison matrix are complete.
