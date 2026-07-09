"""Runnable systems for the public synthetic probe package."""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .metrics import load_jsonl, score_run
from .surface import score_surface_run


WORD_RE = re.compile(r"[0-9A-Za-z가-힣]+")

SIGNAL_TERMS = [
    "암",
    "뇌혈관질환",
    "심장질환",
    "진단비",
    "실손의료보험",
    "실비",
    "비급여",
    "도수치료",
    "치료",
    "해지환급금",
    "환급금",
    "예시표",
    "표",
    "보험계약",
    "청구",
    "청구서",
    "진단서",
    "영수증",
    "서류",
    "지급",
    "거절",
    "분쟁",
    "상품설명서",
    "소비자",
    "유의사항",
    "계약",
    "고지의무",
    "가입",
    "인수",
    "과거",
    "가능",
]

SURFACE_EXPANSIONS = [
    (re.compile(r"암\s*/?\s*뇌\s*/?\s*심|암뇌심"), "암 뇌혈관질환 심장질환 진단비 담보 묶음"),
    (re.compile(r"실비"), "실손의료보험"),
    (re.compile(r"표\s*봐|얼마"), "해지환급금 예시표 산정 기준"),
    (re.compile(r"되는지|되나요|되요"), "보장 여부"),
    (re.compile(r"치료받|치료 이력|과거 치료"), "과거 치료 이력 인수 심사"),
    (re.compile(r"인수 가능|가입 가능"), "인수 가능 가입 가능 고지의무"),
]

ROUTE_RULES = [
    ("human_context_needed", ("가입 가능", "인수 가능", "판단해 주세요", "과거 치료", "치료받은")),
    ("claims_faq", ("청구", "진단서", "영수증", "서류")),
    ("dispute_case", ("분쟁", "지급 거절", "다투")),
    ("official_consumer_info", ("가입 전에", "소비자 유의사항", "계약 전")),
    ("expert_answer", ("고지의무", "일반적인 설명")),
    ("product_disclosure", ("해지환급금", "환급금", "예시표")),
    ("policy_clause", ("암", "뇌", "심", "비급여", "실손", "실비", "보장")),
]


@dataclass(frozen=True)
class ProbeInputs:
    queries: list[dict[str, Any]]
    qrels: list[dict[str, Any]]
    evidence: list[dict[str, Any]]


def load_probe_inputs(probe_dir: Path) -> ProbeInputs:
    return ProbeInputs(
        queries=load_jsonl(probe_dir / "queries.jsonl"),
        qrels=load_jsonl(probe_dir / "qrels.jsonl"),
        evidence=load_jsonl(probe_dir / "evidence.jsonl"),
    )


def tokenize(text: str) -> list[str]:
    lowered = text.lower()
    tokens = [token for token in WORD_RE.findall(lowered) if token]
    tokens.extend(term.lower() for term in SIGNAL_TERMS if term.lower() in lowered)
    return tokens


def expand_surface(text: str) -> str:
    expanded = text
    additions: list[str] = []
    for pattern, addition in SURFACE_EXPANSIONS:
        if pattern.search(text):
            additions.append(addition)
    if additions:
        expanded = f"{expanded} {' '.join(additions)}"
    return expanded


def evidence_text(row: dict[str, Any]) -> str:
    return " ".join(
        str(row.get(field, ""))
        for field in ("title", "text", "search_text")
        if row.get(field)
    )


class BM25Index:
    def __init__(self, evidence: list[dict[str, Any]]) -> None:
        self.evidence = evidence
        self.doc_tokens = [Counter(tokenize(evidence_text(row))) for row in evidence]
        self.doc_lengths = [sum(counter.values()) for counter in self.doc_tokens]
        self.avgdl = sum(self.doc_lengths) / len(self.doc_lengths) if self.doc_lengths else 0.0
        self.df: Counter[str] = Counter()
        for counter in self.doc_tokens:
            self.df.update(counter.keys())

    def score(self, query_tokens: list[str], doc_idx: int) -> float:
        if not query_tokens:
            return 0.0
        doc_counter = self.doc_tokens[doc_idx]
        dl = self.doc_lengths[doc_idx] or 1
        k1 = 1.2
        b = 0.75
        score = 0.0
        for token in query_tokens:
            tf = doc_counter.get(token, 0)
            if not tf:
                continue
            df = self.df[token]
            idf = math.log(1 + (len(self.evidence) - df + 0.5) / (df + 0.5))
            denom = tf + k1 * (1 - b + b * dl / (self.avgdl or 1))
            score += idf * (tf * (k1 + 1)) / denom
        return score


