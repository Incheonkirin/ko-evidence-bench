import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class HumanGoldRehearsalTest(unittest.TestCase):
    def test_reproduce_human_gold_rehearsal(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "human_gold_rehearsal.md"
            subprocess.run(
                [
                    sys.executable,
                    "scripts/reproduce_human_gold_rehearsal.py",
                    "--out",
                    str(out),
                ],
                cwd=root,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            report = out.read_text(encoding="utf-8")

        self.assertIn("Status: **PASS**", report)
        self.assertIn("| route-audit validation errors | 0 | `PASS` |", report)
        self.assertIn("| promoted qid-only labels | 8 | `PASS` |", report)
        self.assertIn("| `formal_only_demo` | 75.0%", report)
        self.assertIn("| `surface_robust_demo` | 100.0%", report)
        self.assertIn("This is not a human-gold result", report)


if __name__ == "__main__":
    unittest.main()
