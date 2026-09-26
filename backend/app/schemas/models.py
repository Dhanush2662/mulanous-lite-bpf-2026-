"""Pydantic schemas aligned with the Mulanous Lite Canon.

Wire names follow the Canon. Planned actions are `ActionStep` entries on
`ActionPlan`. `ActionResult` is the execution result.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Disposition = Literal["VERIFY", "SUPPRESS", "ABSTAIN"]
Domain = Literal["software", "manufacturing", "logistics"]
ChallengeOutcome = Literal["supported", "not_supported", "inconclusive"]
ActionTool = Literal["create_task", "send_message", "update_account_risk"]
InvestigationTool = Literal[
    "get_case",
    "get_evidence",
    "inspect_evidence",
    "reanalyze_case",
]


class ErrorBody(BaseModel):
    error: str


class Case(BaseModel):
    id: str
    domain: Domain
    pattern: str
    account: str
    claim: str
    urgency: str
    source_count: int
    disposition: Disposition | None = None
    last_action_status: Literal["none", "executed"] = "none"


class CaseRecord(Case):
    """Case plus the account key used to filter fixtures. Not an API field."""

    account_id: str


class EvidenceRecord(BaseModel):
    id: str
    source: str
    source_record_id: str
    title: str
    body: str
    observed_at: str | None


class StoredEvidence(BaseModel):
    account_id: str
    record: EvidenceRecord


class ChallengeResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    hypothesis: str = Field(min_length=1, max_length=1000)
    result: ChallengeOutcome
    evidence_ids: list[str] = Field(max_length=20)


class ModelDecision(BaseModel):
    """Structured model output. It has no chain-of-thought and no confidence."""

    model_config = ConfigDict(extra="forbid")

    decision: Disposition
    reason: str = Field(min_length=1, max_length=1000)
    recommended_action: str = Field(min_length=1, max_length=1000)
    suggested_owner: str = Field(min_length=1, max_length=200)
    due_hint: str | None = Field(max_length=300)
    evidence_ids: list[str] = Field(max_length=20)
    contradictions_checked: list[ChallengeResult] = Field(max_length=8)
    missing_evidence: list[str] = Field(max_length=12)


class AnalyzeRequest(BaseModel):
    model_config = ConfigDict(extra="ignore", strict=True)

    case_id: str | None = None


class AnalyzeResponse(BaseModel):
    case_id: str
    account: str
    claim: str
    decision: Disposition
    reason: str
    recommended_action: str
    suggested_owner: str
    due_hint: str | None
    evidence: list[EvidenceRecord]
    contradictions_checked: list[ChallengeResult]
    missing_evidence: list[str]


class AssembledContext(BaseModel):
    """Evidence selected for one case. The model only sees these records."""

    case_id: str
    account: str
    claim: str
    urgency: str
    evidence: list[EvidenceRecord]


class SyntheticTask(BaseModel):
    id: str
    title: str
    owner: str
    case_id: str


class SyntheticMessage(BaseModel):
    id: str
    recipient: str
    body: str
    case_id: str


class SyntheticAccountRisk(BaseModel):
    account: str
    risk_note: str
    case_id: str


class SyntheticState(BaseModel):
    tasks: list[SyntheticTask] = Field(default_factory=list)
    messages: list[SyntheticMessage] = Field(default_factory=list)
    account_risks: list[SyntheticAccountRisk] = Field(default_factory=list)


class ActionStep(BaseModel):
    """One planned tool call. Nothing runs until an approved execute."""

    tool: ActionTool
    summary: str
    args: dict[str, str]


class ActionPlan(BaseModel):
    plan_id: str
    case_id: str
    steps: list[ActionStep]
    requires_approval: Literal[True] = True
    before_state: SyntheticState


class ActionExecutionRequest(BaseModel):
    model_config = ConfigDict(extra="ignore", strict=True)

    plan_id: str | None = None
    approved: bool | None = None


class ActionStepResult(BaseModel):
    tool: ActionTool
    summary: str


class ActionResult(BaseModel):
    plan_id: str
    case_id: str
    status: Literal["executed"]
    results: list[ActionStepResult]
    before_state: SyntheticState
    after_state: SyntheticState


class InvestigateRequest(BaseModel):
    model_config = ConfigDict(extra="ignore", strict=True)

    case_id: str | None = None
    message: str | None = None


class InvestigateResponse(BaseModel):
    case_id: str
    answer: str
    tools_used: list[InvestigationTool]
    evidence_ids: list[str]
