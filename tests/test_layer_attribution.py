import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ko_evidence_bench.layer_attribution import attribute_run, layer_breakdown, summarize_system, trap_failure_layers
from ko_evidence_bench.metrics import load_jsonl


ROOT = Path(__file__).resolve().parents[1]


class LayerAttributionTest(unittest.TestCase):
    def setUp(self):
        self.qrels = load_jsonl(ROOT / "fixtures" / "surface_qrels.jsonl")
        self.baseline = load_jsonl(ROOT / "fixtures" / "surface_runs" / "formal_only_demo.jsonl")
        self.candidate = load_jsonl(ROOT / "fixtures" / "surface_runs" / "surface_robust_demo.jsonl")

    def test_baseline_failures_are_attributed_to_layers(self):
        rows = attribute_run(self.qrels, self.baseline, system="formal_only_demo", k=3)
        summary = summarize_system(rows)
        layer_counts = {
            row["failure_layer"]: row["rows"]
            for row in layer_breakdown(rows)
            if row["system"] == "formal_only_demo"
        }

        self.assertEqual(summary["n"], 8.0)
        self.assertEqual(summary["success_rate"], 3 / 8)
        self.assertEqual(summary["failure_rows"], 5.0)
        self.assertEqual(summary["dominant_failure_layer"], "surface_fragmentation")
        self.assertEqual(layer_counts["surface_fragmentation"], 2.0)
        self.assertEqual(layer_counts["register_gap"], 1.0)
        self.assertEqual(layer_counts["source_route_failure"], 1.0)
        self.assertEqual(layer_counts["abstention_failure"], 1.0)

    def test_candidate_has_no_failure_mass(self):
        rows = attribute_run(self.qrels, self.candidate, system="surface_robust_demo", k=3)
        summary = summarize_system(rows)
        layers = {row["failure_layer"] for row in layer_breakdown(rows)}

        self.assertEqual(summary["success_rate"], 1.0)
        self.assertEqual(summary["failure_rows"], 0.0)
        self.assertEqual(summary["dominant_failure_layer"], "success")
        self.assertEqual(layers, {"success"})

    def test_trap_layer_breakdown_keeps_diagnostic_slices(self):
        rows = attribute_run(self.qrels, self.baseline, system="formal_only_demo", k=3)
        by_trap = {
            row["value"]: row
            for row in trap_failure_layers(rows)
            if row["system"] == "formal_only_demo"
        }

        self.assertEqual(by_trap["messenger_shorthand"]["failure_rows"], 3.0)
        self.assertEqual(by_trap["register_mismatch"]["dominant_failure_layer"], "register_gap")

    def test_reproduce_script_writes_aggregate_only_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "layers.md"
            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/reproduce_layer_attribution.py",
                    "--out",
                    str(out),
                ],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            report = out.read_text(encoding="utf-8")

        self.assertIn("Layer Attribution Fixture", report)
        self.assertIn("Failure Mass By Layer", report)
        self.assertIn("surface_fragmentation", report)
        self.assertIn("register_gap", report)
        self.assertIn("human-gold attribution blocked", report)
        self.assertIn("Table-2-style decomposition", report)
        self.assertIn("Layer Attribution Summary", result.stdout)
        self.assertNotIn("surface_bundle_formal", report)


if __name__ == "__main__":
    unittest.main()
