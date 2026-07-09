import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.build_qualitative_gallery import render_gallery


ROOT = Path(__file__).resolve().parents[1]
PROBE_DIR = ROOT / "probes" / "ko_evidence_probe_v0"


class QualitativeGalleryTest(unittest.TestCase):
    def test_gallery_shows_side_by_side_route_failures(self):
        report = render_gallery(PROBE_DIR)

        self.assertIn("synthetic qualitative examples only", report)
        self.assertIn("policy_only_baseline", report)
        self.assertIn("source_routed_candidate", report)
        self.assertIn("probe-underwriting-messenger", report)
        self.assertIn("probe-claims-docs", report)
        self.assertIn("ABSTAIN", report)
        self.assertIn("source-route behavior the benchmark is meant to measure", report)

    def test_build_script_check_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "qualitative_gallery.md"
            subprocess.run(
                [sys.executable, "scripts/build_qualitative_gallery.py", "--out", str(out)],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            result = subprocess.run(
                [sys.executable, "scripts/build_qualitative_gallery.py", "--out", str(out), "--check"],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertIn("qualitative gallery is current", result.stdout)


if __name__ == "__main__":
    unittest.main()
