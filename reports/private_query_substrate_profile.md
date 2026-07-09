# Private Query Substrate Profile

This report compares query substrates using aggregate text-shape and
intent-signal features only. It does not include qids, raw queries,
conversation snippets, platform identifiers, usernames, URLs, or source
file paths.

The goal is to decide which real-query cohorts deserve separate stress
slices in the retrieval benchmark, not to build a synonym dictionary.

## Inputs

- input rows: 174434
- usable rows after length filtering: 174310
- label status: aggregate private substrate diagnostic
- minimum characters: 2

## Cohort Shape Summary

| cohort | input rows | usable rows | usable share | avg chars | median chars | p90 chars | short messages | long contexts | question-like |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `community_post_context` | 165970 | 165970 | 100.0% | 835.5 | 169.0 | 1730.0 | 6.1% | 44.3% | 80.2% |
| `messenger_conversation` | 7920 | 7796 | 98.4% | 36.8 | 17.0 | 95.0 | 80.6% | 2.0% | 16.8% |
| `search_eval_query` | 544 | 544 | 100.0% | 23.7 | 22.0 | 35.0 | 94.5% | 0.0% | 41.4% |

## Retrieval Stress Signals

| cohort | numeric constraints | negation/exclusion | bundled coverage | underwriting | refund/termination | claims process | dispute/complaint | colloquial/abbrev | formal register | messenger-style |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `community_post_context` | 65.1% | 54.2% | 11.3% | 38.3% | 27.9% | 20.7% | 6.3% | 26.8% | 26.6% | 14.2% |
| `messenger_conversation` | 13.9% | 19.0% | 4.5% | 8.6% | 3.5% | 5.8% | 0.6% | 3.9% | 5.8% | 14.6% |
| `search_eval_query` | 14.2% | 10.3% | 21.3% | 21.0% | 12.3% | 16.2% | 1.3% | 12.3% | 14.2% | 41.4% |

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
