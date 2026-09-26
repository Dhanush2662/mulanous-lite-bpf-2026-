"""Malformed and ungrounded model output fails closed."""

from __future__ import annotations

import json

from app.main import create_app
from fastapi.testclient import TestClient

from tests.conftest import ANALYZE_KEYS, assert_grounded
from tests.fakes import FailingDecisionProvider, ScriptedDecisionProvider

INVENTED_ID = "jira:INVENTED-999"


def test_invented_evidence_ids_are_not_returned() -> None:
    payload = json.dumps(
        {
            "decision": "VERIFY",
            "reason": "A fabricated record says the rollout is blocked.",
            "recommended_action": "Page the customer.",
            "suggested_owner": "Delivery owner",
            "due_hint": "Today",
            "evidence_ids": [INVENTED_ID],
            "contradictions_checked": [
                {
                    "hypothesis": "The blocker is already resolved.",
                    "result": "not_supported",
                    "evidence_ids": [INVENTED_ID],
                }
            ],
            "missing_evidence": [],
        }
    )
    client = TestClient(
        create_app(
            provider=ScriptedDecisionProvider([payload, payload]),
            use_atlas=False,
            force_fake_embeddings=True,
        )
    )
    response = client.post("/api/analyze", json={"case_id": "acme-sso-rollout"})
    assert response.status_code == 200
    body = response.json()
    assert set(body) == ANALYZE_KEYS
    assert body["decision"] == "ABSTAIN"
    assert INVENTED_ID not in response.text
    assert body["evidence"] == []
    assert_grounded(body)


def test_malformed_model_output_abstains() -> None:
    client = TestClient(
        create_app(
            provider=ScriptedDecisionProvider(["not json", "still not json"]),
            use_atlas=False,
            force_fake_embeddings=True,
        )
    )
    response = client.post("/api/analyze", json={"case_id": "acme-sso-rollout"})
    assert response.status_code == 200
    body = response.json()
    assert body["decision"] == "ABSTAIN"
    assert body["missing_evidence"]
    assert_grounded(body)


def test_model_timeout_abstains() -> None:
    client = TestClient(
        create_app(
            provider=FailingDecisionProvider(),
            use_atlas=False,
            force_fake_embeddings=True,
        )
    )
    response = client.post("/api/analyze", json={"case_id": "globex-export-timeout"})
    assert response.status_code == 200
    assert response.json()["decision"] == "ABSTAIN"
    assert response.json()["case_id"] == "globex-export-timeout"


def test_invalid_json_body_is_400(client: TestClient) -> None:
    response = client.post(
        "/api/analyze",
        content="{",
        headers={"content-type": "application/json"},
    )
    assert response.status_code == 400
    assert response.json() == {"error": "Invalid request"}
