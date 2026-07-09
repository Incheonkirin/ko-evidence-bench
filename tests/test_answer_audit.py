import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ko_evidence_bench.answer_audit import answer_quality_summary, validate_answer_audit_rows
from ko_evidence_bench.metrics import load_jsonl


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures" / "answer_audit" / "answer_audit_seed.jsonl"


class AnswerAuditTest(unittest.TestCase):
    def test_fixture_validates_and_summarizes(self):
        rows = load_jsonl(FIXTURE)
        validation = validate_answer_audit_rows(
            rows,
            label_prefix="adjudicated",
            require_complete=True,
            require_qid_only=True,
        )
        summary = answer_quality_summary(rows, label_prefix="adjudicated")

        self.assertEqual(validation["error_count"], 0)
        self.assertEqual(validation["completed"], 10)
        self.assertEqual(validation["label_counts"]["sufficient"], 4)
        self.assertEqual(validation["label_counts"]["unsafe_answer"], 2)
        self.assertEqual(summary["task_success"], 6)
        self.assertIn("formal_only_demo", summary["by_system"])
        self.assertIn("messenger_shorthand", summary["by_surface"])

    def test_raw_text_fields_are_rejected(self):
        rows = load_jsonl(FIXTURE)
        rows[0]["query"] = "raw private text should not be public"

        validation = validate_answer_audit_rows(
            rows,
            label_prefix="adjudicated",
            require_complete=True,
            require_qid_only=True,
        )

        self.assertEqual(validation["error_count"], 1)
        self.assertIn("raw_text_fields_present:query", validation["row_errors"][0]["errors"])

    def test_reproduction_script_check_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "answer_quality.md"
            subprocess.run(
                [sys.executable, "scripts/reproduce_answer_quality_audit.py", "--out", str(out)],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            report = out.read_text(encoding="utf-8")
            self.assertIn("answer-quality audit rehearsal", report)
            self.assertIn("not human-gold answer-quality evidence", report)
            self.assertIn("not a final benchmark claim", report)

            result = subprocess.run(
                [sys.executable, "scripts/reproduce_answer_quality_audit.py", "--out", str(out), "--check"],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertIn("answer quality audit report is current", result.stdout)


if __name__ == "__main__":
    unittest.main()
