"""System comparison matrix coverage checks."""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

VALID_STATUSES = {"implemented", "not_run", "blocked"}
VALID_CLAIM_SCOPES = {"diagnostic", "fixture", "missing_for_full_matrix", "required_for_headline"}


@dataclass(frozen=True)
class MatrixIssue:
    system_id: str
    field: str
    message: str


def load_matrix(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def system_rows(matrix: dict[str, Any]) -> list[dict[str, Any]]:
    rows = matrix.get("systems")
    if not isinstance(rows, list):
        raise ValueError("system matrix must contain a systems list")
    return rows


def validate_matrix(matrix: dict[str, Any], *, root: Path) -> list[MatrixIssue]:
    issues: list[MatrixIssue] = []
    seen: set[str] = set()
    for row in system_rows(matrix):
        system_id = str(row.get("system_id") or "")
        if not system_id:
            issues.append(MatrixIssue("<missing>", "system_id", "system_id is required"))
            continue
        if system_id in seen:
            issues.append(MatrixIssue(system_id, "system_id", "system_id must be unique"))
        seen.add(system_id)

        status = str(row.get("current_status") or "")
        if status not in VALID_STATUSES:
            issues.append(MatrixIssue(system_id, "current_status", f"unknown status: {status}"))

        claim_scope = str(row.get("claim_scope") or "")
        if claim_scope not in VALID_CLAIM_SCOPES:
            issues.append(MatrixIssue(system_id, "claim_scope", f"unknown claim scope: {claim_scope}"))

        rows = row.get("rows")
        if not isinstance(rows, int) or rows < 0:
            issues.append(MatrixIssue(system_id, "rows", "rows must be a non-negative integer"))

        evidence = str(row.get("evidence") or "")
        if status == "implemented":
            if not evidence:
                issues.append(MatrixIssue(system_id, "evidence", "implemented systems require evidence"))
            elif not (root / evidence).exists():
                issues.append(MatrixIssue(system_id, "evidence", f"evidence path does not exist: {evidence}"))
            if rows == 0:
                issues.append(MatrixIssue(system_id, "rows", "implemented systems require rows > 0"))
        if status == "not_run" and evidence:
            issues.append(MatrixIssue(system_id, "evidence", "not_run systems should not cite evidence"))
        if status == "blocked" and not evidence:
            issues.append(MatrixIssue(system_id, "evidence", "blocked systems should cite the blocking gate"))
    return issues


def matrix_summary(matrix: dict[str, Any]) -> dict[str, Any]:
    rows = system_rows(matrix)
    by_status = Counter(str(row["current_status"]) for row in rows)
    by_family = Counter(str(row["family"]) for row in rows)
    implemented_rows = sum(int(row["rows"]) for row in rows if row["current_status"] == "implemented")
    missing_full_matrix = [
        str(row["system_id"])
        for row in rows
        if row["claim_scope"] == "missing_for_full_matrix" or row["current_status"] in {"not_run", "blocked"}
    ]
    return {
        "systems": len(rows),
        "implemented": by_status["implemented"],
        "not_run": by_status["not_run"],
        "blocked": by_status["blocked"],
        "families": len(by_family),
        "implemented_rows": implemented_rows,
        "missing_full_matrix": missing_full_matrix,
    }


def status_label(matrix: dict[str, Any], issues: list[MatrixIssue]) -> str:
    summary = matrix_summary(matrix)
    if issues:
        return "INVALID"
    if summary["not_run"] or summary["blocked"]:
        return "INCOMPLETE"
    return "COMPLETE"
