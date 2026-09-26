"""Build a stored plan from a validated decision. Planning does not execute."""

from __future__ import annotations

import uuid

from app.schemas.models import ActionPlan, ActionStep, AnalyzeResponse, Case, SyntheticState

_ALLOWED = {"create_task", "send_message", "update_account_risk"}


def build_action_plan(
    analysis: AnalyzeResponse,
    case: Case,
    before_state: SyntheticState,
) -> ActionPlan:
    steps = _steps_for(analysis, case)
    for step in steps:
        if step.tool not in _ALLOWED:
            raise ValueError(f"unsupported tool: {step.tool}")
    return ActionPlan(
        plan_id=f"plan-{uuid.uuid4().hex[:12]}",
        case_id=case.id,
        steps=steps,
        requires_approval=True,
        before_state=before_state,
    )


def _steps_for(analysis: AnalyzeResponse, case: Case) -> list[ActionStep]:
    if analysis.decision == "SUPPRESS":
        return []
    if analysis.decision == "ABSTAIN":
        return _clarify_steps(analysis, case)
    return _intervention_steps(analysis, case)


def _intervention_steps(analysis: AnalyzeResponse, case: Case) -> list[ActionStep]:
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


def _clarify_steps(analysis: AnalyzeResponse, case: Case) -> list[ActionStep]:
    gaps = "; ".join(analysis.missing_evidence) or "Required evidence is missing."
    return [
        ActionStep(
            tool="create_task",
            summary="Create a task to gather the missing evidence.",
            args={
                "title": "Gather missing evidence before any intervention",
                "owner": analysis.suggested_owner,
                "detail": gaps,
                "case_id": case.id,
            },
        ),
        ActionStep(
            tool="send_message",
            summary="Ask for clarification. Do not treat the commitment as verified.",
            args={
                "recipient": analysis.suggested_owner,
                "body": (
                    "Please clarify before any intervention. "
                    f"Do not treat this commitment as verified. Missing: {gaps}"
                ),
                "case_id": case.id,
            },
        ),
    ]
