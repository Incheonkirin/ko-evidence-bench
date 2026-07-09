# ko-evidence-bench

Evidence sufficiency and abstention metrics for Korean retrieval. Insurance is
the first testbed.

## Thesis

Real Korean insurance questions are asked in community language. Citable answers
live in clause language. This repo scores whether a retrieval system crossed
that gap, and whether it stopped when it could not.

This is the public shell of a private search lab. It contains metrics, schemas,
fixtures, and reports. It does not contain community crawls, messenger exports,
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

- 36,983 insurer policy clause passages from 111 products.
- 165,970 derived real-user query candidates from community crawls.
- 7,324 meaningful messenger-conversation messages after obvious system-message filtering.
- 56,293 additional community Q&A archive rows.
- Silver retrieval diagnostics where `structural_cross_rrf` reached
  `clause@10 = 83.4%` on a strict silver core of `n=229`.
- Runtime-honest pack-only diagnostics on a larger silver qrel set of `n=544`,
  where `structural_pack` reached `clause@20 = 56.4%` with a 95% bootstrap CI of
  `52.4% - 60.5%`.

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

Private retrieval exports with query-level hit booleans can be summarized without
publishing qids or text:

```bash
python3 scripts/summarize_hit_result.py \
  --result /path/to/private_result.json \
  --baseline structural_pack \
  --run structural_pack \
  --run structural_cross_rrf \
  --out reports/private_aggregate_scorecard.md
```

The current private aggregate report is checked in at
`reports/private_aggregate_scorecard.md`. It is aggregate-only and should be read
as a diagnostic, not a final benchmark.

A larger pack-only diagnostic report is checked in at
`reports/private_544_pack_only_scorecard.md`. It verifies that the 500+ qrel set
can be scored by the existing retrieval stack, but it does not replace the
human-audited route/evidence benchmark.

Private qrel metadata can also be converted into a qid-only source-route silver
label set while publishing only aggregate counts:

```bash
python3 scripts/export_route_labels.py \
  --qrels /path/to/private_qrels.jsonl \
  --labels-out /path/to/private_route_labels.jsonl \
  --report-out reports/private_route_label_summary.md
```

The current route-label inventory has 544 silver rows. It shows that an
`always_policy` router would reach only 21.5% route accuracy on that private
set, but this is still a silver proxy and requires human audit before headline
claims.

To start the human audit gate, build a private audit pack and publish only the
sampling summary:

```bash
python3 scripts/build_route_audit_pack.py \
  --qrels /path/to/private_qrels.jsonl \
  --labels /path/to/private_route_labels.jsonl \
  --audit-out /path/to/private_route_audit_pack.jsonl \
  --report-out reports/private_route_audit_pack_summary.md \
  --sample-size 50
```

The current private audit worksets include a 50-row double-label seed and a
300-row adjudication pack, both stratified across source-route classes. They
must be labeled before any human-gold route metric is reported.

After independent labels are filled, `scripts/summarize_route_audit.py` reports
raw agreement and Cohen's kappa without exposing private rows.

## Public/Private Boundary

Public:

- Metric definitions and reference implementation.
- Query/evidence/run schemas.
- Synthetic fixtures.
- Aggregate reports and data cards.
- Reproduction scripts.

Private:

- Raw community crawl text.
- Raw messenger messages.
- Raw community Q&A content.
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
  eval_core_inventory.md
  measurement_study_v0.md
  private_544_pack_only_scorecard.md
  private_aggregate_scorecard.md
  private_route_audit_pack_300_summary.md
  private_route_audit_pack_summary.md
  private_route_label_summary.md
docs/
  data_statement.md
  route_label_protocol.md
  schemas.md
tests/
```

## Scope Statement

This is not an insurance advice system, a chatbot, or a Korean dictionary. It is
a retrieval evaluation workbench: did the system find enough citable evidence,
and did it abstain when it should?
