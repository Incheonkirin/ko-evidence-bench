import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ko_evidence_bench.study_report import load_study_report_signals, render_measurement_study


ROOT = Path(__file__).resolve().parents[1]


class StudyReportTest(unittest.TestCase):
    def test_report_uses_checked_in_aggregate_values(self):
        signals = load_study_report_signals(ROOT)
        report = render_measurement_study(signals)

        self.assertIn("NO-GO for public headline claims", report)
        self.assertIn("64.9%", report)
        self.assertIn("+8.5%p", report)
        self.assertIn("31.8%", report)
        self.assertIn("0 / 300 adjudicated labels complete", report)

    def test_build_script_check_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "study.md"
            subprocess.run(
                [sys.executable, "scripts/build_measurement_study.py", "--out", str(out)],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            result = subprocess.run(
                [sys.executable, "scripts/build_measurement_study.py", "--out", str(out), "--check"],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertIn("measurement study draft is current", result.stdout)


if __name__ == "__main__":
    unittest.main()
