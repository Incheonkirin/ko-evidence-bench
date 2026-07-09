"""Trap-class mining diagnostics for public probe queries."""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class TrapRule:
    trap_class: str
    diagnostic_layer: str
    pattern: re.Pattern[str]
    rationale: str


TRAP_RULES = (
    TrapRule(
        trap_class="bundle_expansion",
        diagnostic_layer="surface_fragmentation",
        pattern=re.compile(r"암\s*/?\s*뇌\s*/?\s*심|암뇌심|뇌혈관질환.*심장질환|심장질환.*뇌혈관질환"),
        rationale="bundled coverage appears as slash, abbreviation, or fully spelled components",
    ),
    TrapRule(
        trap_class="abbreviation",
        diagnostic_layer="surface_fragmentation",
        pattern=re.compile(r"암뇌심|실비"),
        rationale="consumer shorthand needs expansion before matching formal evidence",
    ),
    TrapRule(
        trap_class="messenger_shorthand",
        diagnostic_layer="surface_fragmentation",
        pattern=re.compile(r"/|보는 거|봐야 해요|가능해요|받은 거|맞나요"),
        rationale="short conversational phrasing often drops formal evidence terms",
    ),
    TrapRule(
        trap_class="negation_or_exclusion",
        diagnostic_layer="semantic_contrast",
        pattern=re.compile(r"비급여|면책|제외|거절|안 되는|안되는"),
        rationale="privative or exclusion terms can invert retrieval semantics",
    ),
    TrapRule(
        trap_class="register_mismatch",
        diagnostic_layer="register_gap",
        pattern=re.compile(r"실비|일반적인 설명|궁금해요"),
        rationale="consumer register differs from formal policy or expert wording",
    ),
    TrapRule(
        trap_class="product_table",
        diagnostic_layer="evidence_form",
        pattern=re.compile(r"해지환급금|환급금|예시표|표 봐|산정"),
        rationale="answer evidence is often tabular or disclosure-specific",
    ),
    TrapRule(
        trap_class="needs_private_context",
        diagnostic_layer="abstention",
        pattern=re.compile(r"가입 가능|인수 가능|판단해 주세요|과거 치료|치료받은|치료 이력"),
        rationale="question asks for case-specific underwriting judgment",
    ),
    TrapRule(
        trap_class="source_routing",
        diagnostic_layer="source_route",
        pattern=re.compile(r"청구|진단서|영수증|서류|분쟁|지급 거절|상품설명서|소비자 유의사항|고지의무"),
        rationale="query points to non-clause evidence or expert/official explanation",
    ),
    TrapRule(
        trap_class="numeric_constraint",
        diagnostic_layer="constraint_precision",
        pattern=re.compile(r"\d+\s*(세|개월|일|년|회|만원|억)|[0-9]+대"),
        rationale="number-unit constraints need exact handling",
    ),
)


def detect_traps(query: str) -> list[dict[str, str]]:
    """Return trap detections for a query, preserving rule order."""

    detections: list[dict[str, str]] = []
    seen: set[str] = set()
    for rule in TRAP_RULES:
        if rule.pattern.search(query):
            if rule.trap_class in seen:
                continue
            detections.append(
                {
                    "trap_class": rule.trap_class,
                    "diagnostic_layer": rule.diagnostic_layer,
                    "rationale": rule.rationale,
                }
            )
            seen.add(rule.trap_class)
    return detections


def compare_probe_traps(queries: list[dict[str, Any]], qrels: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Compare mined trap classes against qrel metadata."""

    qrel_by_qid = {str(row["qid"]): row for row in qrels}
    rows: list[dict[str, Any]] = []
    for query in queries:
        qid = str(query["qid"])
        qrel = qrel_by_qid[qid]
        detected = detect_traps(str(query["query"]))
        detected_classes = [row["trap_class"] for row in detected]
        expected_classes = [str(item) for item in qrel.get("trap_classes") or []]
        detected_set = set(detected_classes)
        expected_set = set(expected_classes)
        rows.append(
            {
                "qid": qid,
                "intent_family": str(qrel.get("intent_family", "")),
                "surface_form": str(qrel.get("surface_form", "")),
                "detected_traps": detected_classes,
                "expected_traps": expected_classes,
                "matched_traps": sorted(detected_set & expected_set),
                "missed_traps": sorted(expected_set - detected_set),
                "extra_traps": sorted(detected_set - expected_set),
                "diagnostic_layers": sorted({row["diagnostic_layer"] for row in detected}),
            }
        )
    return rows


def summarize_trap_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    expected: Counter[str] = Counter()
    detected: Counter[str] = Counter()
    matched: Counter[str] = Counter()
    missed: Counter[str] = Counter()
    extra: Counter[str] = Counter()
    layers: Counter[str] = Counter()
    by_surface: dict[str, Counter[str]] = defaultdict(Counter)
    by_family: dict[str, Counter[str]] = defaultdict(Counter)

    for row in rows:
        expected.update(row["expected_traps"])
        detected.update(row["detected_traps"])
        matched.update(row["matched_traps"])
        missed.update(row["missed_traps"])
        extra.update(row["extra_traps"])
        layers.update(row["diagnostic_layers"])
        by_surface[row["surface_form"]].update(row["detected_traps"])
        by_family[row["intent_family"]].update(row["detected_traps"])

    rows_with_any_detection = sum(1 for row in rows if row["detected_traps"])
    rows_with_full_expected_cover = sum(1 for row in rows if not row["missed_traps"])
    rows_with_extra = sum(1 for row in rows if row["extra_traps"])

    return {
        "rows": len(rows),
        "rows_with_any_detection": rows_with_any_detection,
        "rows_with_full_expected_cover": rows_with_full_expected_cover,
        "rows_with_extra": rows_with_extra,
        "expected": expected,
        "detected": detected,
        "matched": matched,
        "missed": missed,
        "extra": extra,
        "layers": layers,
        "by_surface": by_surface,
        "by_family": by_family,
    }
