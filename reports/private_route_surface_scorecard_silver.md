# Private Route Surface Scorecard

This report scores route and abstention behavior by qid-only intent,
surface, and trap metadata. It does not include qids, raw queries,
conversation snippets, source names, usernames, URLs, or document text.

It is route-only: it does not evaluate whether ranked evidence passages
contain sufficient answer evidence.

## Inputs

- qrels: `surface_qrels_v0_silver.jsonl`
- runs: `route_runs_v0_silver`
- qrel rows: 544
- systems: 4
- label status: silver route labels and silver intent/surface metadata; route-only

## Route Surface Summary

| system | n | intents | surfaces | route_acc | abst_p | abst_r | avg_intent_route_spread | worst_surface_route_acc | missing predictions | missing metadata |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `always_policy` | 544 | 480 | 4 | 21.5% | 0.0% | 0.0% | 0.3% | 14.9% | 0 | 0 |
| `cohort_aware_query_router` | 544 | 480 | 4 | 46.9% | 55.1% | 67.0% | 1.8% | 22.2% | 0 | 0 |
| `query_keyword_router` | 544 | 480 | 4 | 31.8% | 65.9% | 10.5% | 1.3% | 22.4% | 0 | 0 |
| `risk_aware_query_router` | 544 | 480 | 4 | 32.7% | 46.0% | 26.8% | 1.8% | 20.9% | 0 | 0 |

## Surface Form Breakdown

| system | slice | n | route_acc | abst_p | abst_r | missing predictions |
|---|---|---:|---:|---:|---:|---:|
| `always_policy` | `abbreviated` | 67 | 14.9% | 0.0% | 0.0% | 0 |
| `always_policy` | `colloquial` | 9 | 44.4% | 0.0% | 0.0% | 0 |
| `always_policy` | `formal` | 304 | 23.0% | 0.0% | 0.0% | 0 |
| `always_policy` | `messenger_shorthand` | 164 | 20.1% | 0.0% | 0.0% | 0 |
| `cohort_aware_query_router` | `abbreviated` | 67 | 40.3% | 48.8% | 61.8% | 0 |
| `cohort_aware_query_router` | `colloquial` | 9 | 22.2% | 25.0% | 25.0% | 0 |
| `cohort_aware_query_router` | `formal` | 304 | 49.0% | 58.1% | 71.0% | 0 |
| `cohort_aware_query_router` | `messenger_shorthand` | 164 | 47.0% | 52.7% | 63.2% | 0 |
| `query_keyword_router` | `abbreviated` | 67 | 22.4% | 57.1% | 11.8% | 0 |
| `query_keyword_router` | `colloquial` | 9 | 55.6% | 100.0% | 25.0% | 0 |
| `query_keyword_router` | `formal` | 304 | 32.6% | 69.2% | 11.1% | 0 |
| `query_keyword_router` | `messenger_shorthand` | 164 | 32.9% | 60.0% | 7.9% | 0 |
| `risk_aware_query_router` | `abbreviated` | 67 | 20.9% | 29.2% | 20.6% | 0 |
| `risk_aware_query_router` | `colloquial` | 9 | 33.3% | 50.0% | 25.0% | 0 |
| `risk_aware_query_router` | `formal` | 304 | 31.9% | 48.8% | 24.7% | 0 |
| `risk_aware_query_router` | `messenger_shorthand` | 164 | 39.0% | 49.1% | 34.2% | 0 |

## Intent Family Breakdown

