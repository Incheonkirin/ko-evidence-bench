# Human-Gold Promotion Rehearsal Fixture

Status: **PASS**.

This synthetic rehearsal exercises the public path from completed
adjudication to qid-only labels, route scorecards, and surface-route
diagnostics. It uses fixture ids only: no private query, conversation,
community, policy, source-name, or evidence text is published.

## Gate Chain

| gate | evidence | status |
|---|---:|---|
| adjudicated audit rows | 8 | `PASS` |
| route-audit validation errors | 0 | `PASS` |
| promoted qid-only labels | 8 | `PASS` |
| stress-axis coverage | PASS | `PASS` |
| route scorecard generated | route_scorecard.md | `PASS` |
| route-surface scorecard generated | route_surface.md | `PASS` |

## Route Scorecard Rehearsal

| system | route_acc | abst_p | abst_r | missing predictions |
|---|---:|---:|---:|---:|
| `formal_only_demo` | 75.0% | 100.0% | 50.0% | 0 |
| `surface_robust_demo` | 100.0% | 100.0% | 100.0% | 0 |

## Route-Surface Rehearsal

| system | route_acc | abst_r | worst_surface_route_acc | missing metadata |
|---|---:|---:|---:|---:|
| `formal_only_demo` | 75.0% | 50.0% | 33.3% | 0 |
| `surface_robust_demo` | 100.0% | 100.0% | 100.0% | 0 |

## Use Notes

- This is not a human-gold result. It exercises the promotion and scoring
  path that real adjudicated labels will use.
- The private 300-row adjudication pack still needs completed labels,
  validation with zero errors, and agreement evidence before headline
  claims can be promoted.
- The route/surface scorecards are intentionally qid-only so private text
  can remain outside the public repository.
