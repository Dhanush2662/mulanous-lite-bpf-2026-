"""Build a stored plan from a validated decision. The planner does not execute."""

from __future__ import annotations

import uuid

from app.actions.policy import requires_approval
from app.errors import AppError
from app.schemas.models import ActionPlan, ActionStep, AnalyzeResponse, Case, SyntheticState


def build_action_plan(
    analysis: AnalyzeResponse,
    case: Case,
    before_state: SyntheticState,
) -> ActionPlan:
    steps = _steps_for(analysis, case)
    return ActionPlan(
        plan_id=f"plan-{uuid.uuid4().hex[:12]}",
        case_id=case.id,
        steps=steps,
        requires_approval=requires_approval(steps),
        before_state=before_state,
    )


def _steps_for(analysis: AnalyzeResponse, case: Case) -> list[ActionStep]:
    if analysis.decision == "SUPPRESS":
        return [_dismiss(case)]
    if analysis.decision == "ABSTAIN":
        return [_request_evidence(analysis, case)]
    if case.domain == "manufacturing":
        return _manufacturing_steps(analysis, case)
    return _software_steps(analysis, case)


def _software_steps(analysis: AnalyzeResponse, case: Case) -> list[ActionStep]:
    return [
        ActionStep(
            tool="create_task",
            summary=f"Create a task for {analysis.suggested_owner}.",
            args={
                "title": analysis.recommended_action,
                "owner": analysis.suggested_owner,
                "detail": analysis.reason,
                "case_id": case.id,
            },
        ),
        ActionStep(
            tool="send_message",
            summary=f"Message {analysis.suggested_owner} about the intervention.",
            args={
                "recipient": analysis.suggested_owner,
                "body": analysis.recommended_action,
                "case_id": case.id,
            },
        ),
        ActionStep(
            tool="update_account_risk",
            summary=f"Record an account risk note for {case.account}.",
            args={
                "account": case.account,
                "risk_note": analysis.reason,
                "case_id": case.id,
            },
        ),
    ]


def _manufacturing_steps(analysis: AnalyzeResponse, case: Case) -> list[ActionStep]:
    return [
        ActionStep(
            tool="expedite_material",
            summary="Expedite the short material for the committed order.",
            args={
                "material": _material(analysis),
                "detail": analysis.reason,
                "case_id": case.id,
            },
        ),
        ActionStep(
            tool="notify_planner",
            summary=f"Notify {analysis.suggested_owner} about the production commitment.",
            args={
                "recipient": analysis.suggested_owner,
                "body": analysis.recommended_action,
                "case_id": case.id,
            },
        ),
        ActionStep(
            tool="update_order_risk",
            summary="Record that the committed order is at risk.",
            args={
                "order_id": _order_id(analysis),
                "risk_note": analysis.reason,
                "case_id": case.id,
            },
        ),
    ]


def _dismiss(case: Case) -> ActionStep:
    return ActionStep(
        tool="dismiss_resolved",
        summary="Dismiss the resolved case from the attention queue.",
        args={"case_id": case.id, "note": "Evidence shows the issue is already resolved."},
    )


def _request_evidence(analysis: AnalyzeResponse, case: Case) -> ActionStep:
    gaps = "; ".join(analysis.missing_evidence) or "Required evidence is missing."
    return ActionStep(
        tool="request_evidence",
        summary="Request the missing evidence. Do not treat the commitment as verified.",
        args={"case_id": case.id, "detail": gaps},
    )


def _order_id(analysis: AnalyzeResponse) -> str:
    for record in analysis.evidence:
        if record.source == "erp":
            return record.source_record_id
    raise AppError(400, "Manufacturing action requires order evidence")


def _material(analysis: AnalyzeResponse) -> str:
    for record in analysis.evidence:
        if record.source == "inventory":
            return record.title[:120]
    raise AppError(400, "Manufacturing action requires inventory evidence")
