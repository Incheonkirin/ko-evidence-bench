#!/usr/bin/env python3
"""Score qid-only route runs by private query cohort."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ko_evidence_bench.metrics import load_jsonl  # noqa: E402
from ko_evidence_bench.route_score import route_confusion_counts, score_route_run  # noqa: E402


def pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def display_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(ROOT))
    except ValueError:
        return resolved.name


def load_source_map(path: Path) -> tuple[dict[str, str], str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict) and "cohorts" in payload:
        cohorts = payload["cohorts"]
        default = str(payload.get("default_cohort", "unmapped_private_source"))
    else:
        cohorts = payload
        default = "unmapped_private_source"
    if not isinstance(cohorts, dict):
        raise ValueError("source map must be a JSON object or contain a `cohorts` object")
    return {str(key): str(value) for key, value in cohorts.items()}, default


def load_runs(run_dir: Path) -> dict[str, list[dict[str, Any]]]:
    runs: dict[str, list[dict[str, Any]]] = {}
    for path in sorted(run_dir.glob("*.jsonl")):
        runs[path.stem] = load_jsonl(path)
    if not runs:
        raise ValueError(f"no .jsonl runs found under {run_dir}")
    return runs


def qids_by_cohort(
    qrels: list[dict[str, Any]],
    labels: list[dict[str, Any]],
    source_map: dict[str, str],
    *,
    source_field: str,
    default_cohort: str,
) -> tuple[dict[str, set[str]], Counter[str]]:
    label_qids = {row["qid"] for row in labels}
    cohorts: dict[str, set[str]] = {}
    unmapped: Counter[str] = Counter()
    for row in qrels:
        qid = row.get("qid")
        if qid not in label_qids:
            continue
        raw_source = str(row.get(source_field, ""))
        cohort = source_map.get(raw_source, default_cohort)
        cohorts.setdefault(cohort, set()).add(str(qid))
        if cohort == default_cohort:
            unmapped[default_cohort] += 1
    return cohorts, unmapped


def filter_labels(labels: list[dict[str, Any]], qids: set[str]) -> list[dict[str, Any]]:
    return [row for row in labels if row["qid"] in qids]


def context_policy_fallback(
    labels: list[dict[str, Any]],
    run_rows: list[dict[str, Any]],
) -> tuple[int, int]:
    run_by_qid = {row["qid"]: row for row in run_rows}
    context_needed = [row for row in labels if row["route_gold"] == "human_context_needed"]
    fallback = 0
    for label in context_needed:
        pred = run_by_qid.get(label["qid"], {"route_pred": "out_of_scope"})["route_pred"]
        if pred == "policy_clause":
            fallback += 1
    return len(context_needed), fallback


def cohort_inventory_table(cohorts: dict[str, set[str]], labels: list[dict[str, Any]]) -> list[str]:
    label_by_qid = {row["qid"]: row for row in labels}
    total = sum(len(qids) for qids in cohorts.values())
    lines = [
        "## Cohort Inventory",
        "",
        "| query cohort | rows | share | human_context_needed | policy_clause |",
        "|---|---:|---:|---:|---:|",
    ]
    for cohort, qids in sorted(cohorts.items(), key=lambda item: (-len(item[1]), item[0])):
        routes = Counter(label_by_qid[qid]["route_gold"] for qid in qids)
        n = len(qids)
        lines.append(
            f"| `{cohort}` | {n} | {pct(n / total if total else 0.0)} | "
            f"{routes['human_context_needed']} | {routes['policy_clause']} |"
        )
    return lines


def cohort_metric_table(
    cohorts: dict[str, set[str]],
    labels: list[dict[str, Any]],
    runs: dict[str, list[dict[str, Any]]],
) -> list[str]:
    lines = [
        "## Route Metrics By Query Cohort",
        "",
        "| system | query cohort | n | route_acc | abst_p | abst_r |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for system, run_rows in runs.items():
        for cohort, qids in sorted(cohorts.items(), key=lambda item: (-len(item[1]), item[0])):
            subset = filter_labels(labels, qids)
            score = score_route_run(subset, run_rows)
            lines.append(
                f"| `{system}` | `{cohort}` | {int(score['n'])} | "
                f"{pct(score['route_accuracy'])} | {pct(score['abstention_precision'])} | "
                f"{pct(score['abstention_recall'])} |"
            )
    return lines


def fallback_table(
    cohorts: dict[str, set[str]],
    labels: list[dict[str, Any]],
    runs: dict[str, list[dict[str, Any]]],
) -> list[str]:
    lines = [
        "## Context-Needed Policy Fallback",
        "",
        "This table counts cases where the gold route says human context is needed",
        "but the system still predicts policy-clause evidence.",
        "",
        "| system | query cohort | context-needed rows | predicted policy_clause | fallback rate |",
        "|---|---|---:|---:|---:|",
    ]
    for system, run_rows in runs.items():
        for cohort, qids in sorted(cohorts.items(), key=lambda item: (-len(item[1]), item[0])):
            subset = filter_labels(labels, qids)
            context_n, fallback_n = context_policy_fallback(subset, run_rows)
            lines.append(
                f"| `{system}` | `{cohort}` | {context_n} | {fallback_n} | "
                f"{pct(fallback_n / context_n if context_n else 0.0)} |"
            )
    return lines


def confusion_table(
    cohorts: dict[str, set[str]],
    labels: list[dict[str, Any]],
    runs: dict[str, list[dict[str, Any]]],
    *,
    limit_per_system: int,
) -> list[str]:
    lines = [
        "## Largest Cohort Route Confusions",
        "",
        "| system | query cohort | gold source tier | predicted source tier | count | share of cohort |",
        "|---|---|---|---|---:|---:|",
    ]
    added = 0
    for system, run_rows in runs.items():
        added_for_system = 0
        scored_rows: list[tuple[str, str, str, int, int]] = []
        for cohort, qids in cohorts.items():
            subset = filter_labels(labels, qids)
            counts = route_confusion_counts(subset, run_rows)
            total = sum(counts.values())
            for (gold, pred), count in counts.items():
                if gold != pred:
                    scored_rows.append((cohort, gold, pred, count, total))
        for cohort, gold, pred, count, total in sorted(
            scored_rows,
            key=lambda row: (-row[3], row[0], row[1], row[2]),
        ):
            lines.append(
                f"| `{system}` | `{cohort}` | `{gold}` | `{pred}` | {count} | "
                f"{pct(count / total if total else 0.0)} |"
            )
            added += 1
            added_for_system += 1
            if added_for_system >= limit_per_system:
                break
    if not added:
        lines.append("| _(none)_ | _(none)_ | _(none)_ | _(none)_ | 0 | 0.0% |")
    return lines


def render_report(
    *,
    qrels: list[dict[str, Any]],
    labels: list[dict[str, Any]],
    runs: dict[str, list[dict[str, Any]]],
    source_map: dict[str, str],
    default_cohort: str,
    source_field: str,
    qrels_path: Path,
    labels_path: Path,
    run_dir: Path,
    source_map_path: Path,
    label_status: str,
    limit_per_system: int,
) -> str:
    cohorts, unmapped = qids_by_cohort(
        qrels,
        labels,
        source_map,
        source_field=source_field,
        default_cohort=default_cohort,
    )
    label_qids = {row["qid"] for row in labels}
    matched_rows = sum(len(qids) for qids in cohorts.values())
    lines = [
        "# Route Cohort Scorecard",
        "",
        "This report scores qid-only route predictions by query cohort.",
        "It contains aggregate counts only. It does not include raw source names,",
        "qids, raw queries, conversation snippets, or platform identifiers.",
        "",
        "## Inputs",
        "",
        f"- qrels: `{display_path(qrels_path)}`",
        f"- labels: `{display_path(labels_path)}`",
        f"- runs: `{display_path(run_dir)}`",
        f"- source map: `{display_path(source_map_path)}`",
        f"- label status: {label_status}",
        f"- qrel rows: {len(qrels)}",
        f"- label rows: {len(labels)}",
        f"- matched labeled rows: {matched_rows}",
        f"- unmatched label rows: {len(label_qids) - matched_rows}",
        f"- unmapped source rows: {sum(unmapped.values())}",
        "",
    ]
    lines.extend(cohort_inventory_table(cohorts, labels))
    lines.append("")
    lines.extend(cohort_metric_table(cohorts, labels, runs))
    lines.append("")
    lines.extend(fallback_table(cohorts, labels, runs))
    lines.append("")
    lines.extend(confusion_table(cohorts, labels, runs, limit_per_system=limit_per_system))
    lines.extend(
        [
            "",
            "## Use Notes",
            "",
            "- Cohort names come from a source map, not from raw source names.",
            "- Silver-label cohort results are diagnostics until human route labels exist.",
            "- Add messenger-style cohorts through the same qrels/source-map schema before comparing live-query behavior.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--qrels", type=Path, required=True)
    parser.add_argument("--labels", type=Path, required=True)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--source-map", type=Path, required=True)
    parser.add_argument("--source-field", default="source")
    parser.add_argument("--label-status", default="private silver route labels")
    parser.add_argument("--limit-per-system", type=int, default=10)
    parser.add_argument("--fail-on-unmapped", action="store_true")
    parser.add_argument("--out", type=Path, default=ROOT / "reports" / "private_route_cohort_scorecard.md")
    args = parser.parse_args()

    source_map, default_cohort = load_source_map(args.source_map)
    qrels = load_jsonl(args.qrels)
    labels = load_jsonl(args.labels)
    runs = load_runs(args.run_dir)
    report = render_report(
        qrels=qrels,
        labels=labels,
        runs=runs,
        source_map=source_map,
        default_cohort=default_cohort,
        source_field=args.source_field,
        qrels_path=args.qrels,
        labels_path=args.labels,
        run_dir=args.run_dir,
        source_map_path=args.source_map,
        label_status=args.label_status,
        limit_per_system=args.limit_per_system,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(report, encoding="utf-8")
    print(report)

    _, unmapped = qids_by_cohort(
        qrels,
        labels,
        source_map,
        source_field=args.source_field,
        default_cohort=default_cohort,
    )
    if args.fail_on_unmapped and sum(unmapped.values()):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
