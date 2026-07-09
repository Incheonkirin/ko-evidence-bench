import csv
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures" / "answer_audit" / "answer_audit_seed.jsonl"


class AnswerReviewWorkflowTest(unittest.TestCase):
    def test_export_validate_import_workflow_script(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "answer_review_workflow.md"
            subprocess.run(
                [sys.executable, "scripts/reproduce_answer_review_workflow.py", "--out", str(out)],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            report = out.read_text(encoding="utf-8")

            self.assertIn("PASS synthetic answer-quality CSV workflow rehearsal", report)
            self.assertIn("not human-gold evidence", report)
            self.assertIn("promoted qid-only labels | 10", report)

            result = subprocess.run(
                [sys.executable, "scripts/reproduce_answer_review_workflow.py", "--out", str(out), "--check"],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertIn("answer review workflow report is current", result.stdout)

    def test_validation_rejects_missing_support_for_sufficient_label(self):
        with tempfile.TemporaryDirectory() as tmp:
            csv_path = Path(tmp) / "answer_review.csv"
            subprocess.run(
                [
                    sys.executable,
                    "scripts/export_answer_review_csv.py",
                    "--audit",
                    str(FIXTURE),
                    "--csv-out",
                    str(csv_path),
                ],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            with csv_path.open(encoding="utf-8", newline="") as f:
                rows = list(csv.DictReader(f))
                fields = list(rows[0].keys())
            rows[0].update(
                {
                    "answer_label": "sufficient",
                    "supporting_evidence_ids": "",
                    "confidence": "high",
                    "rationale_code": "missing_support_fixture",
                    "labeler": "fixture-reviewer",
                }
            )
            with csv_path.open("w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fields)
                writer.writeheader()
                writer.writerows(rows)

            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/validate_answer_review_csv.py",
                    "--csv",
                    str(csv_path),
                    "--require-complete",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("missing_supporting_evidence_ids", result.stdout)


if __name__ == "__main__":
    unittest.main()
