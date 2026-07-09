import unittest

from ko_evidence_bench.audit_coverage import audit_surface_coverage
from ko_evidence_bench.metrics import load_jsonl


class AuditCoverageTest(unittest.TestCase):
    def test_surface_audit_fixture_covers_all_axes(self):
        qrels = load_jsonl("fixtures/surface_qrels.jsonl")
        audit_rows = load_jsonl("fixtures/route_audit/surface_audit_seed.jsonl")

        coverage = audit_surface_coverage(qrels, audit_rows)
        by_axis = {item.name: item for item in coverage.slices}

        self.assertTrue(coverage.complete)
        self.assertEqual(coverage.matched_rows, 8)
        self.assertEqual(coverage.unmatched_audit_rows, 0)
        self.assertEqual(by_axis["route_gold"].sampled_values, by_axis["route_gold"].full_values)
        self.assertEqual(by_axis["intent_family"].sampled_values, by_axis["intent_family"].full_values)
        self.assertEqual(by_axis["surface_form"].sampled_values, by_axis["surface_form"].full_values)
        self.assertEqual(by_axis["trap_classes"].sampled_values, by_axis["trap_classes"].full_values)


if __name__ == "__main__":
    unittest.main()
