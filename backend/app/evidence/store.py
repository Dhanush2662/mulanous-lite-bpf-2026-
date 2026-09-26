"""Evidence store boundary. Memory is the fallback. Atlas is the demo store."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Protocol

from app.adapters.sources import CaseSeed
from app.evidence.embeddings import (
    FakeEmbedder,
    OpenAIEmbedder,
    attach_embeddings,
    attach_missing_embeddings,
    rank_by_cosine,
)
from app.logging_config import get_logger
from app.schemas.models import StoredEvidence

logger = get_logger(__name__)


class EvidenceStore(Protocol):
    name: str

    def find_structured(
        self,
        account_id: str,
        domain: str,
        *,
        source: str | None = None,
        not_before: str | None = None,
    ) -> list[StoredEvidence]:
        """Exact metadata lookup. Does not rank by vector similarity."""

    def search_semantic(
        self,
        account_id: str,
        domain: str,
        vector: list[float],
        limit: int,
    ) -> list[StoredEvidence]:
        """Semantic records only, ranked by embedding similarity."""

    def get(self, evidence_id: str) -> StoredEvidence | None:
        """One stored row, including rows outside the last page of retrieval."""

    def all_evidence(self) -> list[StoredEvidence]:
        """Every seeded row. Used to count sources and resolve ids."""

    def save_action(self, action: dict[str, object]) -> None:
        """Persist a plan or execution record."""


class MemoryEvidenceStore:
    name = "memory"

    def __init__(self) -> None:
        self._evidence: list[StoredEvidence] = []
        self.actions: list[dict[str, object]] = []

    def upsert(self, records: list[StoredEvidence], cases: list[CaseSeed]) -> None:
        del cases
        self._evidence = list(records)

    def find_structured(
        self,
        account_id: str,
        domain: str,
        *,
        source: str | None = None,
        not_before: str | None = None,
    ) -> list[StoredEvidence]:
        selected = [
            item
            for item in self._evidence
            if item.retrieval_class == "structured"
            and item.account_id == account_id
            and item.domain == domain
            and _source_ok(item, source)
            and _time_ok(item, not_before)
        ]
        selected.sort(key=lambda item: item.record.observed_at or "", reverse=True)
        return selected

    def search_semantic(
        self,
        account_id: str,
        domain: str,
        vector: list[float],
        limit: int,
    ) -> list[StoredEvidence]:
        pool = [
            item
            for item in self._evidence
            if item.retrieval_class == "semantic"
            and item.account_id == account_id
            and item.domain == domain
        ]
        return rank_by_cosine(pool, vector, limit)

    def get(self, evidence_id: str) -> StoredEvidence | None:
        for item in self._evidence:
            if item.record.id == evidence_id:
                return item
        return None

    def all_evidence(self) -> list[StoredEvidence]:
        return list(self._evidence)

    def save_action(self, action: dict[str, object]) -> None:
        plan_id = str(action.get("plan_id", ""))
        self.actions = [item for item in self.actions if item.get("plan_id") != plan_id]
        self.actions.append(action)


@dataclass
class PreparedStore:
    """Working set for one process. Atlas rows win when the collection already has evidence."""

    store: EvidenceStore
    evidence: list[StoredEvidence]
    cases: list[CaseSeed]
    origin: str


def open_evidence_store(
    records: list[StoredEvidence],
    cases: list[CaseSeed],
    *,
    use_atlas: bool | None = None,
) -> EvidenceStore:
    return prepare_store(records, cases, use_atlas=use_atlas).store


def prepare_store(
    records: list[StoredEvidence],
    cases: list[CaseSeed],
    embedder: FakeEmbedder | OpenAIEmbedder | None = None,
    *,
    use_atlas: bool | None = None,
) -> PreparedStore:
    if use_atlas is False or not os.environ.get("MONGODB_URI", "").strip():
        reason = "disabled" if use_atlas is False else "no_uri"
        return _memory_store(records, cases, embedder, reason)
    try:
        from app.evidence.atlas import AtlasEvidenceStore

        atlas = AtlasEvidenceStore.from_env()
    except Exception as exc:
        logger.error(
            "evidence_store name=memory reason=atlas_unavailable error_type=%s",
            type(exc).__name__,
        )
        return _memory_store(records, cases, embedder, "atlas_unavailable")
    existing = atlas.all_evidence()
    if not existing:
        _ensure_embeddings(records, embedder)
        atlas.upsert(records, cases)
        logger.info("evidence_store name=atlas reason=seeded records=%s", len(records))
        return PreparedStore(atlas, records, cases, "atlas_seeded")
    stored_cases = atlas.load_cases()
    if not stored_cases:
        logger.error("evidence_store state=cases_missing_using_files")
        stored_cases = cases
    if embedder is not None:
        for item in attach_missing_embeddings(existing, embedder):
            if item.embedding:
                atlas.save_embedding(item.record.id, item.embedding)
    logger.info("evidence_store name=atlas reason=existing records=%s", len(existing))
    return PreparedStore(atlas, existing, stored_cases, "atlas_existing")


def _memory_store(
    records: list[StoredEvidence],
    cases: list[CaseSeed],
    embedder: FakeEmbedder | OpenAIEmbedder | None,
    reason: str,
) -> PreparedStore:
    _ensure_embeddings(records, embedder)
    memory = MemoryEvidenceStore()
    memory.upsert(records, cases)
    logger.info("evidence_store name=memory reason=%s records=%s", reason, len(records))
    return PreparedStore(memory, records, cases, "memory")


def _ensure_embeddings(
    records: list[StoredEvidence],
    embedder: FakeEmbedder | OpenAIEmbedder | None,
) -> None:
    if embedder is None:
        return
    attach_embeddings(records, embedder)


def _source_ok(item: StoredEvidence, source: str | None) -> bool:
    if not source:
        return True
    return item.record.source == source


def _time_ok(item: StoredEvidence, not_before: str | None) -> bool:
    if not not_before:
        return True
    observed = item.record.observed_at
    if observed is None:
        return False
    return observed >= not_before
