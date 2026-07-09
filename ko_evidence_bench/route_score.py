"""Score qid-only source-route prediction runs."""

from __future__ import annotations

import random
from typing import Any

from .metrics import percentile_ci
from .schemas import ROUTE_LABELS, require_keys


def validate_route_label(row: dict[str, Any]) -> None:
    require_keys(row, {"qid", "route_gold", "should_abstain"}, kind="route label")
    if row["route_gold"] not in ROUTE_LABELS:
        raise ValueError(f"unknown route_gold: {row['route_gold']}")
    if not isinstance(row["should_abstain"], bool):
        raise ValueError("should_abstain must be boolean")
    if "allowed_source_tiers" in row:
        if not isinstance(row["allowed_source_tiers"], list):
            raise ValueError("allowed_source_tiers must be a list")
        unknown = set(row["allowed_source_tiers"]) - ROUTE_LABELS
        if unknown:
            raise ValueError(f"unknown allowed_source_tiers: {sorted(unknown)}")


def validate_route_run(row: dict[str, Any]) -> None:
    require_keys(row, {"qid", "route_pred", "abstained"}, kind="route run")
    if row["route_pred"] not in ROUTE_LABELS:
        raise ValueError(f"unknown route_pred: {row['route_pred']}")
    if not isinstance(row["abstained"], bool):
        raise ValueError("abstained must be boolean")


def score_route_run(labels: list[dict[str, Any]], run_rows: list[dict[str, Any]]) -> dict[str, float]:
    label_by_qid: dict[str, dict[str, Any]] = {}
    for label in labels:
        validate_route_label(label)
        label_by_qid[label["qid"]] = label

    run_by_qid: dict[str, dict[str, Any]] = {}
    for row in run_rows:
        validate_route_run(row)
        run_by_qid[row["qid"]] = row

    qids = sorted(label_by_qid)
    n = len(qids)
    route_hits = 0
    abst_tp = abst_fp = abst_fn = 0
    missing_pred = 0

    for qid in qids:
        label = label_by_qid[qid]
        run = run_by_qid.get(qid)
        if run is None:
            missing_pred += 1
            pred = "out_of_scope"
            abstained = True
        else:
            pred = run["route_pred"]
            abstained = run["abstained"]

        if pred == label["route_gold"]:
            route_hits += 1

        if abstained and label["should_abstain"]:
            abst_tp += 1
        elif abstained and not label["should_abstain"]:
            abst_fp += 1
        elif not abstained and label["should_abstain"]:
            abst_fn += 1

    return {
        "n": float(n),
        "missing_predictions": float(missing_pred),
        "route_accuracy": route_hits / n if n else 0.0,
        "abstention_precision": abst_tp / (abst_tp + abst_fp) if (abst_tp + abst_fp) else 0.0,
        "abstention_recall": abst_tp / (abst_tp + abst_fn) if (abst_tp + abst_fn) else 0.0,
    }


def bootstrap_route_ci(
    labels: list[dict[str, Any]],
    run_rows: list[dict[str, Any]],
    *,
    metric: str,
    samples: int = 2000,
    seed: int = 31,
) -> tuple[float, float]:
    if not labels:
        return 0.0, 0.0
    rng = random.Random(seed)
    run_by_qid = {row["qid"]: row for row in run_rows}
    vals: list[float] = []
    for _ in range(samples):
        sample_labels: list[dict[str, Any]] = []
        sample_runs: list[dict[str, Any]] = []
        for idx, label in enumerate(rng.choice(labels) for _ in labels):
            qid = label["qid"]
            boot_qid = f"{qid}__bootstrap_{idx}"
            sample_labels.append({**label, "qid": boot_qid})
            if qid in run_by_qid:
                sample_runs.append({**run_by_qid[qid], "qid": boot_qid})
        vals.append(score_route_run(sample_labels, sample_runs)[metric])
    return percentile_ci(vals)


def paired_route_delta_ci(
    labels: list[dict[str, Any]],
    baseline_rows: list[dict[str, Any]],
    candidate_rows: list[dict[str, Any]],
    *,
    metric: str = "route_accuracy",
    samples: int = 2000,
    seed: int = 31,
) -> tuple[float, float, float]:
    if metric != "route_accuracy":
        raise ValueError("paired route deltas currently support route_accuracy only")

    base_by_qid = {row["qid"]: row for row in baseline_rows}
    cand_by_qid = {row["qid"]: row for row in candidate_rows}
    deltas: list[float] = []
    for label in labels:
        qid = label["qid"]
        base_pred = base_by_qid.get(qid, {"route_pred": "out_of_scope"})["route_pred"]
        cand_pred = cand_by_qid.get(qid, {"route_pred": "out_of_scope"})["route_pred"]
        gold = label["route_gold"]
        deltas.append(float(cand_pred == gold) - float(base_pred == gold))

    if not deltas:
        return 0.0, 0.0, 0.0

    observed = sum(deltas) / len(deltas)
    rng = random.Random(seed)
    vals: list[float] = []
    for _ in range(samples):
        sample = [rng.choice(deltas) for _ in deltas]
        vals.append(sum(sample) / len(sample))
    lo, hi = percentile_ci(vals)
    return observed, lo, hi
