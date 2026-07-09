import unittest

from ko_evidence_bench.intent_surface_export import export_surface_qrels
from ko_evidence_bench.metrics import load_jsonl


class IntentSurfaceExportTest(unittest.TestCase):
    def test_export_private_like_qrels_to_qid_only_surface_schema(self):
        qrels = load_jsonl("fixtures/private_like_qrels.jsonl")
        labels = load_jsonl("fixtures/private_like_route_labels.jsonl")

        records, stats = export_surface_qrels(qrels, labels)

        self.assertEqual(stats["exported_rows"], 3)
        self.assertEqual(stats["missing_route_label"], 0)
        self.assertEqual(records[0]["intent_family"], "indemnity_noncovered")
        self.assertEqual(records[0]["surface_form"], "abbreviated")
        self.assertIn("negation_or_exclusion", records[0]["trap_classes"])
        self.assertIn("needs_private_context", records[1]["trap_classes"])
        self.assertEqual(records[1]["sufficient_evidence_ids"], [])
        self.assertIn("product_table", records[2]["trap_classes"])
        for record in records:
            self.assertNotIn("query", record)
            self.assertNotIn("intent", record)


if __name__ == "__main__":
    unittest.main()
