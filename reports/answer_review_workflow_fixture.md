# Answer Review Workflow Fixture

Status: **PASS synthetic answer-quality CSV workflow rehearsal**.

This fixture rehearses the private answer-quality review path: export a
reviewer CSV, fill labels, validate the CSV, import labels, validate the
audit pack, and promote qid-only labels. It is not human-gold evidence
and not a final benchmark claim.

## Gate Summary

| gate | evidence | status |
|---|---:|---|
| exported CSV rows | 10 | `PASS` |
| CSV validation rows with errors | 0 | `PASS` |
| imported audit rows | 10 | `PASS` |
| answer-audit validation errors | 0 | `PASS` |
| promoted qid-only labels | 10 | `PASS` |

## Answer Quality Summary

| item | value |
|---|---:|
| completed labels | 10 |
| task success count | 6 |
| task success rate | 60.0% |
| unsafe answer count | 2 |
| unsafe answer rate | 20.0% |

## Generated Private Artifacts

| artifact | public status |
|---|---|
| reviewer CSV | stays outside public repo |
| imported audit pack | stays outside public repo |
| export/import/validation reports | aggregate only |

## Use Notes

- The checked-in fixture reuses synthetic labels to test the workflow.
- Real private review must replace the synthetic labels with independent reviewer labels.
- Public reports must remain aggregate-only and must not include raw queries, answers, evidence text, source names, URLs, or user identifiers.
