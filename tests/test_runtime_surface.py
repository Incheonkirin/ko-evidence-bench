import json
import unittest

from ko_evidence_bench.metrics import load_jsonl
from ko_evidence_bench.runtime_surface import (
    grouped_runtime_surface_scores,
    summarize_runtime_surface_run,
)


class RuntimeSurfaceTest(unittest.TestCase):
    def test_scores_runtime_hits_by_surface_metadata(self):
        qrels = load_jsonl("fixtures/surface_qrels.jsonl")
        with open("fixtures/runtime_results/surface_runtime_fixture.json", encoding="utf-8") as fh:
            result = json.load(fh)

        raw_rows = result["per_run"]["raw_surface_runtime"]
        robust_rows = result["per_run"]["surface_robust_runtime"]

        raw_score = summarize_runtime_surface_run(qrels, raw_rows)
        robust_score = summarize_runtime_surface_run(qrels, robust_rows)

        self.assertLess(raw_score["clause@20"], robust_score["clause@20"])
        self.assertEqual(robust_score["answerable_clause@20"], 1.0)
        self.assertEqual(robust_score["missing_surface_metadata"], 0.0)

        surface_rows = grouped_runtime_surface_scores(qrels, raw_rows, key="surface_form")
        by_surface = {row["value"]: row for row in surface_rows}
        self.assertEqual(by_surface["formal"]["clause@20"], 2 / 3)
        self.assertEqual(by_surface["messenger_shorthand"]["clause@20"], 0.0)


if __name__ == "__main__":
    unittest.main()
