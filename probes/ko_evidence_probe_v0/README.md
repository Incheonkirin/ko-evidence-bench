# Ko Evidence Probe v0

Status: synthetic public probe set.

This package is the public, rights-safe instrument for the fixture
reproductions. It is not a release of private logs, community posts,
conversation messages, or policy corpora.

## Files

- `queries.jsonl`: synthetic Korean user questions with intent and surface-form
  metadata.
- `qrels.jsonl`: intent-level source-route labels and sufficient evidence ids.
- `evidence.jsonl`: synthetic evidence snippets grouped by source tier.
- `DATASET_CARD.md`: generated release-facing card with row counts,
  distributions, intended use, non-goals, and privacy notes.
- `beir/`: BEIR-style retrieval subset exported from the same probe rows.

## Design

Each intent appears in multiple surface conditions where possible. The goal is
to test whether a retrieval or routing system remains stable across formal,
colloquial, abbreviated, and messenger-style phrasings of the same information
need.

## Screening

Run:

```bash
make check-probe-privacy
```

The screen validates schema consistency, qid/evidence joins, source-tier values,
synthetic provenance, common PII patterns, private-source indicators, and
long n-gram overlap against a synthetic source-reference fixture. Private labs
can run the same script with private reference files outside this repo.

## Dataset Card

Run:

```bash
make build-probe-dataset-card
```

The generated `DATASET_CARD.md` is a release-control artifact. It describes
what the probe is for, what it should not be used for, and how the public files
fit together. It is not a human-gold benchmark claim and not a synonym
dictionary.

## BEIR-Style Export

Run:

```bash
make export-probe-beir
```

The export writes `beir/corpus.jsonl`, `beir/queries.jsonl`,
`beir/qrels/test.tsv`, and `beir/query_metadata.jsonl`. It is a standard
retrieval subset for answerable rows only; source-route and abstention labels
remain in `qrels.jsonl` and `query_metadata.jsonl`.
