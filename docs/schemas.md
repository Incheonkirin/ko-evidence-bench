# Schemas

## Qrel Row

```json
{
  "qid": "syn_policy_001",
  "route_gold": "policy_clause",
  "allowed_source_tiers": ["policy_clause"],
  "should_abstain": false,
  "sufficient_evidence_ids": ["clause_cancer_diag"]
}
```

`route_gold` values:

- `policy_clause`
- `product_disclosure`
- `official_consumer_info`
- `claims_faq`
- `dispute_case`
- `expert_answer`
- `human_context_needed`
- `out_of_scope`

## Run Row

```json
{
  "qid": "syn_policy_001",
  "route_pred": "policy_clause",
  "abstained": false,
  "ranked": [
    {
      "evidence_id": "clause_cancer_diag",
      "source_tier": "policy_clause"
    }
  ]
}
```

The schema is intentionally minimal. Private adapters may preserve raw text and
metadata internally, but public scoring only consumes stable ids, route labels,
abstention decisions, and ranked evidence ids.

`allowed_source_tiers` lets the qrel distinguish the primary route from allowed
supporting sources. For example, a dispute question may require a regulator or
dispute-case source while still allowing a policy clause as supporting evidence.
