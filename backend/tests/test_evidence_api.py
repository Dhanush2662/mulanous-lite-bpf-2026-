"""Evidence reads stay on the case account and preserve provenance."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_case_evidence_is_account_scoped(client: TestClient) -> None:
    response = client.get("/api/cases/acme-sso-rollout/evidence")
    assert response.status_code == 200
    records = response.json()
    assert records
    ids = {item["id"] for item in records}
    assert "jira:JIRA-101" in ids
    assert "jira:JIRA-210" not in ids
    assert "crm:CRM-210" not in ids
    for item in records:
        assert item["id"] == f"{item['source']}:{item['source_record_id']}"


def test_evidence_filters_by_source_and_query(client: TestClient) -> None:
    jira = client.get("/api/cases/acme-sso-rollout/evidence", params={"source": "jira"})
    assert jira.status_code == 200
    assert jira.json()
    assert {item["source"] for item in jira.json()} == {"jira"}
    saml = client.get("/api/cases/acme-sso-rollout/evidence", params={"q": "SAML"})
    assert saml.status_code == 200
    assert saml.json()
    assert all("saml" in f"{item['title']} {item['body']}".lower() for item in saml.json())


def test_evidence_by_id_and_unknown_id(client: TestClient) -> None:
    found = client.get("/api/evidence/jira:JIRA-101")
    assert found.status_code == 200
    body = found.json()
    assert body["source"] == "jira"
    assert body["source_record_id"] == "JIRA-101"
    assert body["observed_at"] == "2026-09-25T10:00:00Z"
    missing = client.get("/api/evidence/jira:NO-SUCH")
    assert missing.status_code == 404
    assert missing.json() == {"error": "Unknown evidence"}


def test_missing_source_timestamp_stays_null(client: TestClient) -> None:
    response = client.get("/api/evidence/slack:SLACK-411")
    assert response.status_code == 200
    assert response.json()["observed_at"] is None


def test_unknown_case_evidence_is_404(client: TestClient) -> None:
    response = client.get("/api/cases/missing/evidence")
    assert response.status_code == 404
    assert response.json() == {"error": "Unknown case"}
