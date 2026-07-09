import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.check_probe_privacy import validate_probe_package


ROOT = Path(__file__).resolve().parents[1]
PROBE_DIR = ROOT / "probes" / "ko_evidence_probe_v0"
REFERENCE = ROOT / "fixtures" / "privacy_reference" / "source_snippets.txt"


class ProbePrivacyTest(unittest.TestCase):
    def test_current_public_probe_package_passes(self):
        result = validate_probe_package(PROBE_DIR, [REFERENCE])

        self.assertEqual(result.query_rows, 13)
        self.assertEqual(result.qrel_rows, 13)
        self.assertEqual(result.evidence_rows, 7)
        self.assertEqual(result.intent_count, 8)
        self.assertEqual(result.surface_count, 4)
        self.assertEqual(result.failures, ())

    def test_screen_catches_phone_like_query(self):
        with tempfile.TemporaryDirectory() as tmp:
            probe_dir = Path(tmp) / "probe"
            probe_dir.mkdir()
            for name in ["qrels.jsonl", "evidence.jsonl"]:
                (probe_dir / name).write_text((PROBE_DIR / name).read_text(encoding="utf-8"), encoding="utf-8")
            text = (PROBE_DIR / "queries.jsonl").read_text(encoding="utf-8")
            phone = "010" + "1234" + "5678"
            text = text.replace("암뇌심 진단비가 한 특약에 같이 묶여 있나요?", f"{phone} 암뇌심 진단비 문의")
            (probe_dir / "queries.jsonl").write_text(text, encoding="utf-8")

            result = validate_probe_package(probe_dir, [REFERENCE])

        self.assertTrue(any("phone" in failure for failure in result.failures))

    def test_screen_catches_long_reference_overlap(self):
        with tempfile.TemporaryDirectory() as tmp:
            reference = Path(tmp) / "reference.txt"
            reference.write_text(
                "보험계약 해지 시 해지환급금 산정 기준은 어디에서 확인하나요?",
                encoding="utf-8",
            )
            result = validate_probe_package(PROBE_DIR, [reference])

        self.assertTrue(any("long n-gram overlap" in failure for failure in result.failures))

    def test_build_script_check_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "probe_privacy_report.md"
            subprocess.run(
                [sys.executable, "scripts/check_probe_privacy.py", "--out", str(out)],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            result = subprocess.run(
                [sys.executable, "scripts/check_probe_privacy.py", "--out", str(out), "--check"],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertIn("probe privacy report is current", result.stdout)


if __name__ == "__main__":
    unittest.main()
