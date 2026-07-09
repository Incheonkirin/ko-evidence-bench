import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ko_evidence_bench.system_matrix import load_matrix, matrix_summary, status_label, validate_matrix
from scripts.build_system_matrix_report import render_report


ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "docs" / "system_matrix.json"


class SystemMatrixTest(unittest.TestCase):
    def test_matrix_distinguishes_implemented_from_not_run(self):
        matrix = load_matrix(MATRIX)
        issues = validate_matrix(matrix, root=ROOT)
        summary = matrix_summary(matrix)

        self.assertEqual(issues, [])
        self.assertEqual(status_label(matrix, issues), "INCOMPLETE")
        self.assertGreaterEqual(summary["implemented"], 7)
        self.assertGreaterEqual(summary["not_run"], 7)
        self.assertEqual(summary["blocked"], 1)
        self.assertIn("dense_multilingual_encoder", summary["missing_full_matrix"])
        self.assertIn("human_gold_route_scorecard", summary["missing_full_matrix"])

    def test_report_exposes_full_matrix_gaps(self):
        report = render_report(MATRIX)

        self.assertIn("INCOMPLETE for full comparison matrix", report)
        self.assertIn("full analyzer/dense/hybrid/reranker matrix", report)
        self.assertIn("structural_cross_text", report)
        self.assertIn("bm25_nori", report)
        self.assertIn("dense_korean_encoder", report)
        self.assertIn("hybrid_lexical_dense", report)
        self.assertIn("human_gold_route_scorecard", report)
        self.assertIn("validation issues: 0", report)

    def test_build_script_check_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "system_matrix.md"
            subprocess.run(
                [sys.executable, "scripts/build_system_matrix_report.py", "--out", str(out)],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            result = subprocess.run(
                [sys.executable, "scripts/build_system_matrix_report.py", "--out", str(out), "--check"],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertIn("system matrix report is current", result.stdout)


if __name__ == "__main__":
    unittest.main()
