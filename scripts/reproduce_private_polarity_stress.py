#!/usr/bin/env python3
"""Publish an aggregate-only polarity stress report from a private run export.

The input rows may be private and may contain query or evidence fields. This
script deliberately projects them into a small safe representation before any
aggregation: seed-pair id, intent slice, and boolean wrong-polarity outcomes.
Neither input paths nor raw fields are written to the public artifacts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ko_evidence_bench.metrics import (  # noqa: E402
    clustered_bootstrap_hit_ci,
    load_jsonl,
    summarize_hit_rows,
)


RETRIEVAL_SYSTEMS = (
    ("bm25_analyzer_tokens", "bm25_wrong"),
    ("bm25_lucene_idf_sensitivity", "bm25lucene_wrong"),
    ("dense_bge_m3", "dense_wrong"),
)
RERANKER_SYSTEM = ("cross_encoder_bge_reranker_v2_m3", "wrong")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_string(row: dict[str, Any], key: str) -> str:
    value = row.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"row missing non-empty {key}")
    return value


def require_number(row: dict[str, Any], key: str) -> float:
    value = row.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
        raise ValueError(f"row missing numeric {key}")
    return float(value)


def require_bool(row: dict[str, Any], key: str) -> bool:
    value = row.get(key)
    if not isinstance(value, bool):
        raise ValueError(f"row missing boolean {key}")
    return value


def safe_retrieval_rows(path: Path) -> list[dict[str, Any]]:
    """Keep only the aggregate fields needed for the polarity measurement."""

    safe: list[dict[str, Any]] = []
    for row in load_jsonl(path):
        safe.append(
            {
                "pair_id": require_string(row, "pair_id"),
                "intent": require_string(row, "intent"),
                "bm25_wrong": require_bool(row, "bm25_wrong"),
                "bm25lucene_wrong": require_bool(row, "bm25lucene_wrong"),
                "dense_wrong": require_bool(row, "dense_wrong"),
            }
        )
    if not safe:
        raise ValueError("retrieval export contains no rows")
    return safe


def safe_reranker_rows(path: Path) -> list[dict[str, Any]]:
    """Project raw reranker scores into the same boolean wrong-polarity metric."""

    safe: list[dict[str, Any]] = []
    for row in load_jsonl(path):
        coverage_score = require_number(row, "cov_score")
        exclusion_score = require_number(row, "exc_score")
        expected_doc = require_string(row, "expected_doc")
        if expected_doc == "coverage_doc":
            expected_score, wrong_score = coverage_score, exclusion_score
        elif expected_doc == "exclusion_doc":
            expected_score, wrong_score = exclusion_score, coverage_score
        else:
            raise ValueError("expected_doc must be coverage_doc or exclusion_doc")
        safe.append(
            {
                "pair_id": require_string(row, "pair_id"),
                "intent": require_string(row, "intent"),
                "wrong": wrong_score >= expected_score,
            }
        )
    if not safe:
        raise ValueError("reranker export contains no rows")
    return safe


def summarize_system(
    *,
    system_id: str,
    rows: list[dict[str, Any]],
    metric: str,
    samples: int,
    seed: int,
) -> dict[str, Any]:
    summary = summarize_hit_rows(rows, metric)
    ci_lo, ci_hi = clustered_bootstrap_hit_ci(
        rows,
        metric,
        cluster_key="pair_id",
        samples=samples,
        seed=seed,
    )
    by_intent: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_intent[str(row["intent"])].append(row)
    intent_rows = []
    for intent, slice_rows in sorted(by_intent.items()):
        intent_summary = summarize_hit_rows(slice_rows, metric)
        slice_lo, slice_hi = clustered_bootstrap_hit_ci(
            slice_rows,
            metric,
            cluster_key="pair_id",
            samples=samples,
            seed=seed,
        )
        intent_rows.append(
            {
                "intent": intent,
                "n": int(intent_summary["n"]),
                "wrong_preferred": int(intent_summary["hits"]),
                "wrong_preferred_rate": intent_summary["rate"],
                "ci95_seed_pair_bootstrap": [slice_lo, slice_hi],
            }
        )
    return {
        "system_id": system_id,
        "n": int(summary["n"]),
        "seed_pairs": len({str(row["pair_id"]) for row in rows}),
        "wrong_preferred": int(summary["hits"]),
        "wrong_preferred_rate": summary["rate"],
        "ci95_seed_pair_bootstrap": [ci_lo, ci_hi],
        "intent_slices": intent_rows,
    }


def build_report(
    *,
    retrieval_rows_path: Path,
    reranker_rows_path: Path,
    dense_model: str,
    reranker_model: str,
    experiment_date: str,
    samples: int,
    seed: int,
) -> dict[str, Any]:
    retrieval_rows = safe_retrieval_rows(retrieval_rows_path)
    reranker_rows = safe_reranker_rows(reranker_rows_path)
    systems = [
        summarize_system(
            system_id=system_id,
            rows=retrieval_rows,
            metric=metric,
            samples=samples,
            seed=seed,
        )
        for system_id, metric in RETRIEVAL_SYSTEMS
    ]
    systems.append(
        summarize_system(
            system_id=RERANKER_SYSTEM[0],
            rows=reranker_rows,
            metric=RERANKER_SYSTEM[1],
            samples=samples,
            seed=seed,
        )
    )

    row_counts = {system["n"] for system in systems}
    pair_counts = {system["seed_pairs"] for system in systems}
    retrieval_pair_intents = Counter((row["pair_id"], row["intent"]) for row in retrieval_rows)
    reranker_pair_intents = Counter((row["pair_id"], row["intent"]) for row in reranker_rows)
    if len(row_counts) != 1 or len(pair_counts) != 1 or retrieval_pair_intents != reranker_pair_intents:
        raise ValueError("all system exports must cover the same pair/intent rows and seed pairs")

    return {
        "schema_version": "ko-evidence-bench.polarity-stress.v1",
        "experiment_date": experiment_date,
        "input": {
            "contrastive_triples": row_counts.pop(),
            "seed_evidence_pairs": pair_counts.pop(),
            "intent_counts": dict(sorted(Counter(row["intent"] for row in retrieval_rows).items())),
            "input_sha256": {
                "retrieval_export": file_sha256(retrieval_rows_path),
                "reranker_export": file_sha256(reranker_rows_path),
            },
            "raw_text_exported": False,
        },
        "metric": {
            "name": "wrong_polarity_preference",
            "definition": "opposite-polarity evidence scores at or above expected evidence",
            "ties_count_as_wrong": True,
        },
        "confidence_interval": {
            "method": "percentile bootstrap clustered by seed evidence pair",
            "samples": samples,
            "seed": seed,
        },
        "models": {
            "dense": dense_model,
            "reranker": reranker_model,
        },
        "systems": systems,
    }


def pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def ci_text(ci: list[float]) -> str:
    return f"{pct(ci[0])} - {pct(ci[1])}"


def render_markdown(report: dict[str, Any]) -> str:
    source = report["input"]
    systems = report["systems"]
    lines = [
        "# Korean Polarity Retrieval Stress",
        "",
        "A contrastive stress measurement over a private Korean evidence-retrieval lab.",
        "The public artifact contains aggregate outcomes only: no queries, passages,",
        "source names, URLs, user identifiers, or stable row ids are exported.",
        "",
        "## Result",
        "",
        "| system | triples | seed pairs | wrong-polarity preferred | 95% CI (seed-pair bootstrap) |",
        "|---|---:|---:|---:|---:|",
    ]
    for system in systems:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{system['system_id']}`",
                    str(system["n"]),
                    str(system["seed_pairs"]),
                    pct(system["wrong_preferred_rate"]),
                    ci_text(system["ci95_seed_pair_bootstrap"]),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "The stress test asks a narrower question than recall: when the candidate",
            "set contains expected and opposite-polarity evidence, does a system preserve",
            "the direction of the query? Lower is better. The dense model reduces the",
            "overall error rate relative to the lexical baselines, but the reranker remains",
            "fragile on the same contrastive slice.",
            "",
            "## Slice Asymmetry",
            "",
            "| system | intent slice | triples | wrong-polarity preferred | 95% CI (seed-pair bootstrap) |",
            "|---|---|---:|---:|---:|",
        ]
    )
    for system in systems:
        for slice_row in system["intent_slices"]:
            lines.append(
                "| "
                + " | ".join(
                    [
                        f"`{system['system_id']}`",
                        f"`{slice_row['intent']}`",
                        str(slice_row["n"]),
                        pct(slice_row["wrong_preferred_rate"]),
                        ci_text(slice_row["ci95_seed_pair_bootstrap"]),
                    ]
                )
                + " |"
            )

    lines.extend(
        [
            "",
            "## Measurement Contract",
            "",
            f"- contrastive triples: {source['contrastive_triples']}",
            f"- seed evidence pairs: {source['seed_evidence_pairs']}",
            "- intent balance: "
            + ", ".join(f"`{name}` {count}" for name, count in source["intent_counts"].items()),
            f"- dense model: `{report['models']['dense']}`",
            f"- reranker model: `{report['models']['reranker']}`",
            f"- metric: {report['metric']['definition']} (ties count as wrong)",
            f"- CI: {report['confidence_interval']['method']}; "
            f"{report['confidence_interval']['samples']:,} resamples; seed {report['confidence_interval']['seed']}",
            "",
            "The 444 triples are counterfactual variants derived from seed evidence",
            "pairs, not 444 independent source documents. Intervals therefore resample",
            "the seed pairs as clusters. This is a stress result, not an end-to-end",
            "human-relevance benchmark or a claim of cross-domain generalization.",
            "",
            "## Aggregate Provenance",
            "",
            f"- experiment date: {report['experiment_date']}",
            f"- retrieval input SHA-256: `{source['input_sha256']['retrieval_export']}`",
            f"- reranker input SHA-256: `{source['input_sha256']['reranker_export']}`",
            "- public output contains raw text: `false`",
            "",
            "To regenerate locally, supply the private aggregate row exports to",
            "`scripts/reproduce_private_polarity_stress.py`. The script projects each",
            "input row to pair id, intent, and Boolean outcome before it creates this",
            "report or its JSON companion.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--retrieval-rows", type=Path, required=True)
    parser.add_argument("--reranker-rows", type=Path, required=True)
    parser.add_argument("--report-out", type=Path, default=ROOT / "reports" / "private_polarity_stress_pilot.md")
    parser.add_argument("--json-out", type=Path, default=ROOT / "reports" / "private_polarity_stress_pilot.json")
    parser.add_argument("--dense-model", default="BAAI/bge-m3")
    parser.add_argument("--reranker-model", default="BAAI/bge-reranker-v2-m3")
    parser.add_argument("--experiment-date", default="unspecified")
    parser.add_argument("--samples", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=13)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    report = build_report(
        retrieval_rows_path=args.retrieval_rows,
        reranker_rows_path=args.reranker_rows,
        dense_model=args.dense_model,
        reranker_model=args.reranker_model,
        experiment_date=args.experiment_date,
        samples=args.samples,
        seed=args.seed,
    )
    markdown = render_markdown(report)
    json_text = json.dumps(report, ensure_ascii=True, indent=2, sort_keys=True) + "\n"

    if args.check:
        current_markdown = args.report_out.read_text(encoding="utf-8") if args.report_out.exists() else ""
        current_json = args.json_out.read_text(encoding="utf-8") if args.json_out.exists() else ""
        if current_markdown != markdown or current_json != json_text:
            print("private polarity stress artifacts are stale; rerun the reproduction script")
            return 1
        print("private polarity stress artifacts are current")
        return 0

    args.report_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.report_out.write_text(markdown, encoding="utf-8")
    args.json_out.write_text(json_text, encoding="utf-8")
    print(markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
