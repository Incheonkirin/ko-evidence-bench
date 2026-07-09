import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ko_evidence_bench.metrics import load_jsonl
from scripts.reproduce_answer_agreement_workflow import FIXTURE, build_double_labeled_rows
from scripts.summarize_answer_audit import render_report


ROOT = Path(__file__).resolve().parents[1]


class AnswerAgreementWorkflowTest(unittest.TestCase):
    def test_double_labeled_fixture_has_expected_agreement(self):
        rows = build_double_labeled_rows(load_jsonl(FIXTURE))
        report = render_report(
            rows,
            audit_path=Path("answer_audit.double_labeled.jsonl"),
            field_a="reviewer_a.answer_label",
            field_b="reviewer_b.answer_label",
        )

        self.assertIn("paired completed rows: 10", report)
        self.assertIn("raw agreement: 80.0%", report)
        self.assertIn("Cohen's kappa: 0.733", report)
        self.assertIn("Disagreement Direction Counts", report)

    def test_reproduction_script_check_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "answer_agreement.md"
            subprocess.run(
                [sys.executable, "scripts/reproduce_answer_agreement_workflow.py", "--out", str(out)],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            report = out.read_text(encoding="utf-8")
            self.assertIn("PASS synthetic answer-quality agreement rehearsal", report)
            self.assertIn("not human-gold evidence", report)
            self.assertIn("Cohen's kappa | 0.733", report)

            result = subprocess.run(
                [sys.executable, "scripts/reproduce_answer_agreement_workflow.py", "--out", str(out), "--check"],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertIn("answer agreement workflow report is current", result.stdout)


if __name__ == "__main__":
    unittest.main()
