import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.build_claim_ledger import claim_rows, render_claim_ledger
from scripts.build_hero_signal import load_signals


ROOT = Path(__file__).resolve().parents[1]


class ClaimLedgerTest(unittest.TestCase):
    def test_claim_rows_separate_diagnostic_blocked_and_scope(self):
        rows = claim_rows(load_signals(ROOT))
        statuses = {row.status for row in rows}
        areas = {row.claim_area for row in rows}

        self.assertIn("DIAGNOSTIC", statuses)
        self.assertIn("BLOCKED", statuses)
        self.assertIn("OUT OF SCOPE", statuses)
        self.assertIn("Clause recovery", areas)
        self.assertIn("Human-gold benchmark", areas)
        self.assertIn("General Korean IR", areas)

    def test_rendered_ledger_names_allowed_and_forbidden_wording(self):
        report = render_claim_ledger(load_signals(ROOT))

        self.assertIn("diagnostic claims only; human-gold headline claims blocked", report)
        self.assertIn("allowed wording", report)
        self.assertIn("do not say", report)
        self.assertIn("This is a final benchmark result", report)
        self.assertIn("The results represent all Korean retrieval", report)
        self.assertIn("300 validation errors", report)

    def test_build_script_check_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "claim_ledger.md"
            subprocess.run(
                [sys.executable, "scripts/build_claim_ledger.py", "--out", str(out)],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            result = subprocess.run(
                [sys.executable, "scripts/build_claim_ledger.py", "--out", str(out), "--check"],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertIn("claim ledger is current", result.stdout)


if __name__ == "__main__":
    unittest.main()
