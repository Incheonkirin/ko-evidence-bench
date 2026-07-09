# Answer Agreement Workflow Fixture

Status: **PASS synthetic answer-quality agreement rehearsal**.

This fixture rehearses independent answer-quality label agreement on
synthetic rows. It validates two reviewer payloads and summarizes raw
agreement plus Cohen's kappa without exposing qids, raw queries, answers,
evidence text, audit ids, or reviewer notes. It is not human-gold evidence.

## Gate Summary

| gate | evidence | status |
|---|---:|---|
| reviewer A validation errors | 0 | `PASS` |
| reviewer B validation errors | 0 | `PASS` |
| paired completed rows | 10 | `PASS` |
| raw agreement | 80.0% | `PASS` |
| Cohen's kappa | 0.733 | `PASS` |
| disagreement rows | 2 | `PASS` |

## Agreement Summary

| item | value |
|---|---:|
| paired rows | 10 |
| raw agreement | 80.0% |
| Cohen's kappa | 0.733 |
| disagreement rows | 2 |

## Use Notes

- The checked-in fixture intentionally includes synthetic disagreements.
- Real private review must use independent reviewer labels before reporting inter-annotator agreement.
- Agreement is necessary but not sufficient; adjudication and qid-only promotion still gate headline claims.
