import csv
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RouteReviewBriefTest(unittest.TestCase):
    def test_brief_is_aggregate_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            csv_path = tmp_path / "review.csv"
            report_path = tmp_path / "brief.md"
            rows = [
                {
                    "qid": "private-qid-1",
                    "query": "do not leak query",
                    "context": "do not leak context",
                    "notes": "do not leak notes",
                    "silver_route_gold": "human_context_needed",
                    "silver_confidence": "low",
                    "silver_rationale_code": "needs_private_contract",
                    "silver_should_abstain": "true",
                    "answerability": "partial",
                    "answer_structure": "synthesis_set",
                    "reason_code": "needs_contract",
                    "needs_contract": "true",
                    "product_divergent": "false",
                    "route_gold": "",
                    "allowed_source_tiers": "",
                    "should_abstain": "",
                    "confidence": "",
                    "rationale_code": "",
                    "labeler": "",
                }
            ]
            with csv_path.open("w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(rows)

            subprocess.run(
                [
                    sys.executable,
                    "scripts/build_route_review_brief.py",
                    "--csv",
                    str(csv_path),
                    "--report-out",
                    str(report_path),
                ],
                cwd=ROOT,
                check=True,
            )

            report = report_path.read_text(encoding="utf-8")
            self.assertIn("silver `low` confidence", report)
            self.assertIn("needs_private_contract", report)
            self.assertNotIn("do not leak query", report)
            self.assertNotIn("private-qid-1", report)
            self.assertNotIn("do not leak notes", report)


if __name__ == "__main__":
    unittest.main()
