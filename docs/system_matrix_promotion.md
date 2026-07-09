# System Matrix Promotion Protocol

Status: promotion gate for future private full-matrix runs.

The system matrix report names analyzer, dense, hybrid, and reranker systems
that are still `not_run`. A run bundle is not enough to change those rows.
Before promotion, the bundle must pass mechanical, privacy, scale, and
provenance gates.

Start by creating a qid-only submission template:

```bash
python3 scripts/build_system_matrix_submission_pack.py \
  --qrels /path/to/private_qid_only_qrels.jsonl \
  --pack-dir /path/to/private_matrix_submission_template \
  --out reports/private_system_matrix_submission_pack.md
```

Each external runner fills one JSONL run file per missing system. The template
contains stable qids only and must stay free of raw queries, answers, source
names, URLs, conversation snippets, or evidence text.

## Gates

| gate | Required |
|---|---|
| `validation` | The run bundle has zero schema, qid coverage, duplicate, extra-qid, and leakage errors. |
| `required_systems` | The bundle contains all and only the missing runnable matrix systems. |
| `run_completeness` | Every system covers every qid exactly once. |
| `qid_only_screen` | Run files contain qids, route predictions, abstention flags, evidence ids, source tiers, and scores only. |
| `scale` | Private promotion uses at least 500 qrel rows unless the claim is explicitly narrowed. |
| `run_provenance` | The bundle describes real external-system output, not a synthetic fixture or import rehearsal. |

## What Promotion Means

Promotion may change a system row from `not_run` to diagnostic evidence only.
It does not make the repository headline-ready. Human source-route labels,
answer-quality labels, agreement reporting, and claim-control gates still apply.

The checked-in fixture should remain blocked by the promotion protocol. Its
purpose is to prove that the gate can reject fixture-only evidence while still
checking import, scoring, and privacy behavior.
