"""Coverage checks for qid-only human audit worksets."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Any

from .schemas import validate_qrel


@dataclass(frozen=True)
class CoverageSlice:
    name: str
    full_values: int
    sampled_values: int
    missing_values: tuple[str, ...]
    min_sampled_rows: int
    max_sampled_rows: int

    @property
    def complete(self) -> bool:
        return not self.missing_values


@dataclass(frozen=True)
class AuditCoverage:
    qrel_rows: int
    audit_rows: int
    matched_rows: int
    unmatched_audit_rows: int
    slices: tuple[CoverageSlice, ...]

    @property
    def complete(self) -> bool:
        return self.unmatched_audit_rows == 0 and all(item.complete for item in self.slices)


def audit_qids(audit_rows: list[dict[str, Any]]) -> list[str]:
    qids: list[str] = []
    for row in audit_rows:
        qid = row.get("qid")
        if not qid:
            raise ValueError("audit row missing qid")
        qids.append(str(qid))
    return qids


def _counter(rows: list[dict[str, Any]], key: str) -> Counter[str]:
    counts: Counter[str] = Counter()
    for row in rows:
        if key == "trap_classes":
            for value in row.get("trap_classes") or ["<none>"]:
                counts[str(value)] += 1
        else:
            counts[str(row.get(key) or "<missing>")] += 1
    return counts


def coverage_slice(qrels: list[dict[str, Any]], sampled_qrels: list[dict[str, Any]], key: str) -> CoverageSlice:
    full_counts = _counter(qrels, key)
    sampled_counts = _counter(sampled_qrels, key)
    missing = tuple(sorted(set(full_counts) - set(sampled_counts)))
    sampled_values = [sampled_counts[value] for value in full_counts if value in sampled_counts]
    return CoverageSlice(
        name=key,
        full_values=len(full_counts),
        sampled_values=len(sampled_counts),
        missing_values=missing,
        min_sampled_rows=min(sampled_values) if sampled_values else 0,
        max_sampled_rows=max(sampled_values) if sampled_values else 0,
    )


def audit_surface_coverage(
    qrels: list[dict[str, Any]],
    audit_rows: list[dict[str, Any]],
) -> AuditCoverage:
    for qrel in qrels:
        validate_qrel(qrel)

    qrel_by_qid = {str(row["qid"]): row for row in qrels}
    qids = audit_qids(audit_rows)
    sampled_qrels = [qrel_by_qid[qid] for qid in qids if qid in qrel_by_qid]
    unmatched = sum(1 for qid in qids if qid not in qrel_by_qid)
    slices = tuple(
        coverage_slice(qrels, sampled_qrels, key)
        for key in ("route_gold", "intent_family", "surface_form", "trap_classes")
    )
    return AuditCoverage(
        qrel_rows=len(qrels),
        audit_rows=len(audit_rows),
        matched_rows=len(sampled_qrels),
        unmatched_audit_rows=unmatched,
        slices=slices,
    )
