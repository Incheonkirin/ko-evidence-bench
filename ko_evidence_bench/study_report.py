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
class RouteSliceSignal:
    n: str
    route_accuracy: str
    abstained_rate: str
    expected_abstention_rate: str


@dataclass(frozen=True)
class RouteConfusionSignal:
    count: str
    share: str


@dataclass(frozen=True)
class CohortRouteSignal:
    route_accuracy_range: str
    max_context_policy_fallback: str


@dataclass(frozen=True)
class SubstrateShapeSignal:
    input_rows: str
    usable_rows: str
    avg_chars: str
    median_chars: str
    short_messages: str
    long_contexts: str
    question_like: str


@dataclass(frozen=True)
class IntentSurfaceSignal:
    rows: str
    top_family: str
    top_family_count: str
    top_family_share: str
    top_surface: str
    top_surface_count: str
    top_surface_share: str


@dataclass(frozen=True)
class RouteSurfaceSignal:
    route_accuracy: str
    abstention_recall: str
    avg_intent_route_spread: str
    worst_surface_route_accuracy: str
    missing_metadata: str


@dataclass(frozen=True)
class RuntimeSurfaceSignal:
    clause20: str
    answerable_clause20: str
    exact20: str
    avg_family_surface_spread: str
    worst_surface_clause20: str
    missing_metadata: str


@dataclass(frozen=True)
class AuditCoverageSignal:
    audit_rows: str
    matched_rows: str
    route_coverage: str
    intent_coverage: str
    surface_coverage: str
    trap_coverage: str


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
    cohort_aware_route_accuracy: MetricWithCi
    cohort_aware_route_delta: MetricWithCi
    cohort_aware_abstention_recall: MetricWithCi
    keyword_human_context_slice: RouteSliceSignal
    keyword_human_context_to_policy: RouteConfusionSignal
    cohort_aware_human_context_to_policy: RouteConfusionSignal
    cohort_route_signal: CohortRouteSignal
    community_post_context: SubstrateShapeSignal
    messenger_conversation: SubstrateShapeSignal
    search_eval_query: SubstrateShapeSignal
    intent_surface_signal: IntentSurfaceSignal
    always_policy_route_surface: RouteSurfaceSignal
    keyword_route_surface: RouteSurfaceSignal
    cohort_aware_route_surface: RouteSurfaceSignal
    structural_pack_runtime_surface: RuntimeSurfaceSignal
    structural_cross_text_runtime_surface: RuntimeSurfaceSignal
    audit_coverage: AuditCoverageSignal


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


def route_slice_signal(report: str, system: str, gold_route: str) -> RouteSliceSignal:
    pattern = (
        rf"\| `{re.escape(system)}` \| `{re.escape(gold_route)}` \| "
        r"([\d,]+) \| [\d,]+ \| ([\d.]+%) \| ([\d.]+%) \| ([\d.]+%) \|"
    )
    match = re.search(pattern, report)
    if not match:
        raise ValueError(f"missing route slice row: {system} {gold_route}")
    return RouteSliceSignal(
        n=match.group(1),
        route_accuracy=match.group(2),
        abstained_rate=match.group(3),
        expected_abstention_rate=match.group(4),
    )


def route_confusion_signal(
    report: str,
    system: str,
    gold_route: str,
    predicted_route: str,
) -> RouteConfusionSignal:
    pattern = (
        rf"\| `{re.escape(system)}` \| `{re.escape(gold_route)}` \| "
        rf"`{re.escape(predicted_route)}` \| ([\d,]+) \| ([\d.]+%) \|"
    )
    match = re.search(pattern, report)
    if not match:
        raise ValueError(f"missing route confusion row: {system} {gold_route} -> {predicted_route}")
    return RouteConfusionSignal(count=match.group(1), share=match.group(2))


def percent_float(value: str) -> float:
    return float(value.rstrip("%"))


