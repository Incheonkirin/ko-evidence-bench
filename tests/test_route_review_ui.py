import unittest
from pathlib import Path


class RouteReviewUiTest(unittest.TestCase):
    def test_static_ui_is_public_safe_and_self_contained(self):
        html = (Path(__file__).resolve().parents[1] / "tools" / "route_review_ui.html").read_text(
            encoding="utf-8"
        )
        self.assertIn("FileReader", html)
        self.assertIn("Blob", html)
        self.assertIn("function h(value)", html)
        self.assertIn("allowed_source_tiers", html)
        self.assertNotIn("http://", html)
        self.assertNotIn("https://", html)


if __name__ == "__main__":
    unittest.main()
