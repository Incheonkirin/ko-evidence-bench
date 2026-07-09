# Private Route Audit Pack Summary

This report summarizes a private human-audit pack. It contains aggregate
counts only. The audit pack itself may contain raw queries and must stay
outside the public repository.

- sampled rows: 300
- seed: 23
- minimum per route: 20
- qrels file: `qrels_v1_700_partial.jsonl`
- silver labels file: `route_labels_v0_silver.jsonl`
- private audit pack: `route_audit_pack_v0_300.jsonl`

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
| `human_context_needed` | 152 | 50.7% |
| `policy_clause` | 62 | 20.7% |
| `dispute_case` | 26 | 8.7% |
| `product_disclosure` | 20 | 6.7% |
| `expert_answer` | 20 | 6.7% |
| `claims_faq` | 20 | 6.7% |

## Sampled Confidence Distribution

| value | count | share |
|---|---:|---:|
| `high` | 152 | 50.7% |
| `medium` | 116 | 38.7% |
| `low` | 32 | 10.7% |

## Sampled Abstention Distribution

| value | count | share |
|---|---:|---:|
| `True` | 152 | 50.7% |
| `False` | 148 | 49.3% |

## Use Notes

- Double-label this pack before reporting human agreement.
- Public benchmark claims should use adjudicated fields, not silver fields.
- Do not copy raw audit rows into the public repository.
