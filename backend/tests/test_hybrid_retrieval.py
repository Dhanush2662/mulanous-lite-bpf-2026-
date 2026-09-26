"""Hybrid retrieval keeps exact facts off the vector path."""

from __future__ import annotations

import logging

import pytest
from app.context.assembler import hybrid_retrieve
from app.evidence.embeddings import FakeEmbedder
from app.evidence.store import MemoryEvidenceStore, open_evidence_store
from app.schemas.models import EvidenceRecord, StoredEvidence

SECRET_URI = "mongodb+srv://user:super-secret-password@cluster.example/db"


def test_structured_quantity_is_not_chosen_by_vector_similarity() -> None:
    embedder = FakeEmbedder()
    claim = "5,000 units due Monday"
    vector = embedder.embed(claim)
    inventory = _row(
        "inventory:ORION-MAT-441",
        "inventory",
        "ORION-MAT-441",
        "Housing alloy shortage",
        "On-hand quantity is 1200. Status is short. Material shortage is unresolved.",
        account_id="orion-001",
        retrieval_class="structured",
        facts={"on_hand_qty": "1200", "status": "short"},
        embedding=list(vector),
    )
    decoy = _row(
        "inventory:OTHER-9999",
        "inventory",
        "OTHER-9999",
        "Other plant stock",
        "On-hand quantity is 9999. Status is healthy.",
        account_id="other-001",
        retrieval_class="structured",
        facts={"on_hand_qty": "9999", "status": "healthy"},
        embedding=list(vector),
    )
    note = _row(
        "quality:ORION-QA-17",
        "quality",
        "ORION-QA-17",
        "Quality hold",
        "Quality hold remains open for the units due Monday.",
        account_id="orion-001",
        retrieval_class="semantic",
        embedding=embedder.embed("Quality hold remains open for the units due Monday."),
    )
    store = MemoryEvidenceStore()
    store.upsert([inventory, decoy, note], [])

    selected = hybrid_retrieve(
        store,
        account_id="orion-001",
        domain="manufacturing",
        claim=claim,
        embedder=embedder,
    )
    ids = [item.id for item in selected]
    assert ids[0] == "inventory:ORION-MAT-441"
    assert "inventory:OTHER-9999" not in ids
    assert "quality:ORION-QA-17" in ids
    assert all("9999" not in item.body for item in selected)

    semantic = store.search_semantic("orion-001", "manufacturing", vector, 8)
    assert [item.record.id for item in semantic] == ["quality:ORION-QA-17"]
    assert all(item.retrieval_class == "semantic" for item in semantic)

    exact = store.find_structured("orion-001", "manufacturing", source="inventory")
    assert len(exact) == 1
    assert exact[0].facts["on_hand_qty"] == "1200"
    assert exact[0].facts["status"] == "short"
    other = store.find_structured("other-001", "manufacturing", source="inventory")
    assert other[0].facts["on_hand_qty"] == "9999"


def test_time_filter_keeps_exact_rows_and_drops_null_timestamps() -> None:
    current = _row(
        "erp:CURRENT",
        "erp",
        "CURRENT",
        "Open order",
        "Status is open. Order quantity is 5000.",
        observed_at="2026-09-25T09:00:00Z",
        facts={"order_qty": "5000", "status": "open"},
    )
    stale = _row(
        "erp:STALE",
        "erp",
        "STALE",
        "Old order",
        "Status is open. Order quantity is 100.",
        observed_at="2026-09-01T09:00:00Z",
        facts={"order_qty": "100", "status": "open"},
    )
    undated = _row(
        "jira:UNDATED",
        "jira",
        "UNDATED",
        "Undated ticket",
        "Status is open.",
        observed_at=None,
        facts={"status": "open"},
    )
    store = MemoryEvidenceStore()
    store.upsert([stale, undated, current], [])
    selected = store.find_structured(
        "orion-001",
        "manufacturing",
        not_before="2026-09-20T00:00:00Z",
    )
    assert [item.record.id for item in selected] == ["erp:CURRENT"]
    assert selected[0].facts["order_qty"] == "5000"
    everything = store.find_structured("orion-001", "manufacturing")
    assert {item.record.id for item in everything} == {
        "erp:CURRENT",
        "erp:STALE",
        "jira:UNDATED",
    }


def test_memory_store_is_used_when_atlas_is_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MONGODB_URI", SECRET_URI)
    store = open_evidence_store([], [], use_atlas=False)
    assert store.name == "memory"