def cohort_route_signal(report: str, system: str) -> CohortRouteSignal:
    metric_rows = re.findall(
        rf"\| `{re.escape(system)}` \| `[^`]+` \| [\d,]+ \| ([\d.]+%) \| [\d.]+% \| [\d.]+% \|",
        report,
    )
    fallback_rows = re.findall(
        rf"\| `{re.escape(system)}` \| `[^`]+` \| [\d,]+ \| [\d,]+ \| ([\d.]+%) \|",
        report,
    )
    if not metric_rows:
        raise ValueError(f"missing cohort route metric rows for {system}")
    if not fallback_rows:
        raise ValueError(f"missing cohort fallback rows for {system}")
    route_values = sorted(percent_float(value) for value in metric_rows)
    fallback_values = sorted(percent_float(value) for value in fallback_rows)
    return CohortRouteSignal(
        route_accuracy_range=f"{route_values[0]:.1f}% - {route_values[-1]:.1f}%",
        max_context_policy_fallback=f"{fallback_values[-1]:.1f}%",
    )


def substrate_shape_signal(report: str, cohort: str) -> SubstrateShapeSignal:
    pattern = (
        rf"\| `{re.escape(cohort)}` \| ([\d,]+) \| ([\d,]+) \| [\d.]+% \| "
        r"([\d.]+) \| ([\d.]+) \| [\d.]+ \| ([\d.]+%) \| ([\d.]+%) \| ([\d.]+%) \|"
    )
    match = re.search(pattern, report)
    if not match:
        raise ValueError(f"missing substrate profile row: {cohort}")
    return SubstrateShapeSignal(
        input_rows=match.group(1),
        usable_rows=match.group(2),
        avg_chars=match.group(3),
        median_chars=match.group(4),
        short_messages=match.group(5),
        long_contexts=match.group(6),
        question_like=match.group(7),
    )


def first_counter_row(report: str, title: str) -> tuple[str, str, str]:
    pattern = (
        rf"## {re.escape(title)}\n\n"
        r"\| value \| count \| share \|\n"
        r"\|---\|---:\|---:\|\n"
        r"\| `([^`]+)` \| ([\d,]+) \| ([\d.]+%) \|"
    )
    match = re.search(pattern, report)
    if not match:
        raise ValueError(f"missing first counter row: {title}")
    return match.group(1), match.group(2), match.group(3)


def intent_surface_signal(report: str) -> IntentSurfaceSignal:
    rows_match = re.search(r"^- exported qid-only rows: ([\d,]+)$", report, flags=re.MULTILINE)
    if not rows_match:
        raise ValueError("missing exported qid-only rows")
    top_family = first_counter_row(report, "Intent Family Counts")
    top_surface = first_counter_row(report, "Surface Form Counts")
    return IntentSurfaceSignal(
        rows=rows_match.group(1),
        top_family=top_family[0],
        top_family_count=top_family[1],
        top_family_share=top_family[2],
        top_surface=top_surface[0],
        top_surface_count=top_surface[1],
        top_surface_share=top_surface[2],
    )


def route_surface_signal(report: str, system: str) -> RouteSurfaceSignal:
    pattern = (
        rf"\| `{re.escape(system)}` \| [\d,]+ \| [\d,]+ \| [\d,]+ \| "
        r"([\d.]+%) \| [\d.]+% \| ([\d.]+%) \| ([\d.]+%) \| ([\d.]+%) \| [\d,]+ \| ([\d,]+) \|"
    )
    match = re.search(pattern, report)
    if not match:
        raise ValueError(f"missing route-surface summary row: {system}")
    return RouteSurfaceSignal(
        route_accuracy=match.group(1),
        abstention_recall=match.group(2),
        avg_intent_route_spread=match.group(3),
        worst_surface_route_accuracy=match.group(4),
        missing_metadata=match.group(5),
    )


def runtime_surface_signal(report: str, system: str) -> RuntimeSurfaceSignal:
    pattern = (
        rf"\| `{re.escape(system)}` \| [\d,]+ \| [\d,]+ \| [\d,]+ \| [\d,]+ \| "
        r"([\d.]+%) \| ([\d.]+%) \| ([\d.]+%) \| ([\d.]+%) \| ([\d.]+%) \| [\d,]+ \| ([\d,]+) \|"
    )
    match = re.search(pattern, report)
    if not match:
        raise ValueError(f"missing runtime-surface summary row: {system}")
    return RuntimeSurfaceSignal(
        clause20=match.group(1),
        answerable_clause20=match.group(2),
        exact20=match.group(3),
        avg_family_surface_spread=match.group(4),
        worst_surface_clause20=match.group(5),
        missing_metadata=match.group(6),
    )


