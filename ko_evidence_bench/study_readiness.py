"""Readiness checks for the public measurement-study claim."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class StudyReadiness:
    retrieval_n: int
    best_clause20: str
    always_policy_route_acc: str
    keyword_route_acc: str
    cohort_aware_route_acc: str
    agreement_paired_rows: int
    agreement_raw: str
    agreement_kappa: float
    completed_route_labels: int
    route_validation_errors: int

    @property
    def headline_ready(self) -> bool:
        return (
            self.retrieval_n >= 500
            and self.agreement_paired_rows >= 50
            and self.agreement_kappa >= 0.6
            and self.completed_route_labels >= 300
            and self.route_validation_errors == 0
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
    agreement = read(root / "reports" / "private_route_audit_agreement_pending.md")
    validation = read(root / "reports" / "private_route_audit_validation_pending.md")

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
        agreement_paired_rows=agreement_paired_rows,
        agreement_raw=agreement_raw,
        agreement_kappa=agreement_kappa,
        completed_route_labels=completed_route_labels,
        route_validation_errors=route_validation_errors,
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
        f"| paired double-label rows | {readiness.agreement_paired_rows} | needs at least 50 |",
        f"| double-label raw agreement | {readiness.agreement_raw} | audit quality signal |",
        f"| double-label Cohen's kappa | {readiness.agreement_kappa:.3f} | needs at least 0.600 |",
        f"| completed adjudicated route labels | {readiness.completed_route_labels} | needs at least 300 |",
        f"| route validation errors | {readiness.route_validation_errors} | must be 0 before headline use |",
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
                "The blocking gate is human-adjudicated source-route labels with",
                "independent agreement evidence: the current checked-in reports still",
                "lack paired reviewer labels, complete adjudicated labels, or both.",
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
            "5. Only then write the README/report headline around human-audited numbers.",
            "",
        ]
    )
    return "\n".join(lines)


def render_readme_signals(readiness: StudyReadiness) -> str:
    return "\n".join(
        [
            "<!-- BEGIN: current-verified-signals -->",
            "These are checked-in aggregate diagnostics, not final benchmark claims:",
            "",
            "| Signal | Current Evidence | Status |",
            "|---|---:|---|",
            f"| Retrieval eval size | {readiness.retrieval_n} silver rows | scored with bootstrap CIs |",
            f"| Best checked-in `clause@20` | {readiness.best_clause20} | retrieval signal only |",
            f"| `always_policy` route accuracy | {readiness.always_policy_route_acc} | silver proxy |",
            f"| query-keyword route accuracy | {readiness.keyword_route_acc} | silver proxy |",
            f"| cohort-aware route accuracy | {readiness.cohort_aware_route_acc} | silver proxy |",
            (
                "| Double-label agreement seed | "
                f"{readiness.agreement_paired_rows} / 50 paired; "
                f"kappa {readiness.agreement_kappa:.3f} | headline blocked |"
            ),
            (
                "| Adjudicated human route labels | "
                f"{readiness.completed_route_labels} / 300 complete | headline blocked |"
            ),
            "",
            "The generated readiness report is intentionally conservative:",
            "`reports/study_readiness.md` currently says",
            f"**{readiness.status} for public headline claims** until the 50-row",
            "double-label seed and 300-row human route-label workset are completed",
            "and validated.",
            "<!-- END: current-verified-signals -->",
        ]
    )
