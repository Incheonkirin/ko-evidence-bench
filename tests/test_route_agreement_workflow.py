import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ko_evidence_bench.metrics import load_jsonl
from scripts.reproduce_route_agreement_workflow import FIXTURE, build_double_labeled_rows
from scripts.summarize_route_audit import render_report


ROOT = Path(__file__).resolve().parents[1]


class RouteAgreementWorkflowTest(unittest.TestCase):
    def test_double_labeled_fixture_has_expected_agreement(self):
        rows = build_double_labeled_rows(load_jsonl(FIXTURE))
        report = render_report(
            rows,
            audit_path=Path("route_audit.double_labeled.jsonl"),
            field_a="reviewer_a.route_gold",
            field_b="reviewer_b.route_gold",
        )

        self.assertIn("paired completed rows: 3", report)
        self.assertIn("raw agreement: 66.7%", report)
        self.assertIn("Cohen's kappa: 0.571", report)
        self.assertIn("disagreement rows: 1", report)
        self.assertIn("Disagreement Direction Counts", report)
        self.assertIn("policy_clause -> product_disclosure", report)

    def test_reproduction_script_check_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "route_agreement.md"
            subprocess.run(
                [sys.executable, "scripts/reproduce_route_agreement_workflow.py", "--out", str(out)],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            report = out.read_text(encoding="utf-8")
            self.assertIn("PASS synthetic source-route agreement rehearsal", report)
            self.assertIn("not human-gold evidence", report)
            self.assertIn("Cohen's kappa | 0.571", report)

            result = subprocess.run(
                [sys.executable, "scripts/reproduce_route_agreement_workflow.py", "--out", str(out), "--check"],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertIn("route agreement workflow report is current", result.stdout)


if __name__ == "__main__":
    unittest.main()