def audit_coverage_axis(report: str, axis: str) -> str:
    pattern = rf"\| `{re.escape(axis)}` \| ([\d,]+) \| ([\d,]+) \| 0 \| [\d,]+ \| [\d,]+ \| `PASS` \|"
    match = re.search(pattern, report)
    if not match:
        raise ValueError(f"missing complete audit coverage axis: {axis}")
    return f"{match.group(2)} / {match.group(1)}"


def audit_coverage_signal(report: str) -> AuditCoverageSignal:
    audit_rows = re.search(r"^- audit rows: ([\d,]+)$", report, flags=re.MULTILINE)
    matched_rows = re.search(r"^- matched audit rows: ([\d,]+)$", report, flags=re.MULTILINE)
    if not audit_rows or not matched_rows:
        raise ValueError("missing audit coverage row counts")
    return AuditCoverageSignal(
        audit_rows=audit_rows.group(1),
        matched_rows=matched_rows.group(1),
        route_coverage=audit_coverage_axis(report, "route_gold"),
        intent_coverage=audit_coverage_axis(report, "intent_family"),
        surface_coverage=audit_coverage_axis(report, "surface_form"),
        trap_coverage=audit_coverage_axis(report, "trap_classes"),
    )


def points(value: str) -> str:
    return f"+{value}p"


