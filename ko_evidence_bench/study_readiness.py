"""Readiness checks for the public measurement-study claim."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from .system_matrix import load_matrix, matrix_summary, validate_matrix


@dataclass(frozen=True)
class StudyReadiness:
    retrieval_n: int
    best_clause20: str
    always_policy_route_acc: str
    keyword_route_acc: str
    cohort_aware_route_acc: str
    polarity_n: int
    polarity_dense_wrong: str
    polarity_reranker_wrong: str
    agreement_paired_rows: int
    agreement_raw: str
    agreement_kappa: float
    completed_route_labels: int
    route_validation_errors: int
    matrix_systems: int
    matrix_implemented: int
    matrix_not_run: int
    matrix_blocked: int
    matrix_validation_issues: int

    @property
    def headline_ready(self) -> bool:
        return (
            self.retrieval_n >= 500
            and self.agreement_paired_rows >= 50
            and self.agreement_kappa >= 0.6
            and self.completed_route_labels >= 300
            and self.route_validation_errors == 0
            and self.matrix_not_run == 0
            and self.matrix_blocked == 0
            and self.matrix_validation_issues == 0
        )

    @property
    def status(self) -> str:
        return "EXPANDED STUDY READY" if self.headline_ready else "MEASURED V0"


def read(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8")


def require_int(pattern: str, text: str, *, name: str) -> int:
    match = re.search(pattern, text, flags=re.MULTILINE)
    if not match:
        raise ValueError(f"missing {name}")
    return int(match.group(1).replace(",", ""))


def require_percent(pattern: str, text: str, *, name: str) -> str:
    match = re.search(pattern, text, flags=re.MULTILINE)
    if not match:
        raise ValueError(f"missing {name}")
    return match.group(1)


def require_float(pattern: str, text: str, *, name: str) -> float:
    match = re.search(pattern, text, flags=re.MULTILINE)
    if not match:
        raise ValueError(f"missing {name}")
    return float(match.group(1))


def load_study_readiness(root: Path) -> StudyReadiness:
    full_cross = read(root / "reports" / "private_544_full_cross_scorecard.md")
    route_scorecard = read(root / "reports" / "private_route_scorecard_silver.md")
    polarity = json.loads(read(root / "reports" / "private_polarity_stress_pilot.json"))
    agreement = read(root / "reports" / "private_route_audit_agreement_pending.md")
    validation = read(root / "reports" / "private_route_audit_validation_pending.md")
    matrix = load_matrix(root / "docs" / "system_matrix.json")
    matrix_issues = validate_matrix(matrix, root=root)
    matrix_counts = matrix_summary(matrix)

    retrieval_n = require_int(r"^- source result n: ([\d,]+)$", full_cross, name="retrieval n")
    best_clause20 = require_percent(
        r"\| structural_cross_text \| `clause@20` \| [\d,]+ \| ([\d.]+%) \|",
        full_cross,
        name="structural_cross_text clause@20",
    )
    always_policy_route_acc = require_percent(
        r"\| `always_policy` \| [\d,]+ \| [\d,]+ \| ([\d.]+%) \|",
        route_scorecard,
        name="always_policy route accuracy",
    )
    keyword_route_acc = require_percent(
        r"\| `query_keyword_router` \| [\d,]+ \| [\d,]+ \| ([\d.]+%) \|",
        route_scorecard,
        name="query keyword route accuracy",
    )
    cohort_aware_route_acc = require_percent(
        r"\| `cohort_aware_query_router` \| [\d,]+ \| [\d,]+ \| ([\d.]+%) \|",
        route_scorecard,
        name="cohort-aware route accuracy",
    )
    try:
        polarity_n = int(polarity["input"]["contrastive_triples"])
        polarity_systems = {str(row["system_id"]): row for row in polarity["systems"]}
        polarity_dense_wrong = f"{100 * float(polarity_systems['dense_bge_m3']['wrong_preferred_rate']):.1f}%"
        polarity_reranker_wrong = (
            f"{100 * float(polarity_systems['cross_encoder_bge_reranker_v2_m3']['wrong_preferred_rate']):.1f}%"
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("invalid private polarity stress aggregate") from exc
    agreement_paired_rows = require_int(
        r"^- paired completed rows: ([\d,]+)$",
        agreement,
        name="agreement paired completed rows",
    )
    agreement_raw = require_percent(
        r"^- raw agreement: ([\d.]+%)$",
        agreement,
        name="raw agreement",
    )
    agreement_kappa = require_float(
        r"^- Cohen's kappa: (-?[\d.]+)$",
        agreement,
        name="Cohen's kappa",
    )
    completed_route_labels = require_int(
        r"^- completed labels: ([\d,]+)$",
        validation,
        name="completed route labels",
    )
    route_validation_errors = require_int(
        r"^- rows with validation errors: ([\d,]+)$",
        validation,
        name="route validation errors",
    )

    return StudyReadiness(
        retrieval_n=retrieval_n,
        best_clause20=best_clause20,
        always_policy_route_acc=always_policy_route_acc,
        keyword_route_acc=keyword_route_acc,
        cohort_aware_route_acc=cohort_aware_route_acc,
        polarity_n=polarity_n,
        polarity_dense_wrong=polarity_dense_wrong,
        polarity_reranker_wrong=polarity_reranker_wrong,
        agreement_paired_rows=agreement_paired_rows,
        agreement_raw=agreement_raw,
        agreement_kappa=agreement_kappa,
        completed_route_labels=completed_route_labels,
        route_validation_errors=route_validation_errors,
        matrix_systems=int(matrix_counts["systems"]),
        matrix_implemented=int(matrix_counts["implemented"]),
        matrix_not_run=int(matrix_counts["not_run"]),
        matrix_blocked=int(matrix_counts["blocked"]),
        matrix_validation_issues=len(matrix_issues),
    )


def render_study_readiness(readiness: StudyReadiness) -> str:
    lines = [
        "# Measurement Evidence Scope",
        "",
        f"Status: **{readiness.status}**.",
        "",
        "This report separates measured aggregate v0 findings from the evidence",
        "needed for an expanded, human-validated source-routing study. Retrieval",
        "and polarity results below are reportable within their stated scope; they",
        "do not claim answer quality or completed source routing.",
        "",
        "## Evidence Snapshot",
        "",
        "| item | value | interpretation |",
        "|---|---:|---|",
        f"| retrieval eval rows | {readiness.retrieval_n} | aggregate silver retrieval study |",
        f"| best checked-in `clause@20` | {readiness.best_clause20} | measured clause recovery, not answer quality |",
        f"| `always_policy` route accuracy | {readiness.always_policy_route_acc} | candidate baseline; silver route labels |",
        f"| query-keyword route accuracy | {readiness.keyword_route_acc} | candidate baseline; silver route labels |",
        f"| cohort-aware route accuracy | {readiness.cohort_aware_route_acc} | candidate routing result; silver route labels |",
        (
            f"| polarity stress pilot | {readiness.polarity_n} triples; "
            f"dense wrong-polarity {readiness.polarity_dense_wrong}; "
            f"reranker wrong-polarity {readiness.polarity_reranker_wrong} | "
            "measured contrastive stress result; not a full system matrix |"
        ),
        f"| paired double-label rows | {readiness.agreement_paired_rows} | pending for human-validated routing |",
        f"| double-label raw agreement | {readiness.agreement_raw} | pending human-label agreement |",
        f"| double-label Cohen's kappa | {readiness.agreement_kappa:.3f} | pending human-label agreement |",
        f"| completed adjudicated route labels | {readiness.completed_route_labels} | pending expanded routing study |",
        f"| route validation errors | {readiness.route_validation_errors} | expected until route workset is labeled |",
        f"| system matrix implemented systems | {readiness.matrix_implemented} / {readiness.matrix_systems} | current comparison coverage |",
        f"| system matrix not-run systems | {readiness.matrix_not_run} | pending for full comparison claims |",
        f"| system matrix blocked systems | {readiness.matrix_blocked} | pending environment or model work |",
        f"| system matrix validation issues | {readiness.matrix_validation_issues} | 0 means checked-in manifests are valid |",
        "",
        "## Current Scope",
        "",
    ]
    if readiness.headline_ready:
        lines.extend(
            [
                "The measurement study includes the human-validated route evidence and",
                "full system matrix required for expanded comparison claims, subject to",
                "final report review.",
                "",
            ]
        )
    else:
        lines.extend(
            [
                "The current public finding set is clause recovery, polarity robustness,",
                "and query-substrate distribution under aggregate silver evaluation.",
                "It deliberately does not generalize those findings to human answer",
                "quality, production source routing, or a completed external-model",
                "leaderboard.",
                "",
            ]
        )
    lines.extend(
        [
            "## Pending Extensions",
            "",
            "1. Double-label at least 50 route rows and report raw agreement plus Cohen's kappa.",
            "2. Complete and validate the 300-row adjudicated route-label workset.",
            "3. Promote qid-only human labels and re-run source-routing slices.",
            "4. Run the remaining analyzer, dense, hybrid, and reranker comparisons for a full matrix.",
            "5. Add answer-quality labels only when making answer-quality claims.",
            "",
        ]
    )
    return "\n".join(lines)


def render_readme_signals(readiness: StudyReadiness) -> str:
    return "\n".join(
        [
            "<!-- BEGIN: current-verified-signals -->",
            "## Measured v0.1 Signals",
            "",
            "| Finding | Measured result |",
            "|---|---:|",
            (
                "| Clause retrieval | "
                f"{readiness.retrieval_n} silver qrels; best checked-in `clause@20` "
                f"{readiness.best_clause20} with bootstrap CIs |"
            ),
            (
                "| Polarity preservation | "
                f"{readiness.polarity_n} contrastive triples; dense wrong-polarity "
                f"{readiness.polarity_dense_wrong}; reranker wrong-polarity "
                f"{readiness.polarity_reranker_wrong} |"
            ),
            (
                "| Scope | Retrieval and polarity are aggregate silver studies; "
                "human-validated source routing and answer quality are deliberately reported separately |"
            ),
            "",
            "The result reports state exactly what each number measures and retain the",
            "public/private boundary; they do not release user text or copyrighted evidence.",
            "<!-- END: current-verified-signals -->",
        ]
    )
