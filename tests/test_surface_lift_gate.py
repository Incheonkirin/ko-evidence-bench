import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_surface_lift.py"
spec = importlib.util.spec_from_file_location("check_surface_lift", SCRIPT)
surface_lift = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = surface_lift
spec.loader.exec_module(surface_lift)


SURFACE_REPORT = """# Surface Robustness Scorecard Fixture

## Surface Robustness Summary

| system | n | intents | surfaces | task_success@3 | route_acc | answerable_evidence@3 | avg_intent_spread | robust_intents | worst_surface@3 | missing metadata |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `formal_only_demo` | 8 | 3 | 4 | 37.5% | 75.0% | 33.3% | 100.0% | 0.0% | 0.0% | 0 |
| `surface_robust_demo` | 8 | 3 | 4 | 100.0% | 100.0% | 100.0% | 0.0% | 100.0% | 100.0% | 0 |
"""


class SurfaceLiftGateTest(unittest.TestCase):
    def test_rendered_gate_passes_with_aggregate_only_signals(self):
        with tempfile.TemporaryDirectory() as tmp:
            surface_report = Path(tmp) / "surface.md"
            surface_report.write_text(SURFACE_REPORT, encoding="utf-8")
            signals = surface_lift.load_signals(
                surface_report=surface_report,
                baseline="formal_only_demo",
                candidate="surface_robust_demo",
            )
            report = surface_lift.render_report(
                signals,
                min_task_success_lift_pp=30.0,
                min_spread_reduction_pp=30.0,
                min_worst_surface_lift_pp=30.0,
                max_missing_metadata=0,
            )

        self.assertIn("Status: **PASS**", report)
        self.assertIn("62.5%p", report)
        self.assertIn("100.0%p", report)
        self.assertIn("synthetic fixture, not human-gold", report)
        self.assertNotIn("raw query", report.lower())
        self.assertNotIn("q_open_", report)

    def test_cli_fails_when_thresholds_are_not_met(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            surface_report = tmp_path / "surface.md"
            surface_report.write_text(SURFACE_REPORT, encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--surface-report",
                    str(surface_report),
                    "--min-task-success-lift-pp",
                    "80",
                    "--out",
                    str(tmp_path / "gate.md"),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("surface lift gate failed", result.stderr)

    def test_check_mode_detects_current_and_stale_reports(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            surface_report = tmp_path / "surface.md"
            surface_report.write_text(SURFACE_REPORT, encoding="utf-8")
            out = tmp_path / "gate.md"
            base_cmd = [
                sys.executable,
                str(SCRIPT),
                "--surface-report",
                str(surface_report),
                "--out",
                str(out),
            ]
            subprocess.run(base_cmd, cwd=ROOT, check=True, capture_output=True, text=True)
            current = subprocess.run(
                [*base_cmd, "--check"],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            out.write_text(out.read_text(encoding="utf-8") + "\nextra\n", encoding="utf-8")
            stale = subprocess.run(
                [*base_cmd, "--check"],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )

        self.assertIn("surface lift gate passed", current.stdout)
        self.assertNotEqual(stale.returncode, 0)
        self.assertIn("surface lift gate report is stale", stale.stdout)


if __name__ == "__main__":
    unittest.main()
