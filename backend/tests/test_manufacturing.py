"""Manufacturing uses the same analyze and approval contract as software."""

from __future__ import annotations

from fastapi.testclient import TestClient

from tests.conftest import ANALYZE_KEYS, assert_grounded
from tests.test_actions import _analyze, _empty_state, _plan


def test_orion_verifies_from_evidence_not_from_case_id(client: TestClient) -> None:
    response = client.post("/api/analyze", json={"case_id": "orion-order-5000"})
    assert response.status_code == 200
    body = response.json()
    assert set(body) == ANALYZE_KEYS
    assert_grounded(body)
    assert body["decision"] == "VERIFY"
    assert body["account"] == "Orion Components"
    assert body["claim"] == "5,000 units due Monday"
    assert body["suggested_owner"] == "Production planner"
    assert body["due_hint"] == "Before Monday"
    assert body["missing_evidence"] == []
    assert {item["source"] for item in body["evidence"]} == {
        "erp",
        "schedule",
        "inventory",
        "quality",
    }
    ids = {item["id"] for item in body["evidence"]}
    assert "erp:ORION-PO-5000" in ids
    assert "inventory:ORION-MAT-441" in ids
    public_keys = {"id", "source", "source_record_id", "title", "body", "observed_at"}
    assert all(set(item) == public_keys for item in body["evidence"])
    quality = [item for item in body["evidence"] if item["source"] == "quality"]
    assert len(quality) == 2
    assert all("1200" not in item["body"] for item in quality)
    inventory = next(item for item in body["evidence"] if item["id"] == "inventory:ORION-MAT-441")
    assert "1200" in inventory["body"]

    stored = client.app.state.runtime.store.get("inventory:ORION-MAT-441")
    assert stored is not None
    assert stored.retrieval_class == "structured"
    assert stored.embedding is None
    assert stored.facts["on_hand_qty"] == "1200"
    assert stored.facts["required_qty"] == "5000"
    assert stored.facts["status"] == "short"
    semantic = client.app.state.runtime.store.search_semantic(
        "orion-001",
        "manufacturing",
        client.app.state.runtime.embedder.embed(body["claim"]),
        8,
    )
    assert semantic
    assert {item.record.source for item in semantic} == {"quality"}
    assert all(item.retrieval_class == "semantic" for item in semantic)
    assert all("1200" not in item.record.body for item in semantic)
    case = client.get("/api/cases/orion-order-5000")
    assert case.json()["disposition"] == "VERIFY"


def test_manufacturing_state_changes_wait_for_approval(client: TestClient) -> None:
    _analyze(client, "orion-order-5000")
    plan = _plan(client, "orion-order-5000")
    assert plan["requires_approval"] is True
    assert [step["tool"] for step in plan["steps"]] == [
        "expedite_material",
        "notify_planner",
        "update_order_risk",
    ]
    assert plan["before_state"] == _empty_state()
    assert plan["steps"][0]["args"]["material"] == "Housing alloy shortage"
    assert plan["steps"][2]["args"]["order_id"] == "ORION-PO-5000"
    denied = client.post(
        "/api/actions/execute",
        json={"plan_id": plan["plan_id"], "approved": False},
    )
    assert denied.status_code == 400
    still_open = _plan(client, "orion-order-5000")
    assert still_open["before_state"]["material_expedites"] == []
    approved = client.post(
        "/api/actions/execute",
        json={"plan_id": plan["plan_id"], "approved": True},
    )
    assert approved.status_code == 200
    after = approved.json()["after_state"]
    assert after["tasks"] == []
    assert after["messages"] == []
    assert after["account_risks"] == []
    assert len(after["material_expedites"]) == 1
    assert after["material_expedites"][0]["material"] == "Housing alloy shortage"
    assert len(after["planner_notices"]) == 1
    assert after["planner_notices"][0]["recipient"] == "Production planner"
    assert len(after["order_risks"]) == 1
    assert after["order_risks"][0]["order_id"] == "ORION-PO-5000"
    case = client.get("/api/cases/orion-order-5000")
    assert case.json()["last_action_status"] == "executed"
    assert case.json()["queue_status"] == "open"


def test_routes_do_not_expose_connector_admin() -> None:
    from app.api.routes import router

    paths = " ".join(getattr(route, "path", "") for route in router.routes)
    assert "connector" not in paths
    assert "oauth" not in paths