def test_atlas_outage_falls_back_without_logging_the_uri(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    monkeypatch.setenv("MONGODB_URI", SECRET_URI)

    def boom() -> None:
        raise ConnectionError("refused")

    monkeypatch.setattr("app.evidence.atlas.AtlasEvidenceStore.from_env", boom)
    with caplog.at_level(logging.DEBUG):
        store = open_evidence_store([], [], use_atlas=None)
    assert store.name == "memory"
    assert SECRET_URI not in caplog.text
    assert "super-secret-password" not in caplog.text


def test_atlas_store_filters_structured_facts_and_falls_back_without_an_index(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    pymongo = pytest.importorskip("pymongo")
    monkeypatch.setattr(pymongo, "MongoClient", _FakeClient)
    from app.evidence.atlas import AtlasEvidenceStore

    embedder = FakeEmbedder()
    vector = embedder.embed("quality hold units monday")
    inventory = _row(
        "inventory:ORION-MAT-441",
        "inventory",
        "ORION-MAT-441",
        "Housing alloy shortage",
        "On-hand quantity is 1200.",
        retrieval_class="structured",
        facts={"on_hand_qty": "1200"},
        embedding=list(vector),
        observed_at="2026-09-25T11:30:00Z",
    )
    stale = _row(
        "erp:STALE",
        "erp",
        "STALE",
        "Old order",
        "Order quantity is 100.",
        retrieval_class="structured",
        facts={"order_qty": "100"},
        observed_at="2026-09-01T09:00:00Z",
    )
    note = _row(
        "quality:ORION-QA-17",
        "quality",
        "ORION-QA-17",
        "Quality hold",
        "Quality hold remains open for the units due Monday.",
        retrieval_class="semantic",
        embedding=embedder.embed("Quality hold remains open for the units due Monday."),
        observed_at="2026-09-25T13:00:00Z",
    )
    with caplog.at_level(logging.DEBUG):
        store = AtlasEvidenceStore(SECRET_URI, "mulanous_lite", "evidence_vector")
        store.upsert([inventory, stale, note], [])
        current = store.find_structured(
            "orion-001",
            "manufacturing",
            source="inventory",
            not_before="2026-09-20T00:00:00Z",
        )
        semantic = store.search_semantic("orion-001", "manufacturing", vector, 4)
        store.save_action({"plan_id": "plan-1", "status": "planned"})
        store.save_action({"plan_id": "plan-1", "status": "executed"})
    assert [item.record.id for item in current] == ["inventory:ORION-MAT-441"]
    assert current[0].facts["on_hand_qty"] == "1200"
    assert [item.record.id for item in semantic] == ["quality:ORION-QA-17"]
    assert store._actions.find_one({"plan_id": "plan-1"})["status"] == "executed"
    assert SECRET_URI not in caplog.text


def _row(
    evidence_id: str,
    source: str,
    source_record_id: str,
    title: str,
    body: str,
    *,
    account_id: str = "orion-001",
    domain: str = "manufacturing",
    retrieval_class: str = "structured",
    facts: dict[str, str] | None = None,
    embedding: list[float] | None = None,
    observed_at: str | None = "2026-09-25T10:00:00Z",
) -> StoredEvidence:
    return StoredEvidence(
        account_id=account_id,
        domain=domain,
        retrieval_class=retrieval_class,  # type: ignore[arg-type]
        facts=facts or {},
        embedding=embedding,
        record=EvidenceRecord(
            id=evidence_id,
            source=source,
            source_record_id=source_record_id,
            title=title,
            body=body,
            observed_at=observed_at,
        ),
    )


class _Admin:
    def command(self, name: str) -> dict[str, int]:
        if name != "ping":
            raise RuntimeError(name)
        return {"ok": 1}


class _FakeCursor:
    def __init__(self, docs: list[dict[str, object]]) -> None:
        self._docs = list(docs)

    def sort(self, key: str, direction: int) -> _FakeCursor:
        self._docs.sort(key=lambda doc: str(doc.get(key) or ""), reverse=direction < 0)
        return self

    def __iter__(self):  # type: ignore[no-untyped-def]
        return iter(self._docs)


class _FakeCollection:
    def __init__(self) -> None:
        self.docs: list[dict[str, object]] = []

    def replace_one(self, filt: dict[str, object], doc: dict[str, object], upsert: bool = False) -> None:
        key = next(iter(filt))
        for index, existing in enumerate(self.docs):
            if existing.get(key) == filt[key]:
                self.docs[index] = dict(doc)
                return
        if upsert:
            self.docs.append(dict(doc))

    def find(self, query: dict[str, object]) -> _FakeCursor:
        return _FakeCursor([doc for doc in self.docs if _matches(doc, query)])

    def find_one(self, query: dict[str, object]) -> dict[str, object] | None:
        found = [doc for doc in self.docs if _matches(doc, query)]
        return found[0] if found else None

    def aggregate(self, pipeline: list[object]) -> list[object]:
        del pipeline
        raise RuntimeError("vector index missing")


class _FakeDatabase:
    def __init__(self) -> None:
        self._collections = {
            "cases": _FakeCollection(),
            "evidence": _FakeCollection(),
            "actions": _FakeCollection(),
        }

    def __getitem__(self, name: str) -> _FakeCollection:
        return self._collections[name]


class _FakeClient:
    def __init__(self, uri: str, **kwargs: object) -> None:
        del uri, kwargs
        self.admin = _Admin()
        self._database = _FakeDatabase()

    def __getitem__(self, name: str) -> _FakeDatabase:
        del name
        return self._database


def _matches(doc: dict[str, object], query: dict[str, object]) -> bool:
    for key, expected in query.items():
        value = doc.get(key)
        if isinstance(expected, dict) and "$gte" in expected:
            if not isinstance(value, str) or value < str(expected["$gte"]):
                return False
            continue
        if value != expected:
            return False
    return True
