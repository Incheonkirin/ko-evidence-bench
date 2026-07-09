"""Validation and promotion helpers for route-audit rows."""

from __future__ import annotations

from collections import Counter
from typing import Any

from .agreement import get_path


ROUTE_LABELS = {
    "policy_clause",
    "product_disclosure",
    "official_consumer_info",
    "claims_faq",
    "dispute_case",
    "expert_answer",
    "human_context_needed",
    "out_of_scope",
}

CONFIDENCE_LABELS = {"high", "medium", "low"}


def is_blank(value: Any) -> bool:
    return value in (None, "", [])


def label_payload(row: dict[str, Any], prefix: str) -> dict[str, Any]:
    """Read a route label payload from either nested or flat audit fields."""

    if prefix == "human":
        return {
            "route_gold": row.get("human_route_gold"),
            "allowed_source_tiers": row.get("human_allowed_source_tiers"),
            "should_abstain": row.get("human_should_abstain"),
            "confidence": row.get("human_confidence"),
            "rationale_code": row.get("human_rationale_code"),
            "labeler": row.get("human_labeler"),
            "notes": row.get("human_notes"),
        }
    payload = get_path(row, prefix)
    return payload if isinstance(payload, dict) else {}


def validate_payload(payload: dict[str, Any], *, require_complete: bool) -> list[str]:
    errors: list[str] = []
    route = payload.get("route_gold")
    if is_blank(route):
        if require_complete:
            errors.append("missing_route_gold")
        return errors
    if route not in ROUTE_LABELS:
        errors.append("invalid_route_gold")

    allowed = payload.get("allowed_source_tiers")
    if is_blank(allowed):
        errors.append("missing_allowed_source_tiers")
    elif not isinstance(allowed, list):
        errors.append("allowed_source_tiers_not_list")
    else:
        bad_allowed = [value for value in allowed if value not in ROUTE_LABELS]
        if bad_allowed:
            errors.append("invalid_allowed_source_tiers")

    if payload.get("should_abstain") not in (True, False):
        errors.append("invalid_should_abstain")

    confidence = payload.get("confidence")
    if confidence not in CONFIDENCE_LABELS:
        errors.append("invalid_confidence")

    if is_blank(payload.get("rationale_code")):
        errors.append("missing_rationale_code")

    return errors


def validate_audit_rows(
    rows: list[dict[str, Any]],
    *,
    label_prefix: str,
    require_complete: bool,
) -> dict[str, Any]:
    row_errors: list[dict[str, Any]] = []
    completed = 0
    route_counts: Counter[str] = Counter()
    confidence_counts: Counter[str] = Counter()

    for idx, row in enumerate(rows, 1):
        payload = label_payload(row, label_prefix)
        errors = validate_payload(payload, require_complete=require_complete)
        if errors:
            row_errors.append({"row_index": idx, "errors": errors})
        if not is_blank(payload.get("route_gold")):
            completed += 1
            route_counts[str(payload.get("route_gold"))] += 1
        if not is_blank(payload.get("confidence")):
            confidence_counts[str(payload.get("confidence"))] += 1

    return {
        "n": len(rows),
        "completed": completed,
        "error_count": len(row_errors),
        "row_errors": row_errors,
        "route_counts": route_counts,
        "confidence_counts": confidence_counts,
    }


def promoted_label(row: dict[str, Any], *, label_prefix: str) -> dict[str, Any] | None:
    payload = label_payload(row, label_prefix)
    if validate_payload(payload, require_complete=True):
        return None
    return {
        "qid": row["qid"],
        "route_gold": payload["route_gold"],
        "allowed_source_tiers": payload["allowed_source_tiers"],
        "should_abstain": payload["should_abstain"],
        "labeler": payload.get("labeler") or label_prefix,
        "confidence": payload["confidence"],
        "rationale_code": payload["rationale_code"],
    }


def promote_audit_rows(rows: list[dict[str, Any]], *, label_prefix: str) -> list[dict[str, Any]]:
    promoted: list[dict[str, Any]] = []
    for row in rows:
        label = promoted_label(row, label_prefix=label_prefix)
        if label:
            promoted.append(label)
    return promoted
