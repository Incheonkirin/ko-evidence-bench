import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ko_evidence_bench.metrics import load_jsonl
from ko_evidence_bench.surface_fragmentation import audit_surface_fragmentation, summarize_fragmentation_rows
from scripts.reproduce_surface_fragmentation_audit import render_report


ROOT = Path(__file__).resolve().parents[1]
PROBE_DIR = ROOT / "probes" / "ko_evidence_probe_v0"


class SurfaceFragmentationAuditTest(unittest.TestCase):
    def test_seed_counting_undercounts_public_probe_intents(self):
        rows = audit_surface_fragmentation(
            load_jsonl(PROBE_DIR / "queries.jsonl"),
            load_jsonl(PROBE_DIR / "qrels.jsonl"),
        )
        summary = summarize_fragmentation_rows(rows)

        self.assertEqual(summary["intents"], 4)
        self.assertEqual(summary["qrel_rows"], 9)
        self.assertEqual(summary["seed_rows"], 4)
        self.assertEqual(summary["expanded_rows"], 9)
        self.assertAlmostEqual(summary["seed_recall"], 4 / 9)
        self.assertEqual(summary["max_undercount_factor"], 3.0)
        self.assertEqual(summary["missed_surface_counts"]["messenger_shorthand"], 3)
        self.assertEqual(summary["missed_surface_counts"]["abbreviated"], 1)
        self.assertEqual(summary["missed_surface_counts"]["colloquial"], 1)

    def test_report_and_check_mode(self):
        report = render_report(
            queries_path=PROBE_DIR / "queries.jsonl",
            qrels_path=PROBE_DIR / "qrels.jsonl",
            title="Surface Fragmentation Audit",
        )

        self.assertIn("Surface Fragmentation Audit", report)
        self.assertIn("not a production synonym list", report)
        self.assertIn("aggregate undercount factor", report)
        self.assertIn("cancer_brain_heart_bundle", report)
        self.assertIn("3.0x", report)

        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "surface_fragmentation.md"
            subprocess.run(
                [sys.executable, "scripts/reproduce_surface_fragmentation_audit.py", "--out", str(out)],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            result = subprocess.run(
                [sys.executable, "scripts/reproduce_surface_fragmentation_audit.py", "--out", str(out), "--check"],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )

        self.assertIn("surface fragmentation audit is current", result.stdout)


if __name__ == "__main__":
    unittest.main()
