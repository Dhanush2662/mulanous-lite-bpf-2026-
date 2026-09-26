"""MongoDB Atlas evidence store. Vector search falls back to local cosine."""

from __future__ import annotations

import os

from pydantic import ValidationError

from app.adapters.sources import CaseSeed
from app.evidence.embeddings import rank_by_cosine
from app.logging_config import get_logger
from app.schemas.models import EvidenceRecord, StoredEvidence

logger = get_logger(__name__)


class AtlasEvidenceStore:
    name = "atlas"

    def __init__(self, uri: str, database: str, index_name: str) -> None:
        from pymongo import MongoClient

        self._index = index_name
        self._client = MongoClient(
            uri,
            serverSelectionTimeoutMS=2000,
            connectTimeoutMS=2000,
        )
        self._client.admin.command("ping")
        db = self._client[database]
        self._cases = db["cases"]
        self._evidence = db["evidence"]
        self._actions = db["actions"]

    @classmethod
    def from_env(cls) -> AtlasEvidenceStore:
        uri = os.environ.get("MONGODB_URI", "").strip()
        database = os.environ.get("MONGODB_DB", "mulanous_lite").strip() or "mulanous_lite"
        index_name = os.environ.get("ATLAS_VECTOR_INDEX", "evidence_vector").strip() or "evidence_vector"
        return cls(uri, database, index_name)

    def upsert(self, records: list[StoredEvidence], cases: list[CaseSeed]) -> None:
        for case in cases:
            self._cases.replace_one({"id": case.id}, case.model_dump(), upsert=True)
        for item in records:
            self._evidence.replace_one({"id": item.record.id}, _document(item), upsert=True)

    def find_structured(
        self,
        account_id: str,
        domain: str,
        *,
        source: str | None = None,
        not_before: str | None = None,
    ) -> list[StoredEvidence]:
        query: dict[str, object] = {
            "account_id": account_id,
            "domain": domain,
            "retrieval_class": "structured",
        }
        if source:
            query["source"] = source
        if not_before:
            query["observed_at"] = {"$gte": not_before}
        cursor = self._evidence.find(query).sort("observed_at", -1)
        return [_stored(document) for document in cursor]

    def search_semantic(
        self,
        account_id: str,
        domain: str,
        vector: list[float],
        limit: int,
    ) -> list[StoredEvidence]:
        search_filter = {
            "account_id": account_id,
            "domain": domain,
            "retrieval_class": "semantic",
        }
        try:
            found = self._vector_search(vector, search_filter, limit)
        except Exception as exc:
            logger.error("vector_search state=fallback error_type=%s", type(exc).__name__)
            found = []
        if found:
            return found
        pool = [_stored(document) for document in self._evidence.find(search_filter)]
        return rank_by_cosine(pool, vector, limit)

    def get(self, evidence_id: str) -> StoredEvidence | None:
        document = self._evidence.find_one({"id": evidence_id})
        if document is None:
            return None
        return _stored(document)

    def all_evidence(self) -> list[StoredEvidence]:
        return [_stored(document) for document in self._evidence.find({})]

    def load_cases(self) -> list[CaseSeed]:
        documents = list(self._cases.find({}))
        documents.sort(key=_case_order)
        cases: list[CaseSeed] = []
        for document in documents:
            try:
                cases.append(CaseSeed.model_validate(document))
            except ValidationError:
                logger.error("evidence_store state=skipped_case")
        return cases

    def save_embedding(self, evidence_id: str, embedding: list[float]) -> None:
        self._evidence.update_one({"id": evidence_id}, {"$set": {"embedding": embedding}})

    def save_action(self, action: dict[str, object]) -> None:
        plan_id = str(action.get("plan_id", ""))
        self._actions.replace_one({"plan_id": plan_id}, action, upsert=True)

    def _vector_search(
        self,
        vector: list[float],
        search_filter: dict[str, str],
        limit: int,
    ) -> list[StoredEvidence]:
        pipeline = [
            {
                "$vectorSearch": {
                    "index": self._index,
                    "path": "embedding",
                    "queryVector": vector,
                    "numCandidates": max(limit * 10, 20),
                    "limit": limit,
                    "filter": search_filter,
                }
            }
        ]
        return [_stored(document) for document in self._evidence.aggregate(pipeline)]


def _case_order(document: dict[str, object]) -> tuple[int, str]:
    raw = document.get("ingest_order", 1_000_000)
    try:
        order = int(raw)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        order = 1_000_000
    return order, str(document.get("id", ""))


def _document(item: StoredEvidence) -> dict[str, object]:
    return {
        "id": item.record.id,
        "source": item.record.source,
        "source_record_id": item.record.source_record_id,
        "account_id": item.account_id,
        "domain": item.domain,
        "title": item.record.title,
        "body": item.record.body,
        "observed_at": item.record.observed_at,
        "retrieval_class": item.retrieval_class,
        "facts": item.facts,
        "embedding": item.embedding,
    }


def _stored(document: dict[str, object]) -> StoredEvidence:
    embedding = document.get("embedding")
    vector = [float(value) for value in embedding] if isinstance(embedding, list) else None
    facts = document.get("facts") if isinstance(document.get("facts"), dict) else {}
    observed = document.get("observed_at")
    return StoredEvidence(
        account_id=str(document.get("account_id", "")),
        domain=str(document.get("domain", "")),
        retrieval_class="semantic" if document.get("retrieval_class") == "semantic" else "structured",
        facts={str(key): str(value) for key, value in facts.items()},
        embedding=vector,
        record=EvidenceRecord(
            id=str(document.get("id", "")),
            source=str(document.get("source", "")),
            source_record_id=str(document.get("source_record_id", "")),
            title=str(document.get("title", "")),
            body=str(document.get("body", "")),
            observed_at=observed if isinstance(observed, str) else None,
        ),
    )
