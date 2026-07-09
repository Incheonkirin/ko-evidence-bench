import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ko_evidence_bench.metrics import load_jsonl
from ko_evidence_bench.trap_miner import compare_probe_traps, detect_traps, summarize_trap_rows
from scripts.reproduce_probe_trap_mining import render_report


ROOT = Path(__file__).resolve().parents[1]
PROBE_DIR = ROOT / "probes" / "ko_evidence_probe_v0"


class TrapMinerTest(unittest.TestCase):
    def test_detects_core_surface_and_semantic_traps(self):
        bundle = detect_traps("암/뇌/심 진단비 같이 보는 거 맞나요?")
        indemnity = detect_traps("비급여 치료도 실비에서 되는지 궁금해요.")

        self.assertIn("bundle_expansion", {row["trap_class"] for row in bundle})
        self.assertIn("messenger_shorthand", {row["trap_class"] for row in bundle})
        self.assertIn("negation_or_exclusion", {row["trap_class"] for row in indemnity})
        self.assertIn("register_mismatch", {row["trap_class"] for row in indemnity})

    def test_probe_rows_cover_expected_qrel_traps(self):
        rows = compare_probe_traps(
            load_jsonl(PROBE_DIR / "queries.jsonl"),
            load_jsonl(PROBE_DIR / "qrels.jsonl"),
        )
        summary = summarize_trap_rows(rows)

        self.assertEqual(summary["rows"], 13)
        self.assertEqual(summary["rows_with_full_expected_cover"], 13)
        self.assertGreater(summary["rows_with_extra"], 0)
        self.assertEqual(summary["missed"], {})
        self.assertGreaterEqual(summary["detected"]["source_routing"], 3)

    def test_report_and_check_mode(self):
        report = render_report(PROBE_DIR)

        self.assertIn("Public Probe Trap Mining", report)
        self.assertIn("not a synonym dictionary", report)
        self.assertIn("Extra Diagnostic Traps", report)
        self.assertIn("rows with all expected traps detected", report)

        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "trap_mining.md"
            subprocess.run(
                [sys.executable, "scripts/reproduce_probe_trap_mining.py", "--out", str(out)],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            result = subprocess.run(
                [sys.executable, "scripts/reproduce_probe_trap_mining.py", "--out", str(out), "--check"],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )

        self.assertIn("probe trap mining report is current", result.stdout)


if __name__ == "__main__":
    unittest.main()
