"""Surface-form robustness metrics for intent-level retrieval variants."""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

from .schemas import validate_qrel, validate_run


def _topk(run: dict[str, Any], k: int) -> list[dict[str, Any]]:
    return list(run.get("ranked", []))[:k]


def _safe_div(num: int | float, den: int | float) -> float:
    return float(num) / float(den) if den else 0.0


def _default_run(qid: str) -> dict[str, Any]:
    return {"qid": qid, "route_pred": "out_of_scope", "abstained": True, "ranked": []}


def variant_outcome(qrel: dict[str, Any], run: dict[str, Any], *, k: int) -> dict[str, Any]:
    """Return per-query outcome fields used by surface robustness metrics."""

    route_ok = run["route_pred"] == qrel["route_gold"]
    should_abstain = bool(qrel["should_abstain"])
    expected = set(qrel["sufficient_evidence_ids"])
    evidence_hit = bool(expected and any(item["evidence_id"] in expected for item in _topk(run, k)))

    if should_abstain:
        task_success = route_ok and run["abstained"]
    else:
        task_success = route_ok and not run["abstained"] and evidence_hit

    return {
        "qid": qrel["qid"],
        "intent_id": str(qrel.get("intent_id") or "<missing>"),
        "surface_form": str(qrel.get("surface_form") or "<missing>"),
        "route_ok": route_ok,
        "should_abstain": should_abstain,
        "evidence_hit": evidence_hit,
        "task_success": task_success,
        "missing_surface_metadata": not qrel.get("intent_id") or not qrel.get("surface_form"),
    }


def surface_outcomes(
    qrels: list[dict[str, Any]],
    run_rows: list[dict[str, Any]],
    *,
    k: int = 3,
) -> list[dict[str, Any]]:
    run_by_qid: dict[str, dict[str, Any]] = {}
    for run in run_rows:
        validate_run(run)
        run_by_qid[run["qid"]] = run

    outcomes: list[dict[str, Any]] = []
    for qrel in qrels:
        validate_qrel(qrel)
        run = run_by_qid.get(qrel["qid"], _default_run(qrel["qid"]))
        outcomes.append(variant_outcome(qrel, run, k=k))
    return outcomes


def _rate(rows: list[dict[str, Any]], key: str) -> float:
    return _safe_div(sum(1 for row in rows if row[key]), len(rows))


def _answerable_evidence_rate(rows: list[dict[str, Any]]) -> float:
    answerable = [row for row in rows if not row["should_abstain"]]
    return _safe_div(sum(1 for row in answerable if row["evidence_hit"]), len(answerable))


def score_surface_run(
    qrels: list[dict[str, Any]],
    run_rows: list[dict[str, Any]],
    *,
    k: int = 3,
) -> dict[str, float]:
    outcomes = surface_outcomes(qrels, run_rows, k=k)
    by_intent: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_surface: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in outcomes:
        by_intent[row["intent_id"]].append(row)
        by_surface[row["surface_form"]].append(row)

    spreads: list[float] = []
    robust_intents = 0
    for rows in by_intent.values():
        rates_by_surface: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in rows:
            rates_by_surface[row["surface_form"]].append(row)
        surface_rates = [_rate(surface_rows, "task_success") for surface_rows in rates_by_surface.values()]
        spread = max(surface_rates) - min(surface_rates) if surface_rates else 0.0
        spreads.append(spread)
        if spread == 0.0:
            robust_intents += 1

    surface_rates = [_rate(rows, "task_success") for rows in by_surface.values()]
    return {
        "n": float(len(outcomes)),
        "intent_count": float(len(by_intent)),
        "surface_count": float(len(by_surface)),
        f"task_success@{k}": _rate(outcomes, "task_success"),
        "route_accuracy": _rate(outcomes, "route_ok"),
        f"answerable_evidence@{k}": _answerable_evidence_rate(outcomes),
        "avg_intent_surface_spread": sum(spreads) / len(spreads) if spreads else 0.0,
        "robust_intent_share": _safe_div(robust_intents, len(by_intent)),
        f"worst_surface_task_success@{k}": min(surface_rates) if surface_rates else 0.0,
        "missing_surface_metadata": float(sum(1 for row in outcomes if row["missing_surface_metadata"])),
    }


def surface_breakdown(
    qrels: list[dict[str, Any]],
    run_rows: list[dict[str, Any]],
    *,
    k: int = 3,
) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in surface_outcomes(qrels, run_rows, k=k):
        grouped[row["surface_form"]].append(row)

    rows: list[dict[str, Any]] = []
    for surface_form in sorted(grouped):
        surface_rows = grouped[surface_form]
        rows.append(
            {
                "surface_form": surface_form,
                "n": float(len(surface_rows)),
                f"task_success@{k}": _rate(surface_rows, "task_success"),
                "route_accuracy": _rate(surface_rows, "route_ok"),
                f"answerable_evidence@{k}": _answerable_evidence_rate(surface_rows),
            }
        )
    return rows


def intent_breakdown(
    qrels: list[dict[str, Any]],
    run_rows: list[dict[str, Any]],
    *,
    k: int = 3,
) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in surface_outcomes(qrels, run_rows, k=k):
        grouped[row["intent_id"]].append(row)

    rows: list[dict[str, Any]] = []
    for intent_id in sorted(grouped):
        intent_rows = grouped[intent_id]
        by_surface: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in intent_rows:
            by_surface[row["surface_form"]].append(row)
        surface_rates = {
            surface: _rate(surface_rows, "task_success")
            for surface, surface_rows in sorted(by_surface.items())
        }
        min_rate = min(surface_rates.values()) if surface_rates else 0.0
        max_rate = max(surface_rates.values()) if surface_rates else 0.0
        rows.append(
            {
                "intent_id": intent_id,
                "variant_count": float(len(intent_rows)),
                "surface_count": float(len(surface_rates)),
                "surfaces": ",".join(surface_rates),
                f"task_success@{k}": _rate(intent_rows, "task_success"),
                "min_surface_success": min_rate,
                "max_surface_success": max_rate,
                "surface_spread": max_rate - min_rate,
            }
        )
    return rows


def surface_inventory(qrels: list[dict[str, Any]]) -> dict[str, Counter[str]]:
    by_intent: Counter[str] = Counter()
    by_surface: Counter[str] = Counter()
    for qrel in qrels:
        validate_qrel(qrel)
        by_intent[str(qrel.get("intent_id") or "<missing>")] += 1
        by_surface[str(qrel.get("surface_form") or "<missing>")] += 1
    return {"intent_id": by_intent, "surface_form": by_surface}
