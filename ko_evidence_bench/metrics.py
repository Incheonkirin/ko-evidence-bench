"""Reference metrics for source-aware evidence retrieval."""

from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any, Iterable

from .schemas import validate_qrel, validate_run


def load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with Path(path).open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def _safe_div(num: int | float, den: int | float) -> float:
    return float(num) / float(den) if den else 0.0


def _topk(run: dict[str, Any], k: int) -> list[dict[str, Any]]:
    return list(run.get("ranked", []))[:k]


def percentile_ci(values: list[float], *, alpha: float = 0.05) -> tuple[float, float]:
    """Return a percentile interval from precomputed bootstrap values."""

    if not values:
        return 0.0, 0.0
    vals = sorted(values)
    lo_idx = max(0, int((alpha / 2) * len(vals)))
    hi_idx = min(len(vals) - 1, int((1 - alpha / 2) * len(vals)))
    return vals[lo_idx], vals[hi_idx]


def score_run(
    qrels: Iterable[dict[str, Any]],
    run_rows: Iterable[dict[str, Any]],
    *,
    k: int = 3,
) -> dict[str, float]:
    """Score a single system run against qrels.

    `sufficient_evidence_ids` is interpreted as an intent-level acceptable set.
    A query is sufficient@k if any expected sufficient evidence id appears in top-k.
    """

    qrel_by_qid: dict[str, dict[str, Any]] = {}
    for qrel in qrels:
        validate_qrel(qrel)
        qrel_by_qid[qrel["qid"]] = qrel

    run_by_qid: dict[str, dict[str, Any]] = {}
    for run in run_rows:
        validate_run(run)
        run_by_qid[run["qid"]] = run

    qids = sorted(qrel_by_qid)
    n = len(qids)

    route_hits = 0
    sufficient_hits = 0
    answerable_n = 0
    wrong_source_hits = 0
    clause_hits = 0
    abst_tp = abst_fp = abst_fn = 0

    for qid in qids:
        qrel = qrel_by_qid[qid]
        run = run_by_qid.get(qid, {"route_pred": "out_of_scope", "abstained": True, "ranked": []})
        top = _topk(run, k)
        allowed_sources = set(qrel.get("allowed_source_tiers") or [qrel["route_gold"]])

        if run["route_pred"] == qrel["route_gold"]:
            route_hits += 1

        expected = set(qrel["sufficient_evidence_ids"])
        if not qrel["should_abstain"]:
            answerable_n += 1
            if expected and any(item["evidence_id"] in expected for item in top):
                sufficient_hits += 1

        if any(item["source_tier"] not in allowed_sources for item in top):
            wrong_source_hits += 1

        if qrel["route_gold"] == "policy_clause" and expected:
            if any(item["evidence_id"] in expected for item in top):
                clause_hits += 1

        if run["abstained"] and qrel["should_abstain"]:
            abst_tp += 1
        elif run["abstained"] and not qrel["should_abstain"]:
            abst_fp += 1
        elif not run["abstained"] and qrel["should_abstain"]:
            abst_fn += 1

    policy_qrels = [q for q in qrel_by_qid.values() if q["route_gold"] == "policy_clause"]

    return {
        "n": float(n),
        "route_accuracy": _safe_div(route_hits, n),
        f"evidence_sufficiency@{k}": _safe_div(sufficient_hits, answerable_n),
        f"wrong_source_rate@{k}": _safe_div(wrong_source_hits, n),
        "abstention_precision": _safe_div(abst_tp, abst_tp + abst_fp),
        "abstention_recall": _safe_div(abst_tp, abst_tp + abst_fn),
        f"clause_recall@{k}": _safe_div(clause_hits, len(policy_qrels)),
    }


