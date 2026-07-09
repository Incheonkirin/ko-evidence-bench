# Probe Privacy Report

Status: **PASS**.

This report validates the public synthetic probe package before it is used
as a released evaluation instrument. It checks schema joins, synthetic
provenance, common PII patterns, private-source indicators, and long
n-gram overlap against configured reference material.

## Inputs

- probe dir: `probes/ko_evidence_probe_v0`
- query rows: 13
- qrel rows: 13
- evidence rows: 7
- reference files: 1

## Coverage

| item | value |
|---|---:|
| intents | 8 |
| surface forms | 4 |
| source routes | 7 |
| text fields scanned | 279 |
| max reference n-gram overlap | 0 |

## Failures

- none

## Use Notes

- `PASS` means the public probe package is safe to commit under the
  repository's synthetic-fixture policy.
- This does not prove the private-lab benchmark is human-gold.
- Private runs should pass additional reference files from raw private
  sources that remain outside this repository.
