#!/usr/bin/env python3
"""Scan the public repo for private-source leakage indicators."""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path
from typing import NamedTuple, Union


ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "dist", "build"}
SKIP_SUFFIXES = {".pyc", ".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip", ".gz", ".tgz"}


class Rule(NamedTuple):
    rule_id: str
    pattern: re.Pattern[str]


class HashedTokenRule(NamedTuple):
    # sha256(lowercased candidate) -> rule_id. Hashing keeps the names out of
    # the current working tree, nothing more: names drawn from a small
    # candidate space remain guessable by hashing candidate strings, and
    # earlier commits retain the previous encoding. Treat this as
    # plaintext-avoidance, not secrecy. Moving the list out of the public
    # repository entirely is tracked as a separate decision.
    digests: dict[str, str]


AnyRule = Union[Rule, HashedTokenRule]

TOKEN_RE = re.compile(r"[A-Za-z0-9_]+|[가-힣]+")
MAX_PREFIX_LEN = 12


def regex_rule(rule_id: str, value: str, *, flags: int = re.IGNORECASE) -> Rule:
    return Rule(rule_id, re.compile(value, flags))


def hashed_token_rule() -> HashedTokenRule:
    return HashedTokenRule(
        {
            "30cd4a85fc09f6959b4c7807b4120c3e55e08204cc82c913e3cc7687b500eec2": "source_name_en_1",
            "0ca758e42f6979815a567dfb58e968579596915fe9f7c106f3300be64568bd4f": "source_name_en_2",
            "968e2d5b08687bf42997461cbdef6c844eabbf04f440cee888c95b864c2a4bcc": "source_name_en_3",
            "e5b84c89f624a40cdfdc0c6da3c9f0b47ce587edae0117b8c8b7c0a9523db5c4": "source_name_en_4",
            "b6483bf30eb418ea8c159603501f64a5ca9832dcfe53a05392e42daef2207c19": "source_name_en_5",
            "6d5510a695d0a6146ab0222b6326f61aea63d68e3698402c2f23cbc40c9fc47d": "source_name_en_6",
            "d65dc7531c5334f8680dca56d0115960d8aa31ed8b2f60fcb75f2f2d8b3825e9": "source_name_en_7",
            "28117b9c82fd4e661a41f644ed41af1bdcec50c1b5f3ae5d5816f21c204ce243": "source_name_en_8",
            "807189d6435ac1a166cb34c97a386a8b7ec7924e82540d56a4ba9e088c2a745b": "source_name_en_9",
            "bfd1d1a16a354b641ce4e0cc06a3383403b6b4dc3dbdef4073e8669586e88559": "source_name_ko_1",
            "3513ac628d0fe613d8038c952cf4a4ac1f1f7faa4934b23aded6ae6262bae909": "source_name_ko_2",
            "6e89adf712dc8f280c381c326c2ef998e082f08042efb27a085edffb215cfb5e": "source_name_ko_3",
            "b03c796887483053f29ec9d9304bfc1589eb8dd8d39b5ae2d5484693667aa088": "source_qid_prefix_1",
            "cf3b0f4908981b36ccd640361fcd96bb29b663a3f5e1ed924568cdde0ce540ea": "source_qid_prefix_2",
            "5aff2590c9a4ffba11dbd1a8e3d5e228bfa7bd16eed86a700a61ec6fbcc6b398": "source_qid_prefix_3",
            "339b1ce74f1e45b6cf6566db971a297d0a6e6c9807ed2af7f92a4fc36461830d": "source_qid_prefix_4",
            "704fa5d0b2b5ef953b455d6c1d857852cfeed5034182bf7795219fead5eff1e7": "source_qid_prefix_5",
            "63d51f33333cbe7e464393174f59b9d5663bca37b9f3a6c85bcad8ea8d045414": "source_qid_prefix_6",
        }
    )


def rules() -> list[AnyRule]:
    return [
        hashed_token_rule(),
        regex_rule("phone_number_kr", r"\b010[-\s]?\d{4}[-\s]?\d{4}\b", flags=0),
        regex_rule("chat_system_join", r"님이\s+들어왔습니다", flags=0),
        # The old chat_open_link rule is covered by the hashed token scan: the
        # host token of an open-chat URL hashes to a blocked source name.
    ]


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _hashed_hits(line: str, rule: HashedTokenRule) -> list[str]:
    hits: list[str] = []
    for token in TOKEN_RE.findall(line):
        lowered = token.lower()
        # Exact token plus token prefixes (2..MAX_PREFIX_LEN) catch `Name`,
        # `Name_suffix`, and `NameSuffix` shapes. Mid-token embeddings are not
        # detected; the old substring scan caught those, but it required the
        # plaintext (hex-reversible) names in this file.
        candidates = {lowered}
        upper = min(len(lowered), MAX_PREFIX_LEN)
        for size in range(2, upper + 1):
            candidates.add(lowered[:size])
        for candidate in candidates:
            rule_id = rule.digests.get(_digest(candidate))
            if rule_id is not None:
                hits.append(rule_id)
    return hits


def should_skip(path: Path) -> bool:
    parts = set(path.parts)
    if parts & SKIP_DIRS:
        return True
    return path.suffix.lower() in SKIP_SUFFIXES


def iter_files(root: Path):
    for path in root.rglob("*"):
        if path.is_file() and not should_skip(path.relative_to(root)):
            yield path


def text_hits(text: str, scan_rules: list[AnyRule]) -> list[str]:
    hits: list[str] = []
    for rule in scan_rules:
        if isinstance(rule, HashedTokenRule):
            hits.extend(_hashed_hits(text, rule))
        elif rule.pattern.search(text):
            hits.append(rule.rule_id)
    return hits


def scan_file(path: Path, scan_rules: list[AnyRule]) -> list[tuple[str, int]]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return []
    findings: list[tuple[str, int]] = []
    for lineno, line in enumerate(text.splitlines(), 1):
        for rule_id in text_hits(line, scan_rules):
            findings.append((rule_id, lineno))
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
