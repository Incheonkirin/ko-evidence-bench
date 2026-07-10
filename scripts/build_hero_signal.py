#!/usr/bin/env python3
"""Build the README hero diagnostic signal report and SVG figure."""

from __future__ import annotations

import argparse
import html
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ko_evidence_bench.system_matrix import load_matrix, matrix_summary  # noqa: E402


@dataclass(frozen=True)
class HeroSignals:
    retrieval_n: int
    pack_clause20: str
    cross_clause20: str
    cross_delta: str
    cross_delta_ci: str
    always_route: str
    cohort_route: str
    cohort_delta: str
    cohort_delta_ci: str
    keyword_context_policy: int
    cohort_context_policy: int
    worst_surface_clause20: str
    surface_gap: str
    paired_rows: int
    kappa: str
    completed_labels: int
    validation_errors: int
    matrix_systems: int
    matrix_implemented: int
    matrix_not_run: int
    matrix_blocked: int


def read(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8")


def require_match(pattern: str, text: str, *, name: str) -> re.Match[str]:
    match = re.search(pattern, text, flags=re.MULTILINE)
    if not match:
        raise ValueError(f"missing {name}")
    return match


def require_percent(pattern: str, text: str, *, name: str) -> str:
    return require_match(pattern, text, name=name).group(1)


def require_int(pattern: str, text: str, *, name: str) -> int:
    return int(require_match(pattern, text, name=name).group(1).replace(",", ""))


def percent_number(value: str) -> float:
    return float(value.strip().rstrip("%"))


def pp_gap(high: str, low: str) -> str:
    return f"{percent_number(high) - percent_number(low):.1f}%p"


def load_signals(root: Path) -> HeroSignals:
    full_cross = read(root / "reports" / "private_544_full_cross_scorecard.md")
    route_score = read(root / "reports" / "private_route_scorecard_silver.md")
    runtime_surface = read(root / "reports" / "private_runtime_surface_scorecard_silver.md")
    agreement = read(root / "reports" / "private_route_audit_agreement_pending.md")
    validation = read(root / "reports" / "private_route_audit_validation_pending.md")
    matrix_counts = matrix_summary(load_matrix(root / "docs" / "system_matrix.json"))

    retrieval_n = require_int(r"^- source result n: ([\d,]+)$", full_cross, name="retrieval n")
    pack_clause20 = require_percent(
        r"\| structural_pack \| `clause@20` \| [\d,]+ \| ([\d.]+%) \|",
        full_cross,
        name="structural_pack clause@20",
    )
    cross_clause20 = require_percent(
        r"\| structural_cross_text \| `clause@20` \| [\d,]+ \| ([\d.]+%) \|",
        full_cross,
        name="structural_cross_text clause@20",
    )
    cross_delta_match = require_match(
        r"\| structural_cross_text \| `clause@20` \| ([\d.]+%) \| ([^|]+?) \|",
        full_cross,
        name="structural_cross_text clause@20 delta",
    )
    always_route = require_percent(
        r"\| `always_policy` \| [\d,]+ \| [\d,]+ \| ([\d.]+%) \|",
        route_score,
        name="always_policy route accuracy",
    )
    cohort_route = require_percent(
        r"\| `cohort_aware_query_router` \| [\d,]+ \| [\d,]+ \| ([\d.]+%) \|",
        route_score,
        name="cohort-aware route accuracy",
    )
    cohort_delta_match = require_match(
        r"\| `cohort_aware_query_router` \| `route_accuracy` \| ([\d.]+%) \| ([^|]+?) \|",
        route_score,
        name="cohort-aware route delta",
    )
    keyword_context_policy = require_int(
        r"\| `query_keyword_router` \| `human_context_needed` \| `policy_clause` \| ([\d,]+) \|",
        route_score,
        name="keyword context-needed policy fallback",
    )
    cohort_context_policy = require_int(
        r"\| `cohort_aware_query_router` \| `human_context_needed` \| `policy_clause` \| ([\d,]+) \|",
        route_score,
        name="cohort context-needed policy fallback",
    )
    runtime_match = require_match(
        r"\| `structural_cross_text` \| [\d,]+ \| [\d,]+ \| [\d,]+ \| [\d,]+ \| "
        r"([\d.]+%) \| [\d.]+% \| [\d.]+% \| [\d.]+% \| ([\d.]+%) \|",
        runtime_surface,
        name="structural_cross_text runtime surface row",
    )
    paired_rows = require_int(r"^- paired completed rows: ([\d,]+)$", agreement, name="paired rows")
    kappa = require_match(r"^- Cohen's kappa: (-?[\d.]+)$", agreement, name="kappa").group(1)
    completed_labels = require_int(r"^- completed labels: ([\d,]+)$", validation, name="completed labels")
    validation_errors = require_int(
        r"^- rows with validation errors: ([\d,]+)$",
        validation,
        name="validation errors",
    )

    return HeroSignals(
        retrieval_n=retrieval_n,
        pack_clause20=pack_clause20,
        cross_clause20=cross_clause20,
        cross_delta=cross_delta_match.group(1),
        cross_delta_ci=cross_delta_match.group(2).strip(),
        always_route=always_route,
        cohort_route=cohort_route,
        cohort_delta=cohort_delta_match.group(1),
        cohort_delta_ci=cohort_delta_match.group(2).strip(),
        keyword_context_policy=keyword_context_policy,
        cohort_context_policy=cohort_context_policy,
        worst_surface_clause20=runtime_match.group(2),
        surface_gap=pp_gap(runtime_match.group(1), runtime_match.group(2)),
        paired_rows=paired_rows,
        kappa=kappa,
        completed_labels=completed_labels,
        validation_errors=validation_errors,
        matrix_systems=int(matrix_counts["systems"]),
        matrix_implemented=int(matrix_counts["implemented"]),
        matrix_not_run=int(matrix_counts["not_run"]),
        matrix_blocked=int(matrix_counts["blocked"]),
    )


def color_for_percent(value: str) -> str:
    pct = percent_number(value)
    if pct >= 65:
        return "#2f855a"
    if pct >= 50:
        return "#68a357"
    if pct >= 35:
        return "#c49a2c"
    return "#b84242"


def svg_text(x: int, y: int, text: str, *, size: int = 18, weight: str = "400", fill: str = "#172033") -> str:
    return (
        f'<text x="{x}" y="{y}" font-family="Inter, Arial, sans-serif" '
        f'font-size="{size}" font-weight="{weight}" fill="{fill}">{html.escape(text)}</text>'
    )


def svg_card(x: int, y: int, w: int, h: int, fill: str, label: str, value: str, note: str) -> list[str]:
    return [
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}"/>',
        svg_text(x + 18, y + 34, label, size=18, weight="700", fill="#ffffff"),
        svg_text(x + 18, y + 82, value, size=34, weight="800", fill="#ffffff"),
        svg_text(x + 18, y + 118, note, size=15, weight="500", fill="#eef2f7"),
    ]


