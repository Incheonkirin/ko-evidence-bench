#!/usr/bin/env python3
"""Validate the public probe package and privacy-screen its text fields."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ko_evidence_bench.schemas import ROUTE_LABELS, validate_qrel  # noqa: E402
from scripts.check_public_safety import rules as public_safety_rules  # noqa: E402

PROVENANCE = "synthetic_public_fixture"
NGRAM_SIZE = 24


@dataclass(frozen=True)
class ProbePrivacyResult:
    query_rows: int
    qrel_rows: int
    evidence_rows: int
    intent_count: int
    surface_count: int
    route_count: int
    text_fields_scanned: int
    reference_files: int
    max_reference_overlap: int
    failures: tuple[str, ...]


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for lineno, line in enumerate(handle, 1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{lineno} invalid JSON: {exc}") from exc
            if not isinstance(record, dict):
                raise ValueError(f"{path}:{lineno} must be a JSON object")
            rows.append(record)
    return rows


def require_keys(record: dict[str, Any], keys: set[str], *, label: str) -> list[str]:
    missing = keys - record.keys()
    return [f"{label} missing keys for {record.get('qid', record.get('evidence_id', '<unknown>'))}: {sorted(missing)}"] if missing else []


def string_values(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from string_values(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from string_values(item)


def normalize_text(text: str) -> str:
    return re.sub(r"[^0-9a-zA-Z가-힣]", "", text.lower())


def ngrams(text: str, size: int = NGRAM_SIZE) -> set[str]:
    normalized = normalize_text(text)
    if len(normalized) < size:
        return set()
    return {normalized[i : i + size] for i in range(len(normalized) - size + 1)}


def load_reference_ngrams(paths: list[Path]) -> tuple[set[str], int]:
    out: set[str] = set()
    files = 0
    for path in paths:
        if not path.exists():
            raise FileNotFoundError(path)
        files += 1
        out.update(ngrams(path.read_text(encoding="utf-8")))
    return out, files


def pii_failures(label: str, text: str) -> list[str]:
    checks = {
        "email": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
        "url": re.compile(r"https?://|www\.", re.IGNORECASE),
        "phone": re.compile(r"\b010[-\s]?\d{4}[-\s]?\d{4}\b"),
        "resident_id_like": re.compile(r"\b\d{6}-[1-4]\d{6}\b"),
        "long_digit_sequence": re.compile(r"\d{8,}"),
    }
    failures: list[str] = []
    for name, pattern in checks.items():
        if pattern.search(text):
            failures.append(f"{label} contains {name}")
    for rule in public_safety_rules():
        if rule.pattern.search(text):
            failures.append(f"{label} contains private-source indicator {rule.rule_id}")
    return failures


def validate_probe_package(probe_dir: Path, reference_paths: list[Path]) -> ProbePrivacyResult:
    queries = read_jsonl(probe_dir / "queries.jsonl")
    qrels = read_jsonl(probe_dir / "qrels.jsonl")
    evidence = read_jsonl(probe_dir / "evidence.jsonl")
    reference_ngrams, reference_files = load_reference_ngrams(reference_paths)

    failures: list[str] = []
    query_required = {
        "qid",
        "query",
        "intent_family",
        "intent_id",
        "surface_form",
        "trap_classes",
        "source_substrate",
        "provenance",
    }
    qrel_required = {
        "qid",
        "intent_family",
        "intent_id",
        "surface_form",
        "trap_classes",
        "route_gold",
        "allowed_source_tiers",
        "should_abstain",
        "sufficient_evidence_ids",
        "provenance",
    }
    evidence_required = {"evidence_id", "source_tier", "title", "text", "provenance"}

    qids: list[str] = []
    qrel_qids: list[str] = []
    evidence_ids: list[str] = []
    text_fields_scanned = 0
    max_reference_overlap = 0

    for record in queries:
        failures.extend(require_keys(record, query_required, label="query"))
        qids.append(str(record.get("qid", "")))
        if record.get("provenance") != PROVENANCE:
            failures.append(f"query {record.get('qid')} provenance must be {PROVENANCE}")
        if not isinstance(record.get("trap_classes"), list):
            failures.append(f"query {record.get('qid')} trap_classes must be a list")

    for record in qrels:
        failures.extend(require_keys(record, qrel_required, label="qrel"))
        qrel_qids.append(str(record.get("qid", "")))
        try:
            validate_qrel(record)
        except ValueError as exc:
            failures.append(f"qrel {record.get('qid')} invalid: {exc}")
        if record.get("provenance") != PROVENANCE:
            failures.append(f"qrel {record.get('qid')} provenance must be {PROVENANCE}")
        if not isinstance(record.get("trap_classes"), list):
            failures.append(f"qrel {record.get('qid')} trap_classes must be a list")

    for record in evidence:
        failures.extend(require_keys(record, evidence_required, label="evidence"))
        evidence_id = str(record.get("evidence_id", ""))
        evidence_ids.append(evidence_id)
        if record.get("source_tier") not in ROUTE_LABELS:
            failures.append(f"evidence {evidence_id} has unknown source_tier: {record.get('source_tier')}")
        if record.get("provenance") != PROVENANCE:
            failures.append(f"evidence {evidence_id} provenance must be {PROVENANCE}")

    for label, values in [
        ("query qid", qids),
        ("qrel qid", qrel_qids),
        ("evidence id", evidence_ids),
    ]:
        duplicates = sorted(item for item, count in Counter(values).items() if count > 1)
        if duplicates:
            failures.append(f"duplicate {label}: {duplicates}")

    if set(qids) != set(qrel_qids):
        failures.append(f"query/qrel qid mismatch: query_only={sorted(set(qids)-set(qrel_qids))}, qrel_only={sorted(set(qrel_qids)-set(qids))}")

    evidence_set = set(evidence_ids)
    for record in qrels:
        for evidence_id in record.get("sufficient_evidence_ids", []):
            if evidence_id not in evidence_set:
                failures.append(f"qrel {record.get('qid')} references missing evidence id {evidence_id}")

    all_records = [("query", row) for row in queries] + [("qrel", row) for row in qrels] + [("evidence", row) for row in evidence]
    for kind, record in all_records:
        stable_id = record.get("qid", record.get("evidence_id", "<unknown>"))
        for text in string_values(record):
            text_fields_scanned += 1
            label = f"{kind} {stable_id}"
            failures.extend(pii_failures(label, text))
            overlap = len(ngrams(text) & reference_ngrams)
            max_reference_overlap = max(max_reference_overlap, overlap)
            if overlap:
                failures.append(f"{label} has long n-gram overlap with reference material")

    intent_count = len({record.get("intent_id") for record in queries})
    surface_count = len({record.get("surface_form") for record in queries})
    route_count = len({record.get("route_gold") for record in qrels})

    return ProbePrivacyResult(
        query_rows=len(queries),
        qrel_rows=len(qrels),
        evidence_rows=len(evidence),
        intent_count=intent_count,
        surface_count=surface_count,
        route_count=route_count,
        text_fields_scanned=text_fields_scanned,
        reference_files=reference_files,
        max_reference_overlap=max_reference_overlap,
        failures=tuple(failures),
    )


def display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def render_report(result: ProbePrivacyResult, probe_dir: Path) -> str:
    status = "PASS" if not result.failures else "FAIL"
    lines = [
        "# Probe Privacy Report",
        "",
        f"Status: **{status}**.",
        "",
        "This report validates the public synthetic probe package before it is used",
        "as a released evaluation instrument. It checks schema joins, synthetic",
        "provenance, common PII patterns, private-source indicators, and long",
        "n-gram overlap against configured reference material.",
        "",
        "## Inputs",
        "",
        f"- probe dir: `{display_path(probe_dir)}`",
        f"- query rows: {result.query_rows}",
        f"- qrel rows: {result.qrel_rows}",
        f"- evidence rows: {result.evidence_rows}",
        f"- reference files: {result.reference_files}",
        "",
        "## Coverage",
        "",
        "| item | value |",
        "|---|---:|",
        f"| intents | {result.intent_count} |",
        f"| surface forms | {result.surface_count} |",
        f"| source routes | {result.route_count} |",
        f"| text fields scanned | {result.text_fields_scanned} |",
        f"| max reference n-gram overlap | {result.max_reference_overlap} |",
        "",
        "## Failures",
        "",
    ]
    if result.failures:
        lines.extend(f"- {failure}" for failure in result.failures)
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Use Notes",
            "",
            "- `PASS` means the public probe package is safe to commit under the",
            "  repository's synthetic-fixture policy.",
            "- This does not prove the private-lab benchmark is human-gold.",
            "- Private runs should pass additional reference files from raw private",
            "  sources that remain outside this repository.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--probe-dir", type=Path, default=ROOT / "probes" / "ko_evidence_probe_v0")
    parser.add_argument(
        "--reference",
        type=Path,
        action="append",
        default=[ROOT / "fixtures" / "privacy_reference" / "source_snippets.txt"],
    )
    parser.add_argument("--out", type=Path, default=ROOT / "reports" / "probe_privacy_report.md")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    result = validate_probe_package(args.probe_dir, args.reference)
    report = render_report(result, args.probe_dir)
    if args.check:
        current = args.out.read_text(encoding="utf-8") if args.out.exists() else ""
        if current != report:
            print("probe privacy report is stale; run scripts/check_probe_privacy.py")
            return 1
        if result.failures:
            print("probe privacy report has failures")
            return 1
        print("probe privacy report is current")
        return 0

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(report, encoding="utf-8")
    print(report)
    return 1 if result.failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
