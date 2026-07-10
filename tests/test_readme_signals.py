import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ko_evidence_bench.study_readiness import load_study_readiness, render_readme_signals


ROOT = Path(__file__).resolve().parents[1]


class ReadmeSignalsTest(unittest.TestCase):
    def test_render_uses_current_readiness_values(self):
        block = render_readme_signals(load_study_readiness(ROOT))

        self.assertIn("544 silver rows", block)
        self.assertIn("64.9%", block)
        self.assertIn("444 contrastive triples", block)
        self.assertIn("dense wrong-polarity 29.1%", block)
        self.assertIn("reranker wrong-polarity 48.4%", block)
        self.assertIn("0 / 50 paired", block)
        self.assertIn("kappa 0.000", block)
        self.assertIn("7 not run; 1 blocked", block)
        self.assertIn("NO-GO for public headline claims", block)

    def test_sync_script_replaces_marked_block(self):
        with tempfile.TemporaryDirectory() as tmp:
            readme = Path(tmp) / "README.md"
            readme.write_text(
                "# Example\n\n<!-- BEGIN: current-verified-signals -->\nstale\n<!-- END: current-verified-signals -->\n",
                encoding="utf-8",
            )
            subprocess.run(
                [sys.executable, "scripts/sync_readme_signals.py", "--readme", str(readme)],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )

            text = readme.read_text(encoding="utf-8")
            self.assertIn("544 silver rows", text)
            self.assertNotIn("stale", text)


if __name__ == "__main__":
    unittest.main()
