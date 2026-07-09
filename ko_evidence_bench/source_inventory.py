"""Source inventory readiness checks against private aggregate demand."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .schemas import ROUTE_LABELS
from .source_catalog import SEARCHABLE_TIERS


VALID_INVENTORY_STATUSES = {
    "verified_private",
    "needs_inventory_audit",
    "not_searchable_route",
}
VALID_RIGHTS_STATUSES = {
    "private_eval_only",
    "needs_rights_review",
    "not_applicable",
}
VALID_PUBLIC_RELEASE = {
    "aggregate_only",
    "none",
    "not_applicable",
}


@dataclass(frozen=True)
class SourceInventoryIssue:
    source_tier: str
    field: str
    message: str


@dataclass(frozen=True)
class SourceInventoryRow:
    source_tier: str
    demand_rows: int
    inventory_status: str
    record_count: int | None
    rights_status: str
    public_release: str
    readiness: str
    notes: str


@dataclass(frozen=True)
class SourceInventoryResult:
    rows: tuple[SourceInventoryRow, ...]
    issues: tuple[SourceInventoryIssue, ...]
    total_demand_rows: int

    @property
    def blocked_tiers(self) -> tuple[str, ...]:
        return tuple(row.source_tier for row in self.rows if row.readiness == "BLOCKED")

    @property
    def status(self) -> str:
        if self.issues:
            return "INVALID"
        if self.blocked_tiers:
            return "ACTION_REQUIRED"
        return "READY"


def load_source_inventory(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("source inventory must be a JSON object")
    return data


def inventory_rows(inventory: dict[str, Any]) -> list[dict[str, Any]]:
    rows = inventory.get("inventories")
    if not isinstance(rows, list):
        raise ValueError("source inventory must contain an inventories list")
    return rows


def validate_source_inventory(inventory: dict[str, Any]) -> list[SourceInventoryIssue]:
    issues: list[SourceInventoryIssue] = []
    seen: set[str] = set()
    for row in inventory_rows(inventory):
        tier = str(row.get("source_tier") or "")
        if not tier:
            issues.append(SourceInventoryIssue("<missing>", "source_tier", "source_tier is required"))
            continue
        if tier in seen:
            issues.append(SourceInventoryIssue(tier, "source_tier", "source_tier must be unique"))
        seen.add(tier)
        if tier not in ROUTE_LABELS:
            issues.append(SourceInventoryIssue(tier, "source_tier", f"unknown route label: {tier}"))
        status = str(row.get("inventory_status") or "")
        rights = str(row.get("rights_status") or "")
        release = str(row.get("public_release") or "")
        if status not in VALID_INVENTORY_STATUSES:
            issues.append(SourceInventoryIssue(tier, "inventory_status", f"unknown status: {status}"))
        if rights not in VALID_RIGHTS_STATUSES:
            issues.append(SourceInventoryIssue(tier, "rights_status", f"unknown status: {rights}"))
        if release not in VALID_PUBLIC_RELEASE:
            issues.append(SourceInventoryIssue(tier, "public_release", f"unknown status: {release}"))
        record_count = row.get("record_count")
        if record_count is not None and (not isinstance(record_count, int) or record_count < 0):
            issues.append(SourceInventoryIssue(tier, "record_count", "record_count must be a non-negative integer or null"))
    for tier in sorted(ROUTE_LABELS - seen):
        issues.append(SourceInventoryIssue(tier, "source_tier", "inventory row is missing"))
    return issues


ROUTE_COUNT_RE = re.compile(r"^\| `([^`]+)` \| ([\d,]+) \|")


def parse_route_label_counts(report: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    in_table = False
    for line in report.splitlines():
        if line.strip() == "## Route Label Counts":
            in_table = True
            continue
        if in_table and line.startswith("## "):
            break
        if not in_table:
            continue
        match = ROUTE_COUNT_RE.match(line)
        if match:
            counts[match.group(1)] = int(match.group(2).replace(",", ""))
    return counts


def row_readiness(*, tier: str, demand: int, status: str, record_count: int | None) -> str:
    if tier not in SEARCHABLE_TIERS:
        return "ABSTENTION"
    if demand == 0:
        return "NO_DEMAND"
    if status == "verified_private" and (record_count or 0) > 0:
        return "READY"
    return "BLOCKED"


def source_inventory_readiness(
    *,
    inventory: dict[str, Any],
    route_label_report: str,
) -> SourceInventoryResult:
    issues = validate_source_inventory(inventory)
    demand = parse_route_label_counts(route_label_report)
    rows: list[SourceInventoryRow] = []
    for row in inventory_rows(inventory):
        tier = str(row["source_tier"])
        record_count = row.get("record_count")
        status = str(row["inventory_status"])
        rows.append(
            SourceInventoryRow(
                source_tier=tier,
                demand_rows=demand.get(tier, 0),
                inventory_status=status,
                record_count=record_count if isinstance(record_count, int) else None,
                rights_status=str(row["rights_status"]),
                public_release=str(row["public_release"]),
                readiness=row_readiness(
                    tier=tier,
                    demand=demand.get(tier, 0),
                    status=status,
                    record_count=record_count if isinstance(record_count, int) else None,
                ),
                notes=str(row.get("notes") or ""),
            )
        )
    return SourceInventoryResult(
        rows=tuple(rows),
        issues=tuple(issues),
        total_demand_rows=sum(demand.values()),
    )
