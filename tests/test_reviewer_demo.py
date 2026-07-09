import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.build_hero_signal import load_signals
from scripts.build_reviewer_demo import render_reviewer_demo


ROOT = Path(__file__).resolve().parents[1]


class ReviewerDemoTest(unittest.TestCase):
    def test_rendered_demo_is_a_short_review_path(self):
        report = render_reviewer_demo(load_signals(ROOT))

        self.assertIn("3-minute diagnostic walkthrough", report)
        self.assertIn("Three-Minute Path", report)
        self.assertIn("reports/claim_ledger.md", report)
        self.assertIn("reports/human_gold_rehearsal_fixture.md", report)
        self.assertIn("reports/study_readiness.md", report)
        self.assertIn("What Not To Infer", report)
        self.assertIn("Do not treat the silver diagnostics as final benchmark numbers.", report)
        self.assertIn("0/300", report)

    def test_build_script_check_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "reviewer_demo.md"
            subprocess.run(
                [sys.executable, "scripts/build_reviewer_demo.py", "--out", str(out)],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            result = subprocess.run(
                [sys.executable, "scripts/build_reviewer_demo.py", "--out", str(out), "--check"],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertIn("reviewer demo is current", result.stdout)


if __name__ == "__main__":
    unittest.main()
