# Answer Quality Audit Fixture

Status: **PASS synthetic answer-quality audit rehearsal**.

This qid-only fixture rehearses answer-quality and evidence-sufficiency
labels after retrieval. It is not human-gold answer-quality evidence and
not a final benchmark claim.

It exists to keep retrieval hit metrics separate from the question a
reviewer actually cares about: whether the system had enough cited evidence
to answer, partially answer, abstain correctly, or avoid an unsafe answer.

## Gate Summary

| item | value |
|---|---:|
| fixture | `fixtures/answer_audit/answer_audit_seed.jsonl` |
| rows | 10 |
| completed labels | 10 |
| validation errors | 0 |
| promoted rows | 10 |
| task success count | 6 |
| task success rate | 60.0% |
| unsafe answer count | 2 |
| unsafe answer rate | 20.0% |

## Answer Label Distribution

| value | count | share |
|---|---:|---:|
| `sufficient` | 4 | 40.0% |
| `unsafe_answer` | 2 | 20.0% |
| `correct_abstain` | 2 | 20.0% |
| `insufficient` | 1 | 10.0% |
| `partial` | 1 | 10.0% |

## Confidence Distribution

| value | count | share |
|---|---:|---:|
| `high` | 9 | 90.0% |
| `medium` | 1 | 10.0% |

## By System

| slice | sufficient | partial | insufficient | correct_abstain | unsafe_answer | total | task_success |
|---|---:|---:|---:|---:|---:|---:|---:|
| `formal_only_demo` | 1 | 1 | 1 | 1 | 2 | 6 | 33.3% |
| `surface_robust_demo` | 3 | 0 | 0 | 1 | 0 | 4 | 100.0% |

## By Surface Form

| slice | sufficient | partial | insufficient | correct_abstain | unsafe_answer | total | task_success |
|---|---:|---:|---:|---:|---:|---:|---:|
| `abbreviated` | 1 | 0 | 1 | 0 | 0 | 2 | 50.0% |
| `colloquial` | 1 | 1 | 0 | 0 | 0 | 2 | 50.0% |
| `formal` | 1 | 0 | 0 | 1 | 0 | 2 | 100.0% |
| `messenger_shorthand` | 1 | 0 | 0 | 1 | 2 | 4 | 50.0% |

## By Intent Family

| slice | sufficient | partial | insufficient | correct_abstain | unsafe_answer | total | task_success |
|---|---:|---:|---:|---:|---:|---:|---:|
| `bundled_coverage` | 2 | 0 | 1 | 0 | 0 | 3 | 66.7% |
| `refund_termination` | 2 | 1 | 0 | 0 | 1 | 4 | 50.0% |
| `underwriting_context` | 0 | 0 | 0 | 2 | 1 | 3 | 66.7% |

## Use Notes

- This report is a fixture-only rehearsal for the private audit path.
- Public rows carry qids, system ids, evidence ids, source tiers, and labels only.
- Raw questions, answer text, evidence text, source names, urls, and user identifiers stay outside the public repo.
- Route labels decide which source tier is required; answer-quality labels decide whether the returned evidence was enough to answer.
