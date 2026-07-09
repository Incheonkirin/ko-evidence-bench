import unittest

from ko_evidence_bench.substrate_profile import TextRow, profile_rows, render_profile_report
from scripts.profile_query_substrates import parse_source


class SubstrateProfileTest(unittest.TestCase):
    def test_profiles_shape_and_stress_features(self):
        rows = [
            TextRow("community_post", "고지의무 위반으로 보험금 지급이 거절될 수 있는지 약관 근거가 궁금합니다."),
            TextRow("community_post", "해지환급금과 감액완납 구조를 상품 설명서 기준으로 확인하고 싶습니다."),
            TextRow("messenger_turn", "실비 청구 가능할까요?"),
            TextRow("messenger_turn", "암뇌심 같이 넣어도 돼요?"),
        ]

        profiles = profile_rows(rows)

        self.assertEqual(profiles["community_post"]["usable_rows"], 2)
        self.assertEqual(profiles["messenger_turn"]["usable_rows"], 2)
        community_features = profiles["community_post"]["feature_counts"]
        messenger_features = profiles["messenger_turn"]["feature_counts"]
        self.assertGreater(community_features["formal_register"], 0)
        self.assertGreater(messenger_features["abbrev_or_colloquial"], 0)
        self.assertEqual(messenger_features["messenger_style"], 2)

    def test_report_does_not_include_raw_text(self):
        raw = "실비 청구 가능할까요?"
        report = render_profile_report([TextRow("messenger_turn", raw)])

        self.assertIn("messenger_turn", report)
        self.assertIn("Retrieval Stress Signals", report)
        self.assertNotIn(raw, report)
        self.assertNotIn("source file paths", report.split("## Cohort Shape Summary")[1])

    def test_parse_source_allows_colons_inside_path(self):
        cohort, path, fmt, fields = parse_source("messenger:/tmp/private 1:1 sample.csv:csv:Message")

        self.assertEqual(cohort, "messenger")
        self.assertEqual(str(path), "/tmp/private 1:1 sample.csv")
        self.assertEqual(fmt, "csv")
        self.assertEqual(fields, ["Message"])


if __name__ == "__main__":
    unittest.main()
