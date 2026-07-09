"""Flagship artifact alignment checks."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .study_readiness import StudyReadiness, load_study_readiness, read


@dataclass(frozen=True)
class AlignmentItem:
    area: str
    status: str
    evidence: str
    why_it_matters: str


def has_text(path: Path, needle: str) -> bool:
    return path.exists() and needle in read(path)


def load_alignment_items(root: Path) -> list[AlignmentItem]:
    readiness = load_study_readiness(root)
    return [
        AlignmentItem(
            area="Report-first artifact",
            status="PASS" if (root / "reports" / "measurement_study_draft.md").exists() else "MISSING",
            evidence="reports/measurement_study_draft.md",
            why_it_matters="The study is the product; code is the reproduction apparatus.",
        ),
        AlignmentItem(
            area="Generated finding table",
            status=(
                "PASS"
                if has_text(root / "reports" / "measurement_study_draft.md", "## Current Finding Candidates")
                else "MISSING"
            ),
            evidence="finding candidates are generated from aggregate reports",
            why_it_matters="Reviewers see numbers and claim controls before framework plumbing.",
        ),
        AlignmentItem(
            area="Claim-control gate",
            status="PASS" if (root / "reports" / "study_readiness.md").exists() else "MISSING",
            evidence=f"study readiness is {readiness.status}",
            why_it_matters="The repo refuses to promote silver diagnostics as final benchmark claims.",
        ),
        AlignmentItem(
            area="README signal drift guard",
            status=(
                "PASS"
                if has_text(root / "README.md", "<!-- BEGIN: current-verified-signals -->")
                else "MISSING"
            ),
            evidence="scripts/sync_readme_signals.py --check",
            why_it_matters="The first-screen numbers are generated from checked-in evidence.",
        ),
        AlignmentItem(
            area="Qid-only route scorecard path",
            status=(
                "PASS"
                if (root / "reports" / "private_route_scorecard_silver.md").exists()
                and (root / "scripts" / "export_route_runs.py").exists()
                else "MISSING"
            ),
            evidence="private silver runs are scored through the same path as future human labels",
            why_it_matters="The evaluation path is tested before human-gold labels arrive.",
        ),
        AlignmentItem(
            area="Human audit workflow",
            status=(
                "PASS"
                if (root / "tools" / "route_review_ui.html").exists()
                and (root / "reports" / "route_audit_workflow_fixture.md").exists()
                else "MISSING"
            ),
            evidence="review UI plus synthetic audit workflow dry-run",
            why_it_matters="The remaining work is label production, not missing audit plumbing.",
        ),
        AlignmentItem(
            area="Human-label progress gate",
            status=(
                "PASS"
                if (root / "scripts" / "check_route_review_progress.py").exists()
                and (root / "scripts" / "build_route_review_brief.py").exists()
                and (root / "reports" / "private_route_review_brief_300_adjudicated.md").exists()
                and (root / "reports" / "private_route_review_progress_300_adjudicated.md").exists()
                else "MISSING"
            ),
            evidence="300-row adjudication CSV brief and progress are summarized without raw rows",
            why_it_matters="The remaining human task can be prioritized and tracked before import and promotion.",
        ),
        AlignmentItem(
            area="Human-gold route labels",
            status="PASS" if readiness.headline_ready else "BLOCKED",
            evidence=(
                f"{readiness.completed_route_labels}/300 adjudicated labels complete; "
                f"{readiness.route_validation_errors} validation errors"
            ),
            why_it_matters="This is the required gate before public headline claims.",
        ),
        AlignmentItem(
            area="Public/private boundary",
            status=(
                "PASS"
                if (root / "docs" / "data_statement.md").exists()
                and (root / "scripts" / "check_public_safety.py").exists()
                else "MISSING"
            ),
            evidence="data statement plus public-safety scan",
            why_it_matters="The private logs ground the work without leaking raw rows.",
        ),
        AlignmentItem(
            area="CI verification",
            status=(
                "PASS"
                if has_text(root / "Makefile", "check-measurement-study")
                and has_text(root / "Makefile", "check-readme-signals")
                and has_text(root / ".github" / "workflows" / "ci.yml", "make verify")
                else "MISSING"
            ),
            evidence="make verify in GitHub Actions",
            why_it_matters="The repo continuously checks reports, claims, fixtures, and safety.",
        ),
    ]


def overall_status(items: list[AlignmentItem]) -> str:
    if any(item.status == "MISSING" for item in items):
        return "INCOMPLETE"
    if any(item.status == "BLOCKED" for item in items):
        return "NO-GO FOR HEADLINE CLAIMS"
    return "GO FOR HEADLINE CLAIM REVIEW"


def render_alignment_report(items: list[AlignmentItem]) -> str:
    lines = [
        "# Flagship Alignment",
        "",
        f"Overall status: **{overall_status(items)}**.",
        "",
        "This report checks whether the repository is shaped as a measurement-study",
        "artifact rather than a loose evaluation framework. It intentionally separates",
        "implemented infrastructure from the human-label gate that still blocks public",
        "headline claims.",
        "",
        "| area | status | evidence | why it matters |",
        "|---|---|---|---|",
    ]
    for item in items:
        lines.append(
            f"| {item.area} | `{item.status}` | {item.evidence} | {item.why_it_matters} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The repo now has the public shell expected of a flagship measurement study:",
            "generated study draft, claim-control gates, qid-only scorecards, audit",
            "workflow, and public-safety checks. It is not headline-ready because the",
            "source-route labels are still silver rather than human-adjudicated.",
            "",
            "## Next Gate",
            "",
            "Complete the 300-row adjudicated route-label workset, validate it with zero",
            "errors, promote qid-only human labels, and rerun the route scorecard and",
            "measurement-study draft.",
            "",
        ]
    )
    return "\n".join(lines)
