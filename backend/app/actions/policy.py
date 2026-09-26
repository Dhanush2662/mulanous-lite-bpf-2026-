"""Low-risk internal tools may auto-apply. State-changing tools wait."""

from __future__ import annotations

from app.schemas.models import ActionStep

LOW_RISK_TOOLS = frozenset({"dismiss_resolved", "acknowledge", "request_evidence"})

STATE_CHANGING_TOOLS = frozenset(
    {
        "create_task",
        "send_message",
        "update_account_risk",
        "expedite_material",
        "notify_planner",
        "update_order_risk",
    }
)


def requires_approval(steps: list[ActionStep]) -> bool:
    return any(step.tool not in LOW_RISK_TOOLS for step in steps)
