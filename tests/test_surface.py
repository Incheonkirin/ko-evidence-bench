import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ko_evidence_bench.metrics import load_jsonl
from ko_evidence_bench.surface import (
    intent_breakdown,
    score_surface_run,
    surface_breakdown,
    surface_inventory,
)


ROOT = Path(__file__).resolve().parents[1]


class SurfaceRobustnessTest(unittest.TestCase):
    def setUp(self):
        self.qrels = load_jsonl(ROOT / "fixtures" / "surface_qrels.jsonl")
        self.robust = load_jsonl(ROOT / "fixtures" / "surface_runs" / "surface_robust_demo.jsonl")
        self.formal_only = load_jsonl(ROOT / "fixtures" / "surface_runs" / "formal_only_demo.jsonl")

    def test_robust_run_has_zero_surface_spread(self):
        score = score_surface_run(self.qrels, self.robust, k=3)

        self.assertEqual(score["n"], 8.0)
        self.assertEqual(score["intent_count"], 3.0)
        self.assertEqual(score["surface_count"], 4.0)
        self.assertEqual(score["task_success@3"], 1.0)
        self.assertEqual(score["avg_intent_surface_spread"], 0.0)
        self.assertEqual(score["robust_intent_share"], 1.0)
        self.assertEqual(score["missing_surface_metadata"], 0.0)

    def test_formal_only_run_exposes_surface_fragility(self):
        score = score_surface_run(self.qrels, self.formal_only, k=3)
        by_surface = {row["surface_form"]: row for row in surface_breakdown(self.qrels, self.formal_only, k=3)}
        by_intent = {row["intent_id"]: row for row in intent_breakdown(self.qrels, self.formal_only, k=3)}

        self.assertEqual(score["task_success@3"], 3 / 8)
        self.assertEqual(score["avg_intent_surface_spread"], 1.0)
        self.assertEqual(score["robust_intent_share"], 0.0)
        self.assertEqual(by_surface["formal"]["task_success@3"], 1.0)
        self.assertEqual(by_surface["messenger_shorthand"]["task_success@3"], 0.0)
        self.assertEqual(by_intent["refund_termination"]["surface_spread"], 1.0)

    def test_inventory_counts_intents_and_surface_forms(self):
        inventory = surface_inventory(self.qrels)

        self.assertEqual(inventory["intent_id"]["cancer_brain_heart_bundle"], 3)
        self.assertEqual(inventory["surface_form"]["messenger_shorthand"], 3)

    def test_reproduce_script_writes_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "surface.md"
            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/reproduce_surface_scorecard.py",
                    "--out",
                    str(out),
                ],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )

            report = out.read_text(encoding="utf-8")

        self.assertIn("Surface Robustness Scorecard Fixture", report)
        self.assertIn("surface_robust_demo", report)
        self.assertIn("formal_only_demo", report)
        self.assertIn("avg_intent_spread", report)
        self.assertIn("task_success@3", result.stdout)


if __name__ == "__main__":
    unittest.main()
