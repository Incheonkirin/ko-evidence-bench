"""Export the public probe package to a BEIR-style layout."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class BeirExport:
    corpus: list[dict[str, str]]
    queries: list[dict[str, str]]
    qrels: list[dict[str, str | int]]
    query_metadata: list[dict[str, Any]]
    skipped_abstention_qids: list[str]


def _qid_order(rows: list[dict[str, Any]]) -> dict[str, int]:
    return {str(row["qid"]): index for index, row in enumerate(rows)}


def export_beir_probe(
    queries: list[dict[str, Any]],
    qrels: list[dict[str, Any]],
    evidence: list[dict[str, Any]],
) -> BeirExport:
    """Convert probe JSONL rows into a BEIR-compatible retrieval subset.

    BEIR qrels do not represent "should abstain" rows, so those rows are
    exported only through query metadata and listed in the report summary.
    """

    qrel_by_qid = {str(row["qid"]): row for row in qrels}
    query_order = _qid_order(queries)

    corpus = [
        {
            "_id": str(row["evidence_id"]),
            "title": str(row.get("title") or ""),
            "text": str(row.get("search_text") or row.get("text") or ""),
        }
        for row in evidence
    ]

    beir_queries: list[dict[str, str]] = []
    query_metadata: list[dict[str, Any]] = []
    beir_qrels: list[dict[str, str | int]] = []
    skipped_abstention_qids: list[str] = []

    for query in sorted(queries, key=lambda row: query_order[str(row["qid"])]):
        qid = str(query["qid"])
        qrel = qrel_by_qid[qid]
        beir_queries.append({"_id": qid, "text": str(query.get("query") or "")})
        query_metadata.append(
            {
                "qid": qid,
                "intent_family": str(qrel.get("intent_family") or query.get("intent_family") or ""),
                "intent_id": str(qrel.get("intent_id") or query.get("intent_id") or ""),
                "surface_form": str(qrel.get("surface_form") or query.get("surface_form") or ""),
                "trap_classes": list(qrel.get("trap_classes") or query.get("trap_classes") or []),
                "route_gold": str(qrel.get("route_gold") or ""),
                "should_abstain": bool(qrel.get("should_abstain")),
            }
        )
        if qrel.get("should_abstain"):
            skipped_abstention_qids.append(qid)
            continue
        for evidence_id in qrel.get("sufficient_evidence_ids") or []:
            beir_qrels.append({"query-id": qid, "corpus-id": str(evidence_id), "score": 1})

    return BeirExport(
        corpus=corpus,
        queries=beir_queries,
        qrels=beir_qrels,
        query_metadata=query_metadata,
        skipped_abstention_qids=skipped_abstention_qids,
    )


def validate_beir_export(export: BeirExport) -> list[str]:
    """Return validation issues for the generated BEIR-style package."""

    issues: list[str] = []
    corpus_ids = {row["_id"] for row in export.corpus}
    query_ids = {row["_id"] for row in export.queries}
    metadata_ids = {row["qid"] for row in export.query_metadata}

    if len(corpus_ids) != len(export.corpus):
        issues.append("duplicate corpus ids")
    if len(query_ids) != len(export.queries):
        issues.append("duplicate query ids")
    if query_ids != metadata_ids:
        issues.append("query metadata ids do not match query ids")
    for row in export.qrels:
        if str(row["query-id"]) not in query_ids:
            issues.append(f"qrel query not exported: {row['query-id']}")
        if str(row["corpus-id"]) not in corpus_ids:
            issues.append(f"qrel corpus id not exported: {row['corpus-id']}")
    answerable_qids = query_ids - set(export.skipped_abstention_qids)
    qrel_qids = {str(row["query-id"]) for row in export.qrels}
    if not answerable_qids.issubset(qrel_qids):
        missing = sorted(answerable_qids - qrel_qids)
        issues.append(f"answerable queries without qrels: {','.join(missing)}")
    return issues
