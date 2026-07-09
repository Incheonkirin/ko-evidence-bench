# Source Route Label Protocol

Status: draft for the first 300-500 private labels.

The label answers one question: what kind of source is required before the system
is allowed to answer?

It is not an intent label. It is not a topic label. A question about claims,
refunds, surgery, or underwriting can still require different source tiers.

## Labels

| label | Use when |
|---|---|
| `policy_clause` | The answer can be cited from policy clauses, riders, definitions, tables, or appendices. |
| `product_disclosure` | The answer requires product summaries, disclosure pages, business-method documents, premium/refund tables, or product-specific public material outside the policy clause text. |
| `official_consumer_info` | The answer needs regulator, association, or public consumer guidance rather than a contract clause. |
| `claims_faq` | The answer is mainly about claim documents, submission channels, processing steps, or operational instructions. |
| `dispute_case` | The answer needs dispute, denial, claim-review, medical-review, or complaint precedent material. |
| `expert_answer` | The answer can be grounded only as general professional guidance, not as a citable contract or official source. |
| `human_context_needed` | The user must provide contract, rider, date, diagnosis, denial letter, or other private facts before citation is safe. |
| `out_of_scope` | The question is not an insurance evidence retrieval task. |

## Required Fields

Each labeled row should have:

```json
{
  "qid": "private-stable-id",
  "route_gold": "policy_clause",
  "allowed_source_tiers": ["policy_clause"],
  "should_abstain": false,
  "labeler": "initials-or-model-id",
  "confidence": "high|medium|low",
  "rationale_code": "contract_clause_direct|needs_private_contract|claims_ops|dispute_needed|product_table_needed|official_guidance_needed|out_of_scope"
}
```

Do not export raw question text to the public repo.

## Decision Rules

Prefer the narrowest citable source that can answer the question.

If a policy clause gives the legal rule but a claim FAQ gives the operational
steps, choose the source that answers the user's actual ask. Put the other source
in `allowed_source_tiers` only if it is useful supporting evidence.

Use `human_context_needed` when the public corpus can explain the rule but cannot
decide the user's case. Examples include missing policy version, rider enrollment,
accident date, claim denial reason, diagnosis code, or underwriting condition.

Use `dispute_case` when the question is about whether a denial, medical review,
or claim handling decision is reasonable. A policy clause may be supporting
evidence, but it is usually not sufficient alone.

Use `expert_answer` sparingly. It is acceptable for general process language or
triage examples, but it should not override contract or official sources.

## Agreement Check

For the first 300-500 rows:

- Double-label at least 50 rows.
- Report raw agreement and Cohen's kappa on `route_gold`.
- Adjudicate disagreements before using the label set for headline metrics.
- Track `confidence=low` separately and exclude it from the first public table.

Use `scripts/build_route_audit_pack.py` to create a private double-label seed
and, separately, a larger adjudication workset:

```bash
python3 scripts/build_route_audit_pack.py \
  --qrels /path/to/private_qrels.jsonl \
  --labels /path/to/private_route_labels.jsonl \
  --audit-out /path/to/private_route_audit_pack.jsonl \
  --report-out reports/private_route_audit_pack_summary.md \
  --sample-size 50
```

For the 300-row workset, use the same command with `--sample-size 300` and a
separate private `--audit-out` path.

The audit pack may contain raw private query text and must stay outside this
public repo. Only the aggregate sampling summary should be checked in.

After independent labels are filled, summarize agreement without exposing rows:

```bash
python3 scripts/summarize_route_audit.py \
  --audit /path/to/private_route_audit_pack.jsonl \
  --field-a reviewer_a.route_gold \
  --field-b reviewer_b.route_gold \
  --report-out reports/private_route_audit_agreement.md
```

If only one human label exists, compare `silver.route_gold` to
`human_route_gold` for calibration only. Do not call that inter-annotator
agreement.

After adjudication, validate the final label payload:

```bash
python3 scripts/validate_route_audit.py \
  --audit /path/to/private_route_audit_pack.jsonl \
  --label-prefix adjudicated \
  --require-complete \
  --report-out reports/private_route_audit_validation.md
```

Promote only validated adjudicated rows into the qid-only label file consumed by
route/evidence scorecards:

```bash
python3 scripts/promote_route_audit.py \
  --audit /path/to/private_route_audit_pack.jsonl \
  --label-prefix adjudicated \
  --labels-out /path/to/private_human_route_labels.jsonl \
  --report-out reports/private_promoted_route_labels.md
```

## Public Reporting

Public reports may include label counts, agreement statistics, and aggregate
scorecard metrics. They should not include raw questions, user ids, conversation
snippets, or platform-specific identifiers.
