"""Small schema helpers for JSONL fixtures.

The public schema is intentionally minimal. Private adapters may add fields, but
the scorecard only needs stable query ids, source-route labels, abstention labels,
and ranked evidence items.
"""

from __future__ import annotations

from typing import Any


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


def require_keys(record: dict[str, Any], keys: set[str], *, kind: str) -> None:
    missing = keys - record.keys()
    if missing:
        raise ValueError(f"{kind} missing keys: {sorted(missing)}")


def validate_qrel(record: dict[str, Any]) -> None:
    require_keys(
        record,
        {"qid", "route_gold", "should_abstain", "sufficient_evidence_ids"},
        kind="qrel",
    )
    if record["route_gold"] not in ROUTE_LABELS:
        raise ValueError(f"unknown route_gold: {record['route_gold']}")
    if not isinstance(record["should_abstain"], bool):
        raise ValueError("should_abstain must be boolean")
    if not isinstance(record["sufficient_evidence_ids"], list):
        raise ValueError("sufficient_evidence_ids must be a list")
    if not all(isinstance(value, str) and value for value in record["sufficient_evidence_ids"]):
        raise ValueError("sufficient_evidence_ids must contain non-empty strings")
    if len(set(record["sufficient_evidence_ids"])) != len(record["sufficient_evidence_ids"]):
        raise ValueError("sufficient_evidence_ids must not contain duplicates")
    if not record["should_abstain"] and not record["sufficient_evidence_ids"]:
        raise ValueError("answerable qrels require sufficient_evidence_ids")
    if "required_evidence_ids" in record:
        required = record["required_evidence_ids"]
        if not isinstance(required, list):
            raise ValueError("required_evidence_ids must be a list")
        if not all(isinstance(value, str) and value for value in required):
            raise ValueError("required_evidence_ids must contain non-empty strings")
        if len(set(required)) != len(required):
            raise ValueError("required_evidence_ids must not contain duplicates")
        if record["should_abstain"] and required:
            raise ValueError("abstention qrels cannot require evidence")
        unknown_required = set(required) - set(record["sufficient_evidence_ids"])
        if unknown_required:
            raise ValueError(
                "required_evidence_ids must be included in sufficient_evidence_ids: "
                f"{sorted(unknown_required)}"
            )
    if "allowed_source_tiers" in record:
        if not isinstance(record["allowed_source_tiers"], list):
            raise ValueError("allowed_source_tiers must be a list")
        unknown = set(record["allowed_source_tiers"]) - ROUTE_LABELS
        if unknown:
            raise ValueError(f"unknown allowed_source_tiers: {sorted(unknown)}")


def validate_run(record: dict[str, Any]) -> None:
    require_keys(record, {"qid", "route_pred", "abstained", "ranked"}, kind="run")
    if record["route_pred"] not in ROUTE_LABELS:
        raise ValueError(f"unknown route_pred: {record['route_pred']}")
    if not isinstance(record["abstained"], bool):
        raise ValueError("abstained must be boolean")
    if not isinstance(record["ranked"], list):
        raise ValueError("ranked must be a list")
    for item in record["ranked"]:
        require_keys(item, {"evidence_id", "source_tier"}, kind="ranked item")
        if item["source_tier"] not in ROUTE_LABELS:
            raise ValueError(f"unknown source_tier: {item['source_tier']}")
