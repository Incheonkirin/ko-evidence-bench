import unittest

from ko_evidence_bench.metrics import bootstrap_ci, paired_delta_ci, score_run, summarize_hit_rows


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


if __name__ == "__main__":
    unittest.main()
