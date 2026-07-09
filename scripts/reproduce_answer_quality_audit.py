#!/usr/bin/env python3
"""Reproduce a qid-only answer-quality audit rehearsal on fixtures."""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ko_evidence_bench.answer_audit import (  # noqa: E402
    answer_quality_summary,
    promote_answer_audit_rows,
    validate_answer_audit_rows,
)
from ko_evidence_bench.metrics import load_jsonl  # noqa: E402


FIXTURE = ROOT / "fixtures" / "answer_audit" / "answer_audit_seed.jsonl"


def pct(num: int | float, den: int | float) -> str:
    return f"{(float(num) / float(den) * 100) if den else 0.0:.1f}%"


def counter_table(title: str, counts: Counter[str]) -> list[str]:
    total = sum(counts.values())
    lines = [
        f"## {title}",
        "",
        "| value | count | share |",
        "|---|---:|---:|",
    ]
    for value, count in counts.most_common():
        lines.append(f"| `{value}` | {count} | {pct(count, total)} |")
    if not counts:
        lines.append("| `<none>` | 0 | 0.0% |")
    lines.append("")
    return lines


def nested_table(title: str, rows: dict[str, Counter[str]]) -> list[str]:
    lines = [
        f"## {title}",
        "",
        "| slice | sufficient | partial | insufficient | correct_abstain | unsafe_answer | total | task_success |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    labels = ["sufficient", "partial", "insufficient", "correct_abstain", "unsafe_answer"]
    for key in sorted(rows):
        counts = rows[key]
        total = sum(counts.values())
        task_success = counts["sufficient"] + counts["correct_abstain"]
        values = [str(counts[label]) for label in labels]
        lines.append(
            f"| `{key}` | {' | '.join(values)} | {total} | {pct(task_success, total)} |"
        )
    if not rows:
        lines.append("| `<none>` | 0 | 0 | 0 | 0 | 0 | 0 | 0.0% |")
    lines.append("")
    return lines


def render_report(rows: list[dict], *, fixture_path: Path) -> str:
    validation = validate_answer_audit_rows(
        rows,
        label_prefix="adjudicated",
        require_complete=True,
        require_qid_only=True,
    )
    promoted = promote_answer_audit_rows(rows, label_prefix="adjudicated")
    summary = answer_quality_summary(rows, label_prefix="adjudicated")
    completed = int(summary["completed"])
    task_success = int(summary["task_success"])
    unsafe = int(summary["unsafe_answer"])

    lines = [
        "# Answer Quality Audit Fixture",
        "",
        "Status: **PASS synthetic answer-quality audit rehearsal**."
        if validation["error_count"] == 0
        else "Status: **FAIL synthetic answer-quality audit rehearsal**.",
        "",
        "This qid-only fixture rehearses answer-quality and evidence-sufficiency",
        "labels after retrieval. It is not human-gold answer-quality evidence and",
        "not a final benchmark claim.",
        "",
        "It exists to keep retrieval hit metrics separate from the question a",
        "reviewer actually cares about: whether the system had enough cited evidence",
        "to answer, partially answer, abstain correctly, or avoid an unsafe answer.",
        "",
        "## Gate Summary",
        "",
        "| item | value |",
        "|---|---:|",
        f"| fixture | `{fixture_path.relative_to(ROOT)}` |",
        f"| rows | {validation['n']} |",
        f"| completed labels | {validation['completed']} |",
        f"| validation errors | {validation['error_count']} |",
        f"| promoted rows | {len(promoted)} |",
        f"| task success count | {task_success} |",
        f"| task success rate | {pct(task_success, completed)} |",
        f"| unsafe answer count | {unsafe} |",
        f"| unsafe answer rate | {pct(unsafe, completed)} |",
        "",
    ]
    lines.extend(counter_table("Answer Label Distribution", validation["label_counts"]))
    lines.extend(counter_table("Confidence Distribution", validation["confidence_counts"]))
    lines.extend(nested_table("By System", summary["by_system"]))
    lines.extend(nested_table("By Surface Form", summary["by_surface"]))
    lines.extend(nested_table("By Intent Family", summary["by_intent"]))
    lines.extend(
        [
            "## Use Notes",
            "",
            "- This report is a fixture-only rehearsal for the private audit path.",
            "- Public rows carry qids, system ids, evidence ids, source tiers, and labels only.",
            "- Raw questions, answer text, evidence text, source names, urls, and user identifiers stay outside the public repo.",
            "- Route labels decide which source tier is required; answer-quality labels decide whether the returned evidence was enough to answer.",
            "",
        ]
    )
    if validation["row_errors"]:
        lines.extend(["## Validation Errors", ""])
        for error in validation["row_errors"]:
            lines.append(f"- `{error['audit_id']}`: {', '.join(error['errors'])}")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit", type=Path, default=FIXTURE)
    parser.add_argument("--out", type=Path, default=ROOT / "reports" / "answer_quality_audit_fixture.md")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    rows = load_jsonl(args.audit)
    report = render_report(rows, fixture_path=args.audit)
    if args.check:
        current = args.out.read_text(encoding="utf-8") if args.out.exists() else ""
        if current != report:
            print("answer quality audit report is stale; run scripts/reproduce_answer_quality_audit.py")
            return 1
        print("answer quality audit report is current")
        return 0

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(report, encoding="utf-8")
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
