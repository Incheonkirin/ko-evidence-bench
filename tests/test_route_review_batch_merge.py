import csv
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RouteReviewBatchMergeTest(unittest.TestCase):
    def test_merge_updates_label_fields_without_leaking_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            full_csv = tmp_path / "full.csv"
            batch_csv = tmp_path / "batch.csv"
            out_csv = tmp_path / "merged.csv"
            report_path = tmp_path / "report.md"
            fieldnames = [
                "audit_id",
                "qid",
                "query",
                "context",
                "route_gold",
                "allowed_source_tiers",
                "should_abstain",
                "confidence",
                "rationale_code",
                "labeler",
                "notes",
            ]
            full_rows = [
                {
                    "audit_id": "a1",
                    "qid": "private-q1",
                    "query": "do not leak query",
                    "context": "do not leak context",
                    "route_gold": "",
                    "allowed_source_tiers": "",
                    "should_abstain": "",
                    "confidence": "",
                    "rationale_code": "",
                    "labeler": "",
                    "notes": "",
                }
            ]
            batch_rows = [
                {
                    **full_rows[0],
                    "route_gold": "claims_faq",
                    "allowed_source_tiers": "claims_faq;policy_clause",
                    "should_abstain": "false",
                    "confidence": "high",
                    "rationale_code": "claims_ops",
                    "labeler": "r1",
                    "notes": "do not leak notes",
                }
            ]
            for path, rows in ((full_csv, full_rows), (batch_csv, batch_rows)):
                with path.open("w", encoding="utf-8", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(rows)

            subprocess.run(
                [
                    sys.executable,
                    "scripts/merge_route_review_batch.py",
                    "--full-csv",
                    str(full_csv),
                    "--batch-csv",
                    str(batch_csv),
                    "--out-csv",
                    str(out_csv),
                    "--report-out",
                    str(report_path),
                ],
                cwd=ROOT,
                check=True,
            )

            with out_csv.open(encoding="utf-8", newline="") as f:
                merged = list(csv.DictReader(f))
            self.assertEqual(merged[0]["route_gold"], "claims_faq")
            self.assertEqual(merged[0]["confidence"], "high")

            report = report_path.read_text(encoding="utf-8")
            self.assertIn("updated_rows", report)
            self.assertIn("claims_faq", report)
            self.assertNotIn("do not leak query", report)
            self.assertNotIn("do not leak notes", report)

    def test_empty_batch_rows_are_skipped_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            full_csv = tmp_path / "full.csv"
            batch_csv = tmp_path / "batch.csv"
            out_csv = tmp_path / "merged.csv"
            fieldnames = ["audit_id", "route_gold", "allowed_source_tiers", "should_abstain", "confidence", "rationale_code", "labeler", "notes"]
            rows = [{"audit_id": "a1", "route_gold": "", "allowed_source_tiers": "", "should_abstain": "", "confidence": "", "rationale_code": "", "labeler": "", "notes": ""}]
            for path in (full_csv, batch_csv):
                with path.open("w", encoding="utf-8", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(rows)

            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/merge_route_review_batch.py",
                    "--full-csv",
                    str(full_csv),
                    "--batch-csv",
                    str(batch_csv),
                    "--out-csv",
                    str(out_csv),
                ],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertIn("| `updated_rows` | 0 |", result.stdout)
            self.assertIn("| `skipped_empty_rows` | 1 |", result.stdout)


if __name__ == "__main__":
    unittest.main()
