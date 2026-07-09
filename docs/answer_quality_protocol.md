# Answer Quality Audit Protocol

Status: fixture rehearsal for the private answer-quality audit.

The route-label protocol answers which source tier is required. This protocol
answers a later question: after a system retrieves evidence and chooses whether
to abstain, was there enough cited evidence to answer?

## Labels

| label | Use when |
|---|---|
| `sufficient` | The returned evidence is enough to answer the query with citations from allowed source tiers. |
| `partial` | The returned evidence supports part of the answer but misses a required condition, table, exception, or private-context caveat. |
| `insufficient` | The returned evidence is relevant-looking but not enough to answer the user's ask. |
| `correct_abstain` | The system abstained when the row required private context or was otherwise not safely answerable. |
| `unsafe_answer` | The system answered or selected evidence when it should have abstained, used the wrong source tier, or would likely mislead the user. |

## Public Row Contract

The public fixture uses qid-only rows:

```json
{
  "audit_id": "answer-audit-0001",
  "qid": "stable-id",
  "system_id": "retrieval-system",
  "route_gold": "policy_clause",
  "route_pred": "policy_clause",
  "should_abstain": false,
  "abstained": false,
  "topk_evidence_ids": ["evidence-id"],
  "topk_source_tiers": ["policy_clause"],
  "adjudicated": {
    "answer_label": "sufficient",
    "supporting_evidence_ids": ["evidence-id"],
    "confidence": "high",
    "rationale_code": "direct_citable_clause",
    "labeler": "reviewer-id"
  }
}
```

Do not publish raw query text, answer text, evidence text, source names, urls,
usernames, conversation excerpts, or private-source identifiers.

## Why This Is Separate

`clause@20`, `evidence_sufficiency@k`, and route accuracy are retrieval-side
signals. They do not prove that a final answer was safe or complete. The answer
audit labels the output state directly, so the measurement study can say:

- the system found the right evidence;
- the system found only partial evidence;
- the system should have abstained;
- the system produced an unsafe answer.

The checked-in fixture is synthetic and only rehearses the validation, summary,
and qid-only promotion path. Human-gold answer-quality claims require private
reviewed labels and agreement reporting.

## Review Workflow

Export a private reviewer CSV:

```bash
python3 scripts/export_answer_review_csv.py \
  --audit /path/to/private_answer_audit.jsonl \
  --reviewer-prefix reviewer_a \
  --csv-out /path/to/private_answer_reviewer_a.csv \
  --report-out reports/private_answer_review_csv_export.md
```

Validate progress before import:

```bash
python3 scripts/validate_answer_review_csv.py \
  --csv /path/to/private_answer_reviewer_a.csv \
  --report-out reports/private_answer_review_csv_validation.md
```

Before promotion, run the same validation with `--require-complete`.

Import the reviewed CSV back into a private audit pack:

```bash
python3 scripts/import_answer_review_csv.py \
  --audit /path/to/private_answer_audit.jsonl \
  --csv /path/to/private_answer_reviewer_a.csv \
  --target-prefix reviewer_a \
  --out /path/to/private_answer_audit.reviewer_a.jsonl \
  --report-out reports/private_answer_review_csv_import.md \
  --skip-empty
```

The public rehearsal is:

```bash
make reproduce-answer-review-workflow
```

It proves the export, CSV validation, import, qid-only validation, and promotion
path on synthetic rows only. It does not create human-gold labels.
