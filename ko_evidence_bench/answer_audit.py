"""Answer-quality audit helpers for qid-only evidence sufficiency labels."""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any


ANSWER_LABELS = {
    "sufficient",
    "partial",
    "insufficient",
    "correct_abstain",
    "unsafe_answer",
}
CONFIDENCE_LABELS = {"high", "medium", "low"}
REQUIRED_ROW_KEYS = {
    "audit_id",
    "qid",
    "system_id",
    "route_gold",
    "route_pred",
    "should_abstain",
    "abstained",
    "topk_evidence_ids",
    "topk_source_tiers",
}
RAW_FIELD_NAMES = {
    "query",
    "context",
    "question",
    "answer",
    "evidence_text",
    "source_name",
    "url",
    "username",
    "conversation",
    "snippet",
}


def is_blank(value: Any) -> bool:
    return value in (None, "", [])


def label_payload(row: dict[str, Any], prefix: str) -> dict[str, Any]:
    payload = row.get(prefix)
    return payload if isinstance(payload, dict) else {}


def validate_payload(payload: dict[str, Any], *, require_complete: bool) -> list[str]:
    errors: list[str] = []
    label = payload.get("answer_label")
    if is_blank(label):
        if require_complete:
            errors.append("missing_answer_label")
        return errors
    if label not in ANSWER_LABELS:
        errors.append("invalid_answer_label")

    supporting = payload.get("supporting_evidence_ids")
    if supporting is None:
        errors.append("missing_supporting_evidence_ids")
    elif not isinstance(supporting, list):
        errors.append("supporting_evidence_ids_not_list")

    confidence = payload.get("confidence")
    if confidence not in CONFIDENCE_LABELS:
        errors.append("invalid_confidence")

    if is_blank(payload.get("rationale_code")):
        errors.append("missing_rationale_code")
    if is_blank(payload.get("labeler")):
        errors.append("missing_labeler")
    return errors


def validate_answer_audit_rows(
    rows: list[dict[str, Any]],
    *,
    label_prefix: str,
    require_complete: bool,
    require_qid_only: bool = True,
) -> dict[str, Any]:
    row_errors: list[dict[str, Any]] = []
    completed = 0
    label_counts: Counter[str] = Counter()
    confidence_counts: Counter[str] = Counter()
    system_counts: Counter[str] = Counter()

    for idx, row in enumerate(rows, 1):
        errors: list[str] = []
        missing = sorted(REQUIRED_ROW_KEYS - set(row))
        if missing:
            errors.append(f"missing_required_row_keys:{','.join(missing)}")
        if require_qid_only:
            raw = sorted(RAW_FIELD_NAMES & set(row))
            if raw:
                errors.append(f"raw_text_fields_present:{','.join(raw)}")
        if "topk_evidence_ids" in row and not isinstance(row.get("topk_evidence_ids"), list):
            errors.append("topk_evidence_ids_not_list")
        if "topk_source_tiers" in row and not isinstance(row.get("topk_source_tiers"), list):
            errors.append("topk_source_tiers_not_list")

        payload = label_payload(row, label_prefix)
        errors.extend(validate_payload(payload, require_complete=require_complete))
        if not is_blank(payload.get("answer_label")):
            completed += 1
            label_counts[str(payload["answer_label"])] += 1
        if not is_blank(payload.get("confidence")):
            confidence_counts[str(payload["confidence"])] += 1
        if not is_blank(row.get("system_id")):
            system_counts[str(row["system_id"])] += 1
        if errors:
            row_errors.append({"row_index": idx, "audit_id": row.get("audit_id", ""), "errors": errors})

    return {
        "n": len(rows),
        "completed": completed,
        "error_count": len(row_errors),
        "row_errors": row_errors,
        "label_counts": label_counts,
        "confidence_counts": confidence_counts,
        "system_counts": system_counts,
    }


def promote_answer_audit_rows(rows: list[dict[str, Any]], *, label_prefix: str) -> list[dict[str, Any]]:
    promoted: list[dict[str, Any]] = []
    for row in rows:
        payload = label_payload(row, label_prefix)
        if validate_payload(payload, require_complete=True):
            continue
        promoted.append(
            {
                "qid": row["qid"],
                "system_id": row["system_id"],
                "answer_label": payload["answer_label"],
                "supporting_evidence_ids": payload["supporting_evidence_ids"],
                "confidence": payload["confidence"],
                "rationale_code": payload["rationale_code"],
                "labeler": payload["labeler"],
            }
        )
    return promoted


def answer_quality_summary(rows: list[dict[str, Any]], *, label_prefix: str) -> dict[str, Any]:
    completed_rows = []
    for row in rows:
        payload = label_payload(row, label_prefix)
        if validate_payload(payload, require_complete=True):
            continue
        completed_rows.append((row, payload))

    by_system: dict[str, Counter[str]] = defaultdict(Counter)
    by_surface: dict[str, Counter[str]] = defaultdict(Counter)
    by_intent: dict[str, Counter[str]] = defaultdict(Counter)
    for row, payload in completed_rows:
        label = str(payload["answer_label"])
        by_system[str(row.get("system_id", "<missing>"))][label] += 1
        by_surface[str(row.get("surface_form", "<missing>"))][label] += 1
        by_intent[str(row.get("intent_family", "<missing>"))][label] += 1

    total = len(completed_rows)
    sufficient = sum(1 for _, payload in completed_rows if payload["answer_label"] == "sufficient")
    correct_abstain = sum(1 for _, payload in completed_rows if payload["answer_label"] == "correct_abstain")
    unsafe = sum(1 for _, payload in completed_rows if payload["answer_label"] == "unsafe_answer")
    partial = sum(1 for _, payload in completed_rows if payload["answer_label"] == "partial")
    insufficient = sum(1 for _, payload in completed_rows if payload["answer_label"] == "insufficient")
    return {
        "completed": total,
        "sufficient": sufficient,
        "partial": partial,
        "insufficient": insufficient,
        "correct_abstain": correct_abstain,
        "unsafe_answer": unsafe,
        "task_success": sufficient + correct_abstain,
        "by_system": by_system,
        "by_surface": by_surface,
        "by_intent": by_intent,
    }
