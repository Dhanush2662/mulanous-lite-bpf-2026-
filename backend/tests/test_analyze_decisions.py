"""The three demo dispositions come from the evidence pipeline."""

from __future__ import annotations

from fastapi.testclient import TestClient

from tests.conftest import ANALYZE_KEYS, assert_grounded


def test_acme_verifies_from_evidence(client: TestClient) -> None:
    body = _analyze(client, "acme-sso-rollout")
    assert body["decision"] == "VERIFY"
    assert body["account"] == "Acme"
    assert body["claim"] == "SSO rollout blocked"
    assert body["due_hint"]
    assert body["suggested_owner"] == "Delivery owner"
    assert body["missing_evidence"] == []
    assert {item["source"] for item in body["evidence"]} == {"crm", "jira", "slack", "meetings"}
    assert "jira:JIRA-101" in {item["id"] for item in body["evidence"]}
    assert body["contradictions_checked"][0]["result"] == "not_supported"
    listed = client.get("/api/cases/acme-sso-rollout")
    assert listed.json()["disposition"] == "VERIFY"


def test_globex_suppresses_a_resolved_issue(client: TestClient) -> None:
    body = _analyze(client, "globex-export-timeout")
    assert body["decision"] == "SUPPRESS"
    assert body["account"] == "Globex"
    assert "escalat" in body["recommended_action"].lower()
    assert body["due_hint"] is None
    assert body["missing_evidence"] == []
    assert body["contradictions_checked"][0]["result"] == "not_supported"
    assert any("resolved" in item["body"].lower() for item in body["evidence"])
    assert {item["source"] for item in body["evidence"]} == {"crm", "jira", "slack", "meetings"}


def test_initech_abstains_when_evidence_is_vague(client: TestClient) -> None:
    body = _analyze(client, "initech-europe-expansion")
    assert body["decision"] == "ABSTAIN"
    assert body["account"] == "Initech"
    assert body["missing_evidence"]
    assert body["suggested_owner"] == "Account owner"
    assert body["contradictions_checked"][0]["result"] == "inconclusive"
    assert "milestone" in " ".join(body["missing_evidence"]).lower()


def test_client_cannot_inject_a_decision(client: TestClient) -> None:
    response = client.post(
        "/api/analyze",
        json={"case_id": "acme-sso-rollout", "decision": "SUPPRESS"},
    )
    assert response.status_code == 200
    assert response.json()["decision"] == "VERIFY"


def test_unknown_case_is_404(client: TestClient) -> None:
    response = client.post("/api/analyze", json={"case_id": "missing-case"})
    assert response.status_code == 404
    assert response.json() == {"error": "Unknown case"}


def test_blank_case_id_is_400(client: TestClient) -> None:
    response = client.post("/api/analyze", json={"case_id": "  "})
    assert response.status_code == 400
    assert response.json() == {"error": "case_id is required"}


def _analyze(client: TestClient, case_id: str) -> dict:
    response = client.post("/api/analyze", json={"case_id": case_id})
    assert response.status_code == 200
    body = response.json()
    assert set(body) == ANALYZE_KEYS
    assert body["case_id"] == case_id
    assert_grounded(body)
    return body
