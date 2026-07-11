#!/usr/bin/env python3
"""Build the Korean retrieval correctness evidence summary and SVG figures."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape


ROOT = Path(__file__).resolve().parents[1]
CASE_DIR = ROOT / "case_studies" / "korean-retrieval-correctness"
OBSERVATIONS_PATH = CASE_DIR / "evidence" / "local-observations.json"
UPSTREAM_PATH = CASE_DIR / "evidence" / "upstream-contributions.json"
POLARITY_PATH = ROOT / "reports" / "private_polarity_stress_pilot.json"

COLORS = {
    "ink": "#202124",
    "muted": "#687076",
    "grid": "#D9DEE2",
    "safe": "#167D5A",
    "failure": "#C43D3D",
    "neutral": "#557A95",
    "light": "#F5F7F8",
}
FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Apple SD Gothic Neo', sans-serif"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def attr(value: Any) -> str:
    return escape(str(value), {'"': "&quot;"})


def text(
    x: float,
    y: float,
    value: str,
    *,
    size: int = 18,
    fill: str | None = None,
    weight: int = 400,
    anchor: str = "start",
) -> str:
    return (
        f'<text x="{x}" y="{y}" font-family="{attr(FONT)}" font-size="{size}" '
        f'font-weight="{weight}" fill="{fill or COLORS["ink"]}" '
        f'text-anchor="{anchor}">{escape(value)}</text>'
    )


def svg_document(width: int, height: int, title: str, description: str, body: str) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
  <title id="title">{escape(title)}</title>
  <desc id="desc">{escape(description)}</desc>
  <rect width="100%" height="100%" fill="white"/>
  {body}
</svg>
"""


def render_boundaries() -> str:
    width, height = 1200, 360
    steps = [
        ("Unicode", "text"),
        ("Character", "filter"),
        ("Korean", "tokenizer"),
        ("POS / stop", "filter"),
        ("Token", "graph"),
        ("Query", "builder"),
        ("Ranking", ""),
    ]
    failures = {
        2: "1  canonical form",
        3: "2  polarity",
        5: "3  position gaps",
    }
    box_width = 128
    gap = 36
    start_x = 44
    y = 145
    parts = [
        "<defs><marker id=\"arrow\" markerWidth=\"8\" markerHeight=\"8\" refX=\"7\" refY=\"4\" orient=\"auto\"><path d=\"M0,0 L8,4 L0,8 Z\" fill=\"#687076\"/></marker></defs>",
        text(width / 2, 48, "Three correctness failures happen before ranking", size=27, weight=700, anchor="middle"),
        text(width / 2, 82, "Each boundary must preserve the distinctions relevance depends on", size=17, fill=COLORS["muted"], anchor="middle"),
    ]
    for index, (line_one, line_two) in enumerate(steps):
        x = start_x + index * (box_width + gap)
        fill = "#EAF4EF" if index == len(steps) - 1 else COLORS["light"]
        parts.append(
            f'<rect x="{x}" y="{y}" width="{box_width}" height="76" rx="6" '
            f'fill="{fill}" stroke="{COLORS["grid"]}" stroke-width="2"/>'
        )
        parts.append(text(x + box_width / 2, y + 32, line_one, size=16, weight=700, anchor="middle"))
        if line_two:
            parts.append(text(x + box_width / 2, y + 55, line_two, size=16, weight=700, anchor="middle"))
        if index < len(steps) - 1:
            parts.append(
                f'<line x1="{x + box_width + 5}" y1="{y + 38}" '
                f'x2="{x + box_width + gap - 7}" y2="{y + 38}" '
                f'stroke="{COLORS["muted"]}" stroke-width="2" marker-end="url(#arrow)"/>'
            )
        if index in failures:
            center = x + box_width / 2
            parts.append(
                f'<path d="M {center - 8} {y + 94} L {center + 8} {y + 94} '
                f'L {center} {y + 108} Z" fill="{COLORS["failure"]}"/>'
            )
            parts.append(
                text(center, y + 137, failures[index], size=15, fill=COLORS["failure"], weight=600, anchor="middle")
            )
    return svg_document(
        width,
        height,
        "Three representation boundaries before ranking",
        "A Korean retrieval pipeline with failures at canonical-form, polarity, and token-position boundaries.",
        "\n  ".join(parts),
    )


