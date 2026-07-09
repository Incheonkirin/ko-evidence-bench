import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.build_hero_signal import load_signals, render_markdown, render_svg


ROOT = Path(__file__).resolve().parents[1]


class HeroSignalTest(unittest.TestCase):
    def test_loads_expected_checked_in_signals(self):
        signals = load_signals(ROOT)

        self.assertEqual(signals.retrieval_n, 544)
        self.assertEqual(signals.pack_clause20, "56.4%")
        self.assertEqual(signals.cross_clause20, "64.9%")
        self.assertEqual(signals.cross_delta, "8.5%")
        self.assertEqual(signals.always_route, "21.5%")
        self.assertEqual(signals.cohort_route, "46.9%")
        self.assertEqual(signals.keyword_context_policy, 190)
        self.assertEqual(signals.cohort_context_policy, 28)
        self.assertEqual(signals.completed_labels, 0)
        self.assertEqual(signals.validation_errors, 300)

    def test_rendered_artifacts_keep_claim_gate_visible(self):
        signals = load_signals(ROOT)
        markdown = render_markdown(signals, Path("figures/diagnostic_signal_heatmap.svg"))
        svg = render_svg(signals)

        self.assertIn("diagnostic only; human-gold headline claims blocked", markdown)
        self.assertIn("Unsafe policy fallback", markdown)
        self.assertIn("162 fewer silver fallback errors", markdown)
        self.assertIn("Human-gold gate", markdown)
        self.assertIn("Diagnostic signal heatmap", svg)
        self.assertIn("0/300 labels", svg)

    def test_build_script_check_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = Path(tmp) / "hero_signal.md"
            figure = Path(tmp) / "diagnostic_signal_heatmap.svg"
            subprocess.run(
                [
                    sys.executable,
                    "scripts/build_hero_signal.py",
                    "--report-out",
                    str(report),
                    "--figure-out",
                    str(figure),
                ],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/build_hero_signal.py",
                    "--report-out",
                    str(report),
                    "--figure-out",
                    str(figure),
                    "--check",
                ],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertIn("hero signal artifacts are current", result.stdout)


if __name__ == "__main__":
    unittest.main()
