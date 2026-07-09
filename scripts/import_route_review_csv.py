#!/usr/bin/env python3
"""Import reviewer CSV labels back into a private route-audit pack."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ko_evidence_bench.route_audit import reviewer_template, validate_audit_rows  # noqa: E402


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


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def parse_bool(value: str | None) -> bool | None:
    text = (value or "").strip().lower()
    if not text:
        return None
    if text in {"true", "t", "1", "yes", "y"}:
        return True
    if text in {"false", "f", "0", "no", "n"}:
        return False
    return None


def parse_list(value: str | None) -> list[str]:
    text = (value or "").strip()
    if not text:
        return []
    return [part.strip() for part in re.split(r"[;|,]", text) if part.strip()]


def payload_from_csv(row: dict[str, str]) -> dict[str, Any]:
    return {
        "route_gold": (row.get("route_gold") or "").strip(),
        "allowed_source_tiers": parse_list(row.get("allowed_source_tiers")),
        "should_abstain": parse_bool(row.get("should_abstain")),
        "confidence": (row.get("confidence") or "").strip(),
        "rationale_code": (row.get("rationale_code") or "").strip(),
        "labeler": (row.get("labeler") or "").strip(),
        "notes": (row.get("notes") or "").strip(),
    }


def index_csv(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for row in rows:
        key = (row.get("audit_id") or "").strip()
        if key:
            out[key] = row
    return out


def is_empty_payload(payload: dict[str, Any]) -> bool:
    return not any(
        payload.get(key)
        for key in ("route_gold", "allowed_source_tiers", "should_abstain", "confidence", "rationale_code", "labeler", "notes")
    )


def merge_labels(
    audit_rows: list[dict[str, Any]],
    csv_rows: list[dict[str, str]],
    *,
    target_prefix: str,
    skip_empty: bool,
) -> tuple[list[dict[str, Any]], int]:
    by_audit_id = index_csv(csv_rows)
    updated = 0
    merged: list[dict[str, Any]] = []
    for row in audit_rows:
        out = dict(row)
        csv_row = by_audit_id.get(str(row.get("audit_id") or ""))
        if csv_row:
            payload = payload_from_csv(csv_row)
            if not (skip_empty and is_empty_payload(payload)):
                if target_prefix == "human":
                    out.update(
                        {
                            "human_route_gold": payload["route_gold"],
                            "human_allowed_source_tiers": payload["allowed_source_tiers"],
                            "human_should_abstain": payload["should_abstain"],
                            "human_confidence": payload["confidence"],
                            "human_rationale_code": payload["rationale_code"],
                            "human_labeler": payload["labeler"],
                            "human_notes": payload["notes"],
                        }
                    )
                else:
                    out[target_prefix] = {**reviewer_template(), **payload}
                updated += 1
        merged.append(out)
    return merged, updated


def pct(value: float) -> str:
    return f"{100 * value:.1f}%"


def table(title: str, counts: Counter[str]) -> list[str]:
    total = sum(counts.values())
    lines = [f"## {title}", "", "| value | count | share |", "|---|---:|---:|"]
    for key, value in counts.most_common():
        share = value / total if total else 0.0
        lines.append(f"| `{key}` | {value} | {pct(share)} |")
    return lines


def render_report(
    *,
    audit_rows: list[dict[str, Any]],
    csv_rows: list[dict[str, str]],
    merged_rows: list[dict[str, Any]],
    updated: int,
    target_prefix: str,
    out_path: Path,
) -> str:
    validation = validate_audit_rows(merged_rows, label_prefix=target_prefix, require_complete=False)
    lines = [
        "# Private Route Review CSV Import Summary",
        "",
        "This report summarizes a private reviewer CSV import. It contains",
        "aggregate counts only. It does not include qids, raw queries, context, or",
        "reviewer notes.",
        "",
        f"- audit rows: {len(audit_rows)}",
        f"- csv rows: {len(csv_rows)}",
        f"- updated rows: {updated}",
        f"- target prefix: `{target_prefix}`",
        f"- private audit output: `{out_path.name}`",
        f"- completed labels after import: {validation['completed']}",
        f"- validation rows with errors after import: {validation['error_count']}",
        "",
    ]
    lines.extend(table("Imported Route Distribution", validation["route_counts"]))
    lines.append("")
    lines.extend(table("Imported Confidence Distribution", validation["confidence_counts"]))
    lines.extend(
        [
            "",
            "## Use Notes",
            "",
            "- Run `validate_route_audit.py --require-complete` before promotion.",
            "- Keep the updated private audit pack outside the public repository.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--target-prefix", default="reviewer_a")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--report-out", type=Path)
    parser.add_argument("--skip-empty", action="store_true")
    args = parser.parse_args()

    audit_rows = load_jsonl(args.audit)
    csv_rows = load_csv(args.csv)
    merged_rows, updated = merge_labels(
        audit_rows,
        csv_rows,
        target_prefix=args.target_prefix,
        skip_empty=args.skip_empty,
    )
    write_jsonl(args.out, merged_rows)
    report = render_report(
        audit_rows=audit_rows,
        csv_rows=csv_rows,
        merged_rows=merged_rows,
        updated=updated,
        target_prefix=args.target_prefix,
        out_path=args.out,
    )
    if args.report_out:
        args.report_out.parent.mkdir(parents=True, exist_ok=True)
        args.report_out.write_text(report, encoding="utf-8")
    else:
        print(report, end="")


if __name__ == "__main__":
    main()
