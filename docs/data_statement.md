# Data Statement

This repository contains no raw private user data.

## Private Sources Not Redistributed

- Korean community crawls.
- Messenger conversation exports.
- Community Q&A archive rows.
- Copyrighted policy clause corpora.

These materials stay inside the private lab. Public files use aggregate counts,
metric tables, and synthetic fixtures.

## Public Fixture Policy

Fixtures should be:

- Synthetic or public-domain/public-disclosure excerpts with redistribution
  rights checked.
- Free of personally identifying information.
- Free of platform-owned copied community text.
- Small enough to make metric behavior transparent.

## Public Probe Release Policy

Public probes are released as synthetic queries, intent-level qrels, and
synthetic evidence snippets. They are grounded by private aggregate
distributions, but they are not copied from private rows.

Before publication, probe packages should pass:

- Schema checks for query/qrel/evidence joins.
- Synthetic provenance checks.
- PII and private-source indicator scans.
- Long n-gram overlap checks against private source references kept outside
  this repository.

## Report Policy

Public reports may include aggregate counts, confidence intervals, metric
tables, and synthetic minimal examples. They should not include raw community
posts, messenger messages, or verbatim private-row examples.
