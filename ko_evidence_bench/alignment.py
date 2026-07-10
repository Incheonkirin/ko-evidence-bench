"""Compact result-artifact inventory for the public repository."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .study_readiness import load_study_readiness, read


@dataclass(frozen=True)
class AlignmentItem:
    area: str
    status: str
    evidence: str
    why_it_matters: str


def has_text(path: Path, needle: str) -> bool:
    return path.exists() and needle in read(path)


def measured_or_missing(condition: bool) -> str:
    return "PASS" if condition else "MISSING"


def load_alignment_items(root: Path) -> list[AlignmentItem]:
    """Return the few artifacts a reviewer needs to validate the v0 study."""

    readiness = load_study_readiness(root)
    return [
        AlignmentItem(
            area="Measured retrieval result",
            status=measured_or_missing(
                has_text(root / "reports" / "measurement_study_v0.md", "Finding 1")
                and has_text(root / "reports" / "private_544_full_cross_scorecard.md", "structural_cross_text")
            ),
            evidence="544-row aggregate retrieval scorecard with paired bootstrap",
            why_it_matters="Shows a concrete ranking intervention and a measured lift.",
        ),
        AlignmentItem(
            area="Polarity stress result",
            status=measured_or_missing(
                (root / "reports" / "private_polarity_stress_pilot.json").exists()
                and (root / "scripts" / "reproduce_private_polarity_stress.py").exists()
                and has_text(root / "reports" / "private_polarity_stress_pilot.md", "seed pairs")
            ),
            evidence="444 counterfactual triples clustered into 37 seed evidence pairs",
            why_it_matters="Tests semantic direction, a failure mode hidden by ordinary recall.",
        ),
        AlignmentItem(
            area="Real-query distribution shift",
            status=measured_or_missing(
                has_text(root / "README.md", "Community posts and live chat are different retrieval inputs")
                and has_text(root / "reports" / "private_query_substrate_profile.md", "Cohort Shape Summary")
            ),
            evidence="aggregate community-context, messenger-turn, and cleaned-query profiles",
            why_it_matters="Explains why one corpus cannot stand in for every search input.",
        ),
        AlignmentItem(
            area="Evidence-sufficiency evaluator",
            status=measured_or_missing(
                has_text(root / "ko_evidence_bench" / "metrics.py", "evidence_coverage")
                and has_text(root / "docs" / "schemas.md", "required_evidence_ids")
            ),
            evidence="hit, coverage, and all-required-evidence scorecard semantics",
            why_it_matters="Prevents a single plausible clause from being counted as a complete answer.",
        ),
        AlignmentItem(
            area="Safe external-run contract",
            status=measured_or_missing(
                has_text(root / "ko_evidence_bench" / "system_matrix_bundle.py", "private_external_run")
                and has_text(root / "docs" / "schemas.md", "runner commit")
            ),
            evidence="qid-only bundles with qrel fingerprints and model provenance",
            why_it_matters="Lets the lab publish auditable results without publishing private inputs.",
        ),
        AlignmentItem(
            area="Clean-room public reproduction",
            status=measured_or_missing(
                (root / "probes" / "ko_evidence_probe_v0" / "queries.jsonl").exists()
                and (root / "scripts" / "check_probe_privacy.py").exists()
                and has_text(root / "README.md", "make docker-demo")
            ),
            evidence="synthetic public probes, tests, Docker demo, and privacy screen",
            why_it_matters="A reviewer can execute the scorecard without private data or services.",
        ),
        AlignmentItem(
            area="Public/private boundary",
            status=measured_or_missing(
                (root / "docs" / "data_statement.md").exists()
                and (root / "scripts" / "check_public_safety.py").exists()
            ),
            evidence="data statement and repository-wide leak scan",
            why_it_matters="The real query distribution can inform the work without becoming a data dump.",
        ),
        AlignmentItem(
            area="Human-validated source routing",
            status="PASS" if readiness.headline_ready else "PENDING",
            evidence=(
                f"{readiness.agreement_paired_rows}/50 paired labels; "
                f"{readiness.completed_route_labels}/300 adjudicated labels"
            ),
            why_it_matters="This is the next result required for source-routing effectiveness claims.",
        ),
        AlignmentItem(
            area="Full external-system matrix",
            status=(
                "PASS"
                if readiness.matrix_not_run == 0 and readiness.matrix_blocked == 0
                else "PENDING"
            ),
            evidence=(
                f"{readiness.matrix_implemented}/{readiness.matrix_systems} implemented; "
                f"{readiness.matrix_not_run} not run"
            ),
            why_it_matters="Expands the measured study from implemented paths to a full comparison.",
        ),
    ]


def overall_status(items: list[AlignmentItem]) -> str:
    if any(item.status == "MISSING" for item in items):
        return "INCOMPLETE"
    if any(item.status == "PENDING" for item in items):
        return "MEASURED V0"
    return "READY FOR EXPANDED STUDY"


def render_alignment_report(items: list[AlignmentItem]) -> str:
    lines = [
        "# Research Status",
        "",
        f"Overall status: **{overall_status(items)}**.",
        "",
        "This is a compact inventory of measured results and their reproduction",
        "paths. It is not a release gate ledger.",
        "",
        "| artifact | status | evidence | why it matters |",
        "|---|---|---|---|",
    ]
    for item in items:
        lines.append(
            f"| {item.area} | `{item.status}` | {item.evidence} | {item.why_it_matters} |"
        )
    lines.extend(
        [
            "",
            "## Current Position",
            "",
            "The repository already contains two measured technical results: a paired",
            "retrieval lift on a real-query-derived silver evaluation set and a clustered",
            "polarity stress study. The public package makes those measurements auditable",
            "without exposing raw inputs.",
            "",
            "## Next Results",
            "",
            "1. Complete independent route labels and publish a human-validated routing result.",
            "2. Import the remaining external analyzer, dense, hybrid, and reranker runs",
            "   through the provenance contract and compare them on the same evaluation slice.",
            "3. Add a genuinely labeled messenger-turn retrieval slice before claiming live-chat",
            "   degradation or improvement.",
            "",
        ]
    )
    return "\n".join(lines)
