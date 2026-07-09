import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ko_evidence_bench.source_inventory import (
    load_source_inventory,
    parse_route_label_counts,
    source_inventory_readiness,
)
from scripts.build_source_inventory_report import render_report


ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "docs" / "source_inventory.json"
ROUTE_LABEL_REPORT = ROOT / "reports" / "private_route_label_summary.md"


class SourceInventoryTest(unittest.TestCase):
    def test_route_label_counts_are_parsed_from_aggregate_report(self):
        counts = parse_route_label_counts(ROUTE_LABEL_REPORT.read_text(encoding="utf-8"))

        self.assertEqual(counts["human_context_needed"], 276)
        self.assertEqual(counts["policy_clause"], 117)
        self.assertEqual(counts["product_disclosure"], 51)
        self.assertEqual(counts["dispute_case"], 48)
        self.assertEqual(counts["claims_faq"], 31)
        self.assertEqual(counts["expert_answer"], 21)

    def test_inventory_readiness_blocks_unverified_demanded_tiers(self):
        result = source_inventory_readiness(
            inventory=load_source_inventory(INVENTORY),
            route_label_report=ROUTE_LABEL_REPORT.read_text(encoding="utf-8"),
        )

        self.assertEqual(result.status, "ACTION_REQUIRED")
        self.assertEqual(result.total_demand_rows, 544)
        self.assertEqual(len(result.issues), 0)
        self.assertEqual(
            set(result.blocked_tiers),
            {"product_disclosure", "claims_faq", "dispute_case", "expert_answer"},
        )
        rows = {row.source_tier: row for row in result.rows}
        self.assertEqual(rows["policy_clause"].readiness, "READY")
        self.assertEqual(rows["policy_clause"].record_count, 36983)
        self.assertEqual(rows["human_context_needed"].readiness, "ABSTENTION")

    def test_report_names_action_required_without_raw_sources(self):
        report = render_report(inventory_path=INVENTORY, route_label_report_path=ROUTE_LABEL_REPORT)

        self.assertIn("ACTION_REQUIRED for private source inventory", report)
        self.assertIn("blocked searchable tiers: 4", report)
        self.assertIn("`product_disclosure`", report)
        self.assertIn("inventory gap", report)
        for blocked_name in ("Ka" + "kao", "Sam" + "sung", "A" + "ha"):
            self.assertNotIn(blocked_name, report)

    def test_build_script_check_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "source_inventory.md"
            subprocess.run(
                [sys.executable, "scripts/build_source_inventory_report.py", "--out", str(out)],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            result = subprocess.run(
                [sys.executable, "scripts/build_source_inventory_report.py", "--out", str(out), "--check"],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertIn("source inventory report is current", result.stdout)


if __name__ == "__main__":
    unittest.main()
