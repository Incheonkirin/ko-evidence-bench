# System Matrix Submission Template

Status: template only. It is not model output and must not be promoted.

This pack is a qid-only handoff for missing full-matrix system runs.
It intentionally excludes raw queries, source names, URLs, answers,
conversation snippets, and evidence text.

## Inputs

- qrels: `fixtures/surface_qrels.jsonl`
- system matrix: `docs/system_matrix.json`
- qids: 8

## Required Systems

- `bm25_nori`: analyzer_bm25 / retrieval
- `bm25_kiwi`: analyzer_bm25 / retrieval
- `bm25_mecab`: analyzer_bm25 / retrieval
- `dense_multilingual_encoder`: dense_retrieval / retrieval
- `dense_korean_encoder`: dense_retrieval / retrieval
- `hybrid_lexical_dense`: hybrid_retrieval / retrieval
- `cross_encoder_reranker`: reranker / reranking

## Run Row Schema

Each submitted run file must be JSONL with one row per qid:

```json
{"qid":"stable-id","route_pred":"policy_clause","abstained":false,"ranked":[{"evidence_id":"stable-evidence-id","source_tier":"policy_clause","score":1.0}]}
```

Allowed route labels: `claims_faq`, `dispute_case`, `expert_answer`, `human_context_needed`, `official_consumer_info`, `out_of_scope`, `policy_clause`, `product_disclosure`.

Use `ranked: []` when the system abstains. Ranked items may include only
`evidence_id`, `source_tier`, and optional numeric `score`.

## Promotion

After replacing templates with real run files, validate the bundle:

```bash
python3 scripts/validate_system_matrix_bundle.py \
  --bundle-dir /path/to/private_matrix_bundle \
  --qrels /path/to/private_qid_only_qrels.jsonl \
  --matrix docs/system_matrix.json \
  --out reports/private_system_matrix_bundle.md
```

Then run the promotion rehearsal. Promotion should remain blocked unless
the bundle has real run provenance, enough rows, complete qid coverage,
zero schema errors, and no raw fields.
