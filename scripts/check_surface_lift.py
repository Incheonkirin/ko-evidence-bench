#!/usr/bin/env python3
"""Check that the surface-robust candidate reduces surface fragility."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class SurfaceSummary:
    task_success: float
    avg_intent_spread: float
    worst_surface: float
    missing_metadata: int


@dataclass(frozen=True)
class SurfaceLiftSignals:
    baseline: str
    candidate: str
    baseline_summary: SurfaceSummary
    candidate_summary: SurfaceSummary

    @property
    def task_success_lift_pp(self) -> float:
        return self.candidate_summary.task_success - self.baseline_summary.task_success

    @property
    def spread_reduction_pp(self) -> float:
        return self.baseline_summary.avg_intent_spread - self.candidate_summary.avg_intent_spread

    @property
    def worst_surface_lift_pp(self) -> float:
        return self.candidate_summary.worst_surface - self.baseline_summary.worst_surface


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_percent(value: str) -> float:
    return float(value.strip().rstrip("%"))


def summary_row(report: str, system: str) -> SurfaceSummary:
    pattern = (
        rf"\| `{re.escape(system)}` \| \d+ \| \d+ \| \d+ \| "
        rf"([\d.]+%) \| [\d.]+% \| [\d.]+% \| ([\d.]+%) \| "
        rf"[\d.]+% \| ([\d.]+%) \| (\d+) \|"
    )
    match = re.search(pattern, report)
    if not match:
        raise ValueError(f"missing surface summary row: {system}")
    return SurfaceSummary(
        task_success=parse_percent(match.group(1)),
        avg_intent_spread=parse_percent(match.group(2)),
        worst_surface=parse_percent(match.group(3)),
        missing_metadata=int(match.group(4)),
    )


def load_signals(*, surface_report: Path, baseline: str, candidate: str) -> SurfaceLiftSignals:
    report = read(surface_report)
    return SurfaceLiftSignals(
        baseline=baseline,
        candidate=candidate,
        baseline_summary=summary_row(report, baseline),
        candidate_summary=summary_row(report, candidate),
    )


def pass_fail(ok: bool) -> str:
    return "PASS" if ok else "FAIL"


def fmt_pp(value: float) -> str:
    return f"{value:.1f}%p"


def render_report(
    signals: SurfaceLiftSignals,
    *,
    min_task_success_lift_pp: float,
    min_spread_reduction_pp: float,
    min_worst_surface_lift_pp: float,
    max_missing_metadata: int,
) -> str:
    task_ok = signals.task_success_lift_pp >= min_task_success_lift_pp
    spread_ok = signals.spread_reduction_pp >= min_spread_reduction_pp
    worst_ok = signals.worst_surface_lift_pp >= min_worst_surface_lift_pp
    metadata_ok = signals.candidate_summary.missing_metadata <= max_missing_metadata
    status = "PASS" if task_ok and spread_ok and worst_ok and metadata_ok else "FAIL"

    lines = [
        "# Surface Robustness Lift Gate",
        "",
        f"Status: **{status}**.",
        "",
        "This gate checks the synthetic surface-form robustness report. It contains",
        "aggregate values only and does not include qids, raw queries, source names,",
        "conversation snippets, or platform identifiers.",
        "",
        f"- baseline: `{signals.baseline}`",
        f"- candidate: `{signals.candidate}`",
        "- label status: synthetic fixture, not human-gold",
        "",
        "## Gate Checks",
        "",
        "| check | current value | threshold | status |",
        "|---|---:|---:|---|",
        (
            f"| task success lift vs `{signals.baseline}` | {fmt_pp(signals.task_success_lift_pp)} | "
            f">= {fmt_pp(min_task_success_lift_pp)} | `{pass_fail(task_ok)}` |"
        ),
        (
            f"| average intent-spread reduction | {fmt_pp(signals.spread_reduction_pp)} | "
            f">= {fmt_pp(min_spread_reduction_pp)} | `{pass_fail(spread_ok)}` |"
        ),
        (
            f"| worst-surface lift vs `{signals.baseline}` | {fmt_pp(signals.worst_surface_lift_pp)} | "
            f">= {fmt_pp(min_worst_surface_lift_pp)} | `{pass_fail(worst_ok)}` |"
        ),
        (
            f"| candidate rows missing surface metadata | {signals.candidate_summary.missing_metadata} | "
            f"<= {max_missing_metadata} | `{pass_fail(metadata_ok)}` |"
        ),
        "",
        "## Signal Snapshot",
        "",
        "| signal | baseline | candidate |",
        "|---|---:|---:|",
        (
            f"| task success | {signals.baseline_summary.task_success:.1f}% | "
            f"{signals.candidate_summary.task_success:.1f}% |"
        ),
        (
            f"| average intent spread | {signals.baseline_summary.avg_intent_spread:.1f}% | "
            f"{signals.candidate_summary.avg_intent_spread:.1f}% |"
        ),
        (
            f"| worst-surface success | {signals.baseline_summary.worst_surface:.1f}% | "
            f"{signals.candidate_summary.worst_surface:.1f}% |"
        ),
        "",
        "## Use Notes",
        "",
        "- A passing gate means the synthetic surface-robustness demonstration has not regressed.",
        "- It does not create a private or human-gold surface benchmark by itself.",
        "- Private qrels still need audited `intent_id` and `surface_form` metadata for headline use.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--surface-report", type=Path, default=ROOT / "reports" / "surface_scorecard_fixture.md")
    parser.add_argument("--baseline", default="formal_only_demo")
    parser.add_argument("--candidate", default="surface_robust_demo")
    parser.add_argument("--min-task-success-lift-pp", type=float, default=30.0)
    parser.add_argument("--min-spread-reduction-pp", type=float, default=30.0)
    parser.add_argument("--min-worst-surface-lift-pp", type=float, default=30.0)
    parser.add_argument("--max-missing-metadata", type=int, default=0)
    parser.add_argument("--out", type=Path, default=ROOT / "reports" / "surface_lift_gate.md")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    signals = load_signals(
        surface_report=args.surface_report,
        baseline=args.baseline,
        candidate=args.candidate,
    )
    report = render_report(
        signals,
        min_task_success_lift_pp=args.min_task_success_lift_pp,
        min_spread_reduction_pp=args.min_spread_reduction_pp,
        min_worst_surface_lift_pp=args.min_worst_surface_lift_pp,
        max_missing_metadata=args.max_missing_metadata,
    )
    if args.check:
        current = read(args.out) if args.out.exists() else ""
        if current != report:
            print("surface lift gate report is stale; run scripts/check_surface_lift.py")
            return 1
    else:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(report, encoding="utf-8")
        print(report)

    failed = "`FAIL`" in report
    if failed:
        print("surface lift gate failed", file=sys.stderr)
        return 1
    if args.check:
        print("surface lift gate passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
