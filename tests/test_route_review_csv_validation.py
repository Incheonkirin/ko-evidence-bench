import csv
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RouteReviewCsvValidationTest(unittest.TestCase):
    def test_validation_report_is_aggregate_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            csv_path = tmp_path / "review.csv"
            report_path = tmp_path / "report.md"
            rows = [
                {
                    "audit_id": "audit-private-1",
                    "qid": "private-q1",
                    "query": "private query must not appear",
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
                    "audit_id": "audit-private-2",
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
                    "scripts/validate_route_review_csv.py",
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
            self.assertIn("rows with validation errors: 1", report)
            self.assertIn("missing_route_gold", report)
            self.assertIn("missing_should_abstain", report)
            self.assertNotIn("private query must not appear", report)
            self.assertNotIn("private context must not appear", report)
            self.assertNotIn("private note must not appear", report)
            self.assertNotIn("audit-private-1", report)
            self.assertNotIn("private-q1", report)

    def test_require_complete_fails_on_invalid_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            csv_path = Path(tmp) / "review.csv"
            csv_path.write_text(
                "audit_id,route_gold,allowed_source_tiers,should_abstain,confidence,rationale_code,labeler\n"
                "a1,human_context_needed,human_context_needed,false,high,needs_private_contract,r1\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/validate_route_review_csv.py",
                    "--csv",
                    str(csv_path),
                    "--require-complete",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("should_abstain_route_mismatch", result.stdout)

    def test_require_complete_passes_for_complete_csv(self):
        with tempfile.TemporaryDirectory() as tmp:
            csv_path = Path(tmp) / "review.csv"
            csv_path.write_text(
                "audit_id,route_gold,allowed_source_tiers,should_abstain,confidence,rationale_code,labeler\n"
                "a1,policy_clause,policy_clause,false,high,contract_clause_direct,r1\n"
                "a2,human_context_needed,human_context_needed,true,medium,needs_private_contract,r1\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/validate_route_review_csv.py",
                    "--csv",
                    str(csv_path),
                    "--require-complete",
                    "--expected-rows",
                    "2",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
