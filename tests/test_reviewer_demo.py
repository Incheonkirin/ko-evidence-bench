import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.build_hero_signal import load_signals
from scripts.build_reviewer_demo import render_reviewer_demo


ROOT = Path(__file__).resolve().parents[1]


class ReviewerDemoTest(unittest.TestCase):
    def test_rendered_demo_is_a_short_review_path(self):
        report = render_reviewer_demo(load_signals(ROOT))

        self.assertIn("3-minute diagnostic walkthrough", report)
        self.assertIn("Three-Minute Path", report)
        self.assertIn("reports/claim_ledger.md", report)
        self.assertIn("probes/ko_evidence_probe_v0", report)
        self.assertIn("reports/probe_privacy_report.md", report)
        self.assertIn("probes/ko_evidence_probe_v0/DATASET_CARD.md", report)
        self.assertIn("reports/probe_dataset_card.md", report)
        self.assertIn("release-facing probe card", report)
        self.assertIn("reports/probe_beir_export.md", report)
        self.assertIn("BEIR-style tooling", report)
        self.assertIn("reports/probe_system_comparison.md", report)
        self.assertIn("source-route-aware retrieval", report)
        self.assertIn("reports/probe_trap_mining.md", report)
        self.assertIn("not as dictionary entries", report)
        self.assertIn("reports/surface_fragmentation_audit.md", report)
        self.assertIn("not a synonym list", report)
        self.assertIn("reports/qualitative_gallery.md", report)
        self.assertIn("reports/layer_attribution_fixture.md", report)
        self.assertIn("reports/answer_quality_audit_fixture.md", report)
        self.assertIn("Retrieval hit metrics are not answer-quality claims", report)
        self.assertIn("reports/system_matrix.md", report)
        self.assertIn("reports/system_matrix_bundle_fixture.md", report)
        self.assertIn("qid-only run-bundle contract", report)
        self.assertIn("reports/human_gold_rehearsal_fixture.md", report)
        self.assertIn("reports/study_readiness.md", report)
        self.assertIn("What Not To Infer", report)
        self.assertIn("Do not treat the silver diagnostics as final benchmark numbers.", report)
        self.assertIn("0/300", report)

    def test_build_script_check_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "reviewer_demo.md"
            subprocess.run(
                [sys.executable, "scripts/build_reviewer_demo.py", "--out", str(out)],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            result = subprocess.run(
                [sys.executable, "scripts/build_reviewer_demo.py", "--out", str(out), "--check"],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertIn("reviewer demo is current", result.stdout)


if __name__ == "__main__":
    unittest.main()
