import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ko_evidence_bench.study_report import load_study_report_signals, render_measurement_study


ROOT = Path(__file__).resolve().parents[1]


class StudyReportTest(unittest.TestCase):
    def test_report_uses_checked_in_aggregate_values(self):
        signals = load_study_report_signals(ROOT)
        report = render_measurement_study(signals)

        self.assertIn("NO-GO for public headline claims", report)
        self.assertIn("64.9%", report)
        self.assertIn("+8.5%p", report)
        self.assertIn("System Matrix Evidence", report)
        self.assertIn("full comparison matrix incomplete", report)
        self.assertIn("reports/system_matrix_bundle_fixture.md", report)
        self.assertIn("qid-only bundle contract covers 7 runnable missing systems", report)
        self.assertIn("not external model output", report)
        self.assertIn("31.8%", report)
        self.assertIn("46.9%", report)
        self.assertIn("+25.4%p", report)
        self.assertIn("drops from 190 to 28 rows", report)
        self.assertIn("Silver source-route slices", report)
        self.assertIn("route accuracy range 36.2% - 55.2%", report)
        self.assertIn("context-needed policy fallback up to 54.1%", report)
        self.assertIn("Real-query substrates need separate stress slices", report)
        self.assertIn("live-style turns median 17.0 chars", report)
        self.assertIn("Query Substrate Evidence", report)
        self.assertIn("Private qrels now have silver intent/surface slices", report)
        self.assertIn("Intent/Surface Metadata Evidence", report)
        self.assertIn("544 qid-only rows", report)
        self.assertIn("Exact lexical seed counting misses same-intent surface variants", report)
        self.assertIn("Surface Fragmentation Audit", report)
        self.assertIn("4 exact-seed rows vs 9 qrel intent rows", report)
        self.assertIn("public fixture; not a synonym list", report)
        self.assertIn("Route decisions can now be scored by surface condition", report)
        self.assertIn("Route Surface Evidence", report)
        self.assertIn("Ranked retrieval hits can now be sliced by surface condition", report)
        self.assertIn("Private runtime-surface diagnostics", report)
        self.assertIn("answerable clause@20 71.3%", report)
        self.assertIn("Layer Attribution Evidence", report)
        self.assertIn("Table-2-style decomposition hook", report)
        self.assertIn("make export-probe-beir", report)
        self.assertIn("reports/probe_beir_export.md", report)
        self.assertIn("make validate-system-matrix-bundle", report)
        self.assertIn("Human audit workset covers the stress axes before labeling", report)
        self.assertIn("Human Audit Coverage", report)
        self.assertIn("system matrix not-run systems", report)
        self.assertIn("missing analyzer/dense/hybrid/reranker runs", report)
        self.assertIn("Answer quality needs separate labels after retrieval", report)
        self.assertIn("Answer-Quality Evidence", report)
        self.assertIn("reports/answer_quality_audit_fixture.md", report)
        self.assertIn("10 qid-only fixture rows", report)
        self.assertIn("not human-gold answer quality", report)
        self.assertIn("prevents `clause@20`", report)
        self.assertIn("4 / 4", report)
        self.assertIn("10 / 10", report)
        self.assertIn("0 / 50 paired labels", report)
        self.assertIn("0 / 300 adjudicated labels complete", report)
        self.assertIn("double-label Cohen's kappa", report)

    def test_build_script_check_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "study.md"
            subprocess.run(
                [sys.executable, "scripts/build_measurement_study.py", "--out", str(out)],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            result = subprocess.run(
                [sys.executable, "scripts/build_measurement_study.py", "--out", str(out), "--check"],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertIn("measurement study draft is current", result.stdout)


if __name__ == "__main__":
    unittest.main()
