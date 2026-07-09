import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "build_route_audit_pack.py"
spec = importlib.util.spec_from_file_location("build_route_audit_pack", SCRIPT)
audit = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(audit)


class RouteAuditPackTest(unittest.TestCase):
    def test_audit_rows_keep_raw_text_out_of_report(self):
        qrels = [
            {
                "qid": "q1",
                "query": "private query one",
                "body": "private body one",
                "gate_category": "청구서류",
                "intent": "claim",
                "reason_code": "claims_ops",
            },
            {
                "qid": "q2",
                "query": "private query two",
                "body": "private body two",
                "gate_category": "계약",
                "intent": "contract",
                "reason_code": "needs_contract",
            },
        ]
        labels = [
            {
                "qid": "q1",
                "route_gold": "claims_faq",
                "allowed_source_tiers": ["claims_faq"],
                "should_abstain": False,
                "confidence": "medium",
                "rationale_code": "claims_ops",
            },
            {
                "qid": "q2",
                "route_gold": "human_context_needed",
                "allowed_source_tiers": ["human_context_needed"],
                "should_abstain": True,
                "confidence": "high",
                "rationale_code": "needs_private_contract",
            },
        ]
        rows = audit.build_audit_rows(qrels, labels, sample_size=2, min_per_route=1, seed=3)
        self.assertEqual(len(rows), 2)
        self.assertIn("query", rows[0])
        self.assertIn("human_route_gold", rows[0])

        report = audit.render_report(
            rows,
            qrels_path=Path("private_qrels.jsonl"),
            labels_path=Path("private_labels.jsonl"),
            audit_out=Path("private_audit.jsonl"),
            seed=3,
            min_per_route=1,
        )
        self.assertIn("sampled rows: 2", report)
        self.assertNotIn("private query", report)
        self.assertNotIn("q1", report)
        self.assertNotIn("q2", report)


if __name__ == "__main__":
    unittest.main()
