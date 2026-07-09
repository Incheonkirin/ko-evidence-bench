"""Small query-only source router baselines."""

from __future__ import annotations


def _has(text: str, terms: tuple[str, ...]) -> bool:
    return any(term in text for term in terms)


def query_only_route(query: str) -> str:
    """Route a user query to a source tier using only surface text.

    This is intentionally a simple baseline, not the flagship model. It helps
    show whether source routing is already visible from query language alone.
    """

    text = query or ""
    if _has(text, ("거절", "부지급", "분쟁", "민원", "소송", "심사")):
        return "dispute_case"
    if _has(text, ("청구", "서류", "접수", "팩스", "앱", "지급일", "지급기일")):
        return "claims_faq"
    if _has(text, ("환급", "해지", "해약", "보험료", "갱신", "만기", "사업비")):
        return "product_disclosure"
    if _has(text, ("내 보험", "제 보험", "가입한", "특약 있", "계약", "증권", "부담보", "고지")):
        return "human_context_needed"
    if _has(text, ("전문가", "설계사", "상담", "추천")):
        return "expert_answer"
    return "policy_clause"
