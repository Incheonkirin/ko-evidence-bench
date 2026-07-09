"""Silver source-route labels derived from private qrel metadata.

These helpers intentionally avoid raw query text. They are for building a
private audit workset and aggregate public reports, not for claiming human-gold
route labels.
"""

from __future__ import annotations

from collections import Counter
from typing import Any


ROUTE_PRIORITY = {
    "human_context_needed": 0,
    "dispute_case": 1,
    "claims_faq": 2,
    "product_disclosure": 3,
    "expert_answer": 4,
    "policy_clause": 5,
}


def _haystack(row: dict[str, Any]) -> str:
    fields = [
        row.get("gate_category"),
        row.get("intent"),
        row.get("reason_code"),
        row.get("answer_structure"),
    ]
    fields.extend(row.get("required_facets") or [])
    return " ".join(str(x or "") for x in fields)


def derive_route_label(row: dict[str, Any]) -> dict[str, Any]:
    """Derive a conservative silver route label from qrel metadata.

    The mapping is deliberately simple and auditable. It should be reviewed and
    corrected before it is treated as a headline source-route label set.
    """

    text = _haystack(row)
    reason = str(row.get("reason_code") or "")

    route = "policy_clause"
    rationale = "policy_clause_direct"
    confidence = "medium"
    should_abstain = False

    if row.get("needs_contract") or reason == "needs_contract":
        route = "human_context_needed"
        rationale = "needs_private_contract"
        confidence = "high"
        should_abstain = True
    elif any(token in text for token in ("분쟁", "민원", "지급거절", "거절", "부지급", "심사")):
        route = "dispute_case"
        rationale = "dispute_needed"
        confidence = "medium"
    elif any(token in text for token in ("청구", "서류", "접수", "지급기일", "소멸시효")):
        route = "claims_faq"
        rationale = "claims_ops"
        confidence = "medium"
    elif any(token in text for token in ("해지환급", "해약환급", "환급", "보험료", "사업비", "갱신", "만기")):
        route = "product_disclosure"
        rationale = "product_table_needed"
        confidence = "medium"
    elif reason == "not_in_corpus":
        route = "expert_answer"
        rationale = "policy_corpus_insufficient"
        confidence = "low"
    elif reason == "requires_table_value":
        route = "policy_clause"
        rationale = "contract_table_direct"
        confidence = "medium"

    if row.get("product_divergent") and route == "policy_clause":
        confidence = "low"

    return {
        "qid": row["qid"],
        "route_gold": route,
        "allowed_source_tiers": [route],
        "should_abstain": should_abstain,
        "labeler": "silver-route-heuristic-v0",
        "confidence": confidence,
        "rationale_code": rationale,
    }


def summarize_route_labels(labels: list[dict[str, Any]]) -> dict[str, Counter[str]]:
    return {
        "route_gold": Counter(label["route_gold"] for label in labels),
        "should_abstain": Counter(str(label["should_abstain"]) for label in labels),
        "confidence": Counter(label["confidence"] for label in labels),
        "rationale_code": Counter(label["rationale_code"] for label in labels),
    }


def always_policy_baseline(labels: list[dict[str, Any]]) -> dict[str, float]:
    n = len(labels)
    if not n:
        return {"n": 0.0, "route_accuracy": 0.0, "abstention_recall": 0.0}
    route_hits = sum(1 for label in labels if label["route_gold"] == "policy_clause")
    abstain_needed = sum(1 for label in labels if label["should_abstain"])
    return {
        "n": float(n),
        "route_accuracy": route_hits / n,
        "abstention_recall": 0.0 if abstain_needed else 1.0,
    }


def route_floor(labels: list[dict[str, Any]]) -> dict[str, float]:
    """Return the majority-route floor for context.

    This is not a deployable system; it is a sanity floor for interpreting route
    accuracy on skewed label distributions.
    """

    n = len(labels)
    if not n:
        return {"n": 0.0, "route_accuracy": 0.0}
    counts = Counter(label["route_gold"] for label in labels)
    return {"n": float(n), "route_accuracy": max(counts.values()) / n}
