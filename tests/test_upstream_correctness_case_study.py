import json
import re
import unicodedata
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CASE_DIR = ROOT / "case_studies" / "korean-retrieval-correctness"


class UpstreamCorrectnessCaseStudyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.observations = json.loads(
            (CASE_DIR / "evidence" / "local-observations.json").read_text(
                encoding="utf-8"
            )
        )
        cls.upstream = json.loads(
            (CASE_DIR / "evidence" / "upstream-contributions.json").read_text(
                encoding="utf-8"
            )
        )
        cls.polarity = json.loads(
            (ROOT / "reports" / "private_polarity_stress_pilot.json").read_text(
                encoding="utf-8"
            )
        )

    def analyzer_case(self, case_id: str):
        return next(
            case
            for case in self.observations["analyzer_cases"]
            if case["case_id"] == case_id
        )

    def test_manifest_records_three_merged_contributions(self) -> None:
        contributions = self.upstream["contributions"]
        self.assertEqual(len(contributions), 3)
        self.assertTrue(all(item["state"] == "MERGED" for item in contributions))
        self.assertEqual(
            {item["pull_request"] for item in contributions},
            {16242, 151157, 152931},
        )
        self.assertEqual(
            [item["contribution_type"] for item in contributions].count("implementation"),
            2,
        )

    def test_xpn_removal_collapses_contrastive_terms(self) -> None:
        self.assertEqual(
            self.analyzer_case("xpn_non_covered")["tokens"],
            self.analyzer_case("covered")["tokens"],
        )
        self.assertEqual(
            self.analyzer_case("xpn_excluded_coverage")["tokens"],
            self.analyzer_case("coverage")["tokens"],
        )

    def test_nfc_and_nfd_are_equivalent_input_but_different_analysis(self) -> None:
        nfc = self.analyzer_case("hangul_nfc")
        nfd = self.analyzer_case("hangul_nfd")
        self.assertEqual(unicodedata.normalize("NFC", nfd["input"]), nfc["input"])
        self.assertNotEqual(nfc["tokens"], nfd["tokens"])

    def test_phrase_observation_is_one_zero_one(self) -> None:
        counts = {
            (row["query_type"], row["slop"]): row["hits"]
            for row in self.observations["phrase_cases"]
        }
        self.assertEqual(counts[("match", None)], 1)
        self.assertEqual(counts[("match_phrase", 0)], 0)
        self.assertEqual(counts[("match_phrase", 1)], 1)

    def test_system_stress_contract_stays_linked(self) -> None:
        self.assertEqual(self.polarity["input"]["contrastive_triples"], 444)
        self.assertEqual(self.polarity["input"]["seed_evidence_pairs"], 37)
        rates = {
            item["system_id"]: item["wrong_preferred_rate"]
            for item in self.polarity["systems"]
        }
        self.assertAlmostEqual(rates["bm25_analyzer_tokens"], 0.5382882883)
        self.assertAlmostEqual(rates["dense_bge_m3"], 0.2905405405)
        self.assertAlmostEqual(
            rates["cross_encoder_bge_reranker_v2_m3"], 0.4842342342
        )

    def test_case_study_exports_no_raw_text(self) -> None:
        self.assertFalse(self.observations["scope"]["raw_text_exported"])
        self.assertFalse(self.polarity["input"]["raw_text_exported"])

    def test_case_study_local_links_resolve(self) -> None:
        article_paths = [
            CASE_DIR / "README.md",
            CASE_DIR / "exact-phrase-zero-results.md",
            CASE_DIR / "analyzer-reverses-meaning.md",
        ]
        for article_path in article_paths:
            article = article_path.read_text(encoding="utf-8")
            targets = re.findall(r"\]\((?!https?://)([^)#]+)(?:#[^)]+)?\)", article)
            self.assertGreater(len(targets), 0)
            for target in targets:
                with self.subTest(article=article_path.name, target=target):
                    self.assertTrue((article_path.parent / target).resolve().exists())


if __name__ == "__main__":
    unittest.main()
