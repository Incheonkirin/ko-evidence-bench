"""Run-level ablations for surface normalization and expansion candidates."""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

from .schemas import validate_qrel, validate_run
from .surface import variant_outcome


def _default_run(qid: str) -> dict[str, Any]:
    return {"qid": qid, "route_pred": "out_of_scope", "abstained": True, "ranked": []}


def _trap_classes(qrel: dict[str, Any]) -> list[str]:
    value = qrel.get("trap_classes")
    if isinstance(value, list):
        return [str(item) for item in value if str(item)]
    if isinstance(value, str) and value.strip():
        return [part.strip() for part in value.split(";") if part.strip()]
    return ["<none>"]


def _safe_div(num: int | float, den: int | float) -> float:
    return float(num) / float(den) if den else 0.0


def compare_runs(
    qrels: list[dict[str, Any]],
    baseline_rows: list[dict[str, Any]],
    candidate_rows: list[dict[str, Any]],
    *,
    k: int = 3,
) -> list[dict[str, Any]]:
    baseline_by_qid: dict[str, dict[str, Any]] = {}
    candidate_by_qid: dict[str, dict[str, Any]] = {}
    for row in baseline_rows:
        validate_run(row)
        baseline_by_qid[row["qid"]] = row
    for row in candidate_rows:
        validate_run(row)
        candidate_by_qid[row["qid"]] = row

    rows: list[dict[str, Any]] = []
    for qrel in qrels:
        validate_qrel(qrel)
        baseline = variant_outcome(qrel, baseline_by_qid.get(qrel["qid"], _default_run(qrel["qid"])), k=k)
        candidate = variant_outcome(qrel, candidate_by_qid.get(qrel["qid"], _default_run(qrel["qid"])), k=k)
        baseline_success = bool(baseline["task_success"])
        candidate_success = bool(candidate["task_success"])
        rows.append(
            {
                "qid": qrel["qid"],
                "intent_family": str(qrel.get("intent_family") or "<missing>"),
                "intent_id": str(qrel.get("intent_id") or "<missing>"),
                "surface_form": str(qrel.get("surface_form") or "<missing>"),
                "route_gold": qrel["route_gold"],
                "should_abstain": bool(qrel["should_abstain"]),
                "trap_classes": _trap_classes(qrel),
                "baseline_success": baseline_success,
                "candidate_success": candidate_success,
                "rescued": (not baseline_success) and candidate_success,
                "regressed": baseline_success and (not candidate_success),
            }
        )
    return rows


def summarize_comparison(rows: list[dict[str, Any]]) -> dict[str, float]:
    n = len(rows)
    baseline_success = sum(1 for row in rows if row["baseline_success"])
    candidate_success = sum(1 for row in rows if row["candidate_success"])
    rescued = sum(1 for row in rows if row["rescued"])
    regressed = sum(1 for row in rows if row["regressed"])
    return {
        "n": float(n),
        "baseline_success_rate": _safe_div(baseline_success, n),
        "candidate_success_rate": _safe_div(candidate_success, n),
        "lift": _safe_div(candidate_success - baseline_success, n),
        "rescued_rate": _safe_div(rescued, n),
        "regressed_rate": _safe_div(regressed, n),
        "rescued_rows": float(rescued),
        "regressed_rows": float(regressed),
    }


def grouped_comparison(rows: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row[key])].append(row)

    out: list[dict[str, Any]] = []
    for value in sorted(grouped):
        summary = summarize_comparison(grouped[value])
        out.append({"value": value, **summary})
    return out


def trap_comparison(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        for trap in row["trap_classes"]:
            grouped[trap].append(row)

    out: list[dict[str, Any]] = []
    for value in sorted(grouped):
        summary = summarize_comparison(grouped[value])
        out.append({"value": value, **summary})
    return out


def rescue_route_counts(rows: list[dict[str, Any]]) -> Counter[str]:
    return Counter(row["route_gold"] for row in rows if row["rescued"])
