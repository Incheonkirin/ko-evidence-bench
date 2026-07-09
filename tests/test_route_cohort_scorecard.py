import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


class RouteCohortScorecardTest(unittest.TestCase):
    def test_report_uses_generic_cohorts_and_hides_raw_sources(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            qrels = tmp_path / "qrels.jsonl"
            labels = tmp_path / "labels.jsonl"
            run_dir = tmp_path / "runs"
            source_map = tmp_path / "source_map.json"
            report_path = tmp_path / "report.md"
            run_dir.mkdir()

            write_jsonl(
                qrels,
                [
                    {"qid": "q1", "source": "raw-private-alpha", "query": "private text"},
                    {"qid": "q2", "source": "raw-private-beta", "query": "private text"},
                    {"qid": "q3", "source": "raw-private-alpha", "query": "private text"},
                ],
            )
            write_jsonl(
                labels,
                [
                    {"qid": "q1", "route_gold": "policy_clause", "should_abstain": False},
                    {"qid": "q2", "route_gold": "human_context_needed", "should_abstain": True},
                    {"qid": "q3", "route_gold": "claims_faq", "should_abstain": False},
                ],
            )
            write_jsonl(
                run_dir / "candidate.jsonl",
                [
                    {"qid": "q1", "route_pred": "policy_clause", "abstained": False},
                    {"qid": "q2", "route_pred": "policy_clause", "abstained": False},
                    {"qid": "q3", "route_pred": "claims_faq", "abstained": False},
                ],
            )
            source_map.write_text(
                json.dumps(
                    {
                        "default_cohort": "unmapped_private_source",
                        "cohorts": {
                            "raw-private-alpha": "forum_archive",
                            "raw-private-beta": "expert_qna_archive",
                        },
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            subprocess.run(
                [
                    sys.executable,
                    "scripts/reproduce_route_cohort_scorecard.py",
                    "--qrels",
                    str(qrels),
                    "--labels",
                    str(labels),
                    "--run-dir",
                    str(run_dir),
                    "--source-map",
                    str(source_map),
                    "--out",
                    str(report_path),
                    "--fail-on-unmapped",
                ],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )

            report = report_path.read_text(encoding="utf-8")
            self.assertIn("Route Cohort Scorecard", report)
            self.assertIn("`forum_archive`", report)
            self.assertIn("`expert_qna_archive`", report)
            self.assertIn("| `candidate` | `expert_qna_archive` | 1 | 1 | 100.0% |", report)
            self.assertNotIn("raw-private-alpha", report)
            self.assertNotIn("raw-private-beta", report)
            self.assertNotIn("private text", report)

    def test_fail_on_unmapped(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            qrels = tmp_path / "qrels.jsonl"
            labels = tmp_path / "labels.jsonl"
            run_dir = tmp_path / "runs"
            source_map = tmp_path / "source_map.json"
            run_dir.mkdir()

            write_jsonl(qrels, [{"qid": "q1", "source": "raw-private-alpha"}])
            write_jsonl(labels, [{"qid": "q1", "route_gold": "policy_clause", "should_abstain": False}])
            write_jsonl(run_dir / "candidate.jsonl", [{"qid": "q1", "route_pred": "policy_clause", "abstained": False}])
            source_map.write_text('{"cohorts": {}, "default_cohort": "unmapped_private_source"}', encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/reproduce_route_cohort_scorecard.py",
                    "--qrels",
                    str(qrels),
                    "--labels",
                    str(labels),
                    "--run-dir",
                    str(run_dir),
                    "--source-map",
                    str(source_map),
                    "--out",
                    str(tmp_path / "report.md"),
                    "--fail-on-unmapped",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )

            self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
