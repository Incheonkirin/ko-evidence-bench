# Schemas

## Qrel Row

```json
{
  "qid": "syn_policy_001",
  "route_gold": "policy_clause",
  "allowed_source_tiers": ["policy_clause"],
  "should_abstain": false,
  "sufficient_evidence_ids": ["clause_cancer_diag"]
}
```

`sufficient_evidence_ids` is a one-of acceptable set for legacy qrels: one
matching evidence unit is enough to count an evidence hit. When an answer needs
several independently citable units, add `required_evidence_ids`:

```json
{
  "qid": "syn_coverage_with_limit_001",
  "route_gold": "policy_clause",
  "should_abstain": false,
  "sufficient_evidence_ids": ["clause_coverage", "table_limit"],
  "required_evidence_ids": ["clause_coverage", "table_limit"]
}
```

For this form, `evidence_hit@k` means top-k found at least one acceptable unit,
`evidence_coverage@k` is the share of required units recovered, and
`evidence_sufficiency@k` requires every listed unit. This prevents a single
plausible clause from being counted as a complete answer when a limit, exclusion,
or scope condition is also required.

`route_gold` values:

- `policy_clause`
- `product_disclosure`
- `official_consumer_info`
- `claims_faq`
- `dispute_case`
- `expert_answer`
- `human_context_needed`
- `out_of_scope`

## Run Row

```json
{
  "qid": "syn_policy_001",
  "route_pred": "policy_clause",
  "abstained": false,
  "ranked": [
    {
      "evidence_id": "clause_cancer_diag",
      "source_tier": "policy_clause"
    }
  ]
}
```

The schema is intentionally minimal. Private adapters may preserve raw text and
metadata internally, but public scoring only consumes stable ids, route labels,
abstention decisions, and ranked evidence ids.

`allowed_source_tiers` lets the qrel distinguish the primary route from allowed
supporting sources. For example, a dispute question may require a regulator or
dispute-case source while still allowing a policy clause as supporting evidence.

## Optional Surface-Robustness Fields

Surface-form scorecards can add two metadata fields to qrel rows:

```json
{
  "qid": "surface_bundle_abbrev",
  "intent_family": "bundled_coverage",
  "intent_id": "cancer_brain_heart_bundle",
  "surface_form": "abbreviated",
  "trap_classes": ["bundle_expansion", "abbreviation"],
  "route_gold": "policy_clause",
  "should_abstain": false,
  "sufficient_evidence_ids": ["clause_bundle_diag"]
}
```

`intent_family` is the publishable organizing unit for a family of related
information needs. Examples in this repo include bundled coverage, refund and
termination, and underwriting-context questions.

`intent_id` groups multiple phrasings of the same information need.
`surface_form` names the phrasing condition, such as `formal`, `colloquial`,
`abbreviated`, or `messenger_shorthand`. These fields let the public scorecard
measure whether one intent remains retrievable across consumer, messenger, and
formal wording without publishing raw query text.

`trap_classes` are optional diagnostic slices such as `bundle_expansion`,
`register_mismatch`, `product_table`, or `needs_private_context`. They are
annotations, not the benchmark's organizing unit.

## Public Probe Package

The public probe package uses three JSONL files:

```text
probes/ko_evidence_probe_v0/queries.jsonl
probes/ko_evidence_probe_v0/qrels.jsonl
probes/ko_evidence_probe_v0/evidence.jsonl
probes/ko_evidence_probe_v0/DATASET_CARD.md
```

`queries.jsonl` contains synthetic query text and intent metadata. `qrels.jsonl`
contains the source-route label and sufficient evidence ids for the same qid.
`evidence.jsonl` contains synthetic evidence snippets keyed by `evidence_id`.
`DATASET_CARD.md` is generated from those JSONL files and records release
status, intended use, non-goals, row counts, surface forms, routes, and
trap-class distributions.

Every row must use `provenance = "synthetic_public_fixture"` and pass
`make check-probe-privacy` before publication.

The same package can be exported to a BEIR-style retrieval subset:

```text
probes/ko_evidence_probe_v0/beir/corpus.jsonl
probes/ko_evidence_probe_v0/beir/queries.jsonl
probes/ko_evidence_probe_v0/beir/qrels/test.tsv
probes/ko_evidence_probe_v0/beir/query_metadata.jsonl
```

The BEIR qrels include answerable query-evidence pairs only. Source-route,
surface, trap, and abstention metadata remain in `query_metadata.jsonl` and the
original `qrels.jsonl`.

## System Matrix Run Bundle

The full analyzer, dense, hybrid, and reranker matrix uses a qid-only run bundle
so private text can remain outside the public repository:

```text
fixtures/system_matrix_bundle/manifest.json
fixtures/system_matrix_bundle/runs/{system_id}.jsonl
```

The public fixture bundle is a contract rehearsal, not external model output.
Real private bundles should use the same shape:

```json
{
  "label_status": "private silver run bundle; not human-gold",
  "provenance": {
    "kind": "private_external_run",
    "runner_commit": "git-revision",
    "corpus_fingerprint": "sha256:private-corpus-build",
    "qrels_fingerprint": "sha256:qid-only-qrels",
    "engine": "search-engine-version",
    "generated_at": "2026-07-10T00:00:00Z"
  },
  "systems": [
    {
      "system_id": "bm25_nori",
      "family": "analyzer_bm25",
      "stage": "retrieval",
      "run": "runs/bm25_nori.jsonl",
      "provenance": {
        "model_id": "analysis-nori-bm25",
        "model_revision": "config-or-model-revision"
      }
    }
  ]
}
```

Each run file uses the standard run row schema. To keep the public/private
boundary crisp, matrix bundle run rows may contain only `qid`, `route_pred`,
`abstained`, and `ranked`; ranked items may contain only `evidence_id`,
`source_tier`, and optional `score`. Raw queries, source names, URLs, usernames,
conversation text, and passage text must stay outside the bundle.

The manifest provenance is part of the run contract, not a public data export.
Every private external system must declare its runner commit, corpus and qrel
fingerprints, engine, model id/revision, and generation time. The validator
checks the qrel fingerprint against the supplied qrel file. Synthetic fixtures
use `kind: synthetic_fixture` and are never promotable as external model runs.

Run:

```bash
make validate-system-matrix-bundle
```

The validator checks that every runnable not-yet-run system in
`docs/system_matrix.json` has a run file, every run covers the same qids as the
qrels, and no non-qid-only fields were included.