def render_analyzer(observations: dict[str, Any]) -> str:
    width, height = 1100, 570
    runtime = observations["runtime"]
    cases = observations["analyzer_cases"]
    safe_ids = {"covered", "coverage", "hangul_nfc"}
    parts = [
        text(45, 52, "Observed analyzer outputs", size=28, weight=700),
        text(
            45,
            84,
            f"Elasticsearch {runtime['elasticsearch']} · Lucene {runtime['lucene']} · korean analyzer",
            size=17,
            fill=COLORS["muted"],
        ),
    ]
    for index, case in enumerate(cases):
        y = 145 + index * 67
        output = " / ".join(case["tokens"])
        if case["case_id"] == "hangul_nfd":
            output = "one NFD jamo-sequence token"
        color = COLORS["safe"] if case["case_id"] in safe_ids else COLORS["failure"]
        parts.append(text(60, y, case["input_label"], size=19, weight=700))
        parts.append(text(275, y, "→", size=21, fill=COLORS["muted"], anchor="middle"))
        parts.append(text(320, y, output, size=18, fill=color, weight=600))
        parts.append(
            f'<line x1="55" y1="{y + 24}" x2="1045" y2="{y + 24}" '
            f'stroke="{COLORS["grid"]}" stroke-width="1"/>'
        )
    return svg_document(
        width,
        height,
        "Observed Korean analyzer outputs",
        "Nori collapses two contrastive prefix pairs, and NFC and NFD forms receive different analysis.",
        "\n  ".join(parts),
    )


def render_phrase(observations: dict[str, Any]) -> str:
    width, height = 900, 560
    runtime = observations["runtime"]
    rows = observations["phrase_cases"]
    labels = [("match", ""), ("phrase", "slop=0"), ("phrase", "slop=1")]
    colors = [COLORS["neutral"], COLORS["failure"], COLORS["safe"]]
    chart_top = 170
    baseline = 455
    scale = 250
    bar_width = 145
    centers = [220, 450, 680]
    parts = [
        text(width / 2, 48, "Exact source phrase misses only in the zero-slop graph path", size=25, weight=700, anchor="middle"),
        text(
            width / 2,
            82,
            f"보험계약대출이율 · one-document fixture · Elasticsearch {runtime['elasticsearch']}",
            size=17,
            fill=COLORS["muted"],
            anchor="middle",
        ),
        f'<line x1="105" y1="{baseline}" x2="825" y2="{baseline}" stroke="{COLORS["grid"]}" stroke-width="2"/>',
        f'<line x1="105" y1="{baseline - scale}" x2="825" y2="{baseline - scale}" stroke="{COLORS["grid"]}" stroke-width="1"/>',
        text(90, baseline + 6, "0", size=16, fill=COLORS["muted"], anchor="end"),
        text(90, baseline - scale + 6, "1", size=16, fill=COLORS["muted"], anchor="end"),
    ]
    for index, row in enumerate(rows):
        value = int(row["hits"])
        center = centers[index]
        bar_height = value * scale
        if value:
            parts.append(
                f'<rect x="{center - bar_width / 2}" y="{baseline - bar_height}" '
                f'width="{bar_width}" height="{bar_height}" fill="{colors[index]}"/>'
            )
        else:
            parts.append(
                f'<line x1="{center - bar_width / 2}" y1="{baseline - 2}" '
                f'x2="{center + bar_width / 2}" y2="{baseline - 2}" '
                f'stroke="{colors[index]}" stroke-width="5"/>'
            )
        parts.append(text(center, baseline - bar_height - 18, str(value), size=22, weight=700, anchor="middle"))
        parts.append(text(center, baseline + 34, labels[index][0], size=18, fill=COLORS["muted"], anchor="middle"))
        if labels[index][1]:
            parts.append(text(center, baseline + 58, labels[index][1], size=18, fill=COLORS["muted"], anchor="middle"))
    return svg_document(
        width,
        height,
        "Exact phrase hit counts",
        "The same one-document fixture matches a bag-of-words query and a phrase query with slop one, but not a phrase query with zero slop.",
        "\n  ".join(parts),
    )


