# Measurement Evidence Scope

Status: **MEASURED V0**.

This report separates measured aggregate v0 findings from the evidence
needed for an expanded, human-validated source-routing study. Retrieval
and polarity results below are reportable within their stated scope; they
do not claim answer quality or completed source routing.

## Evidence Snapshot

| item | value | interpretation |
|---|---:|---|
| retrieval eval rows | 544 | aggregate silver retrieval study |
| best checked-in `clause@20` | 64.9% | measured clause recovery, not answer quality |
| `always_policy` route accuracy | 21.5% | candidate baseline; silver route labels |
| query-keyword route accuracy | 31.8% | candidate baseline; silver route labels |
| cohort-aware route accuracy | 46.9% | candidate routing result; silver route labels |
| polarity stress pilot | 444 triples; dense wrong-polarity 29.1%; reranker wrong-polarity 48.4% | measured contrastive stress result; not a full system matrix |
| paired double-label rows | 0 | pending for human-validated routing |
| double-label raw agreement | 0.0% | pending human-label agreement |
| double-label Cohen's kappa | 0.000 | pending human-label agreement |
| completed adjudicated route labels | 0 | pending expanded routing study |
| route validation errors | 300 | expected until route workset is labeled |
| system matrix implemented systems | 14 / 22 | current comparison coverage |
| system matrix not-run systems | 7 | pending for full comparison claims |
| system matrix blocked systems | 1 | pending environment or model work |
| system matrix validation issues | 0 | 0 means checked-in manifests are valid |

## Current Scope

The current public finding set is clause recovery, polarity robustness,
and query-substrate distribution under aggregate silver evaluation.
It deliberately does not generalize those findings to human answer
quality, production source routing, or a completed external-model
leaderboard.

## Pending Extensions

1. Double-label at least 50 route rows and report raw agreement plus Cohen's kappa.
2. Complete and validate the 300-row adjudicated route-label workset.
3. Promote qid-only human labels and re-run source-routing slices.
4. Run the remaining analyzer, dense, hybrid, and reranker comparisons for a full matrix.
5. Add answer-quality labels only when making answer-quality claims.
