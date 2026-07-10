import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ko_evidence_bench.alignment import load_alignment_items, overall_status, render_alignment_report


ROOT = Path(__file__).resolve().parents[1]


class AlignmentTest(unittest.TestCase):
    def test_current_inventory_is_measured_v0_with_expansions_pending(self):
        items = load_alignment_items(ROOT)
        statuses = {item.area: item.status for item in items}

        self.assertEqual(statuses["Measured retrieval result"], "PASS")
        self.assertEqual(statuses["Polarity stress result"], "PASS")
        self.assertEqual(statuses["Real-query distribution shift"], "PASS")
        self.assertEqual(statuses["Evidence-sufficiency evaluator"], "PASS")
        self.assertEqual(statuses["Safe external-run contract"], "PASS")
        self.assertEqual(statuses["Clean-room public reproduction"], "PASS")
        self.assertEqual(statuses["Public/private boundary"], "PASS")
        self.assertEqual(statuses["Human-validated source routing"], "PENDING")
        self.assertEqual(statuses["Full external-system matrix"], "PENDING")
        self.assertEqual(overall_status(items), "MEASURED V0")

    def test_report_is_result_oriented(self):
        report = render_alignment_report(load_alignment_items(ROOT))

        self.assertIn("Overall status: **MEASURED V0**", report)
        self.assertIn("retrieval lift", report)
        self.assertIn("polarity stress study", report)
        self.assertIn("not a release gate ledger", report)
        self.assertIn("genuinely labeled messenger-turn retrieval slice", report)

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

        self.assertIn("research status report is current", result.stdout)


if __name__ == "__main__":
    unittest.main()
