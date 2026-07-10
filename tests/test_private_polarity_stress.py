import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.reproduce_private_polarity_stress import build_report, render_markdown


ROOT = Path(__file__).resolve().parents[1]


class PrivatePolarityStressTest(unittest.TestCase):
    def _write_rows(self, root: Path) -> tuple[Path, Path]:
        retrieval = root / "retrieval.jsonl"
        reranker = root / "reranker.jsonl"
        retrieval_rows = [
            {
                "pair_id": "pair-a",
                "intent": "coverage",
                "bm25_wrong": True,
                "bm25lucene_wrong": False,
                "dense_wrong": False,
                "query": "SENSITIVE_QUERY_MUST_NOT_LEAK",
                "expected_doc": "SENSITIVE_DOC_MUST_NOT_LEAK",
            },
            {
                "pair_id": "pair-a",
                "intent": "coverage",
                "bm25_wrong": True,
                "bm25lucene_wrong": True,
                "dense_wrong": False,
                "query": "SENSITIVE_QUERY_MUST_NOT_LEAK",
            },
            {
                "pair_id": "pair-b",
                "intent": "exclusion",
                "bm25_wrong": False,
                "bm25lucene_wrong": False,
                "dense_wrong": True,
                "query": "SENSITIVE_QUERY_MUST_NOT_LEAK",
            },
            {
                "pair_id": "pair-b",
                "intent": "exclusion",
                "bm25_wrong": False,
                "bm25lucene_wrong": False,
                "dense_wrong": True,
                "query": "SENSITIVE_QUERY_MUST_NOT_LEAK",
            },
        ]
        reranker_rows = [
            {
                "pair_id": "pair-a",
                "intent": "coverage",
                "expected_doc": "coverage_doc",
                "cov_score": 0.2,
                "exc_score": 0.4,
                "query": "SENSITIVE_QUERY_MUST_NOT_LEAK",
            },
            {
                "pair_id": "pair-a",
                "intent": "coverage",
                "expected_doc": "coverage_doc",
                "cov_score": 0.5,
                "exc_score": 0.2,
                "query": "SENSITIVE_QUERY_MUST_NOT_LEAK",
            },
            {
                "pair_id": "pair-b",
                "intent": "exclusion",
                "expected_doc": "exclusion_doc",
                "cov_score": 0.1,
                "exc_score": 0.3,
                "query": "SENSITIVE_QUERY_MUST_NOT_LEAK",
            },
            {
                "pair_id": "pair-b",
                "intent": "exclusion",
                "expected_doc": "exclusion_doc",
                "cov_score": 0.4,
                "exc_score": 0.3,
                "query": "SENSITIVE_QUERY_MUST_NOT_LEAK",
            },
        ]
        retrieval.write_text("\n".join(json.dumps(row) for row in retrieval_rows) + "\n", encoding="utf-8")
        reranker.write_text("\n".join(json.dumps(row) for row in reranker_rows) + "\n", encoding="utf-8")
        return retrieval, reranker

    def test_report_projects_private_rows_to_safe_aggregate(self):
        with tempfile.TemporaryDirectory() as tmp:
            retrieval, reranker = self._write_rows(Path(tmp))
            report = build_report(
                retrieval_rows_path=retrieval,
                reranker_rows_path=reranker,
                dense_model="test-dense",
                reranker_model="test-reranker",
                experiment_date="2026-07-10",
                samples=100,
                seed=7,
            )
            markdown = render_markdown(report)
            rendered = json.dumps(report) + markdown

        self.assertEqual(report["input"]["contrastive_triples"], 4)
        self.assertEqual(report["input"]["seed_evidence_pairs"], 2)
        self.assertFalse(report["input"]["raw_text_exported"])
        reranker = next(
            system for system in report["systems"] if system["system_id"] == "cross_encoder_bge_reranker_v2_m3"
        )
        self.assertEqual(reranker["wrong_preferred_rate"], 0.5)
        self.assertIn("clustered by seed evidence pair", markdown)
        self.assertNotIn("SENSITIVE_QUERY_MUST_NOT_LEAK", rendered)
        self.assertNotIn("SENSITIVE_DOC_MUST_NOT_LEAK", rendered)

    def test_cli_check_mode_reproduces_the_same_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            retrieval, reranker = self._write_rows(tmp_path)
            markdown = tmp_path / "report.md"
            output_json = tmp_path / "report.json"
            command = [
                sys.executable,
                "scripts/reproduce_private_polarity_stress.py",
                "--retrieval-rows",
                str(retrieval),
                "--reranker-rows",
                str(reranker),
                "--report-out",
                str(markdown),
                "--json-out",
                str(output_json),
                "--samples",
                "100",
            ]
            subprocess.run(command, cwd=ROOT, check=True, capture_output=True, text=True)
            result = subprocess.run(command + ["--check"], cwd=ROOT, check=True, capture_output=True, text=True)

        self.assertIn("private polarity stress artifacts are current", result.stdout)

    def test_rejects_reranker_rows_from_a_different_pair_set(self):
        with tempfile.TemporaryDirectory() as tmp:
            retrieval, reranker = self._write_rows(Path(tmp))
            rows = [json.loads(line) for line in reranker.read_text(encoding="utf-8").splitlines()]
            rows[-1]["pair_id"] = "different-pair"
            reranker.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "same pair/intent rows"):
                build_report(
                    retrieval_rows_path=retrieval,
                    reranker_rows_path=reranker,
                    dense_model="test-dense",
                    reranker_model="test-reranker",
                    experiment_date="2026-07-10",
                    samples=100,
                    seed=7,
                )


if __name__ == "__main__":
    unittest.main()
