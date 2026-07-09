import unittest

from ko_evidence_bench.agreement import cohens_kappa, observed_agreement, paired_labels


class AgreementTest(unittest.TestCase):
    def test_observed_agreement_and_kappa(self):
        a = ["x", "x", "y", "y"]
        b = ["x", "y", "y", "y"]
        self.assertAlmostEqual(observed_agreement(a, b), 0.75)
        self.assertAlmostEqual(cohens_kappa(a, b), 0.5)

    def test_paired_labels_ignores_missing_values(self):
        rows = [
            {"silver": {"route_gold": "policy_clause"}, "human_route_gold": "policy_clause"},
            {"silver": {"route_gold": "claims_faq"}, "human_route_gold": ""},
            {"silver": {"route_gold": "expert_answer"}},
        ]
        a, b = paired_labels(rows, "silver.route_gold", "human_route_gold")
        self.assertEqual(a, ["policy_clause"])
        self.assertEqual(b, ["policy_clause"])


if __name__ == "__main__":
    unittest.main()
