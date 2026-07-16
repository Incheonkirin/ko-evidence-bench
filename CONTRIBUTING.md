# Contributing

`korean-search-correctness` accepts contributions that make Korean evidence retrieval
easier to measure and reproduce.

Good contribution surfaces:

- scorecard metrics and bootstrap methods;
- synthetic or public-rights-cleared probe sets;
- analyzer, retriever, reranker, and run-bundle adapters;
- regression tests for evidence sufficiency, polarity, numeric constraints, or
  surface-form robustness;
- documentation that makes a result easier to audit.

Before opening a pull request, run:

```bash
make test
make verify
```

## Data Boundary

Do not add raw user messages, community text, copyrighted evidence passages,
source-specific platform identifiers, URLs, usernames, or query-to-user joins.
Public probes must be synthetic or independently rights-cleared and must pass
the repository privacy screen.

Run exports must remain qid-only. For an external system run, include its
runner commit, corpus/qrel fingerprints, engine, model revision, and timestamp
in the bundle provenance rather than adding raw text to a report.

## Probe Design

A probe should express an information need and an observable retrieval property.
Use equivalence variants when several phrasings should retrieve the same
evidence; use contrast variants when two meanings must not rank alike. A new
probe needs a qrel, a small synthetic evidence set, an expected metric outcome,
and a test that would fail if the behavior regresses.
