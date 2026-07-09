#!/usr/bin/env python3
"""Build a private human-audit pack for source-route labels.

The audit pack may contain raw private query text, so write it outside this
public repository. The report output is aggregate-only and safe to check in.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


HUMAN_FIELDS = {
    "human_route_gold": "",
    "human_allowed_source_tiers": [],
    "human_should_abstain": None,
    "human_confidence": "",
    "human_labeler": "",
    "human_rationale_code": "",
    "human_notes": "",
}


def reviewer_template() -> dict[str, Any]:
    return {
        "route_gold": "",
        "allowed_source_tiers": [],
        "should_abstain": None,
        "confidence": "",
        "rationale_code": "",
        "labeler": "",
        "notes": "",
    }


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def pct(value: float) -> str:
    return f"{100 * value:.1f}%"


def allocate_sample(
    labels: list[dict[str, Any]],
    *,
    sample_size: int,
    min_per_route: int,
    seed: int,
) -> list[dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for label in labels:
        groups[label["route_gold"]].append(label)

    rng = random.Random(seed)
    for rows in groups.values():
        rng.shuffle(rows)

    n = len(labels)
    selected: list[dict[str, Any]] = []
    selected_qids: set[str] = set()

    for route in sorted(groups):
        take = min(len(groups[route]), min_per_route)
        for label in groups[route][:take]:
            selected.append(label)
            selected_qids.add(label["qid"])

    remaining_slots = max(0, sample_size - len(selected))
    remaining = [label for label in labels if label["qid"] not in selected_qids]
    rng.shuffle(remaining)

    # Prefer proportional coverage for the remaining slots, then fill any gaps.
    by_route: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for label in remaining:
        by_route[label["route_gold"]].append(label)
    for route in sorted(by_route):
        if remaining_slots <= 0:
            break
        target = round(sample_size * (len(groups[route]) / n)) if n else 0
        already = sum(1 for label in selected if label["route_gold"] == route)
        take = min(len(by_route[route]), max(0, target - already), remaining_slots)
        for label in by_route[route][:take]:
            selected.append(label)
            selected_qids.add(label["qid"])
        remaining_slots = sample_size - len(selected)

    if remaining_slots > 0:
        tail = [label for label in remaining if label["qid"] not in selected_qids]
        selected.extend(tail[:remaining_slots])

    rng.shuffle(selected)
    return selected[:sample_size]


def build_audit_rows(
    qrels: list[dict[str, Any]],
    labels: list[dict[str, Any]],
    *,
    sample_size: int,
    min_per_route: int,
    seed: int,
) -> list[dict[str, Any]]:
    qrel_by_qid = {row["qid"]: row for row in qrels}
    eligible = [label for label in labels if label["qid"] in qrel_by_qid]
    sample = allocate_sample(eligible, sample_size=sample_size, min_per_route=min_per_route, seed=seed)

    out: list[dict[str, Any]] = []
    for idx, label in enumerate(sample, 1):
        qrel = qrel_by_qid[label["qid"]]
        out.append(
            {
                "audit_id": f"route-audit-{idx:04d}",
                "qid": label["qid"],
                "query": qrel.get("query", ""),
                "context": qrel.get("body", ""),
                "metadata": {
                    "gate_category": qrel.get("gate_category", ""),
                    "intent": qrel.get("intent", ""),
                    "answerability": qrel.get("answerability", ""),
                    "answer_structure": qrel.get("answer_structure", ""),
                    "reason_code": qrel.get("reason_code", ""),
                    "needs_contract": qrel.get("needs_contract"),
                    "product_divergent": qrel.get("product_divergent"),
                    "required_facets": qrel.get("required_facets") or [],
                },
                "silver": {
                    "route_gold": label["route_gold"],
                    "allowed_source_tiers": label.get("allowed_source_tiers") or [],
                    "should_abstain": label["should_abstain"],
                    "confidence": label["confidence"],
                    "rationale_code": label["rationale_code"],
                },
                "reviewer_a": reviewer_template(),
                "reviewer_b": reviewer_template(),
                "adjudicated": reviewer_template(),
                **HUMAN_FIELDS,
            }
        )
    return out


def table(title: str, counts: Counter[str]) -> list[str]:
    total = sum(counts.values())
    lines = [f"## {title}", "", "| value | count | share |", "|---|---:|---:|"]
    for key, value in counts.most_common():
        share = value / total if total else 0.0
        lines.append(f"| `{key}` | {value} | {pct(share)} |")
    return lines


def render_report(
    audit_rows: list[dict[str, Any]],
    *,
    qrels_path: Path,
    labels_path: Path,
    audit_out: Path,
    seed: int,
    min_per_route: int,
) -> str:
    route_counts = Counter(row["silver"]["route_gold"] for row in audit_rows)
    confidence_counts = Counter(row["silver"]["confidence"] for row in audit_rows)
    abstention_counts = Counter(str(row["silver"]["should_abstain"]) for row in audit_rows)

    lines = [
        "# Private Route Audit Pack Summary",
        "",
        "This report summarizes a private human-audit pack. It contains aggregate",
        "counts only. The audit pack itself may contain raw queries and must stay",
        "outside the public repository.",
        "",
        f"- sampled rows: {len(audit_rows)}",
        f"- seed: {seed}",
        f"- minimum per route: {min_per_route}",
        f"- qrels file: `{qrels_path.name}`",
        f"- silver labels file: `{labels_path.name}`",
        f"- private audit pack: `{audit_out.name}`",
        "",
        "## Reviewer Fields",
        "",
        "| field | purpose |",
        "|---|---|",
        "| `human_route_gold` | adjudicated source route |",
        "| `human_allowed_source_tiers` | acceptable supporting source tiers |",
        "| `human_should_abstain` | whether the system should refuse to answer without more facts |",
        "| `human_confidence` | high, medium, or low |",
        "| `human_rationale_code` | compact reason for the route decision |",
        "| `human_notes` | brief adjudication note |",
        "| `reviewer_a.*` | first independent reviewer labels |",
        "| `reviewer_b.*` | second independent reviewer labels |",
        "| `adjudicated.*` | final labels after disagreement review |",
        "",
    ]
    lines.extend(table("Sampled Route Distribution", route_counts))
    lines.append("")
    lines.extend(table("Sampled Confidence Distribution", confidence_counts))
    lines.append("")
    lines.extend(table("Sampled Abstention Distribution", abstention_counts))
    lines.extend(
        [
            "",
            "## Use Notes",
            "",
            "- Double-label this pack before reporting human agreement.",
            "- Public benchmark claims should use adjudicated fields, not silver fields.",
            "- Do not copy raw audit rows into the public repository.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--qrels", type=Path, required=True)
    parser.add_argument("--labels", type=Path, required=True)
    parser.add_argument("--audit-out", type=Path, required=True)
    parser.add_argument("--report-out", type=Path)
    parser.add_argument("--sample-size", type=int, default=50)
    parser.add_argument("--min-per-route", type=int, default=4)
    parser.add_argument("--seed", type=int, default=17)
    args = parser.parse_args()

    qrels = load_jsonl(args.qrels)
    labels = load_jsonl(args.labels)
    audit_rows = build_audit_rows(
        qrels,
        labels,
        sample_size=args.sample_size,
        min_per_route=args.min_per_route,
        seed=args.seed,
    )
    write_jsonl(args.audit_out, audit_rows)
    report = render_report(
        audit_rows,
        qrels_path=args.qrels,
        labels_path=args.labels,
        audit_out=args.audit_out,
        seed=args.seed,
        min_per_route=args.min_per_route,
    )
    if args.report_out:
        args.report_out.parent.mkdir(parents=True, exist_ok=True)
        args.report_out.write_text(report, encoding="utf-8")
    else:
        print(report, end="")


if __name__ == "__main__":
    main()
