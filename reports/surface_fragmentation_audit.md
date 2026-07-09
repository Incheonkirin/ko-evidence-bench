# Surface Fragmentation Audit

Status: **public fixture diagnostic; not a production synonym list**.

This report tests the failure mode behind naive query-log counting:
one exact lexical seed can miss other surface forms of the same intent.
The checked qrels define intent membership; the surface rules only measure
how much seed-only counting misses.

## Inputs

- queries: `probes/ko_evidence_probe_v0/queries.jsonl`
- qrels: `probes/ko_evidence_probe_v0/qrels.jsonl`
- audited intents: 4
- qrel rows in audited intents: 9
- label status: synthetic public fixture

## Summary

| item | value |
|---|---:|
| qrel intent rows | 9 |
| exact-seed rows | 4 |
| expanded-surface rows | 9 |
| exact-seed recall | 44.4% |
| expanded-surface recall | 100.0% |
| aggregate undercount factor | 2.2x |
| max per-intent undercount factor | 3.0x |

## Per-Intent Audit

| intent | seed condition | qrel rows | seed rows | expanded rows | seed recall | undercount | missed surfaces |
|---|---|---:|---:|---:|---:|---:|---|
| `cancer_brain_heart_bundle` | formal component listing only | 3 | 1 | 3 | 33.3% | 3.0x | `abbreviated:1`, `messenger_shorthand:1` |
| `indemnity_noncovered_treatment` | formal product term only | 2 | 1 | 2 | 50.0% | 2.0x | `colloquial:1` |
| `refund_termination` | formal refund calculation wording only | 2 | 1 | 2 | 50.0% | 2.0x | `messenger_shorthand:1` |
| `underwriting_context_needed` | formal underwriting wording only | 2 | 1 | 2 | 50.0% | 2.0x | `messenger_shorthand:1` |

## Missed Rows By Intent

| intent | missed by exact seed | missed by expanded rule |
|---|---|---|
| `cancer_brain_heart_bundle` | `probe-bundle-abbrev`, `probe-bundle-messenger` | none |
| `indemnity_noncovered_treatment` | `probe-indemnity-colloquial` | none |
| `refund_termination` | `probe-refund-messenger` | none |
| `underwriting_context_needed` | `probe-underwriting-messenger` | none |

## Surface Distribution

| surface form | qrel rows | missed by exact seed |
|---|---:|---:|
| `abbreviated` | 1 | 1 |
| `colloquial` | 2 | 1 |
| `formal` | 3 | 0 |
| `messenger_shorthand` | 3 | 3 |

## Use Notes

- This is an audit of counting bias, not a query rewrite system.
- Expanded-surface rules are evaluated against qrels; they are not shipped as production synonyms.
- Private query logs can reuse the same report shape with qid-only outputs and aggregate surface counts.
