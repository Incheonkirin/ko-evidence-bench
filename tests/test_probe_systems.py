import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ko_evidence_bench.probe_systems import build_probe_runs, load_probe_inputs, score_probe_runs
from scripts.reproduce_probe_system_comparison import render_report


ROOT = Path(__file__).resolve().parents[1]
PROBE_DIR = ROOT / "probes" / "ko_evidence_probe_v0"


class ProbeSystemComparisonTest(unittest.TestCase):
    def test_probe_systems_generate_complete_runs(self):
        inputs = load_probe_inputs(PROBE_DIR)
        runs = build_probe_runs(inputs)

        self.assertEqual(set(runs), {"probe_literal_lexical", "probe_normalized_lexical", "probe_route_aware_rerank"})
        self.assertEqual(len(inputs.queries), 13)
        for rows in runs.values():
            self.assertEqual({row["qid"] for row in rows}, {row["qid"] for row in inputs.queries})

    def test_route_aware_system_beats_literal_fixture(self):
        inputs = load_probe_inputs(PROBE_DIR)
        scores = {row["system_id"]: row for row in score_probe_runs(inputs, build_probe_runs(inputs), k=3)}

        literal = scores["probe_literal_lexical"]
        route_aware = scores["probe_route_aware_rerank"]

        self.assertLess(literal["route_accuracy"], route_aware["route_accuracy"])
        self.assertGreater(route_aware["task_success@3"], literal["task_success@3"])
        self.assertEqual(route_aware["wrong_source_rate@3"], 0.0)
        self.assertEqual(route_aware["abstention_recall"], 1.0)

    def test_report_and_check_mode(self):
        report = render_report(PROBE_DIR)
        self.assertIn("Public Probe System Comparison", report)
        self.assertIn("probe_route_aware_rerank", report)
        self.assertIn("not a full private benchmark matrix", report)

        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "probe_systems.md"
            subprocess.run(
                [sys.executable, "scripts/reproduce_probe_system_comparison.py", "--out", str(out)],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            result = subprocess.run(
                [sys.executable, "scripts/reproduce_probe_system_comparison.py", "--out", str(out), "--check"],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )

        self.assertIn("probe system comparison report is current", result.stdout)


if __name__ == "__main__":
    unittest.main()
