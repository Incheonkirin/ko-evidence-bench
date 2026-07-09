import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.build_probe_dataset_card import render_dataset_card, render_summary_report


ROOT = Path(__file__).resolve().parents[1]
PROBE_DIR = ROOT / "probes" / "ko_evidence_probe_v0"


class ProbeDatasetCardTest(unittest.TestCase):
    def test_card_describes_release_boundary_and_inventory(self):
        card = render_dataset_card(PROBE_DIR)

        self.assertIn("Ko Evidence Probe v0 Dataset Card", card)
        self.assertIn("synthetic public fixture", card)
        self.assertIn("not a private benchmark release", card)
        self.assertIn("| queries | 13 |", card)
        self.assertIn("| evidence snippets | 7 |", card)
        self.assertIn("| answerable qrels | 11 |", card)
        self.assertIn("| abstention qrels | 2 |", card)
        self.assertIn("Not Intended Use", card)
        self.assertIn("Do not treat this as a human-gold benchmark.", card)
        self.assertIn("Do not read the surface metadata as a synonym dictionary", card)
        self.assertIn("BEIR-style retrieval subset", card)

    def test_summary_report_points_to_card(self):
        report = render_summary_report(PROBE_DIR, PROBE_DIR / "DATASET_CARD.md")

        self.assertIn("Probe Dataset Card Report", report)
        self.assertIn("dataset card generated from public probe files", report)
        self.assertIn("DATASET_CARD.md", report)
        self.assertIn("| surface forms | 4 |", report)

    def test_build_script_check_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            card = Path(tmp) / "DATASET_CARD.md"
            report = Path(tmp) / "probe_dataset_card.md"
            subprocess.run(
                [
                    sys.executable,
                    "scripts/build_probe_dataset_card.py",
                    "--card-out",
                    str(card),
                    "--report-out",
                    str(report),
                ],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/build_probe_dataset_card.py",
                    "--card-out",
                    str(card),
                    "--report-out",
                    str(report),
                    "--check",
                ],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertIn("probe dataset card is current", result.stdout)


if __name__ == "__main__":
    unittest.main()