def render_svg(signals: HeroSignals) -> str:
    width = 980
    height = 520
    rows: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Diagnostic signal heatmap">',
        '<rect width="980" height="520" fill="#f7f8fb"/>',
        svg_text(36, 54, "ko-evidence-bench diagnostic signals", size=28, weight="800"),
        svg_text(
            36,
            86,
            "Aggregate diagnostics only; human-gold headline claims are blocked.",
            size=16,
            fill="#4a5568",
        ),
    ]
    rows.extend(
        svg_card(
            36,
            124,
            430,
            140,
            color_for_percent(signals.cross_clause20),
            "Clause recovery",
            f"{signals.pack_clause20} -> {signals.cross_clause20}",
            f"+{signals.cross_delta}p paired; CI {signals.cross_delta_ci}",
        )
    )
    rows.extend(
        svg_card(
            514,
            124,
            430,
            140,
            color_for_percent(signals.cohort_route),
            "Source routing",
            f"{signals.always_route} -> {signals.cohort_route}",
            f"+{signals.cohort_delta}p paired; CI {signals.cohort_delta_ci}",
        )
    )
    rows.extend(
        svg_card(
            36,
            304,
            430,
            140,
            color_for_percent(signals.worst_surface_clause20),
            "Surface robustness",
            f"worst surface {signals.worst_surface_clause20}",
            f"{signals.surface_gap} gap vs overall clause@20",
        )
    )
    rows.extend(
        svg_card(
            514,
            304,
            430,
            140,
            "#6b7280",
            "Claim-control gate",
            f"{signals.completed_labels}/300 labels",
            f"{signals.matrix_not_run} not-run systems; {signals.matrix_blocked} blocked",
        )
    )
    rows.append(svg_text(36, 482, f"n={signals.retrieval_n} silver rows. Headline use waits for labels plus matrix completion; validation errors={signals.validation_errors}.", size=15, fill="#4a5568"))
    rows.append("</svg>")
    return "\n".join(rows) + "\n"


