# ko-evidence-bench

Evidence sufficiency and abstention metrics for Korean retrieval. Insurance is
the first testbed.

## Thesis

Real Korean insurance questions are asked in community language. Citable answers
live in clause language. This repo scores whether a retrieval system crossed
that gap, and whether it stopped when it could not.

This is the public shell of a private search lab. It contains metrics, schemas,
fixtures, and reports. It does not contain community crawls, KakaoTalk exports,
or copyrighted policy corpora.

## What This Evaluates

The scorecard treats retrieval as more than "did we find a similar paragraph?"

| Metric | Question Answered |
|---|---|
| `route_accuracy` | Did the system choose the right source tier? |
| `evidence_sufficiency@k` | Did top-k contain enough citable evidence? |
| `wrong_source_rate@k` | Did top-k cite evidence from a disallowed source tier? |
| `abstention_precision/recall` | Did the system correctly stop when evidence was insufficient? |
| `clause_recall@k` | For policy-answerable questions, did top-k include the expected clause? |

The fixture is small on purpose. It exists to make the metrics easy to inspect.
Private aggregate studies can use the same scorecard without exposing raw user
text.

## Data Behind The Work

The private lab currently has:

- 36,983 Samsung Life policy clause passages from 111 products.
- 165,970 derived real-user query candidates from community crawls.
- 7,324 meaningful KakaoTalk open-chat messages after obvious system-message filtering.
- 56,293 additional Aha expert-QA archive rows.
- Silver retrieval diagnostics where `structural_cross_rrf` reached
  `clause@10 = 83.4%` on a strict silver core of `n=229`.

These numbers are context, not final benchmark claims. Public headline numbers
need bootstrap confidence intervals first.

## Quickstart

```bash
make test
make reproduce-table-1
```

Expected output is a small scorecard over synthetic fixture runs:

```text
system  n  route_acc  suff@3  wrong_src@3  abst_p  abst_r  clause@3
always_policy  5  0.200  1.000  0.400  0.000  0.000  1.000
source_routed_demo  5  1.000  1.000  0.000  1.000  1.000  1.000
```

## Public/Private Boundary

Public:

- Metric definitions and reference implementation.
- Query/evidence/run schemas.
- Synthetic fixtures.
- Aggregate reports and data cards.
- Reproduction scripts.

Private:

- Raw community crawl text.
- Raw KakaoTalk messages.
- Raw Aha content.
- Copyrighted policy clauses.
- Any row that can identify a user, product contract, or conversation.

## Repository Layout

```text
ko_evidence_bench/
  metrics.py          # Scorecard metrics with bootstrap CIs.
  schemas.py          # Minimal JSONL schema validators.
scripts/
  reproduce_table_1.py
fixtures/
  qrels.jsonl
  system_runs/
reports/
  measurement_study_v0.md
docs/
  data_statement.md
  schemas.md
tests/
```

## Scope Statement

This is not an insurance advice system, a chatbot, or a Korean dictionary. It is
a retrieval evaluation workbench: did the system find enough citable evidence,
and did it abstain when it should?
