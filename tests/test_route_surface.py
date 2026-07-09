import unittest

from ko_evidence_bench.metrics import load_jsonl
from ko_evidence_bench.route_surface import grouped_scores, summarize_route_surface_run


class RouteSurfaceTest(unittest.TestCase):
    def test_scores_route_behavior_by_surface_metadata(self):
        qrels = load_jsonl("fixtures/surface_qrels.jsonl")
        formal_only = load_jsonl("fixtures/surface_runs/formal_only_demo.jsonl")
        robust = load_jsonl("fixtures/surface_runs/surface_robust_demo.jsonl")

        formal_score = summarize_route_surface_run(qrels, formal_only)
        robust_score = summarize_route_surface_run(qrels, robust)

        self.assertLess(formal_score["route_accuracy"], robust_score["route_accuracy"])
        self.assertEqual(robust_score["route_accuracy"], 1.0)
        self.assertEqual(robust_score["missing_surface_metadata"], 0.0)

        surface_rows = grouped_scores(qrels, formal_only, key="surface_form")
        by_surface = {row["value"]: row for row in surface_rows}
        self.assertEqual(by_surface["formal"]["route_accuracy"], 1.0)
        self.assertLess(by_surface["messenger_shorthand"]["route_accuracy"], 1.0)


if __name__ == "__main__":
    unittest.main()
