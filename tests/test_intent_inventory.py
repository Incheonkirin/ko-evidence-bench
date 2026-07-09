import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ko_evidence_bench.intent_inventory import aggregate_inventory, qrel_metadata
from ko_evidence_bench.metrics import load_jsonl


ROOT = Path(__file__).resolve().parents[1]


class IntentInventoryTest(unittest.TestCase):
    def setUp(self):
        self.qrels = load_jsonl(ROOT / "fixtures" / "surface_qrels.jsonl")

    def test_qrel_metadata_prefers_public_non_raw_fields(self):
        metadata = qrel_metadata(self.qrels[0])

        self.assertEqual(metadata["intent_family"], "bundled_coverage")
        self.assertEqual(metadata["intent_id"], "cancer_brain_heart_bundle")
        self.assertEqual(metadata["surface_form"], "formal")
        self.assertEqual(metadata["trap_classes"], ["bundle_expansion"])

    def test_aggregate_inventory_groups_by_intent_family(self):
        inventory = aggregate_inventory(self.qrels)
        by_family = {row["intent_family"]: row for row in inventory["family_rows"]}

        self.assertEqual(inventory["n"], 8)
        self.assertEqual(inventory["intent_family"]["bundled_coverage"], 3)
        self.assertEqual(inventory["surface_form"]["messenger_shorthand"], 3)
        self.assertEqual(inventory["trap_classes"]["messenger_shorthand"], 3)
        self.assertEqual(by_family["underwriting_context"]["abstain_rows"], 2)
        self.assertEqual(by_family["refund_termination"]["route_counts"]["product_disclosure"], 3)
        self.assertEqual(inventory["metadata_completeness"]["present_intent_family"], 8)

    def test_reproduce_script_writes_aggregate_only_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "intent.md"
            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/build_intent_inventory.py",
                    "--out",
                    str(out),
                ],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            report = out.read_text(encoding="utf-8")

        self.assertIn("Intent-Family Inventory Fixture", report)
        self.assertIn("bundled_coverage", report)
        self.assertIn("Trap-Class Distribution", report)
        self.assertIn("| `intent_family` | 8 | 0 | 100.0% |", report)
        self.assertIn("raw queries", report)
        self.assertIn("intent families", result.stdout.lower())
        self.assertNotIn("surface_bundle_formal", report)


if __name__ == "__main__":
    unittest.main()
