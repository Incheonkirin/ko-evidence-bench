#!/usr/bin/env python3
"""Build a qid-only submission template for the missing system matrix runs."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ko_evidence_bench.metrics import load_jsonl  # noqa: E402
from ko_evidence_bench.schemas import ROUTE_LABELS, validate_qrel  # noqa: E402
from ko_evidence_bench.system_matrix_bundle import runnable_required_system_ids  # noqa: E402
from ko_evidence_bench.system_matrix import load_matrix, system_rows  # noqa: E402


def display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def required_rows(matrix_path: Path) -> list[dict[str, Any]]:
    required = set(runnable_required_system_ids(matrix_path))
    return [
        row
        for row in system_rows(load_matrix(matrix_path))
        if str(row["system_id"]) in required
    ]


def load_qids(qrels_path: Path) -> tuple[list[str], list[str]]:
    qrels = load_jsonl(qrels_path)
    errors: list[str] = []
    qids: list[str] = []
    seen: set[str] = set()
    for index, row in enumerate(qrels, 1):
        try:
            validate_qrel(row)
        except ValueError as exc:
            errors.append(f"row {index}: {exc}")
        qid = str(row.get("qid") or "")
        if not qid:
            errors.append(f"row {index}: qid is required")
            continue
        if qid in seen:
            errors.append(f"row {index}: duplicate qid {qid}")
        seen.add(qid)
        qids.append(qid)
    return qids, errors


def manifest_template(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "label_status": "real external-system run; describe runner, date, corpus, and model versions here",
        "systems": [
            {
                "system_id": row["system_id"],
                "family": row["family"],
                "stage": row["stage"],
                "run": f"runs/{row['system_id']}.jsonl",
            }
            for row in rows
        ],
    }


def run_template_lines(qids: list[str]) -> list[str]:
    rows = [
        {
            "qid": qid,
            "route_pred": "TODO_ROUTE_LABEL",
            "abstained": False,
            "ranked": [],
        }
        for qid in qids
    ]
    return [json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows]


def pack_readme(*, qrels_path: Path, matrix_path: Path, required: list[dict[str, Any]], qid_count: int) -> str:
    route_labels = ", ".join(f"`{label}`" for label in sorted(ROUTE_LABELS))
    systems = "\n".join(
        f"- `{row['system_id']}`: {row['family']} / {row['stage']}"
        for row in required
    )
    return "\n".join(
        [
            "# System Matrix Submission Template",
            "",
            "Status: template only. It is not model output and must not be promoted.",
            "",
            "This pack is a qid-only handoff for missing full-matrix system runs.",
            "It intentionally excludes raw queries, source names, URLs, answers,",
            "conversation snippets, and evidence text.",
            "",
            "## Inputs",
            "",
            f"- qrels: `{display_path(qrels_path)}`",
            f"- system matrix: `{display_path(matrix_path)}`",
            f"- qids: {qid_count}",
            "",
            "## Required Systems",
            "",
            systems,
            "",
            "## Run Row Schema",
            "",
            "Each submitted run file must be JSONL with one row per qid:",
            "",
            "```json",
            '{"qid":"stable-id","route_pred":"policy_clause","abstained":false,"ranked":[{"evidence_id":"stable-evidence-id","source_tier":"policy_clause","score":1.0}]}',
            "```",
            "",
            f"Allowed route labels: {route_labels}.",
            "",
            "Use `ranked: []` when the system abstains. Ranked items may include only",
            "`evidence_id`, `source_tier`, and optional numeric `score`.",
            "",
            "## Promotion",
            "",
            "After replacing templates with real run files, validate the bundle:",
            "",
            "```bash",
            "python3 scripts/validate_system_matrix_bundle.py \\",
            "  --bundle-dir /path/to/private_matrix_bundle \\",
            "  --qrels /path/to/private_qid_only_qrels.jsonl \\",
            "  --matrix docs/system_matrix.json \\",
            "  --out reports/private_system_matrix_bundle.md",
            "```",
            "",
            "Then run the promotion rehearsal. Promotion should remain blocked unless",
            "the bundle has real run provenance, enough rows, complete qid coverage,",
            "zero schema errors, and no raw fields.",
            "",
        ]
    )


def write_pack(*, pack_dir: Path, qrels_path: Path, matrix_path: Path, required: list[dict[str, Any]], qids: list[str]) -> None:
    runs_dir = pack_dir / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)
    (pack_dir / "manifest.template.json").write_text(
        json.dumps(manifest_template(required), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (pack_dir / "README.md").write_text(
        pack_readme(qrels_path=qrels_path, matrix_path=matrix_path, required=required, qid_count=len(qids)),
        encoding="utf-8",
    )
    lines = "\n".join(run_template_lines(qids)) + "\n"
    for row in required:
        (runs_dir / f"{row['system_id']}.jsonl.template").write_text(lines, encoding="utf-8")


def expected_pack_files(pack_dir: Path, required: list[dict[str, Any]]) -> list[Path]:
    return [
        pack_dir / "README.md",
        pack_dir / "manifest.template.json",
        *[pack_dir / "runs" / f"{row['system_id']}.jsonl.template" for row in required],
    ]


def render_report(*, qrels_path: Path, matrix_path: Path, pack_dir: Path) -> str:
    required = required_rows(matrix_path)
    qids, errors = load_qids(qrels_path)
    files = expected_pack_files(pack_dir, required)
    missing_files = [path for path in files if not path.exists()]
    status = "PASS" if not errors and not missing_files and required else "FAIL"
    lines = [
        "# System Matrix Submission Pack Fixture",
        "",
        f"Status: **{status} qid-only matrix submission template**.",
        "",
        "This report checks the handoff pack for external analyzer, dense,",
        "hybrid, and reranker runs. It is a template, not model output; it",
        "must not be used as evidence that the full private matrix has been run.",
        "",
        "## Inputs",
        "",
        f"- qrels: `{display_path(qrels_path)}`",
        f"- system matrix: `{display_path(matrix_path)}`",
        f"- pack dir: `{display_path(pack_dir)}`",
        f"- qrel rows: {len(qids)}",
        f"- required missing-matrix systems: {len(required)}",
        "",
        "## Gate Summary",
        "",
        "| gate | evidence | status |",
        "|---|---:|---|",
        f"| qrel validation | {len(errors)} errors | `{'PASS' if not errors else 'FAIL'}` |",
        f"| required systems | {len(required)} systems | `{'PASS' if required else 'FAIL'}` |",
        f"| template files | {len(files) - len(missing_files)} / {len(files)} present | `{'PASS' if not missing_files else 'FAIL'}` |",
        "| raw-field boundary | qids plus placeholder run schema only | `PASS` |",
        "| promotion status | template only; no external systems run | `BLOCKED` |",
        "",
        "## Required Systems",
        "",
        "| system | family | stage | template |",
        "|---|---|---|---|",
    ]
    for row in required:
        template = pack_dir / "runs" / f"{row['system_id']}.jsonl.template"
        lines.append(
            f"| `{row['system_id']}` | `{row['family']}` | `{row['stage']}` | `{display_path(template)}` |"
        )

    if errors:
        lines.extend(["", "## Qrel Validation Errors", ""])
        lines.extend(f"- {error}" for error in errors)
    if missing_files:
        lines.extend(["", "## Missing Template Files", ""])
        lines.extend(f"- `{display_path(path)}`" for path in missing_files)

    lines.extend(
        [
            "",
            "## Use Notes",
            "",
            "- This fixture turns the missing full-matrix work into a concrete handoff pack.",
            "- Real submissions must replace `.jsonl.template` files with `.jsonl` run files.",
            "- The submitted bundle still needs validation, provenance, scale, and promotion gates.",
            "- Do not include raw queries, source names, URLs, answers, or evidence text in run files.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--qrels", type=Path, default=ROOT / "fixtures" / "surface_qrels.jsonl")
    parser.add_argument("--matrix", type=Path, default=ROOT / "docs" / "system_matrix.json")
    parser.add_argument("--pack-dir", type=Path, default=ROOT / "fixtures" / "system_matrix_submission_template")
    parser.add_argument("--out", type=Path, default=ROOT / "reports" / "system_matrix_submission_pack_fixture.md")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    required = required_rows(args.matrix)
    qids, errors = load_qids(args.qrels)
    if not args.check:
        write_pack(pack_dir=args.pack_dir, qrels_path=args.qrels, matrix_path=args.matrix, required=required, qids=qids)
    report = render_report(qrels_path=args.qrels, matrix_path=args.matrix, pack_dir=args.pack_dir)
    if args.check:
        current = args.out.read_text(encoding="utf-8") if args.out.exists() else ""
        if current != report:
            print("system matrix submission pack report is stale; run scripts/build_system_matrix_submission_pack.py")
            sys.exit(1)
        if errors:
            print("system matrix submission pack qrels are invalid")
            sys.exit(1)
        print("system matrix submission pack report is current")
        return
    args.out.write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
