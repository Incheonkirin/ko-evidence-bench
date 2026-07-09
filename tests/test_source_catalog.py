import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ko_evidence_bench.metrics import load_jsonl
from ko_evidence_bench.source_catalog import load_source_catalog, source_coverage
from scripts.build_source_catalog_report import render_report


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "docs" / "source_catalog.json"
QRELS = ROOT / "probes" / "ko_evidence_probe_v0" / "qrels.jsonl"
EVIDENCE = ROOT / "probes" / "ko_evidence_probe_v0" / "evidence.jsonl"


class SourceCatalogTest(unittest.TestCase):
    def test_catalog_covers_public_probe_source_tiers(self):
        result = source_coverage(
            catalog=load_source_catalog(CATALOG),
            qrels=load_jsonl(QRELS),
            evidence=load_jsonl(EVIDENCE),
        )

        self.assertEqual(result.status, "PASS")
        self.assertEqual(len(result.issues), 0)
        rows = {row.source_tier: row for row in result.rows}
        self.assertEqual(rows["policy_clause"].evidence_rows, 2)
        self.assertEqual(rows["product_disclosure"].gate_status, "COVERED")
        self.assertEqual(rows["official_consumer_info"].gate_status, "COVERED")
        self.assertEqual(rows["claims_faq"].gate_status, "COVERED")
        self.assertEqual(rows["dispute_case"].gate_status, "COVERED")
        self.assertEqual(rows["expert_answer"].gate_status, "COVERED")
        self.assertEqual(rows["human_context_needed"].gate_status, "ABSTENTION")

    def test_report_says_this_is_not_policy_only(self):
        report = render_report(catalog_path=CATALOG, qrels_path=QRELS, evidence_path=EVIDENCE)

        self.assertIn("PASS source-tier catalog fixture", report)
        self.assertIn("not policy-clause-only", report)
        self.assertIn("`official_consumer_info`", report)
        self.assertIn("`expert_answer`", report)
        self.assertIn("not proof that private source corpora", report)

    def test_build_script_check_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "source_catalog.md"
            subprocess.run(
                [sys.executable, "scripts/build_source_catalog_report.py", "--out", str(out)],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            result = subprocess.run(
                [sys.executable, "scripts/build_source_catalog_report.py", "--out", str(out), "--check"],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertIn("source catalog report is current", result.stdout)


if __name__ == "__main__":
    unittest.main()
