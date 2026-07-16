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


    def test_scanner_detects_token_with_suffix(self):
        # e.g. Name + "ed" suffix; built from hex so this file stays clean
        leaked = bytes.fromhex("426c696e64").decode("utf-8") + "ed review"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "leak.txt").write_text(leaked + "\n", encoding="utf-8")
            findings = scanner.scan_file(root / "leak.txt", scanner.rules())
        self.assertTrue(any(rule_id == "source_name_en_4" for rule_id, _ in findings))

    def test_scanner_detects_url_host_token(self):
        host = bytes.fromhex("4b616b616f").decode("utf-8").lower()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "leak.txt").write_text(f"https://open.{host}.com/o/abc\n", encoding="utf-8")
            findings = scanner.scan_file(root / "leak.txt", scanner.rules())
        self.assertTrue(any(rule_id == "source_name_en_1" for rule_id, _ in findings))

    def test_scanner_detects_qid_prefix_token(self):
        qid = bytes.fromhex("626c696e645f").decode("utf-8") + "00123"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "leak.txt").write_text(f"qid={qid}\n", encoding="utf-8")
            findings = scanner.scan_file(root / "leak.txt", scanner.rules())
        self.assertTrue(any(rule_id == "source_qid_prefix_1" for rule_id, _ in findings))

    def test_scanner_detects_korean_name_inside_longer_token(self):
        leaked = bytes.fromhex("ec82bcec84b1").decode("utf-8") + "전자"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "leak.txt").write_text(leaked + "\n", encoding="utf-8")
            findings = scanner.scan_file(root / "leak.txt", scanner.rules())
        self.assertTrue(any(rule_id == "source_name_ko_3" for rule_id, _ in findings))



if __name__ == "__main__":
    unittest.main()
