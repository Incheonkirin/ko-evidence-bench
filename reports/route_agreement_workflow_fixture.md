# Route Agreement Workflow Fixture

Status: **PASS synthetic source-route agreement rehearsal**.

This fixture rehearses independent source-route label agreement on
synthetic rows. It validates two reviewer payloads and summarizes raw
agreement plus Cohen's kappa without exposing qids, raw queries, context,
source names, audit ids, or reviewer notes. It is not human-gold evidence.

## Gate Summary

| gate | evidence | status |
|---|---:|---|
| reviewer A validation errors | 0 | `PASS` |
| reviewer B validation errors | 0 | `PASS` |
| paired completed rows | 3 | `PASS` |
| raw agreement | 66.7% | `PASS` |
| Cohen's kappa | 0.571 | `PASS` |
| disagreement rows | 1 | `PASS` |

## Agreement Summary

| item | value |
|---|---:|
| paired rows | 3 |
| raw agreement | 66.7% |
| Cohen's kappa | 0.571 |
| disagreement rows | 1 |

## Use Notes

- The checked-in fixture intentionally includes a synthetic source-route disagreement.
- Real private review must use independent reviewer labels before reporting inter-annotator agreement.
- Agreement is necessary but not sufficient; adjudication and qid-only promotion still gate headline claims.
