#!/usr/bin/env python3
"""Scan the public repo for private-source leakage indicators."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import NamedTuple


ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "dist", "build"}
SKIP_SUFFIXES = {".pyc", ".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip", ".gz", ".tgz"}


class Rule(NamedTuple):
    rule_id: str
    pattern: re.Pattern[str]


def hx(value: str) -> str:
    return bytes.fromhex(value).decode("utf-8")


def literal_rule(rule_id: str, value: str, *, flags: int = re.IGNORECASE) -> Rule:
    return Rule(rule_id, re.compile(re.escape(value), flags))


def regex_rule(rule_id: str, value: str, *, flags: int = re.IGNORECASE) -> Rule:
    return Rule(rule_id, re.compile(value, flags))


def rules() -> list[Rule]:
    # Hex and unicode escapes keep sensitive source names out of this public file
    # while still allowing CI to reject accidental plaintext leaks.
    literals = {
        "source_name_en_1": "4b616b616f",  # redacted source family
        "source_name_en_2": "416861",
        "source_name_en_3": "53616d73756e67",
        "source_name_en_4": "426c696e64",
        "source_name_en_5": "436c69656e",
        "source_name_en_6": "4e61766572",
        "source_name_en_7": "50706f6d707075",
        "source_name_en_8": "4e61746550616e6e",
        "source_name_en_9": "4443496e73696465",
        "source_name_ko_1": "ecb9b4ecb9b4ec98a4",
        "source_name_ko_2": "ec9584ed9598",
        "source_name_ko_3": "ec82bcec84b1",
    }
    source_prefixes = {
        "source_qid_prefix_1": "626c696e645f",
        "source_qid_prefix_2": "6168615f",
        "source_qid_prefix_3": "6463696e736964655f",
        "source_qid_prefix_4": "70706f6d7070755f",
        "source_qid_prefix_5": "636c69656e5f",
        "source_qid_prefix_6": "6e61746570616e6e5f",
    }
    out = [literal_rule(rule_id, hx(value)) for rule_id, value in literals.items()]
    out.extend(literal_rule(rule_id, hx(value)) for rule_id, value in source_prefixes.items())
    out.extend(
        [
            regex_rule("phone_number_kr", r"\b010[-\s]?\d{4}[-\s]?\d{4}\b", flags=0),
            regex_rule("chat_system_join", r"\ub2d8\uc774\s+\ub4e4\uc5b4\uc654\uc2b5\ub2c8\ub2e4", flags=0),
            regex_rule("chat_open_link", r"open\.\x6b\x61\x6b\x61\x6f", flags=re.IGNORECASE),
        ]
    )
    return out


def should_skip(path: Path) -> bool:
    parts = set(path.parts)
    if parts & SKIP_DIRS:
        return True
    return path.suffix.lower() in SKIP_SUFFIXES


def iter_files(root: Path):
    for path in root.rglob("*"):
        if path.is_file() and not should_skip(path.relative_to(root)):
            yield path


def scan_file(path: Path, scan_rules: list[Rule]) -> list[tuple[str, int]]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return []
    findings: list[tuple[str, int]] = []
    for lineno, line in enumerate(text.splitlines(), 1):
        for rule in scan_rules:
            if rule.pattern.search(line):
                findings.append((rule.rule_id, lineno))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()

    scan_rules = rules()
    failures: list[tuple[Path, str, int]] = []
    for path in iter_files(args.root):
        for rule_id, lineno in scan_file(path, scan_rules):
            failures.append((path.relative_to(args.root), rule_id, lineno))

    if failures:
        print("public-safety scan failed:")
        for path, rule_id, lineno in failures:
            print(f"- {path}:{lineno} {rule_id}")
        return 1
    print("public-safety scan passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
