import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ko_evidence_bench.ablation import compare_runs, grouped_comparison, summarize_comparison, trap_comparison
from ko_evidence_bench.metrics import load_jsonl


ROOT = Path(__file__).resolve().parents[1]


class NormalizationAblationTest(unittest.TestCase):
    def setUp(self):
        self.qrels = load_jsonl(ROOT / "fixtures" / "surface_qrels.jsonl")
        self.baseline = load_jsonl(ROOT / "fixtures" / "surface_runs" / "formal_only_demo.jsonl")
        self.candidate = load_jsonl(ROOT / "fixtures" / "surface_runs" / "surface_robust_demo.jsonl")

    def test_comparison_counts_rescues_and_no_regressions(self):
        rows = compare_runs(self.qrels, self.baseline, self.candidate, k=3)
        summary = summarize_comparison(rows)

        self.assertEqual(summary["n"], 8.0)
        self.assertEqual(summary["baseline_success_rate"], 3 / 8)
        self.assertEqual(summary["candidate_success_rate"], 1.0)
        self.assertEqual(summary["rescued_rows"], 5.0)
        self.assertEqual(summary["regressed_rows"], 0.0)

    def test_grouped_lift_by_family_and_trap_class(self):
        rows = compare_runs(self.qrels, self.baseline, self.candidate, k=3)
        by_family = {row["value"]: row for row in grouped_comparison(rows, "intent_family")}
        by_trap = {row["value"]: row for row in trap_comparison(rows)}

        self.assertEqual(by_family["bundled_coverage"]["rescued_rows"], 2.0)
        self.assertEqual(by_family["underwriting_context"]["rescued_rows"], 1.0)
        self.assertEqual(by_trap["messenger_shorthand"]["rescued_rows"], 3.0)

    def test_reproduce_script_writes_aggregate_only_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "ablation.md"
            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/reproduce_normalization_ablation.py",
                    "--out",
                    str(out),
                ],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            report = out.read_text(encoding="utf-8")

        self.assertIn("Normalization Ablation Fixture", report)
        self.assertIn("Lift By Intent Family", report)
        self.assertIn("rescued rows | 5", report)
        self.assertIn("messenger_shorthand", report)
        self.assertIn("ablation report", report)
        self.assertIn("net lift", result.stdout)
        self.assertNotIn("surface_bundle_formal", report)


if __name__ == "__main__":
    unittest.main()
