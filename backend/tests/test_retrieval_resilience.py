"""A failed semantic query must not hide exact structured evidence."""

from __future__ import annotations

import pytest
from app.context.assembler import hybrid_retrieve
from app.evidence.embeddings import FakeEmbedder
from app.evidence.store import MemoryEvidenceStore, PreparedStore, prepare_store
from app.main import create_app
from app.reasoning.deterministic import DeterministicDecisionProvider
from app.reasoning.read_evidence import record_stance
from app.schemas.models import EvidenceRecord, StoredEvidence
from fastapi.testclient import TestClient


class FailingQueryEmbedder(FakeEmbedder):
    def embed(self, text: str) -> list[float]:
        del text
        raise TimeoutError("embedding provider unavailable")


def test_query_embedding_failure_keeps_structured_evidence() -> None:
    record = EvidenceRecord(
        id="jira:OPEN-1",
        source="jira",
        source_record_id="OPEN-1",
        title="Customer blocker",
        body="The rollout blocker remains open.",
        observed_at="2026-09-25T10:00:00Z",
    )
    store = MemoryEvidenceStore()
    store.upsert(
        [
            StoredEvidence(
                account_id="example-001",
                domain="software",
                retrieval_class="structured",
                facts={"status": "open"},
                embedding=None,
                record=record,
            )
        ],
        [],
    )

    selected = hybrid_retrieve(
        store,
        account_id="example-001",
        domain="software",
        claim="Customer rollout blocked",
        embedder=FailingQueryEmbedder(),
    )
    assert [item.id for item in selected] == [record.id]


def test_resolved_shortage_does_not_read_as_open() -> None:
    record = EvidenceRecord(
        id="inventory:RESOLVED-1",
        source="inventory",
        source_record_id="RESOLVED-1",
        title="Material shortage resolved",
        body="The material shortage was resolved before the production run.",
        observed_at="2026-09-25T10:00:00Z",
    )
    assert record_stance(record) == "resolved"


def test_newer_open_signal_overrides_old_resolution() -> None:
    record = EvidenceRecord(
        id="inventory:OPEN-3",
        source="inventory",
        source_record_id="OPEN-3",
        title="Material shortage resolved, then reopened",
        body="The shortage was resolved, but the line is still blocked.",
        observed_at="2026-09-25T10:00:00Z",
    )
    assert record_stance(record) == "open"


def test_semantic_note_survives_structured_context_cap() -> None:
    embedder = FakeEmbedder()
    rows = [
        StoredEvidence(
            account_id="example-001",
            domain="software",
            retrieval_class="structured",
            facts={"status": "open"},
            embedding=None,
            record=EvidenceRecord(
                id=f"jira:FACT-{index}",
                source="jira",
                source_record_id=f"FACT-{index}",
                title="Operational fact",
                body="The rollout is blocked.",
                observed_at="2026-09-25T10:00:00Z",
            ),
        )
        for index in range(13)
    ]
    rows.append(
        StoredEvidence(
            account_id="example-001",
            domain="software",
            retrieval_class="semantic",
            facts={},
            embedding=embedder.embed("Customer escalation"),
            record=EvidenceRecord(
                id="slack:ESCALATION-1",
                source="slack",
                source_record_id="ESCALATION-1",
                title="Customer escalation",
                body="The customer escalated the rollout blocker.",
                observed_at="2026-09-25T10:00:00Z",
            ),
        )
    )
    store = MemoryEvidenceStore()
    store.upsert(rows, [])

    selected = hybrid_retrieve(
        store,
        account_id="example-001",
        domain="software",
        claim="Customer escalation",
        embedder=embedder,
    )
    assert len(selected) == 12
    assert any(item.id == "slack:ESCALATION-1" for item in selected)


def test_atlas_read_failure_falls_back_to_fixture_store(monkeypatch: pytest.MonkeyPatch) -> None:
    class FailingAtlas:
        def all_evidence(self) -> list[StoredEvidence]:
            raise ConnectionError("Atlas read failed after ping")

    monkeypatch.setenv("MONGODB_URI", "mongodb://unused-test-host")
    monkeypatch.setattr("app.evidence.atlas.AtlasEvidenceStore.from_env", lambda: FailingAtlas())
    row = StoredEvidence(
        account_id="example-001",
        domain="software",
        retrieval_class="structured",
        facts={"status": "open"},
        embedding=None,
        record=EvidenceRecord(
            id="jira:OPEN-2",
            source="jira",
            source_record_id="OPEN-2",
            title="Customer blocker",
            body="The rollout blocker remains open.",
            observed_at="2026-09-25T10:00:00Z",
        ),
    )

    prepared = prepare_store([row], [], FakeEmbedder(), use_atlas=None)
    assert prepared.origin == "memory"
    assert prepared.store.get(row.record.id) is not None


def test_atlas_outage_after_startup_keeps_analysis_available(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    real_prepare = prepare_store

    class FailingAtlas:
        name = "atlas"

        def find_structured(self, *args: object, **kwargs: object) -> list[StoredEvidence]:
            del args, kwargs
            raise ConnectionError("Atlas became unavailable")

    def prepare(records, cases, embedder, *, use_atlas):  # type: ignore[no-untyped-def]
        if use_atlas is False:
            return real_prepare(records, cases, embedder, use_atlas=False)
        return PreparedStore(FailingAtlas(), records, cases, "atlas_existing")

    monkeypatch.setattr("app.runtime.prepare_store", prepare)
    client = TestClient(
        create_app(provider=DeterministicDecisionProvider(), force_fake_embeddings=True)
    )
    response = client.post("/api/analyze", json={"case_id": "acme-sso-rollout"})
    assert response.status_code == 200
    assert response.json()["decision"] == "VERIFY"
    evidence_id = response.json()["evidence"][0]["id"]
    inspected = client.get(f"/api/evidence/{evidence_id}")
    assert inspected.status_code == 200
    assert inspected.json()["id"] == evidence_id