def bootstrap_ci(
    qrels: list[dict[str, Any]],
    run_rows: list[dict[str, Any]],
    *,
    metric: str,
    k: int = 3,
    samples: int = 1000,
    seed: int = 13,
) -> tuple[float, float]:
    """Return a percentile bootstrap CI over query ids."""

    rng = random.Random(seed)
    run_by_qid = {row["qid"]: row for row in run_rows}
    vals: list[float] = []
    for _ in range(samples):
        sample_qrels: list[dict[str, Any]] = []
        sample_runs: list[dict[str, Any]] = []
        for idx, qrel in enumerate(rng.choice(qrels) for _ in qrels):
            original_qid = qrel["qid"]
            boot_qid = f"{original_qid}__bootstrap_{idx}"
            sample_qrels.append({**qrel, "qid": boot_qid})
            if original_qid in run_by_qid:
                sample_runs.append({**run_by_qid[original_qid], "qid": boot_qid})
        vals.append(score_run(sample_qrels, sample_runs, k=k)[metric])
    vals.sort()
    return percentile_ci(vals)


def summarize_hit_rows(rows: list[dict[str, Any]], metric: str) -> dict[str, float]:
    """Summarize boolean hit rows from a private retrieval result export."""

    hits = sum(1 for row in rows if bool(row.get(metric)))
    n = len(rows)
    return {"n": float(n), "hits": float(hits), "rate": _safe_div(hits, n)}


def bootstrap_hit_ci(
    rows: list[dict[str, Any]],
    metric: str,
    *,
    samples: int = 2000,
    seed: int = 13,
) -> tuple[float, float]:
    """Bootstrap a CI over query-level boolean hits."""

    if not rows:
        return 0.0, 0.0
    rng = random.Random(seed)
    vals: list[float] = []
    for _ in range(samples):
        sample = [rng.choice(rows) for _ in rows]
        vals.append(summarize_hit_rows(sample, metric)["rate"])
    return percentile_ci(vals)


def paired_delta_ci(
    baseline_rows: list[dict[str, Any]],
    candidate_rows: list[dict[str, Any]],
    metric: str,
    *,
    samples: int = 2000,
    seed: int = 13,
) -> tuple[float, float, float]:
    """Bootstrap a paired candidate-baseline delta over shared qids."""

    base_by_qid = {row["qid"]: row for row in baseline_rows}
    cand_by_qid = {row["qid"]: row for row in candidate_rows}
    qids = sorted(base_by_qid.keys() & cand_by_qid.keys())
    if not qids:
        return 0.0, 0.0, 0.0

    deltas = [
        float(bool(cand_by_qid[qid].get(metric))) - float(bool(base_by_qid[qid].get(metric)))
        for qid in qids
    ]
    observed = sum(deltas) / len(deltas)

    rng = random.Random(seed)
    vals: list[float] = []
    for _ in range(samples):
        sample = [rng.choice(deltas) for _ in deltas]
        vals.append(sum(sample) / len(sample))
    lo, hi = percentile_ci(vals)
    return observed, lo, hi


def score_runs(
    qrels: list[dict[str, Any]],
    runs: dict[str, list[dict[str, Any]]],
    *,
    k: int = 3,
) -> dict[str, dict[str, float]]:
    return {name: score_run(qrels, rows, k=k) for name, rows in runs.items()}


def format_scorecard(scores: dict[str, dict[str, float]], *, k: int = 3) -> str:
    headers = [
        "system",
        "n",
        "route_acc",
        f"suff@{k}",
        f"wrong_src@{k}",
        "abst_p",
        "abst_r",
        f"clause@{k}",
    ]
    lines = ["  ".join(headers)]
    for name, row in scores.items():
        lines.append(
            "  ".join(
                [
                    name,
                    str(int(row["n"])),
                    f"{row['route_accuracy']:.3f}",
                    f"{row[f'evidence_sufficiency@{k}']:.3f}",
                    f"{row[f'wrong_source_rate@{k}']:.3f}",
                    f"{row['abstention_precision']:.3f}",
                    f"{row['abstention_recall']:.3f}",
                    f"{row[f'clause_recall@{k}']:.3f}",
                ]
            )
        )
    return "\n".join(lines)
