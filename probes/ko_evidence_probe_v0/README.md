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