def render_markdown(signals: HeroSignals, figure_path: Path) -> str:
    figure_ref = figure_path.as_posix()
    fallback_drop = signals.keyword_context_policy - signals.cohort_context_policy
    return "\n".join(
        [
            "# Hero Diagnostic Signal",
            "",
            "Status: **diagnostic only; human-gold headline claims blocked**.",
            "",
            f"![Diagnostic signal heatmap]({figure_ref})",
            "",
            "This report turns the checked-in aggregate diagnostics into a first",
            "screen study signal: a small number of memorable findings with the",
            "claim-control gate kept visible.",
            "",
            "| axis | baseline | current candidate | diagnostic read |",
            "|---|---:|---:|---|",
            (
                "| Clause recovery | "
                f"`structural_pack` {signals.pack_clause20} | "
                f"`structural_cross_text` {signals.cross_clause20} | "
                f"+{signals.cross_delta}p paired, CI {signals.cross_delta_ci} |"
            ),
            (
                "| Source routing | "
                f"`always_policy` {signals.always_route} | "
                f"`cohort_aware_query_router` {signals.cohort_route} | "
                f"+{signals.cohort_delta}p paired, CI {signals.cohort_delta_ci} |"
            ),
            (
                "| Unsafe policy fallback | "
                f"{signals.keyword_context_policy} context-needed rows | "
                f"{signals.cohort_context_policy} context-needed rows | "
                f"{fallback_drop} fewer silver fallback errors |"
            ),
            (
                "| Surface robustness | "
                f"overall clause@20 {signals.cross_clause20} | "
                f"worst surface {signals.worst_surface_clause20} | "
                f"{signals.surface_gap} spread remains |"
            ),
            (
                "| Human-gold gate | "
                f"{signals.paired_rows}/50 paired labels | "
                f"{signals.completed_labels}/300 adjudicated labels | "
                f"kappa {signals.kappa}; {signals.validation_errors} validation errors |"
            ),
            (
                "| System matrix gate | "
                f"{signals.matrix_implemented}/{signals.matrix_systems} systems implemented | "
                f"{signals.matrix_not_run} not run; {signals.matrix_blocked} blocked | "
                "full comparison matrix incomplete |"
            ),
            "",
            "## Use Notes",
            "",
            "- The figure and table are generated from aggregate reports only.",
            "- These are private-lab silver diagnostics, not final benchmark claims.",
            "- The strongest public version starts here but waits for completed",
            "  human labels and full matrix coverage before changing the README",
            "  language from diagnostic to headline.",
            "",
        ]
    )


def write_if_changed(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report-out", type=Path, default=ROOT / "reports" / "hero_signal.md")
    parser.add_argument(
        "--figure-out",
        type=Path,
        default=ROOT / "reports" / "figures" / "diagnostic_signal_heatmap.svg",
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    signals = load_signals(ROOT)
    figure_text = render_svg(signals)
    try:
        figure_ref = args.figure_out.relative_to(args.report_out.parent)
    except ValueError:
        figure_ref = args.figure_out
    report_text = render_markdown(signals, figure_ref)

    if args.check:
        current_report = args.report_out.read_text(encoding="utf-8") if args.report_out.exists() else ""
        current_figure = args.figure_out.read_text(encoding="utf-8") if args.figure_out.exists() else ""
        if current_report != report_text or current_figure != figure_text:
            print("hero signal artifacts are stale; run scripts/build_hero_signal.py")
            return 1
        print("hero signal artifacts are current")
        return 0

    write_if_changed(args.figure_out, figure_text)
    write_if_changed(args.report_out, report_text)
    print(report_text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
