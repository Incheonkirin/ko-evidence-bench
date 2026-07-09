import unittest

from ko_evidence_bench.route_audit import promote_audit_rows, validate_audit_rows


class RouteAuditTest(unittest.TestCase):
    def test_validate_and_promote_adjudicated_rows(self):
        rows = [
            {
                "qid": "q1",
                "adjudicated": {
                    "route_gold": "claims_faq",
                    "allowed_source_tiers": ["claims_faq"],
                    "should_abstain": False,
                    "confidence": "high",
                    "rationale_code": "claims_ops",
                    "labeler": "aa",
                },
            },
            {
                "qid": "q2",
                "adjudicated": {
                    "route_gold": "human_context_needed",
                    "allowed_source_tiers": ["human_context_needed"],
                    "should_abstain": True,
                    "confidence": "medium",
                    "rationale_code": "needs_private_contract",
                    "labeler": "aa",
                },
            },
        ]
        result = validate_audit_rows(rows, label_prefix="adjudicated", require_complete=True)
        self.assertEqual(result["n"], 2)
        self.assertEqual(result["completed"], 2)
        self.assertEqual(result["error_count"], 0)

        promoted = promote_audit_rows(rows, label_prefix="adjudicated")
        self.assertEqual(len(promoted), 2)
        self.assertEqual(sorted(promoted[0]), [
            "allowed_source_tiers",
            "confidence",
            "labeler",
            "qid",
            "rationale_code",
            "route_gold",
            "should_abstain",
        ])

    def test_validation_reports_incomplete_rows(self):
        rows = [
            {
                "qid": "q1",
                "adjudicated": {
                    "route_gold": "",
                    "allowed_source_tiers": [],
                    "should_abstain": None,
                    "confidence": "",
                    "rationale_code": "",
                },
            }
        ]
        result = validate_audit_rows(rows, label_prefix="adjudicated", require_complete=True)
        self.assertEqual(result["completed"], 0)
        self.assertEqual(result["error_count"], 1)
        self.assertIn("missing_route_gold", result["row_errors"][0]["errors"])


if __name__ == "__main__":
    unittest.main()
