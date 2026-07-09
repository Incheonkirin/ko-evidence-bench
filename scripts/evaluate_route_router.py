#!/usr/bin/env python3
"""Evaluate query-only source-routing baselines on private silver labels."""

from __future__ import annotations

import argparse
import json
import random
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ko_evidence_bench.metrics import percentile_ci  # noqa: E402
from ko_evidence_bench.route_router import query_only_route  # noqa: E402


ROUTE_LABELS = [
    "policy_clause",
    "product_disclosure",
    "official_consumer_info",
    "claims_faq",
    "dispute_case",
    "expert_answer",
    "human_context_needed",
    "out_of_scope",
]


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def pct(value: float) -> str:
    return f"{100 * value:.1f}%"


def route_rows(qrels: list[dict[str, Any]], labels: list[dict[str, Any]]) -> list[dict[str, Any]]:
    qrel_by_qid = {row["qid"]: row for row in qrels}
    out: list[dict[str, Any]] = []
    for label in labels:
        qrel = qrel_by_qid.get(label["qid"])
        if not qrel:
            continue
        out.append(
            {
                "query": qrel.get("query", ""),
                "gold": label["route_gold"],
                "should_abstain": bool(label["should_abstain"]),
            }
        )
    return out


def score_predictions(rows: list[dict[str, Any]], predictor: Callable[[dict[str, Any]], str]) -> dict[str, float]:
    n = len(rows)
    if not n:
        return {
            "n": 0.0,
            "route_accuracy": 0.0,
            "abstention_precision": 0.0,
            "abstention_recall": 0.0,
        }
    route_hits = 0
    abst_tp = abst_fp = abst_fn = 0
    for row in rows:
        pred = predictor(row)
        route_hits += int(pred == row["gold"])
        abstained = pred == "human_context_needed"
        if abstained and row["should_abstain"]:
            abst_tp += 1
        elif abstained and not row["should_abstain"]:
            abst_fp += 1
        elif not abstained and row["should_abstain"]:
            abst_fn += 1
    return {
        "n": float(n),
        "route_accuracy": route_hits / n,
        "abstention_precision": abst_tp / (abst_tp + abst_fp) if (abst_tp + abst_fp) else 0.0,
        "abstention_recall": abst_tp / (abst_tp + abst_fn) if (abst_tp + abst_fn) else 0.0,
    }


def bootstrap_metric(
    rows: list[dict[str, Any]],
    predictor: Callable[[dict[str, Any]], str],
    metric: str,
    *,
    samples: int,
    seed: int,
) -> tuple[float, float]:
    if not rows:
        return 0.0, 0.0
    rng = random.Random(seed)
    vals = []
    for _ in range(samples):
        sample = [rng.choice(rows) for _ in rows]
        vals.append(score_predictions(sample, predictor)[metric])
    return percentile_ci(vals)


def paired_delta(
    rows: list[dict[str, Any]],
    baseline: Callable[[dict[str, Any]], str],
    candidate: Callable[[dict[str, Any]], str],
    metric: str,
    *,
    samples: int,
    seed: int,
) -> tuple[float, float, float]:
    if metric != "route_accuracy":
        raise ValueError("paired_delta currently supports route_accuracy only")
    deltas = [
        float(candidate(row) == row["gold"]) - float(baseline(row) == row["gold"])
        for row in rows
    ]
    if not deltas:
        return 0.0, 0.0, 0.0
    observed = sum(deltas) / len(deltas)
    rng = random.Random(seed)
    vals = []
    for _ in range(samples):
        sample = [rng.choice(deltas) for _ in deltas]
        vals.append(sum(sample) / len(sample))
    lo, hi = percentile_ci(vals)
    return observed, lo, hi


def always_policy(_: dict[str, Any]) -> str:
    return "policy_clause"


def query_router(row: dict[str, Any]) -> str:
    return query_only_route(row["query"])


def prediction_counts(rows: list[dict[str, Any]], predictor: Callable[[dict[str, Any]], str]) -> Counter[str]:
    return Counter(predictor(row) for row in rows)


def render_table_counts(title: str, counts: Counter[str]) -> list[str]:
    total = sum(counts.values())
    lines = [f"## {title}", "", "| value | count | share |", "|---|---:|---:|"]
    for key, value in counts.most_common():
        share = value / total if total else 0.0
        lines.append(f"| `{key}` | {value} | {pct(share)} |")
    return lines


def render_report(rows: list[dict[str, Any]], *, samples: int, seed: int) -> str:
    predictors = {
        "always_policy": always_policy,
        "query_keyword_router": query_router,
    }
    metrics = ["route_accuracy", "abstention_precision", "abstention_recall"]
    lines = [
        "# Private Source-Route Router Baselines",
        "",
        "This report evaluates source-route baselines against private silver labels.",
        "It contains aggregate metrics only. It does not include raw queries, qids,",
        "conversation snippets, or platform identifiers.",
        "",
        f"- rows: {len(rows)}",
        f"- bootstrap samples: {samples}",
        f"- seed: {seed}",
        "- label status: silver proxy, not human-gold",
        "",
        "## Metrics",
        "",
        "| system | metric | value | 95% CI |",
        "|---|---|---:|---:|",
    ]
    for name, predictor in predictors.items():
        scores = score_predictions(rows, predictor)
        for metric in metrics:
            lo, hi = bootstrap_metric(rows, predictor, metric, samples=samples, seed=seed)
            lines.append(f"| {name} | `{metric}` | {pct(scores[metric])} | {pct(lo)} - {pct(hi)} |")

    delta, lo, hi = paired_delta(rows, always_policy, query_router, "route_accuracy", samples=samples, seed=seed)
    lines.extend(
        [
            "",
            "## Paired Delta vs `always_policy`",
            "",
            "| system | metric | delta | 95% CI |",
            "|---|---|---:|---:|",
            f"| query_keyword_router | `route_accuracy` | {pct(delta)} | {pct(lo)} - {pct(hi)} |",
            "",
        ]
    )
    lines.extend(render_table_counts("Gold Route Distribution", Counter(row["gold"] for row in rows)))
    lines.append("")
    for name, predictor in predictors.items():
        lines.extend(render_table_counts(f"Prediction Distribution: `{name}`", prediction_counts(rows, predictor)))
        lines.append("")
    lines.extend(
        [
            "## Use Notes",
            "",
            "- These are baselines for source routing, not answer-quality claims.",
            "- Silver-label results should be replaced by human-audited route metrics before headline use.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--qrels", type=Path, required=True)
    parser.add_argument("--labels", type=Path, required=True)
    parser.add_argument("--samples", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=29)
    parser.add_argument("--report-out", type=Path)
    args = parser.parse_args()

    rows = route_rows(load_jsonl(args.qrels), load_jsonl(args.labels))
    report = render_report(rows, samples=args.samples, seed=args.seed)
    if args.report_out:
        args.report_out.parent.mkdir(parents=True, exist_ok=True)
        args.report_out.write_text(report, encoding="utf-8")
    else:
        print(report, end="")


if __name__ == "__main__":
    main()
