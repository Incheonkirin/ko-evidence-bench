# Public Probe BEIR Export

Status: **BEIR-style retrieval subset; source routing and abstention stay in metadata**.

This export makes the synthetic public probe usable with standard IR
tooling that expects BEIR-like `corpus.jsonl`, `queries.jsonl`, and
`qrels/test.tsv` files. It does not replace the source-route scorecards:
BEIR qrels cannot represent abstention or route labels, so those fields
are preserved in `query_metadata.jsonl` and in the original probe qrels.

## Inputs

- probe dir: `probes/ko_evidence_probe_v0`
- output dir: `probes/ko_evidence_probe_v0/beir`
- label status: synthetic public fixture

## Exported Files

| file | rows | purpose |
|---|---:|---|
| `probes/ko_evidence_probe_v0/beir/corpus.jsonl` | 7 | BEIR corpus documents |
| `probes/ko_evidence_probe_v0/beir/queries.jsonl` | 13 | BEIR query rows |
| `probes/ko_evidence_probe_v0/beir/qrels/test.tsv` | 11 | answerable query-evidence labels |
| `probes/ko_evidence_probe_v0/beir/query_metadata.jsonl` | 13 | route, intent, surface, and trap metadata |

## Coverage

| item | value |
|---|---:|
| source query rows | 13 |
| source evidence rows | 7 |
| answerable qrel pairs | 11 |
| abstention rows skipped from BEIR qrels | 2 |
| validation issues | 0 |

## Skipped Abstention Qids

| qid | reason |
|---|---|
| `probe-underwriting-context` | `should_abstain=true` has no BEIR qrel equivalent |
| `probe-underwriting-messenger` | `should_abstain=true` has no BEIR qrel equivalent |

## Validation

| issue |
|---|
| none |

## Use Notes

- Treat this as a public fixture export, not a final benchmark release.
- Use `query_metadata.jsonl` when slicing by intent family, surface form, trap class, or source route.
- Use the original probe qrels for abstention and source-routing evaluation.