def render_polarity(polarity: dict[str, Any]) -> str:
    width, height = 1100, 620
    labels = {
        "bm25_analyzer_tokens": "Analyzer-token BM25",
        "bm25_lucene_idf_sensitivity": "Lucene-style BM25 arm",
        "dense_bge_m3": "BGE-M3 dense retrieval",
        "cross_encoder_bge_reranker_v2_m3": "BGE reranker",
    }
    left, right = 335, 1020
    chart_width = right - left
    top = 175
    row_gap = 92
    parts = [
        text(width / 2, 48, "Wrong-polarity preference remains a system-level failure", size=26, weight=700, anchor="middle"),
        text(
            width / 2,
            82,
            "444 counterfactual triples · 37 seed pairs · lower is better",
            size=17,
            fill=COLORS["muted"],
            anchor="middle",
        ),
    ]
    for percent in (0, 25, 50, 75, 100):
        x = left + chart_width * percent / 100
        parts.append(
            f'<line x1="{x}" y1="{top - 30}" x2="{x}" y2="{top + row_gap * 3 + 55}" '
            f'stroke="{COLORS["grid"]}" stroke-width="1"/>'
        )
        parts.append(text(x, top + row_gap * 3 + 85, f"{percent}%", size=15, fill=COLORS["muted"], anchor="middle"))
    for index, system in enumerate(polarity["systems"]):
        y = top + index * row_gap
        rate = float(system["wrong_preferred_rate"])
        ci_low, ci_high = system["ci95_seed_pair_bootstrap"]
        bar_width = chart_width * rate
        color = COLORS["neutral"] if system["system_id"] == "dense_bge_m3" else COLORS["failure"]
        parts.append(text(left - 24, y + 24, labels[system["system_id"]], size=17, fill=COLORS["muted"], anchor="end"))
        parts.append(
            f'<rect x="{left}" y="{y}" width="{bar_width}" height="34" fill="{color}" rx="2"/>'
        )
        low_x = left + chart_width * float(ci_low)
        high_x = left + chart_width * float(ci_high)
        mid_y = y + 17
        parts.append(
            f'<line x1="{low_x}" y1="{mid_y}" x2="{high_x}" y2="{mid_y}" '
            f'stroke="{COLORS["ink"]}" stroke-width="2"/>'
        )
        parts.append(
            f'<line x1="{low_x}" y1="{mid_y - 7}" x2="{low_x}" y2="{mid_y + 7}" '
            f'stroke="{COLORS["ink"]}" stroke-width="2"/>'
        )
        parts.append(
            f'<line x1="{high_x}" y1="{mid_y - 7}" x2="{high_x}" y2="{mid_y + 7}" '
            f'stroke="{COLORS["ink"]}" stroke-width="2"/>'
        )
        label_x = min(
            left + chart_width * max(rate, float(ci_high)) + 14,
            right - 8,
        )
        anchor = "start" if label_x < right - 8 else "end"
        parts.append(text(label_x, y + 24, f"{rate:.1%}", size=17, weight=700, anchor=anchor))
    parts.append(text((left + right) / 2, height - 35, "Opposite-polarity evidence scored at or above expected evidence", size=17, anchor="middle"))
    return svg_document(
        width,
        height,
        "Wrong-polarity preference by retrieval system",
        "Horizontal bars show wrong-polarity preference rates and clustered bootstrap confidence intervals for four retrieval systems.",
        "\n  ".join(parts),
    )


