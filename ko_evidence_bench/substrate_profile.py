"""Aggregate query-substrate profiles without exposing raw text."""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from statistics import mean, median


QUESTION_RE = re.compile(r"(\?|나요|까요|인가요|되나요|될까요|맞나요|뭔가요|어떻게|언제|왜|얼마나|가능)")
NUMERIC_RE = re.compile(r"(\d+\s*(년|개월|월|일|세|만원|억|회|종|대|급|%)|[일이삼사오육칠팔구십한두세네]\s*(년|개월|달|세|번|회))")
NEGATION_RE = re.compile(r"(비급여|무배당|부담보|미지급|부지급|면책|제외|불가|안\s*\S+|못\s*\S+)")
BUNDLE_RE = re.compile(r"(암\s*/?\s*뇌|뇌\s*/?\s*심|암뇌심|진단비|수술비|치료비)")
UNDERWRITING_RE = re.compile(r"(고지|부담보|인수|심사|가입|청약|병력|조건부)")
REFUND_RE = re.compile(r"(환급|해지|해약|만기|보험료|감액완납|납입)")
CLAIMS_RE = re.compile(r"(청구|서류|접수|지급|심사|보험금)")
DISPUTE_RE = re.compile(r"(민원|분쟁|거절|부지급|지급거절|소송|감독기관)")
ABBREVIATION_RE = re.compile(r"(실비|실손|암뇌심|뇌심|암주치|태아보험|유병자|간편고지)")
FORMAL_RE = re.compile(r"(약관|특약|계약|보장|담보|지급사유|보장개시|계약 전 알릴 의무)")


FEATURES = [
    ("question_like", QUESTION_RE),
    ("numeric_constraint", NUMERIC_RE),
    ("negation_or_exclusion", NEGATION_RE),
    ("bundled_coverage", BUNDLE_RE),
    ("underwriting", UNDERWRITING_RE),
    ("refund_termination", REFUND_RE),
    ("claims_process", CLAIMS_RE),
    ("dispute_or_complaint", DISPUTE_RE),
    ("abbrev_or_colloquial", ABBREVIATION_RE),
    ("formal_register", FORMAL_RE),
]


@dataclass(frozen=True)
class TextRow:
    cohort: str
    text: str


def normalize_text(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _safe_div(num: int | float, den: int | float) -> float:
    return float(num) / float(den) if den else 0.0


def text_features(text: str) -> dict[str, bool]:
    clean = normalize_text(text)
    features = {name: bool(regex.search(clean)) for name, regex in FEATURES}
    features["short_message"] = len(clean) <= 40
    features["long_context"] = len(clean) >= 200
    features["messenger_style"] = len(clean) <= 80 and features["question_like"]
    return features


def profile_rows(rows: list[TextRow], *, min_chars: int = 2) -> dict[str, dict[str, object]]:
    grouped: dict[str, list[str]] = {}
    input_counts: Counter[str] = Counter()
    for row in rows:
        input_counts[row.cohort] += 1
        text = normalize_text(row.text)
        if len(text) < min_chars:
            continue
        grouped.setdefault(row.cohort, []).append(text)

    profiles: dict[str, dict[str, object]] = {}
    for cohort in sorted(input_counts):
        texts = grouped.get(cohort, [])
        lengths = [len(text) for text in texts]
        feature_counts: Counter[str] = Counter()
        for text in texts:
            for key, present in text_features(text).items():
                if present:
                    feature_counts[key] += 1

        profiles[cohort] = {
            "input_rows": input_counts[cohort],
            "usable_rows": len(texts),
            "avg_chars": mean(lengths) if lengths else 0.0,
            "median_chars": median(lengths) if lengths else 0.0,
            "p90_chars": percentile(lengths, 0.9),
            "feature_counts": feature_counts,
        }
    return profiles


def percentile(values: list[int], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = min(len(ordered) - 1, max(0, int(round((len(ordered) - 1) * q))))
    return float(ordered[idx])


def pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def render_profile_report(
    rows: list[TextRow],
    *,
    title: str = "Query Substrate Profile",
    label_status: str = "aggregate profile",
    min_chars: int = 2,
) -> str:
    profiles = profile_rows(rows, min_chars=min_chars)
    total_input = sum(int(item["input_rows"]) for item in profiles.values())
    total_usable = sum(int(item["usable_rows"]) for item in profiles.values())

    lines = [
        f"# {title}",
        "",
        "This report compares query substrates using aggregate text-shape and",
        "intent-signal features only. It does not include qids, raw queries,",
        "conversation snippets, platform identifiers, usernames, URLs, or source",
        "file paths.",
        "",
        "The goal is to decide which real-query cohorts deserve separate stress",
        "slices in the retrieval benchmark, not to build a synonym dictionary.",
        "",
        "## Inputs",
        "",
        f"- input rows: {total_input}",
        f"- usable rows after length filtering: {total_usable}",
        f"- label status: {label_status}",
        f"- minimum characters: {min_chars}",
        "",
        "## Cohort Shape Summary",
        "",
        "| cohort | input rows | usable rows | usable share | avg chars | median chars | p90 chars | short messages | long contexts | question-like |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for cohort, profile in profiles.items():
        usable = int(profile["usable_rows"])
        input_rows = int(profile["input_rows"])
        features: Counter[str] = profile["feature_counts"]  # type: ignore[assignment]
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{cohort}`",
                    str(input_rows),
                    str(usable),
                    pct(_safe_div(usable, input_rows)),
                    f"{float(profile['avg_chars']):.1f}",
                    f"{float(profile['median_chars']):.1f}",
                    f"{float(profile['p90_chars']):.1f}",
                    pct(_safe_div(features["short_message"], usable)),
                    pct(_safe_div(features["long_context"], usable)),
                    pct(_safe_div(features["question_like"], usable)),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Retrieval Stress Signals",
            "",
            "| cohort | numeric constraints | negation/exclusion | bundled coverage | underwriting | refund/termination | claims process | dispute/complaint | colloquial/abbrev | formal register | messenger-style |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    stress_keys = [
        "numeric_constraint",
        "negation_or_exclusion",
        "bundled_coverage",
        "underwriting",
        "refund_termination",
        "claims_process",
        "dispute_or_complaint",
        "abbrev_or_colloquial",
        "formal_register",
        "messenger_style",
    ]
    for cohort, profile in profiles.items():
        usable = int(profile["usable_rows"])
        features: Counter[str] = profile["feature_counts"]  # type: ignore[assignment]
        values = [pct(_safe_div(features[key], usable)) for key in stress_keys]
        lines.append("| " + " | ".join([f"`{cohort}`", *values]) + " |")

    lines.extend(
        [
            "",
            "## Interpretation Guide",
            "",
            "- High `short messages` and `messenger-style` rates mean live-query stress",
            "  should include short, underspecified turns rather than only long posts.",
            "- High `long contexts` means the cohort is better treated as query",
            "  extraction plus retrieval, not a direct search-box query.",
            "- High `negation/exclusion`, `numeric constraints`, or `bundled coverage`",
            "  rates mark slices where surface normalization and source routing should",
            "  be evaluated separately from plain clause recall.",
            "- This report is a substrate diagnostic. It does not create labels and it",
            "  does not promote any private metric to a public benchmark claim.",
            "",
        ]
    )
    return "\n".join(lines)
