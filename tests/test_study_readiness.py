import unittest
from pathlib import Path

from ko_evidence_bench.study_readiness import load_study_readiness, render_study_readiness


ROOT = Path(__file__).resolve().parents[1]


class StudyReadinessTest(unittest.TestCase):
    def test_current_reports_are_parsed_as_no_go(self):
        readiness = load_study_readiness(ROOT)

        self.assertEqual(readiness.retrieval_n, 544)
        self.assertEqual(readiness.best_clause20, "64.9%")
        self.assertEqual(readiness.always_policy_route_acc, "21.5%")
        self.assertEqual(readiness.keyword_route_acc, "31.8%")
        self.assertEqual(readiness.cohort_aware_route_acc, "46.9%")
        self.assertEqual(readiness.agreement_paired_rows, 0)
        self.assertEqual(readiness.agreement_raw, "0.0%")
        self.assertEqual(readiness.agreement_kappa, 0.0)
        self.assertEqual(readiness.completed_route_labels, 0)
        self.assertEqual(readiness.route_validation_errors, 300)
        self.assertFalse(readiness.headline_ready)

    def test_render_names_the_gate_without_private_text(self):
        report = render_study_readiness(load_study_readiness(ROOT))

        self.assertIn("NO-GO for public headline claims", report)
        self.assertIn("human-adjudicated source-route labels", report)
        self.assertIn("paired double-label rows", report)
        self.assertIn("Cohen's kappa", report)
        self.assertNotIn("raw queries", report)


if __name__ == "__main__":
    unittest.main()
