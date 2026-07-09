import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ko_evidence_bench.system_matrix_bundle import validate_matrix_bundle
from scripts.validate_system_matrix_bundle import render_report


ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "fixtures" / "system_matrix_bundle"
QRELS = ROOT / "fixtures" / "surface_qrels.jsonl"
MATRIX = ROOT / "docs" / "system_matrix.json"


class SystemMatrixBundleTest(unittest.TestCase):
    def test_fixture_bundle_covers_all_runnable_missing_systems(self):
        result = validate_matrix_bundle(bundle_dir=BUNDLE, qrels_path=QRELS, matrix_path=MATRIX)

        self.assertEqual(result.qrel_rows, 8)
        self.assertEqual(len(result.required_systems), 7)
        self.assertEqual(len(result.present_systems), 7)
        self.assertEqual(result.complete_systems, 7)
        self.assertEqual(result.validation_errors, 0)
        self.assertIn("bm25_nori", result.required_systems)
        self.assertIn("cross_encoder_reranker", result.required_systems)

    def test_report_is_explicitly_a_contract_not_model_claim(self):
        result = validate_matrix_bundle(bundle_dir=BUNDLE, qrels_path=QRELS, matrix_path=MATRIX)
        report = render_report(result, bundle_dir=BUNDLE, qrels_path=QRELS, matrix_path=MATRIX)

        self.assertIn("PASS synthetic full-matrix run-bundle rehearsal", report)
        self.assertIn("not external model output", report)
        self.assertIn("not model-quality comparisons", report)
        self.assertIn("| required runnable systems | 7 |", report)
        self.assertIn("| validation errors | 0 |", report)
        self.assertIn("bm25_nori", report)
        self.assertIn("dense_korean_encoder", report)

    def test_raw_text_fields_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_bundle = Path(tmp) / "bundle"
            shutil.copytree(BUNDLE, tmp_bundle)
            run_path = tmp_bundle / "runs" / "bm25_nori.jsonl"
            rows = [json.loads(line) for line in run_path.read_text(encoding="utf-8").splitlines()]
            rows[0]["query"] = "raw private query should not be exported"
            run_path.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n", encoding="utf-8")

            result = validate_matrix_bundle(bundle_dir=tmp_bundle, qrels_path=QRELS, matrix_path=MATRIX)

        self.assertGreater(result.validation_errors, 0)
        self.assertTrue(any(system.raw_field_errors for system in result.systems))

    def test_build_script_check_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "system_matrix_bundle.md"
            subprocess.run(
                [sys.executable, "scripts/validate_system_matrix_bundle.py", "--out", str(out)],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            result = subprocess.run(
                [sys.executable, "scripts/validate_system_matrix_bundle.py", "--out", str(out), "--check"],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertIn("system matrix bundle report is current", result.stdout)


if __name__ == "__main__":
    unittest.main()
