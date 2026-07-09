"""Source-tier catalog validation and coverage summaries."""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .schemas import ROUTE_LABELS, validate_qrel


SEARCHABLE_TIERS = ROUTE_LABELS - {"human_context_needed", "out_of_scope"}
VALID_PUBLIC_STATUSES = {"covered", "planned", "abstention_only"}
VALID_PRIVATE_STATUSES = {
    "available_private_corpus",
    "planned_or_partial",
    "requires_user_context",
    "requires_filtering",
}
VALID_HEADLINE_STATUSES = {
    "silver_only",
    "needs_inventory_audit",
    "requires_abstention_audit",
}


@dataclass(frozen=True)
class SourceCatalogIssue:
    source_tier: str
    field: str
    message: str


@dataclass(frozen=True)
class SourceCoverageRow:
    source_tier: str
    role: str
    search_target: str
    public_probe_status: str
    private_status: str
    headline_status: str
    route_demand_rows: int
    allowed_support_rows: int
    evidence_rows: int
    sufficient_refs: int
    gate_status: str


@dataclass(frozen=True)
class SourceCoverageResult:
    issues: tuple[SourceCatalogIssue, ...]
    rows: tuple[SourceCoverageRow, ...]
    qrel_rows: int
    evidence_rows: int

    @property
    def status(self) -> str:
        return "PASS" if not self.issues and all(row.gate_status != "FAIL" for row in self.rows) else "FAIL"


def load_source_catalog(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("source catalog must be a JSON object")
    return data


def source_rows(catalog: dict[str, Any]) -> list[dict[str, Any]]:
    rows = catalog.get("tiers")
    if not isinstance(rows, list):
        raise ValueError("source catalog must contain a tiers list")
    return rows


def validate_source_catalog(catalog: dict[str, Any]) -> list[SourceCatalogIssue]:
    issues: list[SourceCatalogIssue] = []
    seen: set[str] = set()
    for row in source_rows(catalog):
        tier = str(row.get("source_tier") or "")
        if not tier:
            issues.append(SourceCatalogIssue("<missing>", "source_tier", "source_tier is required"))
            continue
        if tier in seen:
            issues.append(SourceCatalogIssue(tier, "source_tier", "source_tier must be unique"))
        seen.add(tier)
        if tier not in ROUTE_LABELS:
            issues.append(SourceCatalogIssue(tier, "source_tier", f"unknown route label: {tier}"))
        for field in ("role", "search_target"):
            if not str(row.get(field) or "").strip():
                issues.append(SourceCatalogIssue(tier, field, f"{field} is required"))
        public_status = str(row.get("public_probe_status") or "")
        private_status = str(row.get("private_status") or "")
        headline_status = str(row.get("headline_status") or "")
        if public_status not in VALID_PUBLIC_STATUSES:
            issues.append(SourceCatalogIssue(tier, "public_probe_status", f"unknown status: {public_status}"))
        if private_status not in VALID_PRIVATE_STATUSES:
            issues.append(SourceCatalogIssue(tier, "private_status", f"unknown status: {private_status}"))
        if headline_status not in VALID_HEADLINE_STATUSES:
            issues.append(SourceCatalogIssue(tier, "headline_status", f"unknown status: {headline_status}"))

    missing = sorted(ROUTE_LABELS - seen)
    for tier in missing:
        issues.append(SourceCatalogIssue(tier, "source_tier", "catalog row is missing"))
    return issues


def allowed_tiers(row: dict[str, Any]) -> list[str]:
    allowed = row.get("allowed_source_tiers")
    if isinstance(allowed, list) and allowed:
        return [str(item) for item in allowed]
    return [str(row["route_gold"])]


def evidence_tier_counts(evidence_rows: list[dict[str, Any]]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for row in evidence_rows:
        counts[str(row.get("source_tier") or "<missing>")] += 1
    return counts


def source_coverage(
    *,
    catalog: dict[str, Any],
    qrels: list[dict[str, Any]],
    evidence: list[dict[str, Any]],
) -> SourceCoverageResult:
    issues = validate_source_catalog(catalog)
    route_counts: Counter[str] = Counter()
    allowed_counts: Counter[str] = Counter()
    sufficient_counts: Counter[str] = Counter()
    evidence_by_id: dict[str, dict[str, Any]] = {}
    evidence_counts = evidence_tier_counts(evidence)

    for row in evidence:
        evidence_id = str(row.get("evidence_id") or "")
        tier = str(row.get("source_tier") or "")
        if tier not in ROUTE_LABELS:
            issues.append(SourceCatalogIssue(tier or "<missing>", "evidence.source_tier", "unknown source tier"))
        if evidence_id:
            evidence_by_id[evidence_id] = row

    for qrel in qrels:
        try:
            validate_qrel(qrel)
        except ValueError as exc:
            issues.append(SourceCatalogIssue(str(qrel.get("qid") or "<missing>"), "qrel", str(exc)))
            continue
        route_counts[str(qrel["route_gold"])] += 1
        allowed_counts.update(allowed_tiers(qrel))
        for evidence_id in qrel.get("sufficient_evidence_ids", []):
            evidence_row = evidence_by_id.get(str(evidence_id))
            if evidence_row is None:
                issues.append(SourceCatalogIssue(str(qrel["qid"]), "sufficient_evidence_ids", f"missing evidence id: {evidence_id}"))
                continue
            sufficient_counts[str(evidence_row.get("source_tier") or "<missing>")] += 1

    rows: list[SourceCoverageRow] = []
    for row in source_rows(catalog):
        tier = str(row["source_tier"])
        route_demand = route_counts[tier]
        allowed_support = allowed_counts[tier]
        evidence_count = evidence_counts[tier]
        sufficient_refs = sufficient_counts[tier]
        if tier in SEARCHABLE_TIERS and (route_demand or allowed_support) and evidence_count == 0:
            gate = "FAIL"
        elif tier in {"human_context_needed", "out_of_scope"}:
            gate = "ABSTENTION"
        elif evidence_count:
            gate = "COVERED"
        else:
            gate = "NO_DEMAND"
        rows.append(
            SourceCoverageRow(
                source_tier=tier,
                role=str(row["role"]),
                search_target=str(row["search_target"]),
                public_probe_status=str(row["public_probe_status"]),
                private_status=str(row["private_status"]),
                headline_status=str(row["headline_status"]),
                route_demand_rows=route_demand,
                allowed_support_rows=allowed_support,
                evidence_rows=evidence_count,
                sufficient_refs=sufficient_refs,
                gate_status=gate,
            )
        )

    return SourceCoverageResult(
        issues=tuple(issues),
        rows=tuple(rows),
        qrel_rows=len(qrels),
        evidence_rows=len(evidence),
    )
