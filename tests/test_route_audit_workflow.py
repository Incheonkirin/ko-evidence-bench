import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class RouteAuditWorkflowTest(unittest.TestCase):
    def test_reproduce_route_audit_workflow(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "workflow.md"
            subprocess.run(
                [sys.executable, "scripts/reproduce_route_audit_workflow.py", str(out)],
                cwd=root,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            report = out.read_text(encoding="utf-8")
        self.assertIn("reviewer raw agreement: 66.7%", report)
        self.assertIn("reviewer Cohen's kappa: 0.571", report)
        self.assertIn("adjudication validation errors: 0", report)
        self.assertIn("promoted labels: 3", report)


if __name__ == "__main__":
    unittest.main()
