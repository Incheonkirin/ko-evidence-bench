import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_script(name):
    path = ROOT / "scripts" / name
    spec = importlib.util.spec_from_file_location(name.replace(".py", ""), path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


export_csv = load_script("export_route_review_csv.py")
import_csv = load_script("import_route_review_csv.py")


class RouteReviewCsvTest(unittest.TestCase):
    def test_csv_round_trip_to_reviewer_prefix(self):
        audit_rows = [
            {
                "audit_id": "route-audit-0001",
                "qid": "q1",
                "query": "private query",
                "context": "private context",
                "metadata": {"gate_category": "청구", "required_facets": ["청구서류"]},
                "silver": {
                    "route_gold": "claims_faq",
                    "should_abstain": False,
                    "confidence": "medium",
                    "rationale_code": "claims_ops",
                },
                "reviewer_a": {},
            }
        ]
        with tempfile.TemporaryDirectory() as tmp:
            csv_path = Path(tmp) / "review.csv"
            csv_rows = [export_csv.csv_row(audit_rows[0], reviewer_prefix="reviewer_a")]
            export_csv.write_csv(csv_path, csv_rows)
            loaded = import_csv.load_csv(csv_path)
            loaded[0].update(
                {
                    "route_gold": "claims_faq",
                    "allowed_source_tiers": "claims_faq",
                    "should_abstain": "false",
                    "confidence": "high",
                    "rationale_code": "claims_ops",
                    "labeler": "aa",
                    "notes": "ok",
                }
            )
            merged, updated = import_csv.merge_labels(
                audit_rows,
                loaded,
                target_prefix="reviewer_a",
                skip_empty=False,
            )
        self.assertEqual(updated, 1)
        self.assertEqual(merged[0]["reviewer_a"]["route_gold"], "claims_faq")
        self.assertEqual(merged[0]["reviewer_a"]["allowed_source_tiers"], ["claims_faq"])
        self.assertFalse(merged[0]["reviewer_a"]["should_abstain"])
        self.assertEqual(merged[0]["reviewer_a"]["confidence"], "high")

    def test_empty_csv_rows_can_be_skipped(self):
        audit_rows = [{"audit_id": "route-audit-0001", "qid": "q1", "reviewer_a": {"route_gold": "old"}}]
        csv_rows = [{"audit_id": "route-audit-0001"}]
        merged, updated = import_csv.merge_labels(
            audit_rows,
            csv_rows,
            target_prefix="reviewer_a",
            skip_empty=True,
        )
        self.assertEqual(updated, 0)
        self.assertEqual(merged[0]["reviewer_a"]["route_gold"], "old")


if __name__ == "__main__":
    unittest.main()
