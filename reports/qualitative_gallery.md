# Qualitative Failure Gallery

Status: **synthetic qualitative examples only; human-gold headline claims blocked**.

This gallery gives a reviewer concrete examples behind the route and
surface diagnostics. Every query and evidence snippet is synthetic and
comes from `probes/ko_evidence_probe_v0/`.

## Gallery

| qid | query | gold route | failure layer | `policy_only_baseline` top result | `source_routed_candidate` top result | read |
|---|---|---|---|---|---|---|
| `probe-underwriting-messenger` | 예전에 치료받은 거 있는데 인수 가능해요? | `human_context_needed` | source routing / abstention | `policy_clause` / `ev-policy-noncovered-treatment`: A synthetic policy clause states that non-covered medical treatment is reimbursed only when the contract, treatment type, and special con... | `ABSTAIN` | The query needs private contract and underwriting context; citing a generic policy clause is unsafe. |
| `probe-claims-docs` | 보험금 청구할 때 진단서와 영수증 중 어떤 서류가 필요한가요? | `claims_faq` | source-tier mismatch | `policy_clause` / `ev-policy-bundle-diagnosis`: A synthetic policy clause states that cancer, cerebrovascular disease, and heart disease diagnosis benefits may be defined as separate co... | `claims_faq` / `ev-claims-document-checklist`: A synthetic claims FAQ says a claim may require a claim form, diagnosis document, treatment receipt, and identity confirmation depending ... | A claim-document question should land on claim-operation evidence, not only on policy wording. |
| `probe-refund-messenger` | 해지하면 환급금 얼마 나오는지 표 봐야 해요? | `product_disclosure` | register and evidence-form mismatch | `policy_clause` / `ev-policy-noncovered-treatment`: A synthetic policy clause states that non-covered medical treatment is reimbursed only when the contract, treatment type, and special con... | `product_disclosure` / `ev-disclosure-refund-table`: A synthetic product disclosure says that surrender value is checked in the refund table and depends on contract duration, paid premium, a... | A colloquial refund question needs a product disclosure table; a generic clause can look relevant but miss the answer form. |
| `probe-dispute-denial` | 보험금 지급 거절에 다투려면 분쟁 사례를 확인해야 하나요? | `dispute_case` | source-tier mismatch | `policy_clause` / `ev-policy-noncovered-treatment`: A synthetic policy clause states that non-covered medical treatment is reimbursed only when the contract, treatment type, and special con... | `dispute_case` / `ev-dispute-denial-case`: A synthetic dispute case summary explains that payment denial disputes should compare the denial reason, policy wording, submitted record... | A denial dispute needs dispute-case evidence; policy clauses may be supporting context, not the primary source. |

## What To Inspect

- The baseline is intentionally route-naive: it shows what goes wrong when
  every question is forced toward policy-clause evidence.
- The candidate is not a production system. It is a compact demonstration
  of the source-route behavior the benchmark is meant to measure.
- These examples should be read with the claim ledger: they illustrate
  diagnostic failure modes, not final benchmark performance.
