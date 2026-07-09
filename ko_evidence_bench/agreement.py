"""Agreement metrics for private label audits."""

from __future__ import annotations

from collections import Counter
from typing import Any


def get_path(row: dict[str, Any], path: str) -> Any:
    value: Any = row
    for part in path.split("."):
        if not isinstance(value, dict):
            return None
        value = value.get(part)
    return value


def observed_agreement(labels_a: list[str], labels_b: list[str]) -> float:
    if not labels_a or len(labels_a) != len(labels_b):
        return 0.0
    hits = sum(1 for a, b in zip(labels_a, labels_b) if a == b)
    return hits / len(labels_a)


def cohens_kappa(labels_a: list[str], labels_b: list[str]) -> float:
    """Compute Cohen's kappa for two categorical label lists."""

    if not labels_a or len(labels_a) != len(labels_b):
        return 0.0
    n = len(labels_a)
    observed = observed_agreement(labels_a, labels_b)
    counts_a = Counter(labels_a)
    counts_b = Counter(labels_b)
    expected = sum((counts_a[label] / n) * (counts_b[label] / n) for label in set(counts_a) | set(counts_b))
    if abs(1.0 - expected) < 1e-12:
        return 1.0 if abs(1.0 - observed) < 1e-12 else 0.0
    return (observed - expected) / (1.0 - expected)


def paired_labels(rows: list[dict[str, Any]], field_a: str, field_b: str) -> tuple[list[str], list[str]]:
    labels_a: list[str] = []
    labels_b: list[str] = []
    for row in rows:
        a = get_path(row, field_a)
        b = get_path(row, field_b)
        if a not in (None, "") and b not in (None, ""):
            labels_a.append(str(a))
            labels_b.append(str(b))
    return labels_a, labels_b
