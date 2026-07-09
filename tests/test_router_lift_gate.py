import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_router_lift.py"
spec = importlib.util.spec_from_file_location("check_router_lift", SCRIPT)
router_lift = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = router_lift
spec.loader.exec_module(router_lift)


ROUTER_REPORT = """# Private Source-Route Router Baselines

## Metrics

| system | metric | value | 95% CI |
|---|---|---:|---:|
| query_keyword_router | `route_accuracy` | 31.8% | 27.8% - 35.7% |
| query_keyword_router | `abstention_recall` | 10.5% | 7.1% - 14.1% |
| cohort_aware_query_router | `route_accuracy` | 46.9% | 43.0% - 51.3% |
| cohort_aware_query_router | `abstention_recall` | 67.0% | 61.5% - 72.7% |

## Paired Delta vs `always_policy`

| system | metric | delta | 95% CI |
|---|---|---:|---:|
| cohort_aware_query_router | `route_accuracy` | 25.4% | 19.3% - 31.6% |
"""


ROUTE_SCORECARD = """# Private Silver Route Scorecard

## Largest Route Confusions

| system | gold source tier | predicted source tier | count | share of run |
|---|---|---|---:|---:|
| `cohort_aware_query_router` | `human_context_needed` | `policy_clause` | 28 | 5.1% |
"""


class RouterLiftGateTest(unittest.TestCase):
    def write_reports(self, directory: Path) -> tuple[Path, Path]:
        router_report = directory / "router.md"
        scorecard = directory / "scorecard.md"
        router_report.write_text(ROUTER_REPORT, encoding="utf-8")
        scorecard.write_text(ROUTE_SCORECARD, encoding="utf-8")
        return router_report, scorecard

    def test_rendered_gate_passes_with_aggregate_only_signals(self):
        with tempfile.TemporaryDirectory() as tmp:
            router_report, scorecard = self.write_reports(Path(tmp))
            signals = router_lift.load_signals(
                router_report=router_report,
                route_scorecard=scorecard,
                baseline="query_keyword_router",
                candidate="cohort_aware_query_router",
            )
            report = router_lift.render_report(
                signals,
                min_route_lift_pp=10.0,
                min_abstention_recall_lift_pp=30.0,
                max_context_policy_fallback_rows=50,
            )

        self.assertIn("Status: **PASS**", report)
        self.assertIn("route accuracy lift", report)
        self.assertIn("15.1%p", report)
        self.assertIn("56.5%p", report)
        self.assertIn("25.4%p", report)
        self.assertIn("silver proxy, not human-gold", report)
        self.assertNotIn("q_open_", report)
        self.assertNotIn("raw query", report.lower())

    def test_cli_fails_when_thresholds_are_not_met(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            router_report, scorecard = self.write_reports(tmp_path)
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--router-report",
                    str(router_report),
                    "--route-scorecard",
                    str(scorecard),
                    "--min-route-lift-pp",
                    "20",
                    "--out",
                    str(tmp_path / "gate.md"),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("router lift gate failed", result.stderr)

    def test_check_mode_detects_current_and_stale_reports(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            router_report, scorecard = self.write_reports(tmp_path)
            out = tmp_path / "gate.md"
            base_cmd = [
                sys.executable,
                str(SCRIPT),
                "--router-report",
                str(router_report),
                "--route-scorecard",
                str(scorecard),
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

        self.assertIn("router lift gate passed", current.stdout)
        self.assertNotEqual(stale.returncode, 0)
        self.assertIn("router lift gate report is stale", stale.stdout)


if __name__ == "__main__":
    unittest.main()
