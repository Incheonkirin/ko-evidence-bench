import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ExportRouteRunsTest(unittest.TestCase):
    def test_cli_writes_qid_only_runs(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            qrels = tmp_path / "qrels.jsonl"
            out_dir = tmp_path / "runs"
            report = tmp_path / "report.md"
            rows = [
                {"qid": "q1", "query": "보험금 청구 서류 알려줘"},
                {"qid": "q2", "query": "내 보험 부담보면 보장돼?"},
                {"qid": "q3", "query": "암 진단비 지급사유"},
            ]
            qrels.write_text(
                "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
                encoding="utf-8",
            )

            subprocess.run(
                [
                    sys.executable,
                    "scripts/export_route_runs.py",
                    "--qrels",
                    str(qrels),
                    "--out-dir",
                    str(out_dir),
                    "--report-out",
                    str(report),
                ],
                cwd=ROOT,
                check=True,
            )

            route_rows = [
                json.loads(line)
                for line in (out_dir / "query_keyword_router.jsonl").read_text(encoding="utf-8").splitlines()
            ]
            self.assertEqual(route_rows[0]["route_pred"], "claims_faq")
            self.assertEqual(route_rows[1]["route_pred"], "human_context_needed")
            self.assertTrue(route_rows[1]["abstained"])
            self.assertNotIn("query", route_rows[0])
            self.assertIn("Private Route Run Export Summary", report.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
