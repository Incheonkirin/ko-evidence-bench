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
    completed_route_labels: int
    route_validation_errors: int

    @property
    def headline_ready(self) -> bool:
        return self.retrieval_n >= 500 and self.completed_route_labels >= 300 and self.route_validation_errors == 0

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


def load_study_readiness(root: Path) -> StudyReadiness:
    full_cross = read(root / "reports" / "private_544_full_cross_scorecard.md")
    route_scorecard = read(root / "reports" / "private_route_scorecard_silver.md")
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
                "The blocking gate is human-adjudicated source-route labels: the current",
                "checked-in validation report still has incomplete labels and validation",
                "errors.",
                "",
            ]
        )
    lines.extend(
        [
            "## Next Required Evidence",
            "",
            "1. Complete and validate the 300-row adjudicated route-label workset.",
            "2. Promote qid-only human labels and run the route scorecard on private route runs.",
            "3. Re-run the retrieval scorecard with human-gold source-route slices.",
            "4. Only then write the README/report headline around human-audited numbers.",
            "",
        ]
    )
    return "\n".join(lines)
