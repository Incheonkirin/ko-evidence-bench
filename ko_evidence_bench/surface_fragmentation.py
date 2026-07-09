"""Surface-fragmentation audit for public probe queries."""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class IntentSurfaceRule:
    intent_id: str
    audit_label: str
    exact_seed_pattern: re.Pattern[str]
    expanded_surface_pattern: re.Pattern[str]
    seed_description: str


PUBLIC_SURFACE_RULES = (
    IntentSurfaceRule(
        intent_id="cancer_brain_heart_bundle",
        audit_label="bundled coverage",
        exact_seed_pattern=re.compile(r"암,\s*뇌혈관질환,\s*심장질환"),
        expanded_surface_pattern=re.compile(r"암\s*/?\s*뇌\s*/?\s*심|암뇌심|뇌혈관질환.*심장질환"),
        seed_description="formal component listing only",
    ),
    IntentSurfaceRule(
        intent_id="indemnity_noncovered_treatment",
        audit_label="indemnity non-covered treatment",
        exact_seed_pattern=re.compile(r"실손의료보험.*비급여"),
        expanded_surface_pattern=re.compile(r"실손의료보험.*비급여|비급여.*실비|실비.*비급여"),
        seed_description="formal product term only",
    ),
    IntentSurfaceRule(
        intent_id="refund_termination",
        audit_label="termination refund",
        exact_seed_pattern=re.compile(r"해지.*해지환급금.*산정"),
        expanded_surface_pattern=re.compile(r"해지.*해지환급금|해지.*환급금|환급금.*표"),
        seed_description="formal refund calculation wording only",
    ),
    IntentSurfaceRule(
        intent_id="underwriting_context_needed",
        audit_label="underwriting context needed",
        exact_seed_pattern=re.compile(r"과거 치료 이력.*가입 가능"),
        expanded_surface_pattern=re.compile(r"과거 치료 이력.*가입 가능|치료받은 거.*인수 가능|인수 가능"),
        seed_description="formal underwriting wording only",
    ),
)


def _qid_to_query(queries: list[dict[str, Any]]) -> dict[str, str]:
    return {str(row["qid"]): str(row.get("query") or "") for row in queries}


def _qid_to_qrel(qrels: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(row["qid"]): row for row in qrels}


def audit_surface_fragmentation(
    queries: list[dict[str, Any]],
    qrels: list[dict[str, Any]],
    rules: tuple[IntentSurfaceRule, ...] = PUBLIC_SURFACE_RULES,
) -> list[dict[str, Any]]:
    """Compare seed-only matches with intent-level qrel membership."""

    query_by_qid = _qid_to_query(queries)
    qrel_by_qid = _qid_to_qrel(qrels)
    rows: list[dict[str, Any]] = []
    for rule in rules:
        intent_qids = [
            qid for qid, row in qrel_by_qid.items() if str(row.get("intent_id") or "") == rule.intent_id
        ]
        seed_qids = [qid for qid in intent_qids if rule.exact_seed_pattern.search(query_by_qid.get(qid, ""))]
        expanded_qids = [
            qid for qid in intent_qids if rule.expanded_surface_pattern.search(query_by_qid.get(qid, ""))
        ]
        qrel_qids = set(intent_qids)
        seed_set = set(seed_qids)
        expanded_set = set(expanded_qids)
        missed_by_seed = sorted(qrel_qids - seed_set)
        missed_by_expanded = sorted(qrel_qids - expanded_set)
        surface_counts = Counter(str(qrel_by_qid[qid].get("surface_form") or "<missing>") for qid in intent_qids)
        missed_surface_counts = Counter(
            str(qrel_by_qid[qid].get("surface_form") or "<missing>") for qid in missed_by_seed
        )
        rows.append(
            {
                "intent_id": rule.intent_id,
                "audit_label": rule.audit_label,
                "seed_description": rule.seed_description,
                "qrel_rows": len(qrel_qids),
                "seed_rows": len(seed_set),
                "expanded_rows": len(expanded_set),
                "seed_recall": len(seed_set & qrel_qids) / len(qrel_qids) if qrel_qids else 0.0,
                "expanded_recall": len(expanded_set & qrel_qids) / len(qrel_qids) if qrel_qids else 0.0,
                "undercount_factor": (len(qrel_qids) / len(seed_set)) if seed_set else float("inf"),
                "missed_by_seed": missed_by_seed,
                "missed_by_expanded": missed_by_expanded,
                "surface_counts": surface_counts,
                "missed_surface_counts": missed_surface_counts,
            }
        )
    return rows


def summarize_fragmentation_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    total_qrel = sum(int(row["qrel_rows"]) for row in rows)
    total_seed = sum(int(row["seed_rows"]) for row in rows)
    total_expanded = sum(int(row["expanded_rows"]) for row in rows)
    surface_counts: Counter[str] = Counter()
    missed_surface_counts: Counter[str] = Counter()
    for row in rows:
        surface_counts.update(row["surface_counts"])
        missed_surface_counts.update(row["missed_surface_counts"])
    return {
        "intents": len(rows),
        "qrel_rows": total_qrel,
        "seed_rows": total_seed,
        "expanded_rows": total_expanded,
        "seed_recall": total_seed / total_qrel if total_qrel else 0.0,
        "expanded_recall": total_expanded / total_qrel if total_qrel else 0.0,
        "undercount_factor": (total_qrel / total_seed) if total_seed else float("inf"),
        "surface_counts": surface_counts,
        "missed_surface_counts": missed_surface_counts,
        "max_undercount_factor": max((float(row["undercount_factor"]) for row in rows), default=0.0),
    }
