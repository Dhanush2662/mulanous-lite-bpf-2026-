"""Apply a stored plan to in-memory synthetic state. No live systems."""

from __future__ import annotations

from collections.abc import Callable

from app.errors import AppError
from app.schemas.models import (
    ActionPlan,
    ActionResult,
    ActionStep,
    ActionStepResult,
    SyntheticAccountRisk,
    SyntheticMessage,
    SyntheticState,
    SyntheticTask,
)

_REQUIRED_ARGS = {
    "create_task": ("title", "owner", "detail", "case_id"),
    "send_message": ("recipient", "body", "case_id"),
    "update_account_risk": ("account", "risk_note", "case_id"),
}


class SyntheticSession:
    """Process-local synthetic state. A restart clears it."""

    def __init__(self) -> None:
        self.synthetic = SyntheticState()
        self.task_seq = 0
        self.message_seq = 0

    def snapshot(self) -> SyntheticState:
        return self.synthetic.model_copy(deep=True)


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
    for step in steps:
        required = _REQUIRED_ARGS.get(step.tool)
        if required is None:
            raise AppError(500, "Stored plan contains an unsupported tool")
        missing = [name for name in required if not step.args.get(name, "").strip()]
        if missing:
            raise AppError(500, "Stored plan is missing tool arguments")


def _apply_step(step: ActionStep, session: SyntheticSession) -> ActionStepResult:
    handlers: dict[str, Callable[[ActionStep, SyntheticSession], None]] = {
        "create_task": _create_task,
        "send_message": _send_message,
        "update_account_risk": _update_account_risk,
    }
    handlers[step.tool](step, session)
    return ActionStepResult(tool=step.tool, summary=step.summary)


def _create_task(step: ActionStep, session: SyntheticSession) -> None:
    session.task_seq += 1
    session.synthetic.tasks.append(
        SyntheticTask(
            id=f"task-{session.task_seq}",
            title=step.args["title"],
            owner=step.args["owner"],
            case_id=step.args["case_id"],
        )
    )


def _send_message(step: ActionStep, session: SyntheticSession) -> None:
    session.message_seq += 1
    session.synthetic.messages.append(
        SyntheticMessage(
            id=f"message-{session.message_seq}",
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
