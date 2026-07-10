"""Small query-only source router baselines."""

from __future__ import annotations


DISPUTE_TERMS = ("거절", "부지급", "분쟁", "민원", "소송", "심사", "손해사정", "지급 거절", "거부")
CLAIMS_TERMS = ("청구", "서류", "접수", "팩스", "앱", "지급일", "지급기일")
PRODUCT_TERMS = ("환급", "해지", "해약", "보험료", "갱신", "만기", "사업비", "납입", "납부", "감액", "감액완납")
EXPERT_TERMS = ("전문가", "설계사", "상담", "추천")
BASE_CONTEXT_TERMS = ("내 보험", "제 보험", "가입한", "특약 있", "계약", "증권", "부담보", "고지")
CONTEXT_RISK_TERMS = BASE_CONTEXT_TERMS + (
    "가입",
    "가입했",
    "가입중",
    "가입되어",
    "들었",
    "들어",
    "보장받",
    "보상받",
    "청구 가능",
    "받을 수",
    "받을수",
    "가능",
    "되나요",
    "될까요",
    "되나",
    "되요",
    "해당",
    "수술했",
    "진단받",
    "입원",
    "치료",
    "검사",
    "병원",
    "진단서",
)

CONTEXT_PRIOR_COHORTS = {
    "expert_qna_archive",
    "general_forum_archive",
    "professional_forum_archive",
}


def _has(text: str, terms: tuple[str, ...]) -> bool:
    return any(term in text for term in terms)


def query_only_route(query: str) -> str:
    """Route a user query to a source tier using only surface text.

    This is intentionally a simple baseline, not the target model. It helps
    show whether source routing is already visible from query language alone.
    """

    text = query or ""
    if _has(text, DISPUTE_TERMS[:6]):
        return "dispute_case"
    if _has(text, CLAIMS_TERMS):
        return "claims_faq"
    if _has(text, PRODUCT_TERMS[:7]):
        return "product_disclosure"
    if _has(text, BASE_CONTEXT_TERMS):
        return "human_context_needed"
    if _has(text, EXPERT_TERMS):
        return "expert_answer"
    return "policy_clause"


def risk_aware_query_route(query: str) -> str:
    """Query-only router that explicitly prioritizes abstention risk.

    This is still a transparent baseline. It broadens the context-needed cue set
    while preserving source-specific cues for claims, disputes, products, and
    expert guidance.
    """

    text = query or ""
    if _has(text, DISPUTE_TERMS):
        return "dispute_case"
    if _has(text, CLAIMS_TERMS):
        return "claims_faq"
    if _has(text, PRODUCT_TERMS):
        return "product_disclosure"
    if _has(text, EXPERT_TERMS):
        return "expert_answer"
    if _has(text, CONTEXT_RISK_TERMS):
        return "human_context_needed"
    return "policy_clause"


def cohort_aware_query_route(query: str, query_cohort: str | None = None) -> str:
    """Route using query text plus a generic, privacy-safe query cohort.

    `query_cohort` is expected to be produced by a private source map. The
    router never needs raw source names.
    """

    route = risk_aware_query_route(query)
    if route != "policy_clause":
        return route
    if query_cohort in CONTEXT_PRIOR_COHORTS:
        return "human_context_needed"
    return route
