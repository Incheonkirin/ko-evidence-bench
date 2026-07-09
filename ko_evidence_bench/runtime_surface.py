"""Surface and intent slices for runtime retrieval hit results."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from .schemas import validate_qrel


HIT_METRICS = (
    "exact@1",
    "exact@5",
    "exact@10",
    "exact@20",
    "clause@1",
    "clause@5",
    "clause@10",
    "clause@20",
)


def _safe_div(num: int | float, den: int | float) -> float:
    return float(num) / float(den) if den else 0.0


def validate_runtime_hit_row(row: dict[str, Any]) -> None:
    if "qid" not in row:
        raise ValueError("runtime hit row missing qid")
    for metric in HIT_METRICS:
        if metric in row and not isinstance(row[metric], bool):
            raise ValueError(f"{metric} must be boolean when present")


def runtime_surface_outcomes(
    qrels: list[dict[str, Any]],
    hit_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    hits_by_qid: dict[str, dict[str, Any]] = {}
    for row in hit_rows:
        validate_runtime_hit_row(row)
        hits_by_qid[row["qid"]] = row

    outcomes: list[dict[str, Any]] = []
    for qrel in qrels:
        validate_qrel(qrel)
        hit_row = hits_by_qid.get(qrel["qid"])
        missing = hit_row is None
        row: dict[str, Any] = {
            "intent_family": str(qrel.get("intent_family") or "<missing>"),
            "intent_id": str(qrel.get("intent_id") or "<missing>"),
            "surface_form": str(qrel.get("surface_form") or "<missing>"),
            "trap_classes": [str(item) for item in qrel.get("trap_classes") or ["<none>"]],
            "should_abstain": bool(qrel["should_abstain"]),
            "answerable": not bool(qrel["should_abstain"]),
            "missing_hit_row": missing,
            "missing_surface_metadata": not qrel.get("intent_family")
            or not qrel.get("intent_id")
            or not qrel.get("surface_form"),
        }
        for metric in HIT_METRICS:
            row[metric] = bool(hit_row and hit_row.get(metric, False))
        outcomes.append(row)
    return outcomes


def hit_rate(rows: list[dict[str, Any]], metric: str) -> float:
    return _safe_div(sum(1 for row in rows if row[metric]), len(rows))


def answerable_hit_rate(rows: list[dict[str, Any]], metric: str) -> float:
    answerable = [row for row in rows if row["answerable"]]
    return _safe_div(sum(1 for row in answerable if row[metric]), len(answerable))


def summarize_runtime_surface_run(
    qrels: list[dict[str, Any]],
    hit_rows: list[dict[str, Any]],
    *,
    primary_metric: str = "clause@20",
) -> dict[str, float]:
    if primary_metric not in HIT_METRICS:
        raise ValueError(f"unknown primary metric: {primary_metric}")

    outcomes = runtime_surface_outcomes(qrels, hit_rows)
    by_family: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_surface: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in outcomes:
        by_family[row["intent_family"]].append(row)
        by_surface[row["surface_form"]].append(row)

    spreads: list[float] = []
    for rows in by_family.values():
        family_by_surface: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in rows:
            family_by_surface[row["surface_form"]].append(row)
        surface_rates = [hit_rate(surface_rows, primary_metric) for surface_rows in family_by_surface.values()]
        if surface_rates:
            spreads.append(max(surface_rates) - min(surface_rates))

    surface_rates = [hit_rate(rows, primary_metric) for rows in by_surface.values()]
    return {
        "n": float(len(outcomes)),
        "answerable_n": float(sum(1 for row in outcomes if row["answerable"])),
        "intent_family_count": float(len(by_family)),
        "surface_count": float(len(by_surface)),
        primary_metric: hit_rate(outcomes, primary_metric),
        f"answerable_{primary_metric}": answerable_hit_rate(outcomes, primary_metric),
        "exact@20": hit_rate(outcomes, "exact@20"),
        "avg_family_surface_spread": sum(spreads) / len(spreads) if spreads else 0.0,
        f"worst_surface_{primary_metric}": min(surface_rates) if surface_rates else 0.0,
        "missing_hit_rows": float(sum(1 for row in outcomes if row["missing_hit_row"])),
        "missing_surface_metadata": float(sum(1 for row in outcomes if row["missing_surface_metadata"])),
    }


def grouped_runtime_surface_scores(
    qrels: list[dict[str, Any]],
    hit_rows: list[dict[str, Any]],
    *,
    key: str,
    primary_metric: str = "clause@20",
) -> list[dict[str, Any]]:
    if primary_metric not in HIT_METRICS:
        raise ValueError(f"unknown primary metric: {primary_metric}")

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in runtime_surface_outcomes(qrels, hit_rows):
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
                "answerable_n": float(sum(1 for row in group if row["answerable"])),
                primary_metric: hit_rate(group, primary_metric),
                f"answerable_{primary_metric}": answerable_hit_rate(group, primary_metric),
                "exact@20": hit_rate(group, "exact@20"),
                "missing_hit_rows": float(sum(1 for row in group if row["missing_hit_row"])),
            }
        )
    return rows
