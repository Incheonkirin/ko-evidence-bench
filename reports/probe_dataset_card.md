# Probe Dataset Card Report

Status: **dataset card generated from public probe files**.

This report checks that the public probe has a reusable release-facing
dataset card. The card is generated from checked-in JSONL files so row
counts, surface distributions, route labels, and abstention counts cannot
drift silently.

## Outputs

- dataset card: `probes/ko_evidence_probe_v0/DATASET_CARD.md`
- probe dir: `probes/ko_evidence_probe_v0`

## Inventory

| item | count |
|---|---:|
| queries | 13 |
| qrels | 13 |
| evidence snippets | 7 |
| answerable qrels | 11 |
| abstention qrels | 2 |
| intent families | 7 |
| surface forms | 4 |

## Use Notes

- The dataset card is a release-control artifact, not a benchmark result.
- It should stay synchronized with `queries.jsonl`, `qrels.jsonl`,
  `evidence.jsonl`, and the BEIR-style export.
- It repeats the public/private boundary so the probe is not mistaken
  for released private data.