def load_study_report_signals(root: Path) -> StudyReportSignals:
    full_cross = read(root / "reports" / "private_544_full_cross_scorecard.md")
    route_scorecard = read(root / "reports" / "private_route_scorecard_silver.md")
    route_cohort_scorecard = read(root / "reports" / "private_route_cohort_scorecard_silver.md")
    substrate_profile = read(root / "reports" / "private_query_substrate_profile.md")
    intent_surface_export = read(root / "reports" / "private_intent_surface_export_summary.md")
    route_surface_scorecard = read(root / "reports" / "private_route_surface_scorecard_silver.md")
    runtime_surface_scorecard = read(root / "reports" / "private_runtime_surface_scorecard_silver.md")
    audit_surface_coverage = read(root / "reports" / "private_audit_surface_coverage_300.md")
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
        cohort_aware_route_accuracy=route_metric_ci(route_scorecard, "cohort_aware_query_router", "route_accuracy"),
        cohort_aware_route_delta=route_delta_ci(route_scorecard, "cohort_aware_query_router", "route_accuracy"),
        cohort_aware_abstention_recall=route_metric_ci(
            route_scorecard,
            "cohort_aware_query_router",
            "abstention_recall",
        ),
        keyword_human_context_slice=route_slice_signal(
            route_scorecard,
            "query_keyword_router",
            "human_context_needed",
        ),
        keyword_human_context_to_policy=route_confusion_signal(
            route_scorecard,
            "query_keyword_router",
            "human_context_needed",
            "policy_clause",
        ),
        cohort_aware_human_context_to_policy=route_confusion_signal(
            route_scorecard,
            "cohort_aware_query_router",
            "human_context_needed",
            "policy_clause",
        ),
        cohort_route_signal=cohort_route_signal(route_cohort_scorecard, "cohort_aware_query_router"),
        community_post_context=substrate_shape_signal(substrate_profile, "community_post_context"),
        messenger_conversation=substrate_shape_signal(substrate_profile, "messenger_conversation"),
        search_eval_query=substrate_shape_signal(substrate_profile, "search_eval_query"),
        intent_surface_signal=intent_surface_signal(intent_surface_export),
        always_policy_route_surface=route_surface_signal(route_surface_scorecard, "always_policy"),
        keyword_route_surface=route_surface_signal(route_surface_scorecard, "query_keyword_router"),
        cohort_aware_route_surface=route_surface_signal(route_surface_scorecard, "cohort_aware_query_router"),
        structural_pack_runtime_surface=runtime_surface_signal(runtime_surface_scorecard, "structural_pack"),
        structural_cross_text_runtime_surface=runtime_surface_signal(
            runtime_surface_scorecard,
            "structural_cross_text",
        ),
        audit_coverage=audit_coverage_signal(audit_surface_coverage),
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
            "| Cohort-aware routing improves source routing without raw source exposure | "
            f"route accuracy {signals.cohort_aware_route_accuracy.value}; paired delta "
            f"{points(signals.cohort_aware_route_delta.value)}; abstention recall "
            f"{signals.cohort_aware_abstention_recall.value} | silver diagnostic |"
        ),
        (
            "| The largest silver route failure is unsafe policy-clause fallback | "
            f"`human_context_needed -> policy_clause` drops from "
            f"{signals.keyword_human_context_to_policy.count} to "
            f"{signals.cohort_aware_human_context_to_policy.count} rows | "
            "silver diagnostic |"
        ),
        (
            "| Route failures vary by private query cohort | "
            f"route accuracy range {signals.cohort_route_signal.route_accuracy_range}; "
            f"context-needed policy fallback up to {signals.cohort_route_signal.max_context_policy_fallback} | "
            "silver diagnostic |"
        ),
        (
            "| Real-query substrates need separate stress slices | "
            f"community contexts avg {signals.community_post_context.avg_chars} chars with "
            f"{signals.community_post_context.long_contexts} long contexts; live-style turns median "
            f"{signals.messenger_conversation.median_chars} chars with "
            f"{signals.messenger_conversation.short_messages} short messages; eval queries "
            f"{signals.search_eval_query.short_messages} short | substrate diagnostic |"
        ),
        (
            "| Private qrels now have silver intent/surface slices | "
            f"{signals.intent_surface_signal.rows} qid-only rows; top silver family "
            f"`{signals.intent_surface_signal.top_family}` "
            f"{signals.intent_surface_signal.top_family_share}; top surface "
            f"`{signals.intent_surface_signal.top_surface}` "
            f"{signals.intent_surface_signal.top_surface_share} | silver metadata |"
        ),
        (
            "| Route decisions can now be scored by surface condition | "
            f"cohort-aware route-only worst surface {signals.cohort_aware_route_surface.worst_surface_route_accuracy}; "
            f"missing metadata {signals.cohort_aware_route_surface.missing_metadata} | silver route diagnostic |"
        ),
        (
            "| Ranked retrieval hits can now be sliced by surface condition | "
            f"`structural_cross_text` clause@20 {signals.structural_cross_text_runtime_surface.clause20}; "
            f"answerable clause@20 {signals.structural_cross_text_runtime_surface.answerable_clause20}; "
            f"worst surface {signals.structural_cross_text_runtime_surface.worst_surface_clause20} | "
            "silver runtime diagnostic |"
        ),
        (
            "| Human audit workset covers the stress axes before labeling | "
            f"{signals.audit_coverage.matched_rows} matched rows; route "
            f"{signals.audit_coverage.route_coverage}, intent "
            f"{signals.audit_coverage.intent_coverage}, surface "
            f"{signals.audit_coverage.surface_coverage}, trap "
            f"{signals.audit_coverage.trap_coverage} values covered | workset diagnostic |"
        ),
        (
            "| Human-gold public headline claim | "
            f"{r.agreement_paired_rows} / 50 paired labels; "
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
        "Private runtime-surface diagnostics:",
        "",
        "| system | clause@20 | answerable clause@20 | exact@20 | avg family surface spread | worst surface clause@20 | missing metadata |",
        "|---|---:|---:|---:|---:|---:|---:|",
        (
            f"| `structural_pack` | {signals.structural_pack_runtime_surface.clause20} | "
            f"{signals.structural_pack_runtime_surface.answerable_clause20} | "
            f"{signals.structural_pack_runtime_surface.exact20} | "
            f"{signals.structural_pack_runtime_surface.avg_family_surface_spread} | "
            f"{signals.structural_pack_runtime_surface.worst_surface_clause20} | "
            f"{signals.structural_pack_runtime_surface.missing_metadata} |"
        ),
        (
            f"| `structural_cross_text` | {signals.structural_cross_text_runtime_surface.clause20} | "
            f"{signals.structural_cross_text_runtime_surface.answerable_clause20} | "
            f"{signals.structural_cross_text_runtime_surface.exact20} | "
            f"{signals.structural_cross_text_runtime_surface.avg_family_surface_spread} | "
            f"{signals.structural_cross_text_runtime_surface.worst_surface_clause20} | "
            f"{signals.structural_cross_text_runtime_surface.missing_metadata} |"
        ),
        "",
        "This joins private runtime hit booleans with qid-only intent/surface",
        "metadata. It does not publish raw ranked evidence ids, but it verifies",
        "whether actual retrieval hits vary across surface conditions.",
        "",
        "## System Matrix Evidence",
        "",
        "| artifact | current evidence | status |",
        "|---|---|---|",
        "| `reports/system_matrix.md` | 7 implemented diagnostic/fixture systems; 7 not-run analyzer/dense/hybrid/reranker systems; 1 human-gold gate blocked | full comparison matrix incomplete |",
        "",
        "This keeps the experiment scope honest. The current study has checked-in",
        "retrieval, routing, surface, and fixture evidence, but it has not yet run",
        "the full analyzer/dense/hybrid/reranker matrix needed for a stronger",
        "public benchmark claim.",
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
        (
            f"| `cohort_aware_query_router` | {signals.cohort_aware_route_accuracy.value} | "
            f"{signals.cohort_aware_route_accuracy.ci} | {signals.cohort_aware_abstention_recall.value} |"
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
        (
            f"| `cohort_aware_query_router` | `route_accuracy` | "
            f"{points(signals.cohort_aware_route_delta.value)} | {signals.cohort_aware_route_delta.ci} |"
        ),
        "",
        "Silver source-route slices:",
        "",
        "| system | gold source tier | n | route accuracy | abstained rate | expected abstention |",
        "|---|---|---:|---:|---:|---:|",
        (
            "| `query_keyword_router` | `human_context_needed` | "
            f"{signals.keyword_human_context_slice.n} | "
            f"{signals.keyword_human_context_slice.route_accuracy} | "
            f"{signals.keyword_human_context_slice.abstained_rate} | "
            f"{signals.keyword_human_context_slice.expected_abstention_rate} |"
        ),
        "",
        "Largest silver confusion:",
        "",
        "| system | gold source tier | predicted source tier | count | share of run |",
        "|---|---|---|---:|---:|",
        (
            "| `query_keyword_router` | `human_context_needed` | `policy_clause` | "
            f"{signals.keyword_human_context_to_policy.count} | "
            f"{signals.keyword_human_context_to_policy.share} |"
        ),
        (
            "| `cohort_aware_query_router` | `human_context_needed` | `policy_clause` | "
            f"{signals.cohort_aware_human_context_to_policy.count} | "
            f"{signals.cohort_aware_human_context_to_policy.share} |"
        ),
        "",
        "Private query-cohort diagnostics:",
        "",
        "| system | route accuracy range across cohorts | max context-needed policy fallback |",
        "|---|---:|---:|",
        (
            "| `cohort_aware_query_router` | "
            f"{signals.cohort_route_signal.route_accuracy_range} | "
            f"{signals.cohort_route_signal.max_context_policy_fallback} |"
        ),
        "",
        "## Query Substrate Evidence",
        "",
        "| cohort | input rows | usable rows | avg chars | median chars | short messages | long contexts | question-like |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
        (
            "| `community_post_context` | "
            f"{signals.community_post_context.input_rows} | "
            f"{signals.community_post_context.usable_rows} | "
            f"{signals.community_post_context.avg_chars} | "
            f"{signals.community_post_context.median_chars} | "
            f"{signals.community_post_context.short_messages} | "
            f"{signals.community_post_context.long_contexts} | "
            f"{signals.community_post_context.question_like} |"
        ),
        (
            "| `messenger_conversation` | "
            f"{signals.messenger_conversation.input_rows} | "
            f"{signals.messenger_conversation.usable_rows} | "
            f"{signals.messenger_conversation.avg_chars} | "
            f"{signals.messenger_conversation.median_chars} | "
            f"{signals.messenger_conversation.short_messages} | "
            f"{signals.messenger_conversation.long_contexts} | "
            f"{signals.messenger_conversation.question_like} |"
        ),
        (
            "| `search_eval_query` | "
            f"{signals.search_eval_query.input_rows} | "
            f"{signals.search_eval_query.usable_rows} | "
            f"{signals.search_eval_query.avg_chars} | "
            f"{signals.search_eval_query.median_chars} | "
            f"{signals.search_eval_query.short_messages} | "
            f"{signals.search_eval_query.long_contexts} | "
            f"{signals.search_eval_query.question_like} |"
        ),
        "",
        "These substrate diagnostics explain why the repo keeps separate cohort,",
        "surface-form, normalization, and abstention slices. Long community posts,",
        "short live-style turns, and cleaned evaluation queries are not the same",
        "retrieval input distribution.",
        "",
        "## Intent/Surface Metadata Evidence",
        "",
        "| exported rows | top silver intent family | family share | top surface form | surface share | status |",
        "|---:|---|---:|---|---:|---|",
        (
            f"| {signals.intent_surface_signal.rows} | "
            f"`{signals.intent_surface_signal.top_family}` | "
            f"{signals.intent_surface_signal.top_family_share} | "
            f"`{signals.intent_surface_signal.top_surface}` | "
            f"{signals.intent_surface_signal.top_surface_share} | silver metadata; needs audit |"
        ),
        "",
        "The qid-only metadata export lets the same private qrels be sliced by",
        "intent family, surface form, and trap class without publishing raw text.",
        "These slices are useful for stress-test design, but still require human",
        "review before public frequency claims.",
        "",
        "## Route Surface Evidence",
        "",
        "| system | route accuracy | abstention recall | avg intent route spread | worst surface route accuracy | missing metadata |",
        "|---|---:|---:|---:|---:|---:|",
        (
            f"| `always_policy` | {signals.always_policy_route_surface.route_accuracy} | "
            f"{signals.always_policy_route_surface.abstention_recall} | "
            f"{signals.always_policy_route_surface.avg_intent_route_spread} | "
            f"{signals.always_policy_route_surface.worst_surface_route_accuracy} | "
            f"{signals.always_policy_route_surface.missing_metadata} |"
        ),
        (
            f"| `query_keyword_router` | {signals.keyword_route_surface.route_accuracy} | "
            f"{signals.keyword_route_surface.abstention_recall} | "
            f"{signals.keyword_route_surface.avg_intent_route_spread} | "
            f"{signals.keyword_route_surface.worst_surface_route_accuracy} | "
            f"{signals.keyword_route_surface.missing_metadata} |"
        ),
        (
            f"| `cohort_aware_query_router` | {signals.cohort_aware_route_surface.route_accuracy} | "
            f"{signals.cohort_aware_route_surface.abstention_recall} | "
            f"{signals.cohort_aware_route_surface.avg_intent_route_spread} | "
            f"{signals.cohort_aware_route_surface.worst_surface_route_accuracy} | "
            f"{signals.cohort_aware_route_surface.missing_metadata} |"
        ),
        "",
        "This is a route-only surface scorecard. It checks source-route and",
        "abstention robustness across surface conditions. Pair it with the",
        "runtime-surface diagnostics above to separate retrieval-hit failures",
        "from source-route failures.",
        "",
        "## Layer Attribution Evidence",
        "",
        "| artifact | current evidence | status |",
        "|---|---|---|",
        "| `reports/layer_attribution_fixture.md` | synthetic failures are decomposed into abstention, source-route, register, surface, evidence-form, and residual evidence-hit layers | fixture path only; human-gold attribution blocked |",
        "",
        "This is the measurement study's Table-2-style decomposition hook. It",
        "proves that the repo can explain where failure mass accumulates, but",
        "the public fixture does not promote layer percentages as final system",
        "claims. Human-audited route labels and private run outputs are still",
        "needed before this becomes a headline table.",
        "",
        "## Human Audit Coverage",
        "",
        "| audit rows | matched rows | route values | intent-family values | surface-form values | trap-class values | status |",
        "|---:|---:|---:|---:|---:|---:|---|",
        (
            f"| {signals.audit_coverage.audit_rows} | "
            f"{signals.audit_coverage.matched_rows} | "
            f"{signals.audit_coverage.route_coverage} | "
            f"{signals.audit_coverage.intent_coverage} | "
            f"{signals.audit_coverage.surface_coverage} | "
            f"{signals.audit_coverage.trap_coverage} | coverage only; labels incomplete |"
        ),
        "",
        "This confirms the private 300-row human audit workset covers every",
        "silver route, intent-family, surface-form, and trap-class value used by",
        "the diagnostics. It does not remove the human-label gate: reviewers still",
        "need to complete independent labels, agreement, adjudication, and validation.",
        "",
        "## Claim Control",
        "",
        "| gate | current value | required before headline use |",
        "|---|---:|---:|",
        f"| retrieval eval rows | {r.retrieval_n} | >= 500 |",
        f"| paired double-label rows | {r.agreement_paired_rows} | >= 50 |",
        f"| double-label Cohen's kappa | {r.agreement_kappa:.3f} | >= 0.600 |",
        f"| completed adjudicated route labels | {r.completed_route_labels} | >= 300 |",
        f"| route validation errors | {r.route_validation_errors} | 0 |",
        f"| system matrix not-run systems | {r.matrix_not_run} | 0 or narrow the claim |",
        f"| system matrix blocked systems | {r.matrix_blocked} | 0 |",
        f"| system matrix validation issues | {r.matrix_validation_issues} | 0 |",
        "",
        "The retrieval rows meet the diagnostic-size threshold, but source-route labels",
        "and the full system matrix do not yet have enough evidence: independent",
        "agreement, adjudicated human-gold coverage, and the missing analyzer/dense/hybrid/reranker runs still block headline use. Therefore this draft should",
        "not be presented as a final benchmark result.",
        "",
        "## Reproduction",
        "",
        "```bash",
        "make reproduce-table-1",
        "make reproduce-route-scorecard",
        "make reproduce-route-cohort-scorecard",
        "make reproduce-human-gold-rehearsal",
        "make reproduce-surface-scorecard",
        "make reproduce-route-surface-scorecard",
        "make reproduce-runtime-surface-scorecard",
        "make reproduce-layer-attribution",
        "make check-audit-surface-coverage",
        "make reproduce-normalization-ablation",
        "make reproduce-intent-inventory",
        "make reproduce-intent-surface-export",
        "make reproduce-substrate-profile",
        "make check-study-readiness",
        "make build-hero-signal",
        "make build-claim-ledger",
        "make build-probe-privacy-report",
        "make build-qualitative-gallery",
        "make build-system-matrix-report",
        "make verify",
        "make docker-demo",
        "```",
        "",
        "The public commands reproduce synthetic fixtures and regenerate aggregate",
        "claim-control reports. The public probe package is synthetic and",
        "screened by `reports/probe_privacy_report.md`; qualitative examples are",
        "generated at `reports/qualitative_gallery.md`, and layer attribution is",
        "generated at `reports/layer_attribution_fixture.md`. System coverage is",
        "tracked at `reports/system_matrix.md`. `make docker-demo` runs",
        "a short containerized reproduction path for reviewers. Private qid-only",
        "route runs and raw qrels stay outside the public repository.",
        "",
        "## Next Evidence",
        "",
        "1. Double-label at least 50 source-route rows and report agreement/kappa.",
        "2. Complete the 300-row adjudicated source-route workset.",
        "3. Validate it with zero route-label errors.",
        "4. Promote qid-only human labels and re-run the same route scorecard path.",
        "5. Run the missing analyzer/dense/hybrid/reranker comparisons or narrow the claim.",
        "6. Re-run retrieval comparisons sliced by human-gold source route.",
        "7. Replace this draft's diagnostic claims with human-audited findings only",
        "   if `reports/study_readiness.md` changes to GO.",
        "",
    ]
    return "\n".join(lines)
