import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_public_safety.py"
spec = importlib.util.spec_from_file_location("check_public_safety", SCRIPT)
scanner = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(scanner)


class PublicSafetyTest(unittest.TestCase):
    def test_scanner_detects_generated_sensitive_literals(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            leaked = bytes.fromhex("4b616b616f").decode("utf-8")
            (root / "leak.txt").write_text(f"{leaked}\n", encoding="utf-8")
            findings = scanner.scan_file(root / "leak.txt", scanner.rules())
        self.assertTrue(any(rule_id == "source_name_en_1" for rule_id, _ in findings))

    def test_scanner_detects_phone_like_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            phone = "010" + "1234" + "5678"
            (root / "leak.txt").write_text(phone + "\n", encoding="utf-8")
            findings = scanner.scan_file(root / "leak.txt", scanner.rules())
        self.assertTrue(any(rule_id == "phone_number_kr" for rule_id, _ in findings))

    def test_scanner_passes_safe_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "safe.txt").write_text("insurer policy clause\n", encoding="utf-8")
            findings = scanner.scan_file(root / "safe.txt", scanner.rules())
        self.assertEqual(findings, [])


if __name__ == "__main__":
    unittest.main()
