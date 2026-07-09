#!/usr/bin/env python3
"""Export the public probe package to a BEIR-style directory."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ko_evidence_bench.beir_export import export_beir_probe, validate_beir_export  # noqa: E402
from ko_evidence_bench.metrics import load_jsonl  # noqa: E402


def display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def write_qrels_tsv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        handle.write("query-id\tcorpus-id\tscore\n")
        for row in rows:
            handle.write(f"{row['query-id']}\t{row['corpus-id']}\t{row['score']}\n")


def render_report(*, probe_dir: Path, out_dir: Path) -> str:
    queries = load_jsonl(probe_dir / "queries.jsonl")
    qrels = load_jsonl(probe_dir / "qrels.jsonl")
    evidence = load_jsonl(probe_dir / "evidence.jsonl")
    export = export_beir_probe(queries, qrels, evidence)
    issues = validate_beir_export(export)

    lines = [
        "# Public Probe BEIR Export",
        "",
        "Status: **BEIR-style retrieval subset; source routing and abstention stay in metadata**.",
        "",
        "This export makes the synthetic public probe usable with standard IR",
        "tooling that expects BEIR-like `corpus.jsonl`, `queries.jsonl`, and",
        "`qrels/test.tsv` files. It does not replace the source-route scorecards:",
        "BEIR qrels cannot represent abstention or route labels, so those fields",
        "are preserved in `query_metadata.jsonl` and in the original probe qrels.",
        "",
        "## Inputs",
        "",
        f"- probe dir: `{display_path(probe_dir)}`",
        f"- output dir: `{display_path(out_dir)}`",
        "- label status: synthetic public fixture",
        "",
        "## Exported Files",
        "",
        "| file | rows | purpose |",
        "|---|---:|---|",
        f"| `{display_path(out_dir / 'corpus.jsonl')}` | {len(export.corpus)} | BEIR corpus documents |",
        f"| `{display_path(out_dir / 'queries.jsonl')}` | {len(export.queries)} | BEIR query rows |",
        f"| `{display_path(out_dir / 'qrels' / 'test.tsv')}` | {len(export.qrels)} | answerable query-evidence labels |",
        f"| `{display_path(out_dir / 'query_metadata.jsonl')}` | {len(export.query_metadata)} | route, intent, surface, and trap metadata |",
        "",
        "## Coverage",
        "",
        "| item | value |",
        "|---|---:|",
        f"| source query rows | {len(queries)} |",
        f"| source evidence rows | {len(evidence)} |",
        f"| answerable qrel pairs | {len(export.qrels)} |",
        f"| abstention rows skipped from BEIR qrels | {len(export.skipped_abstention_qids)} |",
        f"| validation issues | {len(issues)} |",
        "",
        "## Skipped Abstention Qids",
        "",
        "| qid | reason |",
        "|---|---|",
    ]
    if export.skipped_abstention_qids:
        for qid in export.skipped_abstention_qids:
            lines.append(f"| `{qid}` | `should_abstain=true` has no BEIR qrel equivalent |")
    else:
        lines.append("| none | none |")

    lines.extend(
        [
            "",
            "## Validation",
            "",
            "| issue |",
            "|---|",
        ]
    )
    if issues:
        for issue in issues:
            lines.append(f"| `{issue}` |")
    else:
        lines.append("| none |")

    lines.extend(
        [
            "",
            "## Use Notes",
            "",
            "- Treat this as a public fixture export, not a final benchmark release.",
            "- Use `query_metadata.jsonl` when slicing by intent family, surface form, trap class, or source route.",
            "- Use the original probe qrels for abstention and source-routing evaluation.",
            "",
        ]
    )
    return "\n".join(lines)


def export_files(*, probe_dir: Path, out_dir: Path, report_out: Path) -> str:
    queries = load_jsonl(probe_dir / "queries.jsonl")
    qrels = load_jsonl(probe_dir / "qrels.jsonl")
    evidence = load_jsonl(probe_dir / "evidence.jsonl")
    export = export_beir_probe(queries, qrels, evidence)
    issues = validate_beir_export(export)
    if issues:
        raise ValueError("; ".join(issues))

    write_jsonl(out_dir / "corpus.jsonl", export.corpus)
    write_jsonl(out_dir / "queries.jsonl", export.queries)
    write_jsonl(out_dir / "query_metadata.jsonl", export.query_metadata)
    write_qrels_tsv(out_dir / "qrels" / "test.tsv", export.qrels)
    report = render_report(probe_dir=probe_dir, out_dir=out_dir)
    report_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.write_text(report, encoding="utf-8")
    return report


def read_file(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def current_files_match(*, probe_dir: Path, out_dir: Path, report_out: Path) -> bool:
    queries = load_jsonl(probe_dir / "queries.jsonl")
    qrels = load_jsonl(probe_dir / "qrels.jsonl")
    evidence = load_jsonl(probe_dir / "evidence.jsonl")
    export = export_beir_probe(queries, qrels, evidence)
    issues = validate_beir_export(export)
    if issues:
        return False
    expected_corpus = "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in export.corpus)
    expected_queries = "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in export.queries)
    expected_metadata = "".join(
        json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in export.query_metadata
    )
    expected_qrels = "query-id\tcorpus-id\tscore\n" + "".join(
        f"{row['query-id']}\t{row['corpus-id']}\t{row['score']}\n" for row in export.qrels
    )
    expected_report = render_report(probe_dir=probe_dir, out_dir=out_dir)
    return (
        read_file(out_dir / "corpus.jsonl") == expected_corpus
        and read_file(out_dir / "queries.jsonl") == expected_queries
        and read_file(out_dir / "query_metadata.jsonl") == expected_metadata
        and read_file(out_dir / "qrels" / "test.tsv") == expected_qrels
        and read_file(report_out) == expected_report
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--probe-dir", type=Path, default=ROOT / "probes" / "ko_evidence_probe_v0")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "probes" / "ko_evidence_probe_v0" / "beir")
    parser.add_argument("--report-out", type=Path, default=ROOT / "reports" / "probe_beir_export.md")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    if args.check:
        if not current_files_match(probe_dir=args.probe_dir, out_dir=args.out_dir, report_out=args.report_out):
            print("probe BEIR export is stale; run scripts/export_probe_beir.py")
            return 1
        print("probe BEIR export is current")
        return 0

    report = export_files(probe_dir=args.probe_dir, out_dir=args.out_dir, report_out=args.report_out)
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
