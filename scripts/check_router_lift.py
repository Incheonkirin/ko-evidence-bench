#!/usr/bin/env python3
"""Check that the cohort-aware router keeps its silver diagnostic lift."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class RouterLiftSignals:
    baseline: str
    candidate: str
    baseline_route_accuracy: float
    candidate_route_accuracy: float
    baseline_abstention_recall: float
    candidate_abstention_recall: float
    candidate_delta_vs_always: float
    context_policy_fallback_rows: int

    @property
    def route_lift_pp(self) -> float:
        return self.candidate_route_accuracy - self.baseline_route_accuracy

    @property
    def abstention_recall_lift_pp(self) -> float:
        return self.candidate_abstention_recall - self.baseline_abstention_recall


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_percent(value: str) -> float:
    return float(value.strip().rstrip("%"))


def metric_value(report: str, system: str, metric: str) -> float:
    pattern = rf"\| {re.escape(system)} \| `{re.escape(metric)}` \| ([\d.]+%) \|"
    match = re.search(pattern, report)
    if not match:
        raise ValueError(f"missing metric: {system} {metric}")
    return parse_percent(match.group(1))


def route_delta(report: str, system: str) -> float:
    if "## Paired Delta vs `always_policy`" not in report:
        raise ValueError("missing paired delta section")
    delta_section = report.split("## Paired Delta vs `always_policy`", 1)[1]
    pattern = rf"\| {re.escape(system)} \| `route_accuracy` \| ([\d.]+%) \|"
    match = re.search(pattern, delta_section)
    if not match:
        raise ValueError(f"missing route delta: {system}")
    return parse_percent(match.group(1))


def confusion_count(report: str, system: str, gold: str, pred: str) -> int:
    pattern = rf"\| `{re.escape(system)}` \| `{re.escape(gold)}` \| `{re.escape(pred)}` \| ([\d,]+) \|"
    match = re.search(pattern, report)
    if not match:
        raise ValueError(f"missing confusion row: {system} {gold} -> {pred}")
    return int(match.group(1).replace(",", ""))


def load_signals(
    *,
    router_report: Path,
    route_scorecard: Path,
    baseline: str,
    candidate: str,
) -> RouterLiftSignals:
    router_text = read(router_report)
    scorecard_text = read(route_scorecard)
    return RouterLiftSignals(
        baseline=baseline,
        candidate=candidate,
        baseline_route_accuracy=metric_value(router_text, baseline, "route_accuracy"),
        candidate_route_accuracy=metric_value(router_text, candidate, "route_accuracy"),
        baseline_abstention_recall=metric_value(router_text, baseline, "abstention_recall"),
        candidate_abstention_recall=metric_value(router_text, candidate, "abstention_recall"),
        candidate_delta_vs_always=route_delta(router_text, candidate),
        context_policy_fallback_rows=confusion_count(
            scorecard_text,
            candidate,
            "human_context_needed",
            "policy_clause",
        ),
    )


def pass_fail(ok: bool) -> str:
    return "PASS" if ok else "FAIL"


def fmt_pp(value: float) -> str:
    return f"{value:.1f}%p"


def render_report(
    signals: RouterLiftSignals,
    *,
    min_route_lift_pp: float,
    min_abstention_recall_lift_pp: float,
    max_context_policy_fallback_rows: int,
) -> str:
    route_ok = signals.route_lift_pp >= min_route_lift_pp
    recall_ok = signals.abstention_recall_lift_pp >= min_abstention_recall_lift_pp
    fallback_ok = signals.context_policy_fallback_rows <= max_context_policy_fallback_rows
    status = "PASS" if route_ok and recall_ok and fallback_ok else "FAIL"
    lines = [
        "# Private Router Lift Gate",
        "",
        f"Status: **{status}**.",
        "",
        "This gate checks the checked-in silver diagnostic reports. It contains",
        "aggregate values only and does not include qids, raw queries, source names,",
        "conversation snippets, or platform identifiers.",
        "",
        f"- baseline: `{signals.baseline}`",
        f"- candidate: `{signals.candidate}`",
        "- label status: silver proxy, not human-gold",
        "",
        "## Gate Checks",
        "",
        "| check | current value | threshold | status |",
        "|---|---:|---:|---|",
        (
            f"| route accuracy lift vs `{signals.baseline}` | {fmt_pp(signals.route_lift_pp)} | "
            f">= {fmt_pp(min_route_lift_pp)} | `{pass_fail(route_ok)}` |"
        ),
        (
            f"| abstention recall lift vs `{signals.baseline}` | {fmt_pp(signals.abstention_recall_lift_pp)} | "
            f">= {fmt_pp(min_abstention_recall_lift_pp)} | `{pass_fail(recall_ok)}` |"
        ),
        (
            "| `human_context_needed -> policy_clause` fallback rows | "
            f"{signals.context_policy_fallback_rows} | <= {max_context_policy_fallback_rows} | "
            f"`{pass_fail(fallback_ok)}` |"
        ),
        "",
        "## Signal Snapshot",
        "",
        "| signal | value |",
        "|---|---:|",
        f"| `{signals.baseline}` route accuracy | {signals.baseline_route_accuracy:.1f}% |",
        f"| `{signals.candidate}` route accuracy | {signals.candidate_route_accuracy:.1f}% |",
        f"| `{signals.baseline}` abstention recall | {signals.baseline_abstention_recall:.1f}% |",
        f"| `{signals.candidate}` abstention recall | {signals.candidate_abstention_recall:.1f}% |",
        f"| `{signals.candidate}` paired delta vs `always_policy` | {fmt_pp(signals.candidate_delta_vs_always)} |",
        "",
        "## Use Notes",
        "",
        "- A passing gate means the silver diagnostic lift has not regressed.",
        "- It does not turn silver labels into human-gold headline claims.",
        "- If this fails, inspect router changes before updating public-facing diagnostics.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--router-report", type=Path, default=ROOT / "reports" / "private_route_router_baselines.md")
    parser.add_argument("--route-scorecard", type=Path, default=ROOT / "reports" / "private_route_scorecard_silver.md")
    parser.add_argument("--baseline", default="query_keyword_router")
    parser.add_argument("--candidate", default="cohort_aware_query_router")
    parser.add_argument("--min-route-lift-pp", type=float, default=10.0)
    parser.add_argument("--min-abstention-recall-lift-pp", type=float, default=30.0)
    parser.add_argument("--max-context-policy-fallback-rows", type=int, default=50)
    parser.add_argument("--out", type=Path, default=ROOT / "reports" / "private_router_lift_gate.md")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    signals = load_signals(
        router_report=args.router_report,
        route_scorecard=args.route_scorecard,
        baseline=args.baseline,
        candidate=args.candidate,
    )
    report = render_report(
        signals,
        min_route_lift_pp=args.min_route_lift_pp,
        min_abstention_recall_lift_pp=args.min_abstention_recall_lift_pp,
        max_context_policy_fallback_rows=args.max_context_policy_fallback_rows,
    )
    if args.check:
        current = read(args.out) if args.out.exists() else ""
        if current != report:
            print("router lift gate report is stale; run scripts/check_router_lift.py")
            return 1
    else:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(report, encoding="utf-8")
        print(report)

    failed = "`FAIL`" in report
    if failed:
        print("router lift gate failed", file=sys.stderr)
        return 1
    if args.check:
        print("router lift gate passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
