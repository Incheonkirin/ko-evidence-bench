# Query Substrate Profile Fixture

This report compares query substrates using aggregate text-shape and
intent-signal features only. It does not include qids, raw queries,
conversation snippets, platform identifiers, usernames, URLs, or source
file paths.

The goal is to decide which real-query cohorts deserve separate stress
slices in the retrieval benchmark, not to build a synonym dictionary.

## Inputs

- input rows: 10
- usable rows after length filtering: 10
- label status: synthetic query-substrate fixture
- minimum characters: 2

## Cohort Shape Summary

| cohort | input rows | usable rows | usable share | avg chars | median chars | p90 chars | short messages | long contexts | question-like |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `community_post` | 4 | 4 | 100.0% | 100.0 | 96.5 | 118.0 | 0.0% | 0.0% | 50.0% |
| `messenger_turn` | 6 | 6 | 100.0% | 14.8 | 14.5 | 16.0 | 100.0% | 0.0% | 100.0% |

## Retrieval Stress Signals

| cohort | numeric constraints | negation/exclusion | bundled coverage | underwriting | refund/termination | claims process | dispute/complaint | colloquial/abbrev | formal register | messenger-style |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `community_post` | 50.0% | 25.0% | 25.0% | 25.0% | 25.0% | 50.0% | 25.0% | 25.0% | 75.0% | 0.0% |
| `messenger_turn` | 0.0% | 50.0% | 16.7% | 33.3% | 16.7% | 33.3% | 0.0% | 33.3% | 16.7% | 100.0% |

## Interpretation Guide

- High `short messages` and `messenger-style` rates mean live-query stress
  should include short, underspecified turns rather than only long posts.
- High `long contexts` means the cohort is better treated as query
  extraction plus retrieval, not a direct search-box query.
- High `negation/exclusion`, `numeric constraints`, or `bundled coverage`
  rates mark slices where surface normalization and source routing should
  be evaluated separately from plain clause recall.
- This report is a substrate diagnostic. It does not create labels and it
  does not promote any private metric to a public benchmark claim.
