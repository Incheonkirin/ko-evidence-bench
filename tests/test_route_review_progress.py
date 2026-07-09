import csv
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RouteReviewProgressTest(unittest.TestCase):
    def test_progress_report_is_aggregate_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            csv_path = tmp_path / "review.csv"
            report_path = tmp_path / "report.md"
            rows = [
                {
                    "audit_id": "a1",
                    "qid": "private-q1",
                    "query": "private text must not appear",
                    "context": "private context must not appear",
                    "route_gold": "claims_faq",
                    "allowed_source_tiers": "claims_faq;policy_clause",
                    "should_abstain": "false",
                    "confidence": "high",
                    "rationale_code": "claims_ops",
                    "labeler": "r1",
                    "notes": "private note must not appear",
                },
                {
                    "audit_id": "a2",
                    "qid": "private-q2",
                    "query": "another private query",
                    "context": "another private context",
                    "route_gold": "",
                    "allowed_source_tiers": "",
                    "should_abstain": "",
                    "confidence": "",
                    "rationale_code": "",
                    "labeler": "",
                    "notes": "",
                },
            ]
            with csv_path.open("w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(rows)

            subprocess.run(
                [
                    sys.executable,
                    "scripts/check_route_review_progress.py",
                    "--csv",
                    str(csv_path),
                    "--report-out",
                    str(report_path),
                ],
                cwd=ROOT,
                check=True,
            )

            report = report_path.read_text(encoding="utf-8")
            self.assertIn("complete rows: 1", report)
            self.assertIn("completion rate: 50.0%", report)
            self.assertIn("missing_route_gold", report)
            self.assertNotIn("private text must not appear", report)
            self.assertNotIn("private note must not appear", report)

    def test_fail_if_incomplete(self):
        with tempfile.TemporaryDirectory() as tmp:
            csv_path = Path(tmp) / "review.csv"
            csv_path.write_text(
                "audit_id,route_gold,allowed_source_tiers,should_abstain,confidence,rationale_code,labeler\n"
                "a1,,,,,,\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/check_route_review_progress.py",
                    "--csv",
                    str(csv_path),
                    "--fail-if-incomplete",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )

            self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