| system | slice | n | route_acc | abst_p | abst_r | missing predictions |
|---|---|---:|---:|---:|---:|---:|
| `always_policy` | `bundled_coverage` | 96 | 44.8% | 0.0% | 0.0% | 0 |
| `always_policy` | `claims_process` | 54 | 5.6% | 0.0% | 0.0% | 0 |
| `always_policy` | `coverage_terms` | 6 | 83.3% | 0.0% | 0.0% | 0 |
| `always_policy` | `dental_coverage` | 24 | 79.2% | 0.0% | 0.0% | 0 |
| `always_policy` | `dispute_complaint` | 14 | 7.1% | 0.0% | 0.0% | 0 |
| `always_policy` | `indemnity_noncovered` | 37 | 29.7% | 0.0% | 0.0% | 0 |
| `always_policy` | `product_design` | 33 | 57.6% | 0.0% | 0.0% | 0 |
| `always_policy` | `refund_termination` | 256 | 3.9% | 0.0% | 0.0% | 0 |
| `always_policy` | `underwriting_context` | 24 | 25.0% | 0.0% | 0.0% | 0 |
| `cohort_aware_query_router` | `bundled_coverage` | 96 | 52.1% | 54.4% | 72.1% | 0 |
| `cohort_aware_query_router` | `claims_process` | 54 | 46.3% | 72.7% | 55.2% | 0 |
| `cohort_aware_query_router` | `coverage_terms` | 6 | 33.3% | 25.0% | 100.0% | 0 |
| `cohort_aware_query_router` | `dental_coverage` | 24 | 16.7% | 17.4% | 100.0% | 0 |
| `cohort_aware_query_router` | `dispute_complaint` | 14 | 42.9% | 50.0% | 85.7% | 0 |
| `cohort_aware_query_router` | `indemnity_noncovered` | 37 | 51.4% | 55.2% | 84.2% | 0 |
| `cohort_aware_query_router` | `product_design` | 33 | 30.3% | 27.6% | 88.9% | 0 |
| `cohort_aware_query_router` | `refund_termination` | 256 | 51.2% | 67.8% | 62.6% | 0 |
| `cohort_aware_query_router` | `underwriting_context` | 24 | 33.3% | 35.3% | 66.7% | 0 |
| `query_keyword_router` | `bundled_coverage` | 96 | 44.8% | 0.0% | 0.0% | 0 |
| `query_keyword_router` | `claims_process` | 54 | 16.7% | 0.0% | 0.0% | 0 |
| `query_keyword_router` | `coverage_terms` | 6 | 83.3% | 50.0% | 100.0% | 0 |
| `query_keyword_router` | `dental_coverage` | 24 | 79.2% | 0.0% | 0.0% | 0 |
| `query_keyword_router` | `dispute_complaint` | 14 | 0.0% | 0.0% | 0.0% | 0 |
| `query_keyword_router` | `indemnity_noncovered` | 37 | 35.1% | 100.0% | 10.5% | 0 |
| `query_keyword_router` | `product_design` | 33 | 54.5% | 0.0% | 0.0% | 0 |
| `query_keyword_router` | `refund_termination` | 256 | 23.4% | 77.4% | 15.5% | 0 |
| `query_keyword_router` | `underwriting_context` | 24 | 25.0% | 28.6% | 22.2% | 0 |
| `risk_aware_query_router` | `bundled_coverage` | 96 | 36.5% | 34.8% | 18.6% | 0 |
| `risk_aware_query_router` | `claims_process` | 54 | 31.5% | 72.7% | 27.6% | 0 |
| `risk_aware_query_router` | `coverage_terms` | 6 | 50.0% | 33.3% | 100.0% | 0 |
| `risk_aware_query_router` | `dental_coverage` | 24 | 37.5% | 8.3% | 25.0% | 0 |
| `risk_aware_query_router` | `dispute_complaint` | 14 | 14.3% | 28.6% | 28.6% | 0 |
| `risk_aware_query_router` | `indemnity_noncovered` | 37 | 32.4% | 46.2% | 31.6% | 0 |
| `risk_aware_query_router` | `product_design` | 33 | 51.5% | 33.3% | 33.3% | 0 |
| `risk_aware_query_router` | `refund_termination` | 256 | 30.5% | 59.2% | 27.1% | 0 |
| `risk_aware_query_router` | `underwriting_context` | 24 | 20.8% | 25.0% | 33.3% | 0 |

## Trap-Class Breakdown

