#!/usr/bin/env python3
"""Profile private or fixture query substrates without writing raw text."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ko_evidence_bench.substrate_profile import TextRow, render_profile_report  # noqa: E402


def nested_get(row: dict[str, Any], path: str) -> Any:
    value: Any = row
    for part in path.split("."):
        if not isinstance(value, dict):
            return None
        value = value.get(part)
    return value


def combine_fields(row: dict[str, Any], fields: list[str]) -> str:
    values: list[str] = []
    for field in fields:
        value = nested_get(row, field)
        if value not in (None, ""):
            values.append(str(value))
    return "\n".join(values)


def load_json(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return [row for row in data if isinstance(row, dict)]
    if isinstance(data, dict):
        for value in data.values():
            if isinstance(value, list):
                return [row for row in value if isinstance(row, dict)]
    raise ValueError(f"could not find list rows in {path}")


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.strip():
                row = json.loads(line)
                if isinstance(row, dict):
                    rows.append(row)
    return rows


def load_csv(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8-sig", errors="replace", newline="") as f:
        return list(csv.DictReader(f))


def load_rows(path: Path, fmt: str) -> list[dict[str, Any]]:
    if fmt == "auto":
        suffix = path.suffix.lower()
        if suffix == ".jsonl":
            fmt = "jsonl"
        elif suffix == ".json":
            fmt = "json"
        elif suffix == ".csv":
            fmt = "csv"
        else:
            raise ValueError(f"cannot infer format for {path}")
    if fmt == "jsonl":
        return load_jsonl(path)
    if fmt == "json":
        return load_json(path)
    if fmt == "csv":
        return load_csv(path)
    raise ValueError(f"unknown format: {fmt}")


def parse_source(spec: str) -> tuple[str, Path, str, list[str]]:
    if ":" not in spec:
        raise ValueError("--source must be cohort:path:format:field[,field...]")
    cohort, rest = spec.split(":", 1)
    parts = rest.rsplit(":", 2)
    if len(parts) != 3:
        raise ValueError("--source must be cohort:path:format:field[,field...]")
    path, fmt, fields = parts
    if not cohort:
        raise ValueError("cohort name is required")
    field_list = [field.strip() for field in fields.split(",") if field.strip()]
    if not field_list:
        raise ValueError("at least one text field is required")
    return cohort, Path(path), fmt, field_list


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source",
        action="append",
        required=True,
        help="cohort:path:format:field[,field...]",
    )
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--title", default="Query Substrate Profile")
    parser.add_argument("--label-status", default="aggregate profile")
    parser.add_argument("--min-chars", type=int, default=2)
    parser.add_argument("--max-rows-per-source", type=int)
    args = parser.parse_args()

    text_rows: list[TextRow] = []
    for source in args.source:
        cohort, path, fmt, fields = parse_source(source)
        rows = load_rows(path, fmt)
        if args.max_rows_per_source is not None:
            rows = rows[: args.max_rows_per_source]
        for row in rows:
            text_rows.append(TextRow(cohort=cohort, text=combine_fields(row, fields)))

    report = render_profile_report(
        text_rows,
        title=args.title,
        label_status=args.label_status,
        min_chars=args.min_chars,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
