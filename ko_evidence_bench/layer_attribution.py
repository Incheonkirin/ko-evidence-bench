"""Failure-layer attribution for surface/evidence retrieval runs."""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

from .schemas import validate_qrel, validate_run

SUCCESS_LAYER = "success"


def _safe_div(num: int | float, den: int | float) -> float:
    return float(num) / float(den) if den else 0.0


def _default_run(qid: str) -> dict[str, Any]:
    return {"qid": qid, "route_pred": "out_of_scope", "abstained": True, "ranked": []}


def _topk(run: dict[str, Any], k: int) -> list[dict[str, Any]]:
    return list(run.get("ranked", []))[:k]


def trap_classes(qrel: dict[str, Any]) -> list[str]:
    value = qrel.get("trap_classes")
    if isinstance(value, list):
        traps = [str(item) for item in value if str(item)]
    elif isinstance(value, str) and value.strip():
        traps = [part.strip() for part in value.split(";") if part.strip()]
    else:
        traps = []
    return traps or ["<none>"]


def evidence_hit(qrel: dict[str, Any], run: dict[str, Any], *, k: int) -> bool:
    expected = set(qrel.get("sufficient_evidence_ids") or [])
    return bool(expected and any(item.get("evidence_id") in expected for item in _topk(run, k)))


def task_success(qrel: dict[str, Any], run: dict[str, Any], *, k: int) -> bool:
    route_ok = run["route_pred"] == qrel["route_gold"]
    should_abstain = bool(qrel["should_abstain"])
    if should_abstain:
        return route_ok and bool(run["abstained"])
    return route_ok and (not bool(run["abstained"])) and evidence_hit(qrel, run, k=k)


def failure_layer(qrel: dict[str, Any], run: dict[str, Any], *, k: int) -> str:
    if task_success(qrel, run, k=k):
        return SUCCESS_LAYER

    route_ok = run["route_pred"] == qrel["route_gold"]
    should_abstain = bool(qrel["should_abstain"])
    abstained = bool(run["abstained"])
    traps = set(trap_classes(qrel))

    if should_abstain and not abstained:
        return "abstention_failure"
    if abstained and not should_abstain:
        return "over_abstention"
    if not route_ok:
        return "source_route_failure"
    if "register_mismatch" in traps:
        return "register_gap"
    if traps & {"abbreviation", "bundle_expansion", "messenger_shorthand"}:
        return "surface_fragmentation"
    if "product_table" in traps:
        return "evidence_form_mismatch"
    return "evidence_miss"


def attribute_run(
    qrels: list[dict[str, Any]],
    run_rows: list[dict[str, Any]],
    *,
    system: str,
    k: int = 3,
) -> list[dict[str, Any]]:
    run_by_qid: dict[str, dict[str, Any]] = {}
    for row in run_rows:
        validate_run(row)
        run_by_qid[row["qid"]] = row

    rows: list[dict[str, Any]] = []
    for qrel in qrels:
        validate_qrel(qrel)
        run = run_by_qid.get(qrel["qid"], _default_run(qrel["qid"]))
        layer = failure_layer(qrel, run, k=k)
        rows.append(
            {
                "system": system,
                "qid": qrel["qid"],
                "intent_family": str(qrel.get("intent_family") or "<missing>"),
                "intent_id": str(qrel.get("intent_id") or "<missing>"),
                "surface_form": str(qrel.get("surface_form") or "<missing>"),
                "route_gold": qrel["route_gold"],
                "route_pred": run["route_pred"],
                "should_abstain": bool(qrel["should_abstain"]),
                "abstained": bool(run["abstained"]),
                "evidence_hit": evidence_hit(qrel, run, k=k),
                "task_success": layer == SUCCESS_LAYER,
                "failure_layer": layer,
                "trap_classes": trap_classes(qrel),
            }
        )
    return rows


def summarize_system(rows: list[dict[str, Any]]) -> dict[str, Any]:
    n = len(rows)
    failures = [row for row in rows if row["failure_layer"] != SUCCESS_LAYER]
    counter = Counter(str(row["failure_layer"]) for row in failures)
    dominant = counter.most_common(1)[0][0] if counter else SUCCESS_LAYER
    return {
        "system": str(rows[0]["system"]) if rows else "<empty>",
        "n": float(n),
        "success_rate": _safe_div(n - len(failures), n),
        "failure_rows": float(len(failures)),
        "dominant_failure_layer": dominant,
    }


def layer_breakdown(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_system: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_system[str(row["system"])].append(row)

    out: list[dict[str, Any]] = []
    for system in sorted(by_system):
        system_rows = by_system[system]
        failures = [row for row in system_rows if row["failure_layer"] != SUCCESS_LAYER]
        counts = Counter(str(row["failure_layer"]) for row in system_rows)
        for layer, count in sorted(counts.items(), key=lambda item: (item[0] != SUCCESS_LAYER, item[0])):
            out.append(
                {
                    "system": system,
                    "failure_layer": layer,
                    "rows": float(count),
                    "share_of_run": _safe_div(count, len(system_rows)),
                    "share_of_failures": 0.0 if layer == SUCCESS_LAYER else _safe_div(count, len(failures)),
                }
            )
    return out


def grouped_failure_layers(rows: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(str(row["system"]), str(row[key]))].append(row)

    out: list[dict[str, Any]] = []
    for (system, value), group in sorted(grouped.items()):
        failures = [row for row in group if row["failure_layer"] != SUCCESS_LAYER]
        counter = Counter(str(row["failure_layer"]) for row in failures)
        dominant = counter.most_common(1)[0][0] if counter else SUCCESS_LAYER
        out.append(
            {
                "system": system,
                "value": value,
                "n": float(len(group)),
                "success_rate": _safe_div(len(group) - len(failures), len(group)),
                "failure_rows": float(len(failures)),
                "dominant_failure_layer": dominant,
            }
        )
    return out


def trap_failure_layers(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    expanded: list[dict[str, Any]] = []
    for row in rows:
        for trap in row["trap_classes"]:
            expanded.append({**row, "trap_class": trap})
    return grouped_failure_layers(expanded, "trap_class")
