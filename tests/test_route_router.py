import importlib.util
import unittest
from pathlib import Path

from ko_evidence_bench.route_router import query_only_route


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "evaluate_route_router.py"
spec = importlib.util.spec_from_file_location("evaluate_route_router", SCRIPT)
eval_router = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(eval_router)


class RouteRouterTest(unittest.TestCase):
    def test_query_only_route(self):
        self.assertEqual(query_only_route("보험금 청구 서류 알려줘"), "claims_faq")
        self.assertEqual(query_only_route("해지환급금 얼마야"), "product_disclosure")
        self.assertEqual(query_only_route("내 보험 부담보면 보장돼?"), "human_context_needed")
        self.assertEqual(query_only_route("암 진단비 지급사유"), "policy_clause")

    def test_route_score(self):
        rows = [
            {"query": "보험금 청구 서류", "gold": "claims_faq", "should_abstain": False},
            {"query": "내 보험 부담보", "gold": "human_context_needed", "should_abstain": True},
            {"query": "암 진단비 지급사유", "gold": "policy_clause", "should_abstain": False},
        ]
        scores = eval_router.score_predictions(rows, eval_router.query_router)
        self.assertEqual(scores["n"], 3.0)
        self.assertEqual(scores["route_accuracy"], 1.0)
        self.assertEqual(scores["abstention_precision"], 1.0)
        self.assertEqual(scores["abstention_recall"], 1.0)


if __name__ == "__main__":
    unittest.main()
