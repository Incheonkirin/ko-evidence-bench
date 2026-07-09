"""Build qid-only intent/surface qrels from private qrel metadata."""

from __future__ import annotations

import hashlib
import re
from collections import Counter
from typing import Any

from .schemas import validate_qrel


FAMILY_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("refund_termination", re.compile(r"(해지|해약|환급|만기|보험료|납입|감액완납|갱신|사업비)")),
    ("claims_process", re.compile(r"(청구|서류|접수|지급기일|소멸시효)")),
    ("indemnity_noncovered", re.compile(r"(실손|실비|비급여|급여|도수|통원|입원|의료비)")),
    ("underwriting_context", re.compile(r"(고지|인수|부담보|청약|병력|계약 전 알릴 의무|조건부)")),
    ("dispute_complaint", re.compile(r"(분쟁|민원|부지급|지급거절|소송|감독기관|분쟁조정)")),
    ("bundled_coverage", re.compile(r"(암\s*/?\s*뇌|뇌\s*/?\s*심|암뇌심|진단비|수술비|치료비|심장|뇌혈관|암보험)")),
    ("dental_coverage", re.compile(r"(치아|임플란트|충치|치과|보존치료|보철|인레이|레진)")),
    ("product_design", re.compile(r"(특약|설계|상품|보장범위|보장여부|지급조건|지급사유|계약조항|용어정의)")),
]

ABBREVIATION_RE = re.compile(r"(실비|실손|암뇌심|뇌심|암주치|태아보험|유병자|간편고지)")
FORMAL_RE = re.compile(r"(약관|특약|계약|보장|담보|지급사유|보장개시|계약 전 알릴 의무)")
QUESTION_RE = re.compile(r"(\?|나요|까요|인가요|되나요|될까요|맞나요|뭔가요|가능|궁금)")
NUMERIC_RE = re.compile(r"(\d+\s*(년|개월|월|일|세|만원|억|회|종|대|급|%)|[일이삼사오육칠팔구십한두세네]\s*(년|개월|달|세|번|회))")
NEGATION_RE = re.compile(r"(비급여|무배당|부담보|미지급|부지급|면책|제외|불가|안\s*\S+|못\s*\S+)")
BUNDLE_RE = re.compile(r"(암\s*/?\s*뇌|뇌\s*/?\s*심|암뇌심|진단비|수술비|치료비)")


def _text(row: dict[str, Any]) -> str:
    values = [
        row.get("query"),
        row.get("gate_category"),
        row.get("intent"),
        row.get("reason_code"),
        row.get("answer_structure"),
    ]
    values.extend(row.get("required_facets") or [])
    return " ".join(str(value or "") for value in values)


def _query(row: dict[str, Any]) -> str:
    return re.sub(r"\s+", " ", str(row.get("query") or "")).strip()


def intent_family(row: dict[str, Any]) -> str:
    text = _text(row)
    for family, pattern in FAMILY_PATTERNS:
        if pattern.search(text):
            return family
    return "coverage_terms"


def surface_form(row: dict[str, Any]) -> str:
    query = _query(row)
    if ABBREVIATION_RE.search(query):
        return "abbreviated"
    if len(query) <= 40 and QUESTION_RE.search(query) and not FORMAL_RE.search(query):
        return "messenger_shorthand"
    if FORMAL_RE.search(query):
        return "formal"
    if QUESTION_RE.search(query):
        return "colloquial"
    return "formal"


def trap_classes(row: dict[str, Any], route_label: dict[str, Any]) -> list[str]:
    text = _text(row)
    surface = surface_form(row)
    traps: list[str] = []
    if NUMERIC_RE.search(text):
        traps.append("numeric_constraint")
    if NEGATION_RE.search(text):
        traps.append("negation_or_exclusion")
    if BUNDLE_RE.search(text):
        traps.append("bundle_expansion")
    if surface in {"abbreviated", "colloquial", "messenger_shorthand"}:
        traps.append("register_mismatch")
    if route_label.get("should_abstain") or route_label.get("route_gold") == "human_context_needed":
        traps.append("needs_private_context")
    if route_label.get("route_gold") != "policy_clause":
        traps.append("source_routing")
    if intent_family(row) == "refund_termination" or row.get("reason_code") == "requires_table_value":
        traps.append("product_table")
    if intent_family(row) == "claims_process":
        traps.append("claim_ops")
    if intent_family(row) == "dispute_complaint":
        traps.append("dispute_needed")
    return sorted(dict.fromkeys(traps)) or ["plain_clause_recall"]


def _stable_intent_id(row: dict[str, Any], family: str) -> str:
    seed = "|".join(
        [
            family,
            str(row.get("gate_category") or ""),
            str(row.get("answer_structure") or ""),
            str(row.get("reason_code") or ""),
        ]
    )
    digest = hashlib.sha1(seed.encode("utf-8")).hexdigest()[:10]
    return f"{family}_{digest}"


def evidence_ids(row: dict[str, Any]) -> list[str]:
    ids: list[str] = []
    for key in ("expanded_gold", "gold"):
        for item in row.get(key) or []:
            if not isinstance(item, dict):
                continue
            value = item.get("passage_id") or item.get("clause_id")
            if value:
                ids.append(str(value))
    return sorted(dict.fromkeys(ids))


def export_surface_qrel(row: dict[str, Any], route_label: dict[str, Any]) -> dict[str, Any]:
    family = intent_family(row)
    record = {
        "qid": row["qid"],
        "intent_family": family,
        "intent_id": _stable_intent_id(row, family),
        "surface_form": surface_form(row),
        "trap_classes": trap_classes(row, route_label),
        "route_gold": route_label["route_gold"],
        "allowed_source_tiers": route_label.get("allowed_source_tiers") or [route_label["route_gold"]],
        "should_abstain": bool(route_label["should_abstain"]),
        "sufficient_evidence_ids": [] if route_label["should_abstain"] else evidence_ids(row),
        "label_status": "silver_intent_surface_metadata",
    }
    validate_qrel(record)
    return record


def export_surface_qrels(
    qrels: list[dict[str, Any]],
    route_labels: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    labels_by_qid = {label["qid"]: label for label in route_labels}
    records: list[dict[str, Any]] = []
    stats = Counter()
    for row in qrels:
        stats["qrel_rows"] += 1
        label = labels_by_qid.get(row.get("qid"))
        if not label:
            stats["missing_route_label"] += 1
            continue
        record = export_surface_qrel(row, label)
        if not record["sufficient_evidence_ids"] and not record["should_abstain"]:
            stats["answerable_without_evidence_ids"] += 1
        records.append(record)
    stats["exported_rows"] = len(records)
    stats["route_label_rows"] = len(route_labels)
    stats.setdefault("missing_route_label", 0)
    stats.setdefault("answerable_without_evidence_ids", 0)
    return records, dict(stats)


def summarize_export(records: list[dict[str, Any]], stats: dict[str, int]) -> dict[str, Counter[str] | int]:
    return {
        **stats,
        "intent_family": Counter(record["intent_family"] for record in records),
        "surface_form": Counter(record["surface_form"] for record in records),
        "route_gold": Counter(record["route_gold"] for record in records),
        "trap_classes": Counter(trap for record in records for trap in record["trap_classes"]),
    }
