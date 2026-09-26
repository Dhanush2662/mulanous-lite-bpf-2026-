"""Shared API client for the deterministic evidence reader."""

from __future__ import annotations

import pytest
from app.main import create_app
from app.reasoning.deterministic import DeterministicDecisionProvider
from fastapi.testclient import TestClient


@pytest.fixture
def client() -> TestClient:
    app = create_app(provider=DeterministicDecisionProvider())
    return TestClient(app)


def assert_no_score_fields(payload: object) -> None:
    if isinstance(payload, dict):
        assert "confidence" not in payload
        assert "risk_score" not in payload
        for value in payload.values():
            assert_no_score_fields(value)
    elif isinstance(payload, list):
        for item in payload:
            assert_no_score_fields(item)


def assert_grounded(body: dict) -> None:
    evidence_ids = {item["id"] for item in body["evidence"]}
    for item in body["evidence"]:
        assert item["id"] == f"{item['source']}:{item['source_record_id']}"
        assert item["source"] in {"crm", "jira", "slack", "meetings"}
    for challenge in body["contradictions_checked"]:
        assert set(challenge["evidence_ids"]) <= evidence_ids
        assert challenge["result"] in {"supported", "not_supported", "inconclusive"}
    assert_no_score_fields(body)


ANALYZE_KEYS = {
    "case_id",
    "account",
    "claim",
    "decision",
    "reason",
    "recommended_action",
    "suggested_owner",
    "due_hint",
    "evidence",
    "contradictions_checked",
    "missing_evidence",
}