def render_summary(
    observations: dict[str, Any], upstream: dict[str, Any], polarity: dict[str, Any]
) -> str:
    runtime = observations["runtime"]
    cases = {case["case_id"]: case for case in observations["analyzer_cases"]}
    phrase = {
        (row["query_type"], row["slop"]): row["hits"]
        for row in observations["phrase_cases"]
    }
    contribution_rows = "\n".join(
        f"| `{item['repository']}#{item['pull_request']}` | {item['contribution_type']} | "
        f"`{item['merge_commit'][:12]}` | {item['merged_at'][:10]} |"
        for item in upstream["contributions"]
    )
    system_names = {
        "bm25_analyzer_tokens": "Analyzer-token BM25",
        "bm25_lucene_idf_sensitivity": "Lucene-style BM25 sensitivity arm",
        "dense_bge_m3": "BGE-M3 dense retrieval",
        "cross_encoder_bge_reranker_v2_m3": "BGE reranker",
    }
    polarity_rows = "\n".join(
        f"| {system_names[item['system_id']]} | {item['wrong_preferred_rate']:.1%} | "
        f"{item['ci95_seed_pair_bootstrap'][0]:.1%} - {item['ci95_seed_pair_bootstrap'][1]:.1%} |"
        for item in polarity["systems"]
    )
    return f"""# Generated Evidence Summary

This file is generated from checked-in synthetic or aggregate evidence by
`scripts/build_upstream_correctness_case_study.py`. It is not a general Korean
retrieval benchmark.

## Upstream Record

| Contribution | Type | Merge commit | Merged |
|---|---|---|---|
{contribution_rows}

## Local Boundary Observations

Runtime: Elasticsearch `{runtime['elasticsearch']}`, Lucene `{runtime['lucene']}`.

| Probe | Observed result |
|---|---|
| XPN polarity | `비급여` -> `{' / '.join(cases['xpn_non_covered']['tokens'])}`; `급여` -> `{' / '.join(cases['covered']['tokens'])}` |
| XPN polarity | `부담보` -> `{' / '.join(cases['xpn_excluded_coverage']['tokens'])}`; `담보` -> `{' / '.join(cases['coverage']['tokens'])}` |
| Hangul canonical form | NFC -> `{' / '.join(cases['hangul_nfc']['tokens'])}`; NFD -> one jamo-sequence token |
| Graph phrase | `match`={phrase[('match', None)]}, `match_phrase(slop=0)`={phrase[('match_phrase', 0)]}, `match_phrase(slop=1)`={phrase[('match_phrase', 1)]} |

## System-Level Polarity Stress

Metric: opposite-polarity evidence scores at or above expected evidence. The
study contains `{polarity['input']['contrastive_triples']}` counterfactual triples
derived from `{polarity['input']['seed_evidence_pairs']}` seed evidence pairs.

| System | Wrong-polarity preferred | Seed-pair bootstrap 95% CI |
|---|---:|---:|
{polarity_rows}

## Scope

- No queries, passages, source names, URLs, usernames, or stable row identifiers
  are exported by this case study.
- Analyzer inputs and the phrase fixture are synthetic.
- The phrase chart records pre-fix behavior on Elasticsearch
  `{runtime['elasticsearch']}`. Post-fix behavior is supported by the merged
  upstream regression tests, not a patched local runtime in this artifact.
- The polarity rates are stress measurements, not production prevalence estimates
  or an end-to-end human-relevance benchmark.
"""


def build_outputs() -> dict[Path, str]:
    observations = load_json(OBSERVATIONS_PATH)
    upstream = load_json(UPSTREAM_PATH)
    polarity = load_json(POLARITY_PATH)
    return {
        CASE_DIR / "evidence" / "SUMMARY.md": render_summary(
            observations, upstream, polarity
        ),
        CASE_DIR / "figures" / "representation-boundaries.svg": render_boundaries(),
        CASE_DIR / "figures" / "analyzer-outputs.svg": render_analyzer(observations),
        CASE_DIR / "figures" / "phrase-hit-counts.svg": render_phrase(observations),
        CASE_DIR / "figures" / "polarity-stress.svg": render_polarity(polarity),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Fail if generated outputs are stale.")
    args = parser.parse_args()

    stale: list[Path] = []
    for path, content in build_outputs().items():
        if not content.endswith("\n"):
            content += "\n"
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                stale.append(path.relative_to(ROOT))
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        print(path.relative_to(ROOT))

    if stale:
        print("stale upstream correctness artifacts:")
        for path in stale:
            print(f"- {path}")
        return 1
    if args.check:
        print("upstream correctness artifacts are current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
