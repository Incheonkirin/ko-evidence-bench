"""Route and abstention robustness by intent and surface metadata."""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

from .route_score import validate_route_run
from .schemas import validate_qrel


def _safe_div(num: int | float, den: int | float) -> float:
    return float(num) / float(den) if den else 0.0


def route_surface_outcomes(qrels: list[dict[str, Any]], run_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    run_by_qid: dict[str, dict[str, Any]] = {}
    for row in run_rows:
        validate_route_run(row)
        run_by_qid[row["qid"]] = row

    outcomes: list[dict[str, Any]] = []
    for qrel in qrels:
        validate_qrel(qrel)
        run = run_by_qid.get(qrel["qid"])
        if run is None:
            route_pred = "out_of_scope"
            abstained = True
            missing = True
        else:
            route_pred = run["route_pred"]
            abstained = bool(run["abstained"])
            missing = False
        route_gold = qrel["route_gold"]
        should_abstain = bool(qrel["should_abstain"])
        outcomes.append(
            {
                "intent_family": str(qrel.get("intent_family") or "<missing>"),
                "intent_id": str(qrel.get("intent_id") or "<missing>"),
                "surface_form": str(qrel.get("surface_form") or "<missing>"),
                "trap_classes": [str(item) for item in qrel.get("trap_classes") or ["<none>"]],
                "route_gold": route_gold,
                "route_pred": route_pred,
                "route_ok": route_pred == route_gold,
                "should_abstain": should_abstain,
                "abstained": abstained,
                "abstain_tp": abstained and should_abstain,
                "abstain_fp": abstained and not should_abstain,
                "abstain_fn": (not abstained) and should_abstain,
                "missing": missing,
                "missing_surface_metadata": not qrel.get("intent_id") or not qrel.get("surface_form"),
            }
        )
    return outcomes


def rate(rows: list[dict[str, Any]], key: str) -> float:
    return _safe_div(sum(1 for row in rows if row[key]), len(rows))


def abstention_precision(rows: list[dict[str, Any]]) -> float:
    tp = sum(1 for row in rows if row["abstain_tp"])
    fp = sum(1 for row in rows if row["abstain_fp"])
    return _safe_div(tp, tp + fp)


def abstention_recall(rows: list[dict[str, Any]]) -> float:
    tp = sum(1 for row in rows if row["abstain_tp"])
    fn = sum(1 for row in rows if row["abstain_fn"])
    return _safe_div(tp, tp + fn)


def summarize_route_surface_run(qrels: list[dict[str, Any]], run_rows: list[dict[str, Any]]) -> dict[str, float]:
    outcomes = route_surface_outcomes(qrels, run_rows)
    by_intent: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_surface: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in outcomes:
        by_intent[row["intent_id"]].append(row)
        by_surface[row["surface_form"]].append(row)

    spreads: list[float] = []
    for rows in by_intent.values():
        rates_by_surface: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in rows:
            rates_by_surface[row["surface_form"]].append(row)
        surface_rates = [rate(surface_rows, "route_ok") for surface_rows in rates_by_surface.values()]
        if surface_rates:
            spreads.append(max(surface_rates) - min(surface_rates))

    surface_rates = [rate(rows, "route_ok") for rows in by_surface.values()]
    return {
        "n": float(len(outcomes)),
        "intent_count": float(len(by_intent)),
        "surface_count": float(len(by_surface)),
        "route_accuracy": rate(outcomes, "route_ok"),
        "abstention_precision": abstention_precision(outcomes),
        "abstention_recall": abstention_recall(outcomes),
        "avg_intent_route_spread": sum(spreads) / len(spreads) if spreads else 0.0,
        "worst_surface_route_accuracy": min(surface_rates) if surface_rates else 0.0,
        "missing_predictions": float(sum(1 for row in outcomes if row["missing"])),
        "missing_surface_metadata": float(sum(1 for row in outcomes if row["missing_surface_metadata"])),
    }


def grouped_scores(
    qrels: list[dict[str, Any]],
    run_rows: list[dict[str, Any]],
    *,
    key: str,
) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in route_surface_outcomes(qrels, run_rows):
        if key == "trap_classes":
            for trap in row["trap_classes"]:
                grouped[trap].append(row)
        else:
            grouped[row[key]].append(row)

    rows: list[dict[str, Any]] = []
    for value in sorted(grouped):
        group = grouped[value]
        rows.append(
            {
                "value": value,
                "n": float(len(group)),
                "route_accuracy": rate(group, "route_ok"),
                "abstention_precision": abstention_precision(group),
                "abstention_recall": abstention_recall(group),
                "missing_predictions": float(sum(1 for row in group if row["missing"])),
            }
        )
    return rows


def route_surface_confusions(qrels: list[dict[str, Any]], run_rows: list[dict[str, Any]]) -> Counter[tuple[str, str, str]]:
    counts: Counter[tuple[str, str, str]] = Counter()
    for row in route_surface_outcomes(qrels, run_rows):
        if row["route_gold"] != row["route_pred"]:
            counts[(row["surface_form"], row["route_gold"], row["route_pred"])] += 1
    return counts
