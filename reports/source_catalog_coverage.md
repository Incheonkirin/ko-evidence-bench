# Source Catalog Coverage

Status: **PASS source-tier catalog fixture**.

This report checks that the evaluation is not policy-clause-only. It
joins the source-tier catalog with public probe qrels and synthetic
evidence snippets, then verifies that each demanded searchable source
tier has fixture evidence. It is not proof that private source corpora
are complete.

## Inputs

- source catalog: `docs/source_catalog.json`
- qrels: `probes/ko_evidence_probe_v0/qrels.jsonl`
- evidence: `probes/ko_evidence_probe_v0/evidence.jsonl`
- qrel rows: 13
- evidence rows: 7
- validation issues: 0

## Source-Tier Coverage

| source tier | route-demand rows | allowed-support rows | evidence snippets | sufficient refs | public fixture | private status | headline status | gate |
|---|---:|---:|---:|---:|---|---|---|---|
| `policy_clause` | 5 | 9 | 2 | 5 | `covered` | `available_private_corpus` | `silver_only` | `COVERED` |
| `product_disclosure` | 2 | 3 | 1 | 2 | `covered` | `planned_or_partial` | `needs_inventory_audit` | `COVERED` |
| `official_consumer_info` | 1 | 4 | 1 | 1 | `covered` | `planned_or_partial` | `needs_inventory_audit` | `COVERED` |
| `claims_faq` | 1 | 1 | 1 | 1 | `covered` | `planned_or_partial` | `needs_inventory_audit` | `COVERED` |
| `dispute_case` | 1 | 1 | 1 | 1 | `covered` | `planned_or_partial` | `needs_inventory_audit` | `COVERED` |
| `expert_answer` | 1 | 1 | 1 | 1 | `covered` | `planned_or_partial` | `needs_inventory_audit` | `COVERED` |
| `human_context_needed` | 2 | 2 | 0 | 0 | `abstention_only` | `requires_user_context` | `requires_abstention_audit` | `ABSTENTION` |
| `out_of_scope` | 0 | 0 | 0 | 0 | `abstention_only` | `requires_filtering` | `requires_abstention_audit` | `ABSTENTION` |

## Search Role Catalog

| source tier | role | search target |
|---|---|---|
| `policy_clause` | Contractual clause evidence for definitions, coverage triggers, exclusions, riders, and tables. | insurer policy clauses, riders, appendices, and contract tables |
| `product_disclosure` | Product-level disclosure evidence for summaries, refund tables, product options, and pre-contract material. | product disclosures, product summaries, refund tables, and public product pages |
| `official_consumer_info` | Official consumer guidance for general rules, public notices, comparison material, and consumer-facing explanations. | official consumer guidance, public association material, and regulator-style consumer documents |
| `claims_faq` | Operational claim guidance for documents, submission steps, processing channels, and workflow instructions. | claim guides, claim FAQ material, document checklists, and operational help pages |
| `dispute_case` | Dispute and denial precedent material for contested payments, reviews, complaints, and similar resolved cases. | dispute summaries, denial-case explanations, review precedents, and complaint-resolution material |
| `expert_answer` | General professional guidance when the answer is explanatory and not safely grounded in a contract or official source alone. | licensed or reviewable expert guidance archives and general professional explanations |
| `human_context_needed` | Abstention route when private contract, rider, date, diagnosis, denial, or underwriting context is required. | not a searchable corpus tier |
| `out_of_scope` | Abstention route for requests outside insurance evidence retrieval. | not a searchable corpus tier |

## Use Notes

- This is a source-routing coverage gate, not a corpus acquisition claim.
- `human_context_needed` and `out_of_scope` are abstention routes, not searchable corpora.
- Private reports may reuse this shape with aggregate inventory counts only.
- Keep raw source names, URLs, and document text outside public reports.
