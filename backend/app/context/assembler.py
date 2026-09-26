"""Hybrid retrieval: structured metadata filters plus semantic vector rank."""

from __future__ import annotations

from app.evidence.embeddings import FakeEmbedder, OpenAIEmbedder
from app.evidence.store import EvidenceStore
from app.logging_config import get_logger
from app.schemas.models import EvidenceRecord, StoredEvidence

logger = get_logger(__name__)

EVIDENCE_CAP = 12
SEMANTIC_LIMIT = 8


def hybrid_retrieve(
    store: EvidenceStore,
    *,
    account_id: str,
    domain: str,
    claim: str,
    embedder: FakeEmbedder | OpenAIEmbedder,
    not_before: str | None = None,
) -> list[EvidenceRecord]:
    structured = store.find_structured(account_id, domain, not_before=not_before)
    try:
        semantic = store.search_semantic(
            account_id,
            domain,
            embedder.embed(claim),
            SEMANTIC_LIMIT,
        )
    except Exception as exc:
        logger.error("semantic_retrieval state=unavailable error_type=%s", type(exc).__name__)
        semantic = []
    merged = _dedupe(structured + semantic)[:EVIDENCE_CAP]
    logger.info(
        "hybrid_retrieve account_id=%s domain=%s structured=%s semantic=%s context_size=%s",
        account_id,
        domain,
        len(structured),
        len(semantic),
        len(merged),
    )
    return [item.record for item in merged]


def filter_evidence(
    records: list[EvidenceRecord],
    source: str | None,
    query: str | None,
) -> list[EvidenceRecord]:
    selected = records
    if source and source.strip():
        selected = [record for record in selected if record.source == source.strip()]
    needle = (query or "").strip().lower()
    if needle:
        selected = [record for record in selected if needle in _haystack(record)]
    return selected


def _dedupe(records: list[StoredEvidence]) -> list[StoredEvidence]:
    selected: list[StoredEvidence] = []
    seen: set[str] = set()
    for item in records:
        if item.record.id in seen:
            continue
        seen.add(item.record.id)
        selected.append(item)
    return selected


def _haystack(record: EvidenceRecord) -> str:
    return f"{record.title} {record.body} {record.source_record_id}".lower()
