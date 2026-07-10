# Research Status

Overall status: **MEASURED V0**.

This is a compact inventory of measured results and their reproduction
paths. It is not a release gate ledger.

| artifact | status | evidence | why it matters |
|---|---|---|---|
| Measured retrieval result | `PASS` | 544-row aggregate retrieval scorecard with paired bootstrap | Shows a concrete ranking intervention and a measured lift. |
| Polarity stress result | `PASS` | 444 counterfactual triples clustered into 37 seed evidence pairs | Tests semantic direction, a failure mode hidden by ordinary recall. |
| Real-query distribution shift | `PASS` | aggregate community-context, messenger-turn, and cleaned-query profiles | Explains why one corpus cannot stand in for every search input. |
| Evidence-sufficiency evaluator | `PASS` | hit, coverage, and all-required-evidence scorecard semantics | Prevents a single plausible clause from being counted as a complete answer. |
| Safe external-run contract | `PASS` | qid-only bundles with qrel fingerprints and model provenance | Lets the lab publish auditable results without publishing private inputs. |
| Clean-room public reproduction | `PASS` | synthetic public probes, tests, Docker demo, and privacy screen | A reviewer can execute the scorecard without private data or services. |
| Public/private boundary | `PASS` | data statement and repository-wide leak scan | The real query distribution can inform the work without becoming a data dump. |
| Human-validated source routing | `PENDING` | 0/50 paired labels; 0/300 adjudicated labels | This is the next result required for source-routing effectiveness claims. |
| Full external-system matrix | `PENDING` | 14/22 implemented; 7 not run | Expands the measured study from implemented paths to a full comparison. |

## Current Position

The repository already contains two measured technical results: a paired
retrieval lift on a real-query-derived silver evaluation set and a clustered
polarity stress study. The public package makes those measurements auditable
without exposing raw inputs.

## Next Results

1. Complete independent route labels and publish a human-validated routing result.
2. Import the remaining external analyzer, dense, hybrid, and reranker runs
   through the provenance contract and compare them on the same evaluation slice.
3. Add a genuinely labeled messenger-turn retrieval slice before claiming live-chat
   degradation or improvement.
