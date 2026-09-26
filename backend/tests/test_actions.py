"""Plan shows work. Execute changes synthetic state only after approval."""

from __future__ import annotations

from fastapi.testclient import TestClient


def _analyze(client: TestClient, case_id: str) -> dict:
    response = client.post("/api/analyze", json={"case_id": case_id})
    assert response.status_code == 200
    return response.json()


def _plan(client: TestClient, case_id: str) -> dict:
    response = client.post("/api/actions/plan", json={"case_id": case_id})
    assert response.status_code == 200
    body = response.json()
    assert body["requires_approval"] is True
    assert body["case_id"] == case_id
    assert body["plan_id"]
    return body


def test_plan_does_not_execute(client: TestClient) -> None:
    _analyze(client, "acme-sso-rollout")
    first = _plan(client, "acme-sso-rollout")
    second = _plan(client, "acme-sso-rollout")
    assert first["before_state"] == {"tasks": [], "messages": [], "account_risks": []}
    assert second["before_state"] == first["before_state"]
    assert first["plan_id"] != second["plan_id"]
    assert {step["tool"] for step in first["steps"]} == {
        "create_task",
        "send_message",
        "update_account_risk",
    }


def test_execute_requires_approval_and_then_changes_state(client: TestClient) -> None:
    _analyze(client, "acme-sso-rollout")
    plan = _plan(client, "acme-sso-rollout")
    denied = client.post(
        "/api/actions/execute",
        json={"plan_id": plan["plan_id"], "approved": False},
    )
    assert denied.status_code == 400
    assert denied.json() == {"error": "Approval is required before execution"}
    omitted = client.post("/api/actions/execute", json={"plan_id": plan["plan_id"]})
    assert omitted.status_code == 400
    still_planned = _plan(client, "acme-sso-rollout")
    assert still_planned["before_state"]["tasks"] == []

    approved = client.post(
        "/api/actions/execute",
        json={
            "plan_id": plan["plan_id"],
            "approved": True,
            "steps": [{"tool": "send_message", "args": {"body": "injected"}}],
        },
    )
    assert approved.status_code == 200
    body = approved.json()
    assert body["status"] == "executed"
    assert body["before_state"]["tasks"] == []
    assert len(body["after_state"]["tasks"]) == 1
    assert len(body["after_state"]["messages"]) == 1
    assert len(body["after_state"]["account_risks"]) == 1
    assert body["after_state"]["tasks"][0]["case_id"] == "acme-sso-rollout"
    assert "injected" not in approved.text
    assert body["after_state"]["tasks"][0]["title"] == plan["steps"][0]["args"]["title"]
    case = client.get("/api/cases/acme-sso-rollout")
    assert case.json()["last_action_status"] == "executed"

    again = client.post(
        "/api/actions/execute",
        json={"plan_id": plan["plan_id"], "approved": True},
    )
    assert again.status_code == 409
    assert again.json() == {"error": "Plan already executed"}


def test_suppress_plan_has_no_intervention_and_execute_leaves_state(client: TestClient) -> None:
    _analyze(client, "globex-export-timeout")
    plan = _plan(client, "globex-export-timeout")
    assert plan["steps"] == []
    approved = client.post(
        "/api/actions/execute",
        json={"plan_id": plan["plan_id"], "approved": True},
    )
    assert approved.status_code == 200
    body = approved.json()
    assert body["results"] == []
    assert body["before_state"] == body["after_state"]
    assert body["after_state"] == {"tasks": [], "messages": [], "account_risks": []}
    case = client.get("/api/cases/globex-export-timeout")
    assert case.json()["last_action_status"] == "none"


def test_abstain_plan_asks_for_evidence_and_does_not_assert_risk(client: TestClient) -> None:
    _analyze(client, "initech-europe-expansion")
    plan = _plan(client, "initech-europe-expansion")
    tools = [step["tool"] for step in plan["steps"]]
    assert tools == ["create_task", "send_message"]
    assert "update_account_risk" not in tools
    message = next(step for step in plan["steps"] if step["tool"] == "send_message")
    assert "not treat this commitment as verified" in message["args"]["body"].lower()


def test_plan_before_analyze_is_rejected(client: TestClient) -> None:
    response = client.post("/api/actions/plan", json={"case_id": "acme-sso-rollout"})
    assert response.status_code == 400
    assert response.json() == {"error": "Analyze the case before planning an action"}


def test_unknown_plan_is_404(client: TestClient) -> None:
    response = client.post(
        "/api/actions/execute",
        json={"plan_id": "plan-missing", "approved": True},
    )
    assert response.status_code == 404
    assert response.json() == {"error": "Unknown plan"}
