"""Aggregate intent-family inventories without exposing raw query text."""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

from .schemas import validate_qrel


def _value(row: dict[str, Any], *keys: str, default: str = "<missing>") -> str:
    for key in keys:
        value = row.get(key)
        if value not in (None, "", []):
            return str(value)
    return default


def _list_value(row: dict[str, Any], key: str) -> list[str]:
    value = row.get(key)
    if value is None or value == "":
        return []
    if isinstance(value, list):
        return [str(item) for item in value if str(item)]
    return [part.strip() for part in str(value).split(";") if part.strip()]


def qrel_metadata(row: dict[str, Any]) -> dict[str, Any]:
    validate_qrel(row)
    return {
        "intent_family": _value(row, "intent_family", "gate_category"),
        "intent_id": _value(row, "intent_id", "intent"),
        "surface_form": _value(row, "surface_form"),
        "route_gold": row["route_gold"],
        "should_abstain": bool(row["should_abstain"]),
        "trap_classes": _list_value(row, "trap_classes"),
    }


def aggregate_inventory(qrels: list[dict[str, Any]]) -> dict[str, Any]:
    rows = [qrel_metadata(row) for row in qrels]
    families: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        families[row["intent_family"]].append(row)

    family_rows: list[dict[str, Any]] = []
    for family in sorted(families):
        family_items = families[family]
        route_counts = Counter(item["route_gold"] for item in family_items)
        surface_counts = Counter(item["surface_form"] for item in family_items)
        intent_ids = {item["intent_id"] for item in family_items}
        trap_counts: Counter[str] = Counter()
        for item in family_items:
            trap_counts.update(item["trap_classes"] or ["<none>"])
        family_rows.append(
            {
                "intent_family": family,
                "rows": len(family_items),
                "intent_count": len(intent_ids),
                "surface_count": len(surface_counts),
                "abstain_rows": sum(1 for item in family_items if item["should_abstain"]),
                "route_counts": route_counts,
                "surface_counts": surface_counts,
                "trap_counts": trap_counts,
            }
        )

    completeness = Counter()
    for item in rows:
        for key in ("intent_family", "intent_id", "surface_form"):
            if item[key] == "<missing>":
                completeness[f"missing_{key}"] += 1
            else:
                completeness[f"present_{key}"] += 1

    trap_counts: Counter[str] = Counter()
    for item in rows:
        trap_counts.update(item["trap_classes"] or ["<none>"])

    return {
        "n": len(rows),
        "family_rows": family_rows,
        "intent_family": Counter(item["intent_family"] for item in rows),
        "surface_form": Counter(item["surface_form"] for item in rows),
        "route_gold": Counter(item["route_gold"] for item in rows),
        "trap_classes": trap_counts,
        "metadata_completeness": completeness,
    }


def pct(num: int, den: int) -> str:
    return f"{100 * (num / den if den else 0.0):.1f}%"


def format_counter(counter: Counter[str], *, max_items: int = 3) -> str:
    if not counter:
        return "<none>"
    return ", ".join(f"{key}:{value}" for key, value in counter.most_common(max_items))
