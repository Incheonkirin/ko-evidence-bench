# Private Route Audit Pack Summary

This report summarizes a private human-audit pack. It contains aggregate
counts only. The audit pack itself may contain raw queries and must stay
outside the public repository.

- sampled rows: 50
- seed: 17
- minimum per route: 4
- qrels file: `qrels_v1_700_partial.jsonl`
- silver labels file: `route_labels_v0_silver.jsonl`
- private audit pack: `route_audit_pack_v0_50.jsonl`

## Reviewer Fields

| field | purpose |
|---|---|
| `human_route_gold` | adjudicated source route |
| `human_allowed_source_tiers` | acceptable supporting source tiers |
| `human_should_abstain` | whether the system should refuse to answer without more facts |
| `human_confidence` | high, medium, or low |
| `human_rationale_code` | compact reason for the route decision |
| `human_notes` | brief adjudication note |

## Sampled Route Distribution

| value | count | share |
|---|---:|---:|
| `human_context_needed` | 25 | 50.0% |
| `policy_clause` | 9 | 18.0% |
| `dispute_case` | 4 | 8.0% |
| `claims_faq` | 4 | 8.0% |
| `expert_answer` | 4 | 8.0% |
| `product_disclosure` | 4 | 8.0% |

## Sampled Confidence Distribution

| value | count | share |
|---|---:|---:|
| `high` | 25 | 50.0% |
| `medium` | 21 | 42.0% |
| `low` | 4 | 8.0% |

## Sampled Abstention Distribution

| value | count | share |
|---|---:|---:|
| `False` | 25 | 50.0% |
| `True` | 25 | 50.0% |

## Use Notes

- Double-label this pack before reporting human agreement.
- Public benchmark claims should use adjudicated fields, not silver fields.
- Do not copy raw audit rows into the public repository.
