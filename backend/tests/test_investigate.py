"""Investigation is grounded in the four read tools and cannot plan actions."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient


def test_investigate_quotes_the_validated_decision(client: TestClient) -> None:
    analyzed = client.post("/api/analyze", json={"case_id": "acme-sso-rollout"})
    assert analyzed.status_code == 200
    response = client.post(
        "/api/investigate",
        json={"case_id": "acme-sso-rollout", "message": "Why this disposition?"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["case_id"] == "acme-sso-rollout"
    assert "VERIFY" in body["answer"]
    assert "get_case" in body["tools_used"]
    assert "get_evidence" in body["tools_used"]
    assert body["evidence_ids"]
    known = {item["id"] for item in analyzed.json()["evidence"]}
    assert set(body["evidence_ids"]) <= known


def test_investigate_can_reanalyze_and_inspect(client: TestClient) -> None:
    response = client.post(
        "/api/investigate",
        json={
            "case_id": "initech-europe-expansion",
            "message": "Please reanalyze and inspect crm:CRM-210",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert "reanalyze_case" in body["tools_used"]
    assert "inspect_evidence" in body["tools_used"]
    assert "ABSTAIN" in body["answer"]
    assert "crm:CRM-210" in body["evidence_ids"]
    assert "crm:CRM-210" in body["answer"]
    case = client.get("/api/cases/initech-europe-expansion")
    assert case.json()["disposition"] == "ABSTAIN"


def test_investigate_unknown_case_is_404(client: TestClient) -> None:
    response = client.post(
        "/api/investigate",
        json={"case_id": "missing", "message": "Why?"},
    )
    assert response.status_code == 404
    assert response.json() == {"error": "Unknown case"}


def test_investigation_package_has_no_action_tools() -> None:
    root = Path(__file__).resolve().parents[1] / "app" / "investigate"
    text = "\n".join(path.read_text(encoding="utf-8") for path in root.rglob("*.py"))
    assert "create_task" not in text
    assert "send_message" not in text
    assert "update_account_risk" not in text
