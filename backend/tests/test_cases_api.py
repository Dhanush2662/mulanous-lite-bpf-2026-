"""Attention Today queue."""

from __future__ import annotations

from fastapi.testclient import TestClient

from tests.conftest import assert_no_score_fields


def test_cases_list_returns_software_and_manufacturing(client: TestClient) -> None:
    response = client.get("/api/cases")
    assert response.status_code == 200
    body = response.json()
    assert [item["id"] for item in body] == [
        "acme-sso-rollout",
        "globex-export-timeout",
        "initech-europe-expansion",
        "orion-order-5000",
    ]
    by_id = {item["id"]: item for item in body}
    assert by_id["acme-sso-rollout"]["account"] == "Acme"
    assert by_id["acme-sso-rollout"]["claim"] == "SSO rollout blocked"
    assert by_id["globex-export-timeout"]["account"] == "Globex"
    assert by_id["globex-export-timeout"]["claim"] == "Export timeout escalation"
    assert by_id["initech-europe-expansion"]["account"] == "Initech"
    assert by_id["initech-europe-expansion"]["claim"] == "Europe expansion at risk"
    for item in body:
        if item["id"] == "orion-order-5000":
            assert item["domain"] == "manufacturing"
            assert item["pattern"] == "production_commitment_intervention"
        else:
            assert item["domain"] == "software"
            assert item["pattern"] == "customer_commitment_intervention"
        assert item["disposition"] is None
        assert item["queue_status"] == "open"
        assert item["last_action_status"] == "none"
        assert item["source_count"] > 1
        assert item["urgency"]
        assert_no_score_fields(item)
    assert by_id["acme-sso-rollout"]["source_count"] == 8
    assert by_id["globex-export-timeout"]["source_count"] == 8
    assert by_id["initech-europe-expansion"]["source_count"] == 7
    orion = by_id["orion-order-5000"]
    assert orion["account"] == "Orion Components"
    assert orion["claim"] == "5,000 units due Monday"
    assert orion["urgency"] == "Due Monday"
    assert orion["source_count"] == 5


def test_get_case_and_unknown_case(client: TestClient) -> None:
    found = client.get("/api/cases/globex-export-timeout")
    assert found.status_code == 200
    assert found.json()["claim"] == "Export timeout escalation"
    missing = client.get("/api/cases/not-a-case")
    assert missing.status_code == 404
    assert missing.json() == {"error": "Unknown case"}
