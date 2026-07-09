#!/usr/bin/env python3
"""Build the public probe dataset card from checked-in probe files."""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ko_evidence_bench.metrics import load_jsonl  # noqa: E402


def display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def count_values(rows: list[dict[str, Any]], field: str) -> Counter[str]:
    counts: Counter[str] = Counter()
    for row in rows:
        value = row.get(field)
        if isinstance(value, list):
            counts.update(str(item) for item in value)
        else:
            counts[str(value or "<missing>")] += 1
    return counts


def render_count_table(title: str, counts: Counter[str]) -> list[str]:
    lines = [
        f"## {title}",
        "",
        "| value | rows |",
        "|---|---:|",
    ]
    for value, count in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"| `{value}` | {count} |")
    lines.append("")
    return lines


def load_probe(probe_dir: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    return (
        load_jsonl(probe_dir / "queries.jsonl"),
        load_jsonl(probe_dir / "qrels.jsonl"),
        load_jsonl(probe_dir / "evidence.jsonl"),
    )


def render_dataset_card(probe_dir: Path) -> str:
    queries, qrels, evidence = load_probe(probe_dir)
    qrel_by_qid = {str(row["qid"]): row for row in qrels}
    answerable = [row for row in qrels if not row.get("should_abstain")]
    abstention = [row for row in qrels if row.get("should_abstain")]
    qrel_pairs = sum(len(row.get("sufficient_evidence_ids", [])) for row in answerable)
    beir_dir = probe_dir / "beir"

    lines = [
        "# Ko Evidence Probe v0 Dataset Card",
        "",
        "Status: **synthetic public fixture; not a private benchmark release**.",
        "",
        "## Summary",
        "",
        "Ko Evidence Probe v0 is a small Korean evidence-retrieval probe for",
        "source routing, abstention, and surface-form robustness. It is designed",
        "to make the evaluation protocol reusable without releasing private",
        "community crawls, messenger exports, community Q&A rows, or copyrighted",
        "policy corpora.",
        "",
        "The probe is intentionally small. Its job is to exercise the public",
        "schema, privacy screen, BEIR-style export, and diagnostic scorecards.",
        "It should not be cited as a production benchmark or as evidence about",
        "all Korean retrieval systems.",
        "",
        "## Files",
        "",
        f"- probe directory: `{display_path(probe_dir)}`",
        "- `queries.jsonl`: synthetic Korean query variants with intent and surface metadata.",
        "- `qrels.jsonl`: source-route labels, abstention labels, and sufficient evidence ids.",
        "- `evidence.jsonl`: synthetic evidence snippets by source tier.",
        f"- `beir/`: answerable-only BEIR-style subset at `{display_path(beir_dir)}`.",
        "",
        "## Size",
        "",
        "| item | count |",
        "|---|---:|",
        f"| queries | {len(queries)} |",
        f"| qrels | {len(qrels)} |",
        f"| evidence snippets | {len(evidence)} |",
        f"| answerable qrels | {len(answerable)} |",
        f"| abstention qrels | {len(abstention)} |",
        f"| sufficient query-evidence pairs | {qrel_pairs} |",
        f"| intent families | {len({row.get('intent_family') for row in queries})} |",
        f"| intent ids | {len({row.get('intent_id') for row in queries})} |",
        f"| surface forms | {len({row.get('surface_form') for row in queries})} |",
        "",
        "## Intended Use",
        "",
        "- Regression-test source-aware retrieval metrics.",
        "- Check whether one intent remains retrievable across formal, colloquial,",
        "  abbreviated, and messenger-style surface forms.",
        "- Exercise BEIR-style retrieval tooling on answerable rows while keeping",
        "  route and abstention metadata available for richer diagnostics.",
        "- Demonstrate privacy-preserving release mechanics for a larger private",
        "  Korean search-lab workflow.",
        "",
        "## Not Intended Use",
        "",
        "- Do not treat this as a human-gold benchmark.",
        "- Do not use it to claim broad Korean IR model quality.",
        "- Do not use it as an insurance advice dataset.",
        "- Do not read the surface metadata as a synonym dictionary or rewrite product.",
        "",
        "## Labels",
        "",
        "Each query has an `intent_family`, `intent_id`, `surface_form`, and",
        "`trap_classes` annotation. Qrels add `route_gold`,",
        "`allowed_source_tiers`, `should_abstain`, and",
        "`sufficient_evidence_ids`. BEIR qrels contain answerable rows only;",
        "abstention, route, surface, and trap metadata remain in",
        "`query_metadata.jsonl` and the original qrels.",
        "",
    ]
    lines.extend(render_count_table("Intent-Family Distribution", count_values(queries, "intent_family")))
    lines.extend(render_count_table("Surface-Form Distribution", count_values(queries, "surface_form")))
    lines.extend(render_count_table("Route Distribution", count_values(qrels, "route_gold")))
    lines.extend(render_count_table("Trap-Class Distribution", count_values(qrels, "trap_classes")))
    lines.extend(
        [
            "## Privacy And Provenance",
            "",
            "All rows use `provenance = synthetic_public_fixture`. The probe is built",
            "from synthetic Korean examples and synthetic evidence snippets. It is",
            "screened by `make check-probe-privacy` for schema joins, source-tier",
            "validity, PII-like patterns, private-source indicators, and long",
            "n-gram overlap against configured reference material.",
            "",
            "## Evaluation Hooks",
            "",
            "- `make reproduce-probe-system-comparison` runs lexical, surface-expanded,",
            "  semantic-centroid, hybrid, and source-route-aware systems.",
            "- `make reproduce-probe-trap-mining` checks diagnostic trap mining.",
            "- `make reproduce-surface-fragmentation-audit` measures lexical seed",
            "  undercounting across surface variants.",
            "- `make export-probe-beir` regenerates the BEIR-style retrieval subset.",
            "",
            "## Release Notes",
            "",
            "- License: repository license.",
            "- Language: Korean query text with English synthetic evidence summaries.",
            "- Domain: insurance evidence retrieval as a first testbed.",
            "- Claim status: fixture only; human-gold headline claims remain blocked",
            "  until independent labels and the full comparison matrix are complete.",
            "",
        ]
    )
    missing_qrels = sorted(str(row["qid"]) for row in queries if str(row["qid"]) not in qrel_by_qid)
    if missing_qrels:
        lines.extend(["## Card Warnings", "", f"- queries without qrels: `{', '.join(missing_qrels)}`", ""])
    return "\n".join(lines)


def render_summary_report(probe_dir: Path, card_path: Path) -> str:
    queries, qrels, evidence = load_probe(probe_dir)
    answerable = [row for row in qrels if not row.get("should_abstain")]
    abstention = [row for row in qrels if row.get("should_abstain")]
    return "\n".join(
        [
            "# Probe Dataset Card Report",
            "",
            "Status: **dataset card generated from public probe files**.",
            "",
            "This report checks that the public probe has a reusable release-facing",
            "dataset card. The card is generated from checked-in JSONL files so row",
            "counts, surface distributions, route labels, and abstention counts cannot",
            "drift silently.",
            "",
            "## Outputs",
            "",
            f"- dataset card: `{display_path(card_path)}`",
            f"- probe dir: `{display_path(probe_dir)}`",
            "",
            "## Inventory",
            "",
            "| item | count |",
            "|---|---:|",
            f"| queries | {len(queries)} |",
            f"| qrels | {len(qrels)} |",
            f"| evidence snippets | {len(evidence)} |",
            f"| answerable qrels | {len(answerable)} |",
            f"| abstention qrels | {len(abstention)} |",
            f"| intent families | {len({row.get('intent_family') for row in queries})} |",
            f"| surface forms | {len({row.get('surface_form') for row in queries})} |",
            "",
            "## Use Notes",
            "",
            "- The dataset card is a release-control artifact, not a benchmark result.",
            "- It should stay synchronized with `queries.jsonl`, `qrels.jsonl`,",
            "  `evidence.jsonl`, and the BEIR-style export.",
            "- It repeats the public/private boundary so the probe is not mistaken",
            "  for released private data.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--probe-dir", type=Path, default=ROOT / "probes" / "ko_evidence_probe_v0")
    parser.add_argument(
        "--card-out",
        type=Path,
        default=ROOT / "probes" / "ko_evidence_probe_v0" / "DATASET_CARD.md",
    )
    parser.add_argument("--report-out", type=Path, default=ROOT / "reports" / "probe_dataset_card.md")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    card = render_dataset_card(args.probe_dir)
    report = render_summary_report(args.probe_dir, args.card_out)

    if args.check:
        current_card = args.card_out.read_text(encoding="utf-8") if args.card_out.exists() else ""
        current_report = args.report_out.read_text(encoding="utf-8") if args.report_out.exists() else ""
        if current_card != card or current_report != report:
            print("probe dataset card is stale; run scripts/build_probe_dataset_card.py")
            return 1
        print("probe dataset card is current")
        return 0

    args.card_out.parent.mkdir(parents=True, exist_ok=True)
    args.report_out.parent.mkdir(parents=True, exist_ok=True)
    args.card_out.write_text(card, encoding="utf-8")
    args.report_out.write_text(report, encoding="utf-8")
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
