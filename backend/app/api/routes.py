"""JSON routes for the P0 decision and action loop."""

from __future__ import annotations

from fastapi import APIRouter, Request

from app.errors import AppError
from app.runtime import Runtime
from app.schemas.models import (
    ActionExecutionRequest,
    ActionPlan,
    ActionResult,
    AnalyzeRequest,
    AnalyzeResponse,
    Case,
    EvidenceRecord,
    InvestigateRequest,
    InvestigateResponse,
)

router = APIRouter()


def _runtime(request: Request) -> Runtime:
    return request.app.state.runtime


@router.get("/cases", response_model=list[Case])
def list_cases(request: Request) -> list[Case]:
    return _runtime(request).list_cases()


@router.get("/cases/{case_id}", response_model=Case)
def get_case(case_id: str, request: Request) -> Case:
    return _runtime(request).get_case(case_id)


@router.get("/cases/{case_id}/evidence", response_model=list[EvidenceRecord])
def list_case_evidence(
    case_id: str,
    request: Request,
    source: str | None = None,
    q: str | None = None,
) -> list[EvidenceRecord]:
    return _runtime(request).list_case_evidence(case_id, source, q)


@router.get("/evidence/{evidence_id}", response_model=EvidenceRecord)
def get_evidence(evidence_id: str, request: Request) -> EvidenceRecord:
    return _runtime(request).get_evidence(evidence_id)


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze(body: AnalyzeRequest, request: Request) -> AnalyzeResponse:
    case_id = _required(body.case_id, "case_id is required")
    return _runtime(request).analyze(case_id)


@router.post("/actions/plan", response_model=ActionPlan)
def plan_action(body: AnalyzeRequest, request: Request) -> ActionPlan:
    case_id = _required(body.case_id, "case_id is required")
    return _runtime(request).plan(case_id)


@router.post("/actions/execute", response_model=ActionResult)
def execute_action(body: ActionExecutionRequest, request: Request) -> ActionResult:
    plan_id = _required(body.plan_id, "plan_id is required")
    return _runtime(request).execute(plan_id, body.approved)


@router.post("/investigate", response_model=InvestigateResponse)
def investigate(body: InvestigateRequest, request: Request) -> InvestigateResponse:
    case_id = _required(body.case_id, "case_id is required")
    message = _required(body.message, "message is required")
    return _runtime(request).investigate(case_id, message)


def _required(value: str | None, message: str) -> str:
    text = (value or "").strip()
    if not text:
        raise AppError(400, message)
    return text
