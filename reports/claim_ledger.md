# Claim Ledger

Status: **diagnostic claims only; human-gold headline claims blocked**.

This ledger is the public wording guard for the measurement study. It
separates what the checked-in aggregate evidence supports from what still
needs human labels, external replication, or rights-cleared data.

| claim area | status | allowed wording | do not say | next evidence |
|---|---|---|---|---|
| Clause recovery | `DIAGNOSTIC` | On the private silver qrel set, cross-text reranking improved `clause@20` from 56.4% to 64.9% with a paired delta of +8.5%p (95% CI 5.9% - 11.2%). | This is a final benchmark result or proof of answer quality. | Re-run after human-gold source-route labels and answer-quality audit. |
| Source routing | `DIAGNOSTIC` | On silver route labels, a cohort-aware router improved route accuracy from 21.5% to 46.9% versus the always-policy baseline (+25.4%p, 95% CI 19.3% - 31.2%). | The router is human-validated or production-safe. | Complete 300 adjudicated route labels and score the same route runs. |
| Unsafe policy fallback | `DIAGNOSTIC` | In silver diagnostics, context-needed rows routed to policy clauses fell from 190 to 28 rows (162 fewer fallback errors). | The system safely refuses all context-dependent questions. | Human-audit context-needed rows and report abstention precision/recall. |
| Surface robustness | `DIAGNOSTIC` | `structural_cross_text` reached 64.9% overall `clause@20`, but its worst surface slice was 44.4%, leaving a 20.5%p spread. | The system is robust to Korean surface-form variation. | Audit intent/surface metadata and rerun surface slices with human-gold labels. |
| Human-gold benchmark | `BLOCKED` | The human-gold gate is not open: 0/50 paired labels, kappa 0.000, 0/300 adjudicated labels, and 300 validation errors. | The private-lab numbers are final public benchmark claims. | Double-label 50 rows, complete 300 adjudications, validate with zero errors. |
| Full system comparison matrix | `BLOCKED` | The system matrix is explicit and incomplete: 13/21 systems are implemented, 7 are not run, and 1 is blocked. | The analyzer, dense, hybrid, and reranker comparison matrix is complete. | Run the missing systems or narrow the claim to the implemented diagnostics. |
| General Korean IR | `OUT OF SCOPE` | The method is intended to transfer, but the checked-in diagnostics are from one private Korean insurance search lab. | The results represent all Korean retrieval or all insurance search. | Run the same scorecard on another domain or independently built corpus. |
| Public data release | `OUT OF SCOPE` | The public repo releases schemas, metrics, synthetic fixtures, aggregate reports, and privacy-preserving reproduction paths. | Raw community crawls, messenger exports, or copyrighted corpora are included. | Add only rights-cleared public fixtures or build scripts with verified licenses. |

## Use Notes

- README and report prose should use the allowed wording until the
  human-gold gate opens.
- `DIAGNOSTIC` means useful engineering evidence, not a public benchmark
  headline.
- `BLOCKED` means the repo has the path and fixtures, but the private
  labels are not complete enough for the claim.
- `OUT OF SCOPE` means the project can discuss transferability as a
  hypothesis, not as a measured result.
