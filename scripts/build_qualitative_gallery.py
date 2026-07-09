#!/usr/bin/env python3
"""Build a qualitative failure gallery from the public probe package."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


@dataclass(frozen=True)
class Ranking:
    system: str
    route_pred: str
    abstained: bool
    ranked_evidence_ids: tuple[str, ...]


@dataclass(frozen=True)
class GalleryCase:
    qid: str
    failure_layer: str
    why_it_matters: str
    baseline: Ranking
    candidate: Ranking


CASES = [
    GalleryCase(
        qid="probe-underwriting-messenger",
        failure_layer="source routing / abstention",
        why_it_matters="The query needs private contract and underwriting context; citing a generic policy clause is unsafe.",
        baseline=Ranking(
            system="policy_only_baseline",
            route_pred="policy_clause",
            abstained=False,
            ranked_evidence_ids=("ev-policy-noncovered-treatment",),
        ),
        candidate=Ranking(
            system="source_routed_candidate",
            route_pred="human_context_needed",
            abstained=True,
            ranked_evidence_ids=(),
        ),
    ),
    GalleryCase(
        qid="probe-claims-docs",
        failure_layer="source-tier mismatch",
        why_it_matters="A claim-document question should land on claim-operation evidence, not only on policy wording.",
        baseline=Ranking(
            system="policy_only_baseline",
            route_pred="policy_clause",
            abstained=False,
            ranked_evidence_ids=("ev-policy-bundle-diagnosis",),
        ),
        candidate=Ranking(
            system="source_routed_candidate",
            route_pred="claims_faq",
            abstained=False,
            ranked_evidence_ids=("ev-claims-document-checklist",),
        ),
    ),
    GalleryCase(
        qid="probe-refund-messenger",
        failure_layer="register and evidence-form mismatch",
        why_it_matters="A colloquial refund question needs a product disclosure table; a generic clause can look relevant but miss the answer form.",
        baseline=Ranking(
            system="policy_only_baseline",
            route_pred="policy_clause",
            abstained=False,
            ranked_evidence_ids=("ev-policy-noncovered-treatment",),
        ),
        candidate=Ranking(
            system="source_routed_candidate",
            route_pred="product_disclosure",
            abstained=False,
            ranked_evidence_ids=("ev-disclosure-refund-table",),
        ),
    ),
    GalleryCase(
        qid="probe-dispute-denial",
        failure_layer="source-tier mismatch",
        why_it_matters="A denial dispute needs dispute-case evidence; policy clauses may be supporting context, not the primary source.",
        baseline=Ranking(
            system="policy_only_baseline",
            route_pred="policy_clause",
            abstained=False,
            ranked_evidence_ids=("ev-policy-noncovered-treatment",),
        ),
        candidate=Ranking(
            system="source_routed_candidate",
            route_pred="dispute_case",
            abstained=False,
            ranked_evidence_ids=("ev-dispute-denial-case",),
        ),
    ),
]


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def one_line(text: str, limit: int = 140) -> str:
    text = " ".join(text.split())
    return text if len(text) <= limit else text[: limit - 3] + "..."


def evidence_cell(ranking: Ranking, evidence_by_id: dict[str, dict[str, Any]]) -> str:
    if ranking.abstained:
        return "`ABSTAIN`"
    if not ranking.ranked_evidence_ids:
        return "`NO_EVIDENCE`"
    evidence = evidence_by_id[ranking.ranked_evidence_ids[0]]
    return (
        f"`{ranking.route_pred}` / `{evidence['evidence_id']}`: "
        f"{one_line(str(evidence['text']))}"
    )


def render_gallery(probe_dir: Path) -> str:
    queries = {row["qid"]: row for row in read_jsonl(probe_dir / "queries.jsonl")}
    qrels = {row["qid"]: row for row in read_jsonl(probe_dir / "qrels.jsonl")}
    evidence_by_id = {row["evidence_id"]: row for row in read_jsonl(probe_dir / "evidence.jsonl")}

    lines = [
        "# Qualitative Failure Gallery",
        "",
        "Status: **synthetic qualitative examples only; human-gold headline claims blocked**.",
        "",
        "This gallery gives a reviewer concrete examples behind the route and",
        "surface diagnostics. Every query and evidence snippet is synthetic and",
        "comes from `probes/ko_evidence_probe_v0/`.",
        "",
        "## Gallery",
        "",
        "| qid | query | gold route | failure layer | `policy_only_baseline` top result | `source_routed_candidate` top result | read |",
        "|---|---|---|---|---|---|---|",
    ]
    for case in CASES:
        query = queries[case.qid]
        qrel = qrels[case.qid]
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{case.qid}`",
                    str(query["query"]),
                    f"`{qrel['route_gold']}`",
                    case.failure_layer,
                    evidence_cell(case.baseline, evidence_by_id),
                    evidence_cell(case.candidate, evidence_by_id),
                    case.why_it_matters,
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## What To Inspect",
            "",
            "- The baseline is intentionally route-naive: it shows what goes wrong when",
            "  every question is forced toward policy-clause evidence.",
            "- The candidate is not a production system. It is a compact demonstration",
            "  of the source-route behavior the benchmark is meant to measure.",
            "- These examples should be read with the claim ledger: they illustrate",
            "  diagnostic failure modes, not final benchmark performance.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--probe-dir", type=Path, default=ROOT / "probes" / "ko_evidence_probe_v0")
    parser.add_argument("--out", type=Path, default=ROOT / "reports" / "qualitative_gallery.md")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    report = render_gallery(args.probe_dir)
    if args.check:
        current = args.out.read_text(encoding="utf-8") if args.out.exists() else ""
        if current != report:
            print("qualitative gallery is stale; run scripts/build_qualitative_gallery.py")
            return 1
        print("qualitative gallery is current")
        return 0

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(report, encoding="utf-8")
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
