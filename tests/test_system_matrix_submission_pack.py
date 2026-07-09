import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.build_system_matrix_submission_pack import (
    load_qids,
    render_report,
    required_rows,
    write_pack,
)


ROOT = Path(__file__).resolve().parents[1]
QRELS = ROOT / "fixtures" / "surface_qrels.jsonl"
MATRIX = ROOT / "docs" / "system_matrix.json"


class SystemMatrixSubmissionPackTest(unittest.TestCase):
    def test_required_rows_cover_missing_full_matrix_systems(self):
        rows = required_rows(MATRIX)
        qids, errors = load_qids(QRELS)

        self.assertEqual(len(rows), 7)
        self.assertEqual(len(qids), 8)
        self.assertEqual(errors, [])
        self.assertIn("bm25_nori", {row["system_id"] for row in rows})
        self.assertIn("dense_korean_encoder", {row["system_id"] for row in rows})
        self.assertIn("cross_encoder_reranker", {row["system_id"] for row in rows})

    def test_pack_writes_qid_only_templates(self):
        rows = required_rows(MATRIX)
        qids, _ = load_qids(QRELS)
        with tempfile.TemporaryDirectory() as tmp:
            pack_dir = Path(tmp) / "submission"
            write_pack(pack_dir=pack_dir, qrels_path=QRELS, matrix_path=MATRIX, required=rows, qids=qids)

            self.assertTrue((pack_dir / "manifest.template.json").exists())
            self.assertTrue((pack_dir / "README.md").exists())
            template = pack_dir / "runs" / "bm25_nori.jsonl.template"
            text = template.read_text(encoding="utf-8")

        self.assertIn('"qid":"surface_bundle_formal"', text)
        self.assertIn('"route_pred":"TODO_ROUTE_LABEL"', text)
        self.assertNotIn("query", text)
        self.assertNotIn("answer", text)
        self.assertNotIn("source_name", text)

    def test_report_is_explicitly_template_not_model_output(self):
        report = render_report(
            qrels_path=QRELS,
            matrix_path=MATRIX,
            pack_dir=ROOT / "fixtures" / "system_matrix_submission_template",
        )

        self.assertIn("PASS qid-only matrix submission template", report)
        self.assertIn("required missing-matrix systems: 7", report)
        self.assertIn("promotion status | template only; no external systems run", report)
        self.assertIn("bm25_nori", report)
        self.assertIn("hybrid_lexical_dense", report)
        self.assertIn("cross_encoder_reranker", report)

    def test_build_script_check_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "submission.md"
            pack_dir = Path(tmp) / "pack"
            subprocess.run(
                [
                    sys.executable,
                    "scripts/build_system_matrix_submission_pack.py",
                    "--pack-dir",
                    str(pack_dir),
                    "--out",
                    str(out),
                ],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/build_system_matrix_submission_pack.py",
                    "--pack-dir",
                    str(pack_dir),
                    "--out",
                    str(out),
                    "--check",
                ],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertIn("system matrix submission pack report is current", result.stdout)


if __name__ == "__main__":
    unittest.main()
