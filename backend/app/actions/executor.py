"""Apply a stored plan to in-memory synthetic state. No live systems."""

from __future__ import annotations

from collections.abc import Callable

from app.actions.policy import LOW_RISK_TOOLS, STATE_CHANGING_TOOLS
from app.errors import AppError
from app.schemas.models import (
    Acknowledgement,
    ActionPlan,
    ActionResult,
    ActionStep,
    ActionStepResult,
    EvidenceRequestNote,
    MaterialExpedite,
    OrderRisk,
    PlannerNotice,
    SyntheticAccountRisk,
    SyntheticMessage,
    SyntheticState,
    SyntheticTask,
)

_REQUIRED_ARGS = {
    "create_task": ("title", "owner", "detail", "case_id"),
    "send_message": ("recipient", "body", "case_id"),
    "update_account_risk": ("account", "risk_note", "case_id"),
    "expedite_material": ("material", "detail", "case_id"),
    "notify_planner": ("recipient", "body", "case_id"),
    "update_order_risk": ("order_id", "risk_note", "case_id"),
    "dismiss_resolved": ("case_id",),
    "acknowledge": ("case_id", "note"),
    "request_evidence": ("case_id", "detail"),
}


class SyntheticSession:
    """Process-local synthetic state. A restart clears it."""

    def __init__(self) -> None:
        self.synthetic = SyntheticState()
        self._sequences = dict.fromkeys(
            ("task", "message", "expedite", "notice", "order", "ack", "request"),
            0,
        )

    def snapshot(self) -> SyntheticState:
        return self.synthetic.model_copy(deep=True)

    def next_id(self, kind: str) -> str:
        self._sequences[kind] += 1
        return f"{kind}-{self._sequences[kind]}"


def apply_stored_plan(plan: ActionPlan, session: SyntheticSession) -> ActionResult:
    _require_valid_steps(plan.steps)
    before = session.snapshot()
    results = [_apply_step(step, session) for step in plan.steps]
    return ActionResult(
        plan_id=plan.plan_id,
        case_id=plan.case_id,
        status="executed",
        results=results,
        before_state=before,
        after_state=session.snapshot(),
    )


def _require_valid_steps(steps: list[ActionStep]) -> None:
    allowed = LOW_RISK_TOOLS | STATE_CHANGING_TOOLS
    for step in steps:
        if step.tool not in allowed:
            raise AppError(500, "Stored plan contains an unsupported tool")
        required = _REQUIRED_ARGS[step.tool]
        missing = [name for name in required if not step.args.get(name, "").strip()]
        if missing:
            raise AppError(500, "Stored plan is missing tool arguments")


def _apply_step(step: ActionStep, session: SyntheticSession) -> ActionStepResult:
    handlers: dict[str, Callable[[ActionStep, SyntheticSession], None]] = {
        "create_task": _create_task,
        "send_message": _send_message,
        "update_account_risk": _update_account_risk,
        "expedite_material": _expedite_material,
        "notify_planner": _notify_planner,
        "update_order_risk": _update_order_risk,
        "dismiss_resolved": _dismiss_resolved,
        "acknowledge": _acknowledge,
        "request_evidence": _request_evidence,
    }
    handlers[step.tool](step, session)
    return ActionStepResult(tool=step.tool, summary=step.summary)


def _create_task(step: ActionStep, session: SyntheticSession) -> None:
    session.synthetic.tasks.append(
        SyntheticTask(
            id=session.next_id("task"),
            title=step.args["title"],
            owner=step.args["owner"],
            case_id=step.args["case_id"],
        )
    )


def _send_message(step: ActionStep, session: SyntheticSession) -> None:
    session.synthetic.messages.append(
        SyntheticMessage(
            id=session.next_id("message"),
            recipient=step.args["recipient"],
            body=step.args["body"],
            case_id=step.args["case_id"],
        )
    )


def _update_account_risk(step: ActionStep, session: SyntheticSession) -> None:
    session.synthetic.account_risks.append(
        SyntheticAccountRisk(
            account=step.args["account"],
            risk_note=step.args["risk_note"],
            case_id=step.args["case_id"],
        )
    )


def _expedite_material(step: ActionStep, session: SyntheticSession) -> None:
    session.synthetic.material_expedites.append(
        MaterialExpedite(
            id=session.next_id("expedite"),
            material=step.args["material"],
            detail=step.args["detail"],
            case_id=step.args["case_id"],
        )
    )


def _notify_planner(step: ActionStep, session: SyntheticSession) -> None:
    session.synthetic.planner_notices.append(
        PlannerNotice(
            id=session.next_id("notice"),
            recipient=step.args["recipient"],
            body=step.args["body"],
            case_id=step.args["case_id"],
        )
    )


def _update_order_risk(step: ActionStep, session: SyntheticSession) -> None:
    session.synthetic.order_risks.append(
        OrderRisk(
            id=session.next_id("order"),
            order_id=step.args["order_id"],
            risk_note=step.args["risk_note"],
            case_id=step.args["case_id"],
        )
    )


def _dismiss_resolved(step: ActionStep, session: SyntheticSession) -> None:
    case_id = step.args["case_id"]
    if case_id not in session.synthetic.dismissed_case_ids:
        session.synthetic.dismissed_case_ids.append(case_id)


def _acknowledge(step: ActionStep, session: SyntheticSession) -> None:
    session.synthetic.acknowledgements.append(
        Acknowledgement(
            id=session.next_id("ack"),
            case_id=step.args["case_id"],
            note=step.args["note"],
        )
    )


def _request_evidence(step: ActionStep, session: SyntheticSession) -> None:
    session.synthetic.evidence_requests.append(
        EvidenceRequestNote(
            id=session.next_id("request"),
            case_id=step.args["case_id"],
            detail=step.args["detail"],
        )
    )
