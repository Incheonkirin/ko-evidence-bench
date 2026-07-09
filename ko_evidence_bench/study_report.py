"""Generate the public measurement-study draft from aggregate reports."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .study_readiness import StudyReadiness, load_study_readiness, read, require_percent


@dataclass(frozen=True)
class MetricWithCi:
    value: str
    ci: str


@dataclass(frozen=True)
class StudyReportSignals:
    readiness: StudyReadiness
    structural_pack_clause20: MetricWithCi
    structural_cross_text_clause20: MetricWithCi
    structural_cross_text_delta_clause20: MetricWithCi
    always_policy_route_accuracy: MetricWithCi
    keyword_route_accuracy: MetricWithCi
    keyword_route_delta: MetricWithCi
    keyword_abstention_recall: MetricWithCi


def metric_ci(report: str, run: str, metric: str) -> MetricWithCi:
    pattern = rf"\| {re.escape(run)} \| `{re.escape(metric)}` \| [\d,]+ \| ([\d.]+%) \| ([^|]+?) \|"
    match = re.search(pattern, report)
    if not match:
        raise ValueError(f"missing metric row: {run} {metric}")
    return MetricWithCi(value=match.group(1), ci=match.group(2).strip())


def route_metric_ci(report: str, system: str, metric_col: str) -> MetricWithCi:
    header = r"\| system \| n \| missing \| route_acc \| 95% CI \| abst_p \| abst_r \|"
    if not re.search(header, report):
        raise ValueError("missing route scorecard header")
    pattern = (
        rf"\| `{re.escape(system)}` \| [\d,]+ \| [\d,]+ \| "
        r"([\d.]+%) \| ([^|]+?) \| ([\d.]+%) \| ([\d.]+%) \|"
    )
    match = re.search(pattern, report)
    if not match:
        raise ValueError(f"missing route scorecard row: {system}")
    if metric_col == "route_accuracy":
        return MetricWithCi(value=match.group(1), ci=match.group(2).strip())
    if metric_col == "abstention_precision":
        return MetricWithCi(value=match.group(3), ci="not bootstrapped in compact scorecard")
    if metric_col == "abstention_recall":
        return MetricWithCi(value=match.group(4), ci="not bootstrapped in compact scorecard")
    raise ValueError(f"unknown route metric column: {metric_col}")


def route_delta_ci(report: str, system: str, metric: str) -> MetricWithCi:
    pattern = rf"\| `{re.escape(system)}` \| `{re.escape(metric)}` \| ([\d.]+%) \| ([^|]+?) \|"
    match = re.search(pattern, report)
    if not match:
        raise ValueError(f"missing route delta row: {system} {metric}")
    return MetricWithCi(value=match.group(1), ci=match.group(2).strip())


def points(value: str) -> str:
    return f"+{value}p"


def load_study_report_signals(root: Path) -> StudyReportSignals:
    full_cross = read(root / "reports" / "private_544_full_cross_scorecard.md")
    route_scorecard = read(root / "reports" / "private_route_scorecard_silver.md")
    readiness = load_study_readiness(root)

    return StudyReportSignals(
        readiness=readiness,
        structural_pack_clause20=metric_ci(full_cross, "structural_pack", "clause@20"),
        structural_cross_text_clause20=metric_ci(full_cross, "structural_cross_text", "clause@20"),
        structural_cross_text_delta_clause20=MetricWithCi(
            value=require_percent(
                r"\| structural_cross_text \| `clause@20` \| ([\d.]+%) \|",
                full_cross,
                name="structural_cross_text clause@20 delta",
            ),
            ci=require_percent(
                r"\| structural_cross_text \| `clause@20` \| [\d.]+% \| ([^|]+?) \|",
                full_cross,
                name="structural_cross_text clause@20 delta ci",
            ).strip(),
        ),
        always_policy_route_accuracy=route_metric_ci(route_scorecard, "always_policy", "route_accuracy"),
        keyword_route_accuracy=route_metric_ci(route_scorecard, "query_keyword_router", "route_accuracy"),
        keyword_route_delta=route_delta_ci(route_scorecard, "query_keyword_router", "route_accuracy"),
        keyword_abstention_recall=route_metric_ci(route_scorecard, "query_keyword_router", "abstention_recall"),
    )


def render_measurement_study(signals: StudyReportSignals) -> str:
    r = signals.readiness
    lines = [
        "# Measurement Study Draft",
        "",
        f"Status: **{r.status} for public headline claims**.",
        "",
        "## Abstract",
        "",
        "Korean insurance questions are written in consumer language, while citable",
        "answers often live in source-specific evidence: policy clauses, product",
        "disclosures, official consumer guidance, claim-operation material, dispute",
        "cases, or expert guidance. This draft measures two things separately:",
        "whether retrieval finds citable clause evidence, and whether a source router",
        "can tell when policy clauses are not the right evidence tier.",
        "",
        "All numbers below are aggregate-only private-lab diagnostics. They are useful",
        "for steering the work, but they are blocked from headline use until the",
        "300-row human source-route adjudication workset is complete.",
        "",
        "## Current Finding Candidates",
        "",
        "| candidate finding | current evidence | status |",
        "|---|---:|---|",
        (
            "| Cross-text reranking improves clause recovery | "
            f"`clause@20` {signals.structural_pack_clause20.value} -> "
            f"{signals.structural_cross_text_clause20.value}; paired delta "
            f"{points(signals.structural_cross_text_delta_clause20.value)} | silver diagnostic |"
        ),
        (
            "| Always searching policy clauses is a weak source-routing baseline | "
            f"`always_policy` route accuracy {signals.always_policy_route_accuracy.value} | "
            "silver diagnostic |"
        ),
        (
            "| Query-language routing helps but misses most abstention-needed cases | "
            f"route accuracy {signals.keyword_route_accuracy.value}; abstention recall "
            f"{signals.keyword_abstention_recall.value} | silver diagnostic |"
        ),
        (
            "| Human-gold public headline claim | "
            f"{r.completed_route_labels} / 300 adjudicated labels complete | blocked |"
        ),
        "",
        "## Retrieval Evidence",
        "",
        "| system | metric | value | 95% CI |",
        "|---|---|---:|---:|",
        (
            f"| `structural_pack` | `clause@20` | "
            f"{signals.structural_pack_clause20.value} | {signals.structural_pack_clause20.ci} |"
        ),
        (
            f"| `structural_cross_text` | `clause@20` | "
            f"{signals.structural_cross_text_clause20.value} | {signals.structural_cross_text_clause20.ci} |"
        ),
        "",
        "Paired delta vs `structural_pack`:",
        "",
        "| candidate | metric | delta | 95% CI |",
        "|---|---|---:|---:|",
        (
            f"| `structural_cross_text` | `clause@20` | "
            f"{points(signals.structural_cross_text_delta_clause20.value)} | "
            f"{signals.structural_cross_text_delta_clause20.ci} |"
        ),
        "",
        "## Source-Route Evidence",
        "",
        "| system | route accuracy | 95% CI | abstention recall |",
        "|---|---:|---:|---:|",
        (
            f"| `always_policy` | {signals.always_policy_route_accuracy.value} | "
            f"{signals.always_policy_route_accuracy.ci} | 0.0% |"
        ),
        (
            f"| `query_keyword_router` | {signals.keyword_route_accuracy.value} | "
            f"{signals.keyword_route_accuracy.ci} | {signals.keyword_abstention_recall.value} |"
        ),
        "",
        "Paired delta vs `always_policy`:",
        "",
        "| candidate | metric | delta | 95% CI |",
        "|---|---|---:|---:|",
        (
            f"| `query_keyword_router` | `route_accuracy` | "
            f"{points(signals.keyword_route_delta.value)} | {signals.keyword_route_delta.ci} |"
        ),
        "",
        "## Claim Control",
        "",
        "| gate | current value | required before headline use |",
        "|---|---:|---:|",
        f"| retrieval eval rows | {r.retrieval_n} | >= 500 |",
        f"| completed adjudicated route labels | {r.completed_route_labels} | >= 300 |",
        f"| route validation errors | {r.route_validation_errors} | 0 |",
        "",
        "The retrieval rows meet the diagnostic-size threshold, but source-route labels",
        "are not human-adjudicated yet. Therefore this draft should not be presented",
        "as a final benchmark result.",
        "",
        "## Reproduction",
        "",
        "```bash",
        "make reproduce-table-1",
        "make reproduce-route-scorecard",
        "make check-study-readiness",
        "make verify",
        "```",
        "",
        "The public commands reproduce synthetic fixtures and regenerate aggregate",
        "claim-control reports. Private qid-only route runs and raw qrels stay outside",
        "the public repository.",
        "",
        "## Next Evidence",
        "",
        "1. Complete the 300-row adjudicated source-route workset.",
        "2. Validate it with zero route-label errors.",
        "3. Promote qid-only human labels and re-run the same route scorecard path.",
        "4. Re-run retrieval comparisons sliced by human-gold source route.",
        "5. Replace this draft's diagnostic claims with human-audited findings only",
        "   if `reports/study_readiness.md` changes to GO.",
        "",
    ]
    return "\n".join(lines)
