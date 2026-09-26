"""The judged P0 path works in one synthetic session."""

from __future__ import annotations

from fastapi.testclient import TestClient

from tests.conftest import assert_grounded


def test_p0_decide_approve_execute_then_suppress_and_abstain(client: TestClient) -> None:
    cases = client.get("/api/cases")
    assert cases.status_code == 200
    assert {case["id"] for case in cases.json()} >= {
        "acme-sso-rollout",
        "globex-export-timeout",
        "initech-europe-expansion",
        "orion-order-5000",
    }

    acme = client.post("/api/analyze", json={"case_id": "acme-sso-rollout"})
    assert acme.status_code == 200
    assert acme.json()["decision"] == "VERIFY"
    assert_grounded(acme.json())
    evidence_id = acme.json()["evidence"][0]["id"]
    inspected = client.get(f"/api/evidence/{evidence_id}")
    assert inspected.status_code == 200
    assert inspected.json()["id"] == evidence_id

    planned = client.post("/api/actions/plan", json={"case_id": "acme-sso-rollout"})
    assert planned.status_code == 200
    plan = planned.json()
    assert plan["requires_approval"] is True
    assert all(not entries for entries in plan["before_state"].values())

    denied = client.post("/api/actions/execute", json={"plan_id": plan["plan_id"]})
    assert denied.status_code == 400
    approved = client.post(
        "/api/actions/execute", json={"plan_id": plan["plan_id"], "approved": True}
    )
    assert approved.status_code == 200
    assert approved.json()["after_state"] != approved.json()["before_state"]

    globex = client.post("/api/analyze", json={"case_id": "globex-export-timeout"})
    assert globex.status_code == 200
    assert globex.json()["decision"] == "SUPPRESS"
    assert_grounded(globex.json())
    no_escalation = client.post("/api/actions/plan", json={"case_id": "globex-export-timeout"})
    assert no_escalation.status_code == 200
    assert no_escalation.json()["requires_approval"] is False
    assert [step["tool"] for step in no_escalation.json()["steps"]] == ["dismiss_resolved"]
    assert client.get("/api/cases/globex-export-timeout").json()["queue_status"] == "dismissed"

    initech = client.post("/api/analyze", json={"case_id": "initech-europe-expansion"})
    assert initech.status_code == 200
    assert initech.json()["decision"] == "ABSTAIN"
    assert initech.json()["missing_evidence"]
    assert_grounded(initech.json())
    request = client.post("/api/actions/plan", json={"case_id": "initech-europe-expansion"})
    assert request.status_code == 200
    assert request.json()["requires_approval"] is False
    assert [step["tool"] for step in request.json()["steps"]] == ["request_evidence"]

    orion = client.post("/api/analyze", json={"case_id": "orion-order-5000"})
    assert orion.status_code == 200
    assert orion.json()["decision"] == "VERIFY"
    assert {item["source"] for item in orion.json()["evidence"]} == {
        "erp", "schedule", "inventory", "quality"
    }
    assert_grounded(orion.json())
    manufacturing_plan = client.post("/api/actions/plan", json={"case_id": "orion-order-5000"})
    assert manufacturing_plan.status_code == 200
    assert manufacturing_plan.json()["requires_approval"] is True
