import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ko_evidence_bench.alignment import load_alignment_items, overall_status, render_alignment_report


ROOT = Path(__file__).resolve().parents[1]


class AlignmentTest(unittest.TestCase):
    def test_current_alignment_is_blocked_only_by_human_gold(self):
        items = load_alignment_items(ROOT)
        statuses = {item.area: item.status for item in items}

        self.assertEqual(statuses["Report-first artifact"], "PASS")
        self.assertEqual(statuses["Hero diagnostic figure"], "PASS")
        self.assertEqual(statuses["Claim wording ledger"], "PASS")
        self.assertEqual(statuses["Reviewer demo path"], "PASS")
        self.assertEqual(statuses["Containerized reproduction path"], "PASS")
        self.assertEqual(statuses["Public probe set and privacy screen"], "PASS")
        self.assertEqual(statuses["Qualitative failure gallery"], "PASS")
        self.assertEqual(statuses["Dictionary scope guard"], "PASS")
        self.assertEqual(statuses["Multi-source evidence frame"], "PASS")
        self.assertEqual(statuses["Real-query substrate inventory"], "PASS")
        self.assertEqual(statuses["Surface-form robustness axis"], "PASS")
        self.assertEqual(statuses["Route-surface diagnostic axis"], "PASS")
        self.assertEqual(statuses["Runtime-surface retrieval-hit axis"], "PASS")
        self.assertEqual(statuses["Layer attribution axis"], "PASS")
        self.assertEqual(statuses["Intent-family inventory axis"], "PASS")
        self.assertEqual(statuses["Normalization ablation axis"], "PASS")
        self.assertEqual(statuses["Qid-only route scorecard path"], "PASS")
        self.assertEqual(statuses["Per-source route failure slices"], "PASS")
        self.assertEqual(statuses["Query-cohort route slices"], "PASS")
        self.assertEqual(statuses["Query-substrate profile"], "PASS")
        self.assertEqual(statuses["Cohort-aware routing baseline"], "PASS")
        self.assertEqual(statuses["Human-label progress gate"], "PASS")
        self.assertEqual(statuses["Human-audit coverage gate"], "PASS")
        self.assertEqual(statuses["Human-gold promotion rehearsal"], "PASS")
        self.assertEqual(statuses["Human-gold route labels"], "BLOCKED")
        self.assertEqual(overall_status(items), "NO-GO FOR HEADLINE CLAIMS")

    def test_report_names_remaining_gate(self):
        report = render_alignment_report(load_alignment_items(ROOT))

        self.assertIn("Overall status: **NO-GO FOR HEADLINE CLAIMS**", report)
        self.assertIn("Dictionary scope guard", report)
        self.assertIn("Hero diagnostic figure", report)
        self.assertIn("memorable findings", report)
        self.assertIn("Claim wording ledger", report)
        self.assertIn("what the evidence can and cannot support", report)
        self.assertIn("Reviewer demo path", report)
        self.assertIn("understand the study artifact before reading framework code", report)
        self.assertIn("Containerized reproduction path", report)
        self.assertIn("without first configuring a Python environment", report)
        self.assertIn("Public probe set and privacy screen", report)
        self.assertIn("screened probe set", report)
        self.assertIn("Qualitative failure gallery", report)
        self.assertIn("concrete failure modes", report)
        self.assertIn("Multi-source evidence frame", report)
        self.assertIn("Real-query substrate inventory", report)
        self.assertIn("Surface-form robustness axis", report)
        self.assertIn("Route-surface diagnostic axis", report)
        self.assertIn("Runtime-surface retrieval-hit axis", report)
        self.assertIn("Layer attribution axis", report)
        self.assertIn("where failures accumulate", report)
        self.assertIn("Intent-family inventory axis", report)
        self.assertIn("private silver inventories", report)
        self.assertIn("Normalization ablation axis", report)
        self.assertIn("lift gate measure", report)
        self.assertIn("Per-source route failure slices", report)
        self.assertIn("Query-cohort route slices", report)
        self.assertIn("Query-substrate profile", report)
        self.assertIn("Cohort-aware routing baseline", report)
        self.assertIn("silver lift gate", report)
        self.assertIn("CSV validation", report)
        self.assertIn("Human-audit coverage gate", report)
        self.assertIn("surface/intent design", report)
        self.assertIn("Human-gold promotion rehearsal", report)
        self.assertIn("remaining path to measurement-study scorecards", report)
        self.assertIn("lack independent", report)
        self.assertIn("agreement", report)
        self.assertIn("evidence", report)
        self.assertIn("kappa 0.000", report)

    def test_build_script_check_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "alignment.md"
            subprocess.run(
                [sys.executable, "scripts/build_alignment_report.py", "--out", str(out)],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            result = subprocess.run(
                [sys.executable, "scripts/build_alignment_report.py", "--out", str(out), "--check"],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertIn("flagship alignment report is current", result.stdout)


if __name__ == "__main__":
    unittest.main()
