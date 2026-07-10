"""Readiness checks for the public measurement-study claim."""

from __future__ import annotations

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
        return "GO" if self.headline_ready else "NO-GO"


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
    polarity = read(root / "reports" / "private_polarity_stress_pilot.md")
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
    polarity_n = require_int(
        r"\| contrastive triples \| ([\d,]+) \|",
        polarity,
        name="polarity contrastive triples",
    )
    polarity_dense_wrong = require_percent(
        r"\| `dense_multilingual_encoder` \| [\d,]+ \| [\d,]+ \| ([\d.]+%) \|",
        polarity,
        name="dense polarity wrong-preferred rate",
    )
    polarity_reranker_wrong = require_percent(
        r"\| `cross_encoder_reranker` \| [\d,]+ \| [\d,]+ \| ([\d.]+%) \|",
        polarity,
        name="reranker polarity wrong-preferred rate",
    )
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
        "# Measurement Study Readiness",
        "",
        f"Status: **{readiness.status} for public headline claims**.",
        "",
        "This report is generated from aggregate-only checked-in reports. It is a",
        "claim-control gate: it prevents the repository from presenting private-lab",
        "diagnostics as final benchmark results before human route labels exist.",
        "",
        "## Evidence Snapshot",
        "",
        "| item | value | interpretation |",
        "|---|---:|---|",
        f"| retrieval eval rows | {readiness.retrieval_n} | enough for diagnostic CIs, still silver |",
        f"| best checked-in `clause@20` | {readiness.best_clause20} | retrieval signal, not answer quality |",
        f"| `always_policy` route accuracy | {readiness.always_policy_route_acc} | silver baseline only |",
        f"| query-keyword route accuracy | {readiness.keyword_route_acc} | silver baseline only |",
        f"| cohort-aware route accuracy | {readiness.cohort_aware_route_acc} | silver diagnostic only |",
        (
            f"| polarity stress pilot | {readiness.polarity_n} triples; "
            f"dense wrong-polarity {readiness.polarity_dense_wrong}; "
            f"reranker wrong-polarity {readiness.polarity_reranker_wrong} | "
            "aggregate pilot, not full matrix |"
        ),
        f"| paired double-label rows | {readiness.agreement_paired_rows} | needs at least 50 |",
        f"| double-label raw agreement | {readiness.agreement_raw} | audit quality signal |",
        f"| double-label Cohen's kappa | {readiness.agreement_kappa:.3f} | needs at least 0.600 |",
        f"| completed adjudicated route labels | {readiness.completed_route_labels} | needs at least 300 |",
        f"| route validation errors | {readiness.route_validation_errors} | must be 0 before headline use |",
        f"| system matrix implemented systems | {readiness.matrix_implemented} / {readiness.matrix_systems} | diagnostic coverage only |",
        f"| system matrix not-run systems | {readiness.matrix_not_run} | must be 0 for full comparison claims |",
        f"| system matrix blocked systems | {readiness.matrix_blocked} | must be 0 for headline use |",
        f"| system matrix validation issues | {readiness.matrix_validation_issues} | must be 0 |",
        "",
        "## Decision",
        "",
    ]
    if readiness.headline_ready:
        lines.extend(
            [
                "The measurement study can promote route metrics from diagnostic status to",
                "human-gold headline candidates, subject to final report review.",
                "",
            ]
        )
    else:
        lines.extend(
            [
                "Do not use the private-lab numbers as final public benchmark claims yet.",
                "The blocking gates are human-adjudicated source-route labels and",
                "complete system-matrix coverage: the current checked-in reports still",
                "lack paired reviewer labels, complete adjudicated labels, or the full analyzer/dense/hybrid/reranker comparison matrix.",
                "",
            ]
        )
    lines.extend(
        [
            "## Next Required Evidence",
            "",
            "1. Double-label at least 50 route rows and report raw agreement plus Cohen's kappa.",
            "2. Complete and validate the 300-row adjudicated route-label workset.",
            "3. Promote qid-only human labels and run the route scorecard on private route runs.",
            "4. Re-run the retrieval scorecard with human-gold source-route slices.",
            "5. Run the missing analyzer, dense, hybrid, and reranker comparisons or narrow the claim.",
            "6. Only then write the README/report headline around human-audited numbers.",
            "",
        ]
    )
    return "\n".join(lines)


def render_readme_signals(readiness: StudyReadiness) -> str:
    return "\n".join(
        [
            "<!-- BEGIN: current-verified-signals -->",
            "These are checked-in v0.1 silver diagnostics, not final benchmark claims:",
            "",
            "| Signal | Current Evidence | Status |",
            "|---|---:|---|",
            f"| Retrieval eval size | {readiness.retrieval_n} silver rows | scored with bootstrap CIs |",
            f"| Best checked-in `clause@20` | {readiness.best_clause20} | retrieval signal only |",
            f"| `always_policy` route accuracy | {readiness.always_policy_route_acc} | silver proxy |",
            f"| query-keyword route accuracy | {readiness.keyword_route_acc} | silver proxy |",
            f"| cohort-aware route accuracy | {readiness.cohort_aware_route_acc} | silver proxy |",
            (
                "| Polarity stress pilot | "
                f"{readiness.polarity_n} contrastive triples; dense wrong-polarity "
                f"{readiness.polarity_dense_wrong}; reranker wrong-polarity "
                f"{readiness.polarity_reranker_wrong} | aggregate pilot |"
            ),
            (
                "| Double-label agreement seed | "
                f"{readiness.agreement_paired_rows} / 50 paired; "
                f"kappa {readiness.agreement_kappa:.3f} | headline blocked |"
            ),
            (
                "| Adjudicated human route labels | "
                f"{readiness.completed_route_labels} / 300 complete | headline blocked |"
            ),
            (
                "| Full system comparison matrix | "
                f"{readiness.matrix_implemented} / {readiness.matrix_systems} implemented; "
                f"{readiness.matrix_not_run} not run; {readiness.matrix_blocked} blocked | headline blocked |"
            ),
            "",
            "The generated readiness report is intentionally conservative:",
            "`reports/study_readiness.md` currently says",
            f"**{readiness.status} for public headline claims** until the 50-row",
            "double-label seed, 300-row human route-label workset, and full system",
            "comparison matrix are completed and validated.",
            "<!-- END: current-verified-signals -->",
        ]
    )
