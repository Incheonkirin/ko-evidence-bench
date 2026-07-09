import unittest

from ko_evidence_bench.route_labels import (
    always_policy_baseline,
    derive_route_label,
    route_floor,
    summarize_route_labels,
)


class RouteLabelTest(unittest.TestCase):
    def test_contract_need_routes_to_human_context(self):
        label = derive_route_label(
            {
                "qid": "q1",
                "needs_contract": True,
                "reason_code": "needs_contract",
                "gate_category": "coverage",
            }
        )
        self.assertEqual(label["route_gold"], "human_context_needed")
        self.assertTrue(label["should_abstain"])
        self.assertEqual(label["confidence"], "high")

    def test_claim_language_routes_to_claims_faq(self):
        label = derive_route_label(
            {
                "qid": "q2",
                "needs_contract": False,
                "reason_code": "single_sufficient",
                "gate_category": "청구서류",
            }
        )
        self.assertEqual(label["route_gold"], "claims_faq")
        self.assertFalse(label["should_abstain"])

    def test_baseline_summaries(self):
        labels = [
            {"route_gold": "policy_clause", "should_abstain": False, "confidence": "medium", "rationale_code": "x"},
            {
                "route_gold": "human_context_needed",
                "should_abstain": True,
                "confidence": "high",
                "rationale_code": "y",
            },
            {"route_gold": "policy_clause", "should_abstain": False, "confidence": "low", "rationale_code": "x"},
        ]
        summary = summarize_route_labels(labels)
        self.assertEqual(summary["route_gold"]["policy_clause"], 2)
        self.assertAlmostEqual(always_policy_baseline(labels)["route_accuracy"], 2 / 3)
        self.assertAlmostEqual(route_floor(labels)["route_accuracy"], 2 / 3)


if __name__ == "__main__":
    unittest.main()
