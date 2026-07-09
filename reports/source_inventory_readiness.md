# Source Inventory Readiness

Status: **ACTION_REQUIRED for private source inventory**.

This report joins aggregate private route-label demand with a generic
source inventory manifest. It contains no raw source names, URLs,
queries, document text, or evidence ids.

It is deliberately stricter than the public source catalog: a source tier
can be part of the evaluation design while still being blocked for
headline claims until its private inventory and rights status are audited.

## Inputs

- inventory manifest: `docs/source_inventory.json`
- route-demand report: `reports/private_route_label_summary.md`
- aggregate demand rows: 544
- validation issues: 0
- blocked searchable tiers: 4

## Readiness By Source Tier

| source tier | private route demand | inventory records | inventory status | rights status | public release | readiness |
|---|---:|---:|---|---|---|---|
| `policy_clause` | 117 | 36,983 | `verified_private` | `private_eval_only` | `aggregate_only` | `READY` |
| `product_disclosure` | 51 | 0 | `needs_inventory_audit` | `needs_rights_review` | `none` | `BLOCKED` |
| `official_consumer_info` | 0 | 0 | `needs_inventory_audit` | `needs_rights_review` | `none` | `NO_DEMAND` |
| `claims_faq` | 31 | 0 | `needs_inventory_audit` | `needs_rights_review` | `none` | `BLOCKED` |
| `dispute_case` | 48 | 0 | `needs_inventory_audit` | `needs_rights_review` | `none` | `BLOCKED` |
| `expert_answer` | 21 | 0 | `needs_inventory_audit` | `needs_rights_review` | `none` | `BLOCKED` |
| `human_context_needed` | 276 | n/a | `not_searchable_route` | `not_applicable` | `not_applicable` | `ABSTENTION` |
| `out_of_scope` | 0 | n/a | `not_searchable_route` | `not_applicable` | `not_applicable` | `ABSTENTION` |

## Blockers

- `product_disclosure` has 51 silver-demand rows, but inventory status is `needs_inventory_audit` with 0 verified records.
- `claims_faq` has 31 silver-demand rows, but inventory status is `needs_inventory_audit` with 0 verified records.
- `dispute_case` has 48 silver-demand rows, but inventory status is `needs_inventory_audit` with 0 verified records.
- `expert_answer` has 21 silver-demand rows, but inventory status is `needs_inventory_audit` with 0 verified records.

## Use Notes

- This is an inventory-readiness gate, not a source acquisition script.
- `READY` means the tier has aggregate private inventory for diagnostics, not public redistributable data.
- `BLOCKED` tiers can remain in the route taxonomy, but headline claims should name the inventory gap.
- `human_context_needed` and `out_of_scope` are abstention/filtering routes, not searchable corpora.