| system | slice | n | route_acc | abst_p | abst_r | missing predictions |
|---|---|---:|---:|---:|---:|---:|
| `always_policy` | `bundle_expansion` | 190 | 24.7% | 0.0% | 0.0% | 0 |
| `always_policy` | `claim_ops` | 54 | 5.6% | 0.0% | 0.0% | 0 |
| `always_policy` | `dispute_needed` | 14 | 7.1% | 0.0% | 0.0% | 0 |
| `always_policy` | `needs_private_context` | 276 | 0.0% | 0.0% | 0.0% | 0 |
| `always_policy` | `negation_or_exclusion` | 312 | 20.8% | 0.0% | 0.0% | 0 |
| `always_policy` | `numeric_constraint` | 365 | 18.9% | 0.0% | 0.0% | 0 |
| `always_policy` | `plain_clause_recall` | 6 | 100.0% | 0.0% | 0.0% | 0 |
| `always_policy` | `product_table` | 306 | 12.1% | 0.0% | 0.0% | 0 |
| `always_policy` | `register_mismatch` | 240 | 19.6% | 0.0% | 0.0% | 0 |
| `always_policy` | `source_routing` | 427 | 0.0% | 0.0% | 0.0% | 0 |
| `cohort_aware_query_router` | `bundle_expansion` | 190 | 48.9% | 61.8% | 66.7% | 0 |
| `cohort_aware_query_router` | `claim_ops` | 54 | 46.3% | 72.7% | 55.2% | 0 |
| `cohort_aware_query_router` | `dispute_needed` | 14 | 42.9% | 50.0% | 85.7% | 0 |
| `cohort_aware_query_router` | `needs_private_context` | 276 | 67.0% | 100.0% | 67.0% | 0 |
| `cohort_aware_query_router` | `negation_or_exclusion` | 312 | 48.1% | 57.4% | 69.5% | 0 |
| `cohort_aware_query_router` | `numeric_constraint` | 365 | 49.3% | 61.4% | 67.3% | 0 |
| `cohort_aware_query_router` | `plain_clause_recall` | 6 | 33.3% | 0.0% | 0.0% | 0 |
| `cohort_aware_query_router` | `product_table` | 306 | 50.3% | 63.6% | 63.2% | 0 |
| `cohort_aware_query_router` | `register_mismatch` | 240 | 44.2% | 50.7% | 61.4% | 0 |
| `cohort_aware_query_router` | `source_routing` | 427 | 53.2% | 71.7% | 67.0% | 0 |
| `query_keyword_router` | `bundle_expansion` | 190 | 26.8% | 40.0% | 2.0% | 0 |
| `query_keyword_router` | `claim_ops` | 54 | 16.7% | 0.0% | 0.0% | 0 |
| `query_keyword_router` | `dispute_needed` | 14 | 0.0% | 0.0% | 0.0% | 0 |
| `query_keyword_router` | `needs_private_context` | 276 | 10.5% | 100.0% | 10.5% | 0 |
| `query_keyword_router` | `negation_or_exclusion` | 312 | 32.1% | 75.0% | 14.4% | 0 |
| `query_keyword_router` | `numeric_constraint` | 365 | 29.3% | 76.7% | 11.1% | 0 |
| `query_keyword_router` | `plain_clause_recall` | 6 | 66.7% | 0.0% | 0.0% | 0 |
| `query_keyword_router` | `product_table` | 306 | 28.1% | 77.4% | 13.8% | 0 |
| `query_keyword_router` | `register_mismatch` | 240 | 30.8% | 61.1% | 9.6% | 0 |
| `query_keyword_router` | `source_routing` | 427 | 15.9% | 76.3% | 10.5% | 0 |
| `risk_aware_query_router` | `bundle_expansion` | 190 | 28.9% | 44.2% | 22.5% | 0 |
| `risk_aware_query_router` | `claim_ops` | 54 | 31.5% | 72.7% | 27.6% | 0 |
| `risk_aware_query_router` | `dispute_needed` | 14 | 14.3% | 28.6% | 28.6% | 0 |
| `risk_aware_query_router` | `needs_private_context` | 276 | 26.8% | 100.0% | 26.8% | 0 |
| `risk_aware_query_router` | `negation_or_exclusion` | 312 | 34.0% | 50.0% | 30.5% | 0 |
| `risk_aware_query_router` | `numeric_constraint` | 365 | 29.9% | 50.5% | 25.0% | 0 |
| `risk_aware_query_router` | `plain_clause_recall` | 6 | 50.0% | 0.0% | 0.0% | 0 |
| `risk_aware_query_router` | `product_table` | 306 | 32.0% | 54.1% | 26.4% | 0 |
| `risk_aware_query_router` | `register_mismatch` | 240 | 33.8% | 43.0% | 29.8% | 0 |
| `risk_aware_query_router` | `source_routing` | 427 | 27.2% | 63.2% | 26.8% | 0 |

## Largest Surface Route Confusions

