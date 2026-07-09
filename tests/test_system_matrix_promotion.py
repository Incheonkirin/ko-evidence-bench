import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ko_evidence_bench.system_matrix_promotion import evaluate_system_matrix_promotion
from scripts.rehearse_system_matrix_promotion import render_report


ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "fixtures" / "system_matrix_bundle"
QRELS = ROOT / "fixtures" / "surface_qrels.jsonl"
MATRIX = ROOT / "docs" / "system_matrix.json"


class SystemMatrixPromotionTest(unittest.TestCase):
    def test_fixture_is_mechanically_ready_but_not_promotable(self):
        result = evaluate_system_matrix_promotion(bundle_dir=BUNDLE, qrels_path=QRELS, matrix_path=MATRIX)
        statuses = {gate.gate: gate.status for gate in result.gates}

        self.assertTrue(result.mechanical_ready)
        self.assertFalse(result.promotion_ready)
        self.assertEqual(result.status, "REHEARSAL_ONLY")
        self.assertEqual(statuses["validation"], "PASS")
        self.assertEqual(statuses["qid_only_screen"], "PASS")
        self.assertEqual(statuses["scale"], "BLOCKED")
        self.assertEqual(statuses["run_provenance"], "BLOCKED")

    def test_report_refuses_matrix_update_for_fixture(self):
        result = evaluate_system_matrix_promotion(bundle_dir=BUNDLE, qrels_path=QRELS, matrix_path=MATRIX)
        report = render_report(
            result,
            bundle_dir=BUNDLE,
            qrels_path=QRELS,
            matrix_path=MATRIX,
            min_rows=500,
        )

        self.assertIn("BLOCKED synthetic promotion rehearsal; no matrix update", report)
        self.assertIn("Do not update `docs/system_matrix.json` from this fixture.", report)
        self.assertIn("real external-run provenance", report)
        self.assertIn("not a model-quality benchmark", report)

    def test_script_check_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "promotion.md"
            subprocess.run(
                [sys.executable, "scripts/rehearse_system_matrix_promotion.py", "--out", str(out)],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            result = subprocess.run(
                [sys.executable, "scripts/rehearse_system_matrix_promotion.py", "--out", str(out), "--check"],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertIn("system matrix promotion report is current", result.stdout)


if __name__ == "__main__":
    unittest.main()
