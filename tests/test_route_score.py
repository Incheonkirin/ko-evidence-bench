import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ko_evidence_bench.route_score import (
    bootstrap_route_ci,
    paired_route_delta_ci,
    route_confusion_counts,
    route_slice_scores,
    score_route_run,
)


ROOT = Path(__file__).resolve().parents[1]


class RouteScoreTest(unittest.TestCase):
    def test_route_metrics(self):
        labels = [
            {"qid": "q1", "route_gold": "policy_clause", "should_abstain": False},
            {"qid": "q2", "route_gold": "claims_faq", "should_abstain": False},
            {"qid": "q3", "route_gold": "human_context_needed", "should_abstain": True},
        ]
        run = [
            {"qid": "q1", "route_pred": "policy_clause", "abstained": False},
            {"qid": "q2", "route_pred": "claims_faq", "abstained": False},
            {"qid": "q3", "route_pred": "human_context_needed", "abstained": True},
        ]

        scores = score_route_run(labels, run)

        self.assertEqual(scores["n"], 3.0)
        self.assertEqual(scores["missing_predictions"], 0.0)
        self.assertEqual(scores["route_accuracy"], 1.0)
        self.assertEqual(scores["abstention_precision"], 1.0)
        self.assertEqual(scores["abstention_recall"], 1.0)

    def test_missing_prediction_counts_as_abstained_out_of_scope(self):
        labels = [
            {"qid": "q1", "route_gold": "policy_clause", "should_abstain": False},
            {"qid": "q2", "route_gold": "human_context_needed", "should_abstain": True},
        ]
        run = [{"qid": "q1", "route_pred": "policy_clause", "abstained": False}]

        scores = score_route_run(labels, run)

        self.assertEqual(scores["missing_predictions"], 1.0)
        self.assertEqual(scores["route_accuracy"], 0.5)
        self.assertEqual(scores["abstention_precision"], 1.0)
        self.assertEqual(scores["abstention_recall"], 1.0)

    def test_route_slice_scores_and_confusions(self):
        labels = [
            {"qid": "q1", "route_gold": "policy_clause", "should_abstain": False},
            {"qid": "q2", "route_gold": "claims_faq", "should_abstain": False},
            {"qid": "q3", "route_gold": "human_context_needed", "should_abstain": True},
        ]
        run = [
            {"qid": "q1", "route_pred": "policy_clause", "abstained": False},
            {"qid": "q2", "route_pred": "policy_clause", "abstained": False},
        ]

        slices = route_slice_scores(labels, run)
        confusions = route_confusion_counts(labels, run)

        self.assertEqual(slices["policy_clause"]["route_accuracy"], 1.0)
        self.assertEqual(slices["claims_faq"]["route_accuracy"], 0.0)
        self.assertEqual(slices["human_context_needed"]["missing_predictions"], 1.0)
        self.assertEqual(slices["human_context_needed"]["abstained_rate"], 1.0)
        self.assertEqual(slices["human_context_needed"]["expected_abstention_rate"], 1.0)
        self.assertEqual(confusions[("claims_faq", "policy_clause")], 1)
        self.assertEqual(confusions[("human_context_needed", "out_of_scope")], 1)

    def test_bootstrap_and_paired_delta(self):
        labels = [
            {"qid": "q1", "route_gold": "policy_clause", "should_abstain": False},
            {"qid": "q2", "route_gold": "claims_faq", "should_abstain": False},
            {"qid": "q3", "route_gold": "human_context_needed", "should_abstain": True},
        ]
        baseline = [
            {"qid": "q1", "route_pred": "policy_clause", "abstained": False},
            {"qid": "q2", "route_pred": "policy_clause", "abstained": False},
            {"qid": "q3", "route_pred": "policy_clause", "abstained": False},
        ]
        candidate = [
            {"qid": "q1", "route_pred": "policy_clause", "abstained": False},
            {"qid": "q2", "route_pred": "claims_faq", "abstained": False},
            {"qid": "q3", "route_pred": "human_context_needed", "abstained": True},
        ]

        lo, hi = bootstrap_route_ci(labels, candidate, metric="route_accuracy", samples=100, seed=7)
        delta, delta_lo, delta_hi = paired_route_delta_ci(
            labels,
            baseline,
            candidate,
            samples=100,
            seed=7,
        )

        self.assertLessEqual(0.0, lo)
        self.assertLessEqual(lo, hi)
        self.assertLessEqual(hi, 1.0)
        self.assertAlmostEqual(delta, 2 / 3)
        self.assertLessEqual(delta_lo, delta)
        self.assertGreaterEqual(delta_hi, delta)

    def test_reproduce_route_scorecard_script(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "route_scorecard.md"
            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/reproduce_route_scorecard.py",
                    "--out",
                    str(out),
                    "--samples",
                    "100",
                ],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertIn("Route Scorecard Fixture", result.stdout)
            report = out.read_text(encoding="utf-8")
            self.assertIn("`source_routed_demo`", report)
            self.assertIn("Route Accuracy By Gold Source Tier", report)
            self.assertIn("Largest Route Confusions", report)


if __name__ == "__main__":
    unittest.main()
