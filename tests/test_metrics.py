import unittest

from ko_evidence_bench.metrics import score_run


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


if __name__ == "__main__":
    unittest.main()