| system | surface form | gold route | predicted route | count | share of run |
|---|---|---|---|---:|---:|
| `always_policy` | `formal` | `human_context_needed` | `policy_clause` | 162 | 29.8% |
| `always_policy` | `messenger_shorthand` | `human_context_needed` | `policy_clause` | 76 | 14.0% |
| `always_policy` | `abbreviated` | `human_context_needed` | `policy_clause` | 34 | 6.2% |
| `always_policy` | `formal` | `dispute_case` | `policy_clause` | 27 | 5.0% |
| `always_policy` | `formal` | `product_disclosure` | `policy_clause` | 25 | 4.6% |
| `always_policy` | `messenger_shorthand` | `product_disclosure` | `policy_clause` | 18 | 3.3% |
| `always_policy` | `messenger_shorthand` | `claims_faq` | `policy_clause` | 17 | 3.1% |
| `always_policy` | `messenger_shorthand` | `dispute_case` | `policy_clause` | 12 | 2.2% |
| `always_policy` | `formal` | `claims_faq` | `policy_clause` | 12 | 2.2% |
| `always_policy` | `abbreviated` | `dispute_case` | `policy_clause` | 9 | 1.7% |
| `always_policy` | `abbreviated` | `product_disclosure` | `policy_clause` | 8 | 1.5% |
| `always_policy` | `formal` | `expert_answer` | `policy_clause` | 8 | 1.5% |
| `cohort_aware_query_router` | `formal` | `policy_clause` | `human_context_needed` | 47 | 8.6% |
| `cohort_aware_query_router` | `messenger_shorthand` | `policy_clause` | `human_context_needed` | 22 | 4.0% |
| `cohort_aware_query_router` | `formal` | `human_context_needed` | `product_disclosure` | 22 | 4.0% |
| `cohort_aware_query_router` | `formal` | `dispute_case` | `human_context_needed` | 18 | 3.3% |
| `cohort_aware_query_router` | `formal` | `human_context_needed` | `policy_clause` | 16 | 2.9% |
| `cohort_aware_query_router` | `messenger_shorthand` | `human_context_needed` | `product_disclosure` | 10 | 1.8% |
| `cohort_aware_query_router` | `formal` | `product_disclosure` | `human_context_needed` | 10 | 1.8% |
| `cohort_aware_query_router` | `messenger_shorthand` | `human_context_needed` | `claims_faq` | 9 | 1.7% |
| `cohort_aware_query_router` | `messenger_shorthand` | `dispute_case` | `human_context_needed` | 8 | 1.5% |
| `cohort_aware_query_router` | `abbreviated` | `dispute_case` | `human_context_needed` | 7 | 1.3% |
| `cohort_aware_query_router` | `formal` | `human_context_needed` | `claims_faq` | 7 | 1.3% |
| `cohort_aware_query_router` | `messenger_shorthand` | `human_context_needed` | `policy_clause` | 7 | 1.3% |
| `query_keyword_router` | `formal` | `human_context_needed` | `policy_clause` | 117 | 21.5% |
| `query_keyword_router` | `messenger_shorthand` | `human_context_needed` | `policy_clause` | 50 | 9.2% |
| `query_keyword_router` | `abbreviated` | `human_context_needed` | `policy_clause` | 23 | 4.2% |
| `query_keyword_router` | `formal` | `human_context_needed` | `product_disclosure` | 18 | 3.3% |
| `query_keyword_router` | `formal` | `dispute_case` | `policy_clause` | 18 | 3.3% |
| `query_keyword_router` | `formal` | `product_disclosure` | `policy_clause` | 13 | 2.4% |
| `query_keyword_router` | `messenger_shorthand` | `human_context_needed` | `product_disclosure` | 9 | 1.7% |
| `query_keyword_router` | `messenger_shorthand` | `human_context_needed` | `claims_faq` | 9 | 1.7% |
| `query_keyword_router` | `messenger_shorthand` | `dispute_case` | `policy_clause` | 8 | 1.5% |
| `query_keyword_router` | `messenger_shorthand` | `product_disclosure` | `policy_clause` | 8 | 1.5% |
| `query_keyword_router` | `messenger_shorthand` | `expert_answer` | `policy_clause` | 8 | 1.5% |
| `query_keyword_router` | `abbreviated` | `dispute_case` | `policy_clause` | 7 | 1.3% |
| `risk_aware_query_router` | `formal` | `human_context_needed` | `policy_clause` | 91 | 16.7% |
| `risk_aware_query_router` | `messenger_shorthand` | `human_context_needed` | `policy_clause` | 29 | 5.3% |
| `risk_aware_query_router` | `formal` | `policy_clause` | `human_context_needed` | 24 | 4.4% |
| `risk_aware_query_router` | `formal` | `human_context_needed` | `product_disclosure` | 22 | 4.0% |
| `risk_aware_query_router` | `abbreviated` | `human_context_needed` | `policy_clause` | 19 | 3.5% |
| `risk_aware_query_router` | `messenger_shorthand` | `policy_clause` | `human_context_needed` | 13 | 2.4% |
| `risk_aware_query_router` | `formal` | `dispute_case` | `human_context_needed` | 12 | 2.2% |
| `risk_aware_query_router` | `messenger_shorthand` | `human_context_needed` | `product_disclosure` | 10 | 1.8% |
| `risk_aware_query_router` | `formal` | `product_disclosure` | `policy_clause` | 10 | 1.8% |
| `risk_aware_query_router` | `formal` | `dispute_case` | `policy_clause` | 10 | 1.8% |
| `risk_aware_query_router` | `messenger_shorthand` | `human_context_needed` | `claims_faq` | 9 | 1.7% |
| `risk_aware_query_router` | `formal` | `human_context_needed` | `claims_faq` | 7 | 1.3% |

## Use Notes

- Use this report to find route and abstention regressions across surface
  conditions independently from retrieval-hit regressions.
- Treat silver-label results as diagnostics until the route labels and
  intent/surface metadata are human-audited.
- Pair this route-only report with runtime-surface or full surface
  scorecards to separate routing failures from evidence-hit failures.
