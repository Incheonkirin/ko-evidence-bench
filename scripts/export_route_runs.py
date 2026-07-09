#!/usr/bin/env python3
"""Export qid-only source-route prediction runs from private qrels."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ko_evidence_bench.metrics import load_jsonl  # noqa: E402
from ko_evidence_bench.route_router import query_only_route  # noqa: E402
from ko_evidence_bench.schemas import ROUTE_LABELS  # noqa: E402


Predictor = Callable[[dict[str, Any]], str]


def always_policy(_: dict[str, Any]) -> str:
    return "policy_clause"


def query_keyword_router(row: dict[str, Any]) -> str:
    return query_only_route(str(row.get("query") or row.get("search_query_rewrite") or ""))


PREDICTORS: dict[str, Predictor] = {
    "always_policy": always_policy,
    "query_keyword_router": query_keyword_router,
}


def abstained(route_pred: str) -> bool:
    return route_pred in {"human_context_needed", "out_of_scope"}


def predict_rows(qrels: list[dict[str, Any]], predictor: Predictor) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in qrels:
        qid = row.get("qid")
        if not qid:
            continue
        route_pred = predictor(row)
        if route_pred not in ROUTE_LABELS:
            raise ValueError(f"unknown route prediction: {route_pred}")
        out.append(
            {
                "qid": qid,
                "route_pred": route_pred,
                "abstained": abstained(route_pred),
            }
        )
    return out


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def export_runs(qrels: list[dict[str, Any]], out_dir: Path) -> dict[str, list[dict[str, Any]]]:
    runs: dict[str, list[dict[str, Any]]] = {}
    for name, predictor in PREDICTORS.items():
        rows = predict_rows(qrels, predictor)
        write_jsonl(out_dir / f"{name}.jsonl", rows)
        runs[name] = rows
    return runs


def pct(value: float) -> str:
    return f"{100 * value:.1f}%"


def render_counts(title: str, counts: Counter[str]) -> list[str]:
    total = sum(counts.values())
    lines = [f"## {title}", "", "| value | count | share |", "|---|---:|---:|"]
    for key, count in counts.most_common():
        share = count / total if total else 0.0
        lines.append(f"| `{key}` | {count} | {pct(share)} |")
    return lines


def render_report(runs: dict[str, list[dict[str, Any]]], *, out_dir: Path) -> str:
    lines = [
        "# Private Route Run Export Summary",
        "",
        "This report summarizes qid-only route prediction files generated from a",
        "private qrel source. It contains aggregate counts only and does not include",
        "raw queries, qids, conversations, or platform identifiers.",
        "",
        f"- output dir: `{out_dir.name}`",
        f"- systems: {len(runs)}",
        "",
        "## Exported Runs",
        "",
        "| system | rows | abstained |",
        "|---|---:|---:|",
    ]
    for name, rows in runs.items():
        abstain_count = sum(1 for row in rows if row["abstained"])
        lines.append(f"| `{name}` | {len(rows)} | {abstain_count} |")
    lines.append("")
    for name, rows in runs.items():
        counts = Counter(str(row["route_pred"]) for row in rows)
        lines.extend(render_counts(f"Prediction Distribution: `{name}`", counts))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--qrels", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--report-out", type=Path)
    args = parser.parse_args()

    runs = export_runs(load_jsonl(args.qrels), args.out_dir)
    if args.report_out:
        args.report_out.parent.mkdir(parents=True, exist_ok=True)
        args.report_out.write_text(render_report(runs, out_dir=args.out_dir), encoding="utf-8")


if __name__ == "__main__":
    main()
