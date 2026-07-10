import unittest

from ko_evidence_bench.metrics import (
    bootstrap_ci,
    clustered_bootstrap_hit_ci,
    paired_delta_ci,
    score_run,
    summarize_hit_rows,
)
from ko_evidence_bench.schemas import validate_qrel


class ScoreRunTest(unittest.TestCase):
    def test_route_and_sufficiency_metrics(self):
        qrels = [
            {
                "qid": "q1",
                "route_gold": "policy_clause",
                "allowed_source_tiers": ["policy_clause"],
                "should_abstain": False,
                "sufficient_evidence_ids": ["d1"],
            },
            {
                "qid": "q2",
                "route_gold": "human_context_needed",
                "allowed_source_tiers": [],
                "should_abstain": True,
                "sufficient_evidence_ids": [],
            },
        ]
        run = [
            {
                "qid": "q1",
                "route_pred": "policy_clause",
                "abstained": False,
                "ranked": [{"evidence_id": "d1", "source_tier": "policy_clause"}],
            },
            {
                "qid": "q2",
                "route_pred": "human_context_needed",
                "abstained": True,
                "ranked": [],
            },
        ]
        scores = score_run(qrels, run, k=3)
        self.assertEqual(scores["route_accuracy"], 1.0)
        self.assertEqual(scores["evidence_hit@3"], 1.0)
        self.assertEqual(scores["evidence_coverage@3"], 1.0)
        self.assertEqual(scores["evidence_sufficiency@3"], 1.0)
        self.assertEqual(scores["wrong_source_rate@3"], 0.0)
        self.assertEqual(scores["abstention_precision"], 1.0)
        self.assertEqual(scores["abstention_recall"], 1.0)
        self.assertEqual(scores["clause_recall@3"], 1.0)

    def test_hit_summary_and_paired_delta(self):
        baseline = [
            {"qid": "q1", "clause@20": True},
            {"qid": "q2", "clause@20": False},
            {"qid": "q3", "clause@20": False},
        ]
        candidate = [
            {"qid": "q1", "clause@20": True},
            {"qid": "q2", "clause@20": True},
            {"qid": "q3", "clause@20": False},
        ]
        summary = summarize_hit_rows(candidate, "clause@20")
        self.assertEqual(summary["n"], 3.0)
        self.assertEqual(summary["hits"], 2.0)
        self.assertAlmostEqual(summary["rate"], 2 / 3)

        delta, lo, hi = paired_delta_ci(baseline, candidate, "clause@20", samples=200, seed=7)
        self.assertAlmostEqual(delta, 1 / 3)
        self.assertLessEqual(lo, delta)
        self.assertGreaterEqual(hi, delta)

    def test_bootstrap_ci_keeps_resampling_weights(self):
        qrels = [
            {
                "qid": "q1",
                "route_gold": "policy_clause",
                "should_abstain": False,
                "sufficient_evidence_ids": ["d1"],
            },
            {
                "qid": "q2",
                "route_gold": "policy_clause",
                "should_abstain": False,
                "sufficient_evidence_ids": ["d2"],
            },
            {
                "qid": "q3",
                "route_gold": "policy_clause",
                "should_abstain": False,
                "sufficient_evidence_ids": ["d3"],
            },
        ]
        run = [
            {
                "qid": "q1",
                "route_pred": "policy_clause",
                "abstained": False,
                "ranked": [{"evidence_id": "d1", "source_tier": "policy_clause"}],
            },
            {
                "qid": "q2",
                "route_pred": "policy_clause",
                "abstained": False,
                "ranked": [{"evidence_id": "x", "source_tier": "policy_clause"}],
            },
            {
                "qid": "q3",
                "route_pred": "policy_clause",
                "abstained": False,
                "ranked": [{"evidence_id": "x", "source_tier": "policy_clause"}],
            },
        ]
        lo, hi = bootstrap_ci(
            qrels,
            run,
            metric="evidence_sufficiency@1",
            k=1,
            samples=1,
            seed=1,
        )
        self.assertAlmostEqual(lo, 2 / 3)
        self.assertAlmostEqual(hi, 2 / 3)

    def test_multi_evidence_requires_all_required_units(self):
        qrels = [
            {
                "qid": "q1",
                "route_gold": "policy_clause",
                "should_abstain": False,
                "sufficient_evidence_ids": ["coverage", "limitation"],
                "required_evidence_ids": ["coverage", "limitation"],
            }
        ]
        partial_run = [
            {
                "qid": "q1",
                "route_pred": "policy_clause",
                "abstained": False,
                "ranked": [{"evidence_id": "coverage", "source_tier": "policy_clause"}],
            }
        ]
        full_run = [
            {
                "qid": "q1",
                "route_pred": "policy_clause",
                "abstained": False,
                "ranked": [
                    {"evidence_id": "coverage", "source_tier": "policy_clause"},
                    {"evidence_id": "limitation", "source_tier": "policy_clause"},
                ],
            }
        ]

        partial = score_run(qrels, partial_run, k=3)
        full = score_run(qrels, full_run, k=3)

        self.assertEqual(partial["evidence_hit@3"], 1.0)
        self.assertEqual(partial["evidence_coverage@3"], 0.5)
        self.assertEqual(partial["evidence_sufficiency@3"], 0.0)
        self.assertEqual(partial["multi_evidence_qrels"], 1.0)
        self.assertEqual(full["evidence_sufficiency@3"], 1.0)

    def test_required_evidence_must_be_part_of_acceptable_set(self):
        with self.assertRaisesRegex(ValueError, "required_evidence_ids must be included"):
            validate_qrel(
                {
                    "qid": "q1",
                    "route_gold": "policy_clause",
                    "should_abstain": False,
                    "sufficient_evidence_ids": ["coverage"],
                    "required_evidence_ids": ["limitation"],
                }
            )

    def test_clustered_bootstrap_keeps_counterfactual_seed_groups_intact(self):
        rows = [
            {"pair_id": "p1", "wrong": True},
            {"pair_id": "p1", "wrong": True},
            {"pair_id": "p1", "wrong": True},
            {"pair_id": "p1", "wrong": True},
            {"pair_id": "p2", "wrong": False},
        ]

        lo, hi = clustered_bootstrap_hit_ci(
            rows,
            "wrong",
            cluster_key="pair_id",
            samples=500,
            seed=7,
        )

        self.assertGreaterEqual(lo, 0.0)
        self.assertLessEqual(hi, 1.0)
        self.assertLess(lo, hi)
        with self.assertRaisesRegex(ValueError, "cluster key"):
            clustered_bootstrap_hit_ci(rows, "wrong", cluster_key="missing", samples=5)


if __name__ == "__main__":
    unittest.main()
