import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ko_evidence_bench.beir_export import export_beir_probe, validate_beir_export
from ko_evidence_bench.metrics import load_jsonl
from scripts.export_probe_beir import export_files


ROOT = Path(__file__).resolve().parents[1]
PROBE_DIR = ROOT / "probes" / "ko_evidence_probe_v0"


class BeirExportTest(unittest.TestCase):
    def test_public_probe_exports_answerable_retrieval_subset(self):
        export = export_beir_probe(
            load_jsonl(PROBE_DIR / "queries.jsonl"),
            load_jsonl(PROBE_DIR / "qrels.jsonl"),
            load_jsonl(PROBE_DIR / "evidence.jsonl"),
        )

        self.assertEqual(len(export.corpus), 7)
        self.assertEqual(len(export.queries), 13)
        self.assertEqual(len(export.qrels), 11)
        self.assertEqual(len(export.query_metadata), 13)
        self.assertEqual(
            export.skipped_abstention_qids,
            ["probe-underwriting-context", "probe-underwriting-messenger"],
        )
        self.assertEqual(validate_beir_export(export), [])

    def test_script_writes_beir_layout_and_check_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "beir"
            report = Path(tmp) / "probe_beir_export.md"
            export_files(probe_dir=PROBE_DIR, out_dir=out_dir, report_out=report)

            corpus = [json.loads(line) for line in (out_dir / "corpus.jsonl").read_text(encoding="utf-8").splitlines()]
            queries = [json.loads(line) for line in (out_dir / "queries.jsonl").read_text(encoding="utf-8").splitlines()]
            metadata = [
                json.loads(line) for line in (out_dir / "query_metadata.jsonl").read_text(encoding="utf-8").splitlines()
            ]
            with (out_dir / "qrels" / "test.tsv").open(encoding="utf-8") as handle:
                qrels = list(csv.DictReader(handle, delimiter="\t"))

            self.assertEqual(corpus[0]["_id"], "ev-policy-bundle-diagnosis")
            self.assertEqual(queries[0]["_id"], "probe-bundle-formal")
            self.assertEqual(metadata[0]["intent_family"], "bundled_coverage")
            self.assertEqual(qrels[0]["query-id"], "probe-bundle-formal")
            self.assertIn("BEIR-style retrieval subset", report.read_text(encoding="utf-8"))

            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/export_probe_beir.py",
                    "--out-dir",
                    str(out_dir),
                    "--report-out",
                    str(report),
                    "--check",
                ],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )

        self.assertIn("probe BEIR export is current", result.stdout)


if __name__ == "__main__":
    unittest.main()