def predict_route(query: str) -> str | None:
    for route, needles in ROUTE_RULES:
        if any(needle in query for needle in needles):
            return route
    return None


def run_probe_system(inputs: ProbeInputs, *, system_id: str) -> list[dict[str, Any]]:
    if system_id not in {"probe_literal_lexical", "probe_normalized_lexical", "probe_route_aware_rerank"}:
        raise ValueError(f"unknown probe system: {system_id}")

    index = BM25Index(inputs.evidence)
    rows: list[dict[str, Any]] = []
    use_expansion = system_id in {"probe_normalized_lexical", "probe_route_aware_rerank"}
    use_route = system_id == "probe_route_aware_rerank"

    for query in inputs.queries:
        qid = str(query["qid"])
        raw_query = str(query["query"])
        route_hint = predict_route(raw_query) if use_route else None
        if route_hint == "human_context_needed":
            rows.append({"qid": qid, "route_pred": route_hint, "abstained": True, "ranked": []})
            continue

        query_text = expand_surface(raw_query) if use_expansion else raw_query
        query_tokens = tokenize(query_text)
        scored: list[tuple[float, dict[str, Any]]] = []
        for idx, evidence in enumerate(inputs.evidence):
            if use_route and route_hint and evidence["source_tier"] != route_hint:
                continue
            score = index.score(query_tokens, idx)
            if use_route and route_hint and evidence["source_tier"] == route_hint:
                score += 2.0
            scored.append((score, evidence))

        scored.sort(key=lambda item: (-item[0], item[1]["evidence_id"]))
        top_score = scored[0][0] if scored else 0.0
        ranked = [
            {
                "evidence_id": evidence["evidence_id"],
                "source_tier": evidence["source_tier"],
                "score": round(score, 6),
            }
            for score, evidence in scored
            if score > 0
        ]
        route_pred = ranked[0]["source_tier"] if ranked else "out_of_scope"
        rows.append(
            {
                "qid": qid,
                "route_pred": route_hint or route_pred,
                "abstained": top_score <= 0,
                "ranked": ranked,
            }
        )
    return rows


def build_probe_runs(inputs: ProbeInputs) -> dict[str, list[dict[str, Any]]]:
    return {
        system_id: run_probe_system(inputs, system_id=system_id)
        for system_id in ("probe_literal_lexical", "probe_normalized_lexical", "probe_route_aware_rerank")
    }


def score_probe_runs(inputs: ProbeInputs, runs: dict[str, list[dict[str, Any]]], *, k: int = 3) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for system_id, run_rows in runs.items():
        score = score_run(inputs.qrels, run_rows, k=k)
        surface = score_surface_run(inputs.qrels, run_rows, k=k)
        rows.append(
            {
                "system_id": system_id,
                "n": int(score["n"]),
                "route_accuracy": score["route_accuracy"],
                f"evidence_sufficiency@{k}": score[f"evidence_sufficiency@{k}"],
                f"wrong_source_rate@{k}": score[f"wrong_source_rate@{k}"],
                "abstention_precision": score["abstention_precision"],
                "abstention_recall": score["abstention_recall"],
                f"clause_recall@{k}": score[f"clause_recall@{k}"],
                f"task_success@{k}": surface[f"task_success@{k}"],
                "avg_intent_surface_spread": surface["avg_intent_surface_spread"],
                f"worst_surface_task_success@{k}": surface[f"worst_surface_task_success@{k}"],
            }
        )
    return rows
