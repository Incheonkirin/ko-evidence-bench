import csv
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RouteReviewBatchTest(unittest.TestCase):
    def test_batch_selects_priority_rows_and_report_is_aggregate_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source = tmp_path / "review.csv"
            out_csv = tmp_path / "batch.csv"
            report_path = tmp_path / "summary.md"
            rows = [
                {
                    "audit_id": "a1",
                    "qid": "private-q1",
                    "query": "do not leak query one",
                    "context": "do not leak context one",
                    "silver_confidence": "high",
                    "silver_should_abstain": "false",
                    "silver_route_gold": "policy_clause",
                    "reason_code": "single_sufficient",
                    "needs_contract": "false",
                    "product_divergent": "false",
                    "route_gold": "",
                    "allowed_source_tiers": "",
                    "should_abstain": "",
                    "confidence": "",
                    "rationale_code": "",
                    "labeler": "",
                },
                {
                    "audit_id": "a2",
                    "qid": "private-q2",
                    "query": "do not leak query two",
                    "context": "do not leak context two",
                    "silver_confidence": "low",
                    "silver_should_abstain": "true",
                    "silver_route_gold": "human_context_needed",
                    "reason_code": "requires_exclusion_check",
                    "needs_contract": "true",
                    "product_divergent": "true",
                    "route_gold": "",
                    "allowed_source_tiers": "",
                    "should_abstain": "",
                    "confidence": "",
                    "rationale_code": "",
                    "labeler": "",
                },
            ]
            with source.open("w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(rows)

            subprocess.run(
                [
                    sys.executable,
                    "scripts/build_route_review_batch.py",
                    "--csv",
                    str(source),
                    "--out-csv",
                    str(out_csv),
                    "--report-out",
                    str(report_path),
                    "--limit",
                    "1",
                ],
                cwd=ROOT,
                check=True,
            )

            with out_csv.open(encoding="utf-8", newline="") as f:
                batch_rows = list(csv.DictReader(f))
            self.assertEqual(batch_rows[0]["audit_id"], "a2")

            report = report_path.read_text(encoding="utf-8")
            self.assertIn("silver_low_confidence", report)
            self.assertIn("selected rows: 1", report)
            self.assertNotIn("do not leak query", report)
            self.assertNotIn("private-q2", report)


if __name__ == "__main__":
    unittest.main()
