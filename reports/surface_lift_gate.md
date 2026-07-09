# Surface Robustness Lift Gate

Status: **PASS**.

This gate checks the synthetic surface-form robustness report. It contains
aggregate values only and does not include qids, raw queries, source names,
conversation snippets, or platform identifiers.

- baseline: `formal_only_demo`
- candidate: `surface_robust_demo`
- label status: synthetic fixture, not human-gold

## Gate Checks

| check | current value | threshold | status |
|---|---:|---:|---|
| task success lift vs `formal_only_demo` | 62.5%p | >= 30.0%p | `PASS` |
| average intent-spread reduction | 100.0%p | >= 30.0%p | `PASS` |
| worst-surface lift vs `formal_only_demo` | 100.0%p | >= 30.0%p | `PASS` |
| candidate rows missing surface metadata | 0 | <= 0 | `PASS` |

## Signal Snapshot

| signal | baseline | candidate |
|---|---:|---:|
| task success | 37.5% | 100.0% |
| average intent spread | 100.0% | 0.0% |
| worst-surface success | 0.0% | 100.0% |

## Use Notes

- A passing gate means the synthetic surface-robustness demonstration has not regressed.
- It does not create a private or human-gold surface benchmark by itself.
- Private qrels still need audited `intent_id` and `surface_form` metadata for headline use.
