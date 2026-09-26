"""Model output must be grounded and satisfy the P0 decision contract."""

from __future__ import annotations

import json

import pytest
from app.actions.planner import build_action_plan
from app.errors import AppError
from app.reasoning.decision_agent import DecisionAgent
from app.schemas.models import (
    AnalyzeResponse,
    AssembledContext,
    Case,
    ChallengeResult,
    EvidenceRecord,
    SyntheticState,
)
from app.validation.validator import AnalysisAccepted, AnalysisRejected, validate_model_output


def _open_context() -> AssembledContext:
    return AssembledContext(
        case_id="test-open-commitment",
        domain="software",
        pattern="customer_commitment_intervention",
        account="Example",
        claim="Rollout blocked",
        urgency="Today",
        evidence=[
            EvidenceRecord(
                id="jira:OPEN-1",
                source="jira",
                source_record_id="OPEN-1",
                title="Rollout blocker still open",
                body="The blocker remains unresolved and the rollout cannot finish.",
                observed_at="2026-09-25T10:00:00Z",
            )
        ],
    )


def _candidate(decision: str = "VERIFY") -> dict:
    return {
        "decision": decision,
        "reason": "The supplied issue is open.",
        "recommended_action": "Ask the delivery owner to resolve the blocker.",
        "suggested_owner": "Delivery owner",
        "due_hint": "Today",
        "evidence_ids": ["jira:OPEN-1"],
        "contradictions_checked": [
            {
                "hypothesis": "The blocker is already resolved.",
                "result": "not_supported",
                "evidence_ids": ["jira:OPEN-1"],
            }
        ],
        "missing_evidence": [],
    }


def _validate(candidate: dict) -> AnalysisRejected:
    result = validate_model_output(json.dumps(candidate), _open_context())
    assert isinstance(result, AnalysisRejected)
    return result


def test_unknown_challenge_reference_is_rejected() -> None:
    candidate = _candidate()
    candidate["contradictions_checked"][0]["evidence_ids"] = ["jira:INVENTED-2"]
    _validate(candidate)


def test_unknown_decision_state_is_rejected() -> None:
    _validate(_candidate("ESCALATE"))


def test_verify_without_evidence_is_rejected() -> None:
    candidate = _candidate()
    candidate["evidence_ids"] = []
    candidate["contradictions_checked"] = []
    _validate(candidate)


def test_verify_requires_a_contradiction_check() -> None:
    candidate = _candidate()
    candidate["contradictions_checked"] = []
    _validate(candidate)


def test_verify_rejects_whitespace_action() -> None:
    candidate = _candidate()
    candidate["recommended_action"] = "   "
    _validate(candidate)


def test_suppress_requires_resolving_evidence() -> None:
    candidate = _candidate("SUPPRESS")
    candidate["reason"] = "The issue is resolved."
    candidate["recommended_action"] = "Do not escalate."
    _validate(candidate)


def _resolved_record() -> EvidenceRecord:
    return EvidenceRecord(
        id="jira:RESOLVED-1",
        source="jira",
        source_record_id="RESOLVED-1",
        title="Rollout resolved",
        body="The customer verified the rollout issue is fixed. No further action is needed.",
        observed_at="2026-09-24T10:00:00Z",
    )


def _resolved_candidate() -> dict:
    candidate = _candidate("SUPPRESS")
    candidate["reason"] = "The customer verified the issue is resolved."
    candidate["recommended_action"] = "Do not escalate the resolved issue."
    candidate["evidence_ids"] = ["jira:RESOLVED-1"]
    candidate["contradictions_checked"][0]["evidence_ids"] = ["jira:RESOLVED-1"]
    return candidate


def test_suppress_accepts_a_resolved_record() -> None:
    context = _open_context().model_copy(update={"evidence": [_resolved_record()]})
    result = validate_model_output(json.dumps(_resolved_candidate()), context)
    assert isinstance(result, AnalysisAccepted)


def test_suppress_rejects_newer_open_evidence_omitted_by_model() -> None:
    context = _open_context().model_copy(
        update={"evidence": [_resolved_record(), *_open_context().evidence]}
    )
    result = validate_model_output(json.dumps(_resolved_candidate()), context)
    assert isinstance(result, AnalysisRejected)


def test_suppress_handles_an_undated_resolution_record() -> None:
    undated = _resolved_record().model_copy(
        update={"id": "jira:RESOLVED-2", "source_record_id": "RESOLVED-2", "observed_at": None}
    )
    context = _open_context().model_copy(update={"evidence": [_resolved_record(), undated]})
    candidate = _resolved_candidate()
    candidate["evidence_ids"].append(undated.id)
    result = validate_model_output(json.dumps(candidate), context)
    assert isinstance(result, AnalysisAccepted)


def test_manufacturing_verify_requires_order_and_inventory_evidence() -> None:
    quality = EvidenceRecord(
        id="quality:HOLD-1",
        source="quality",
        source_record_id="HOLD-1",
        title="Production hold",
        body="A quality hold remains open for the production commitment.",
        observed_at="2026-09-25T10:00:00Z",
    )
    context = _open_context().model_copy(
        update={
            "domain": "manufacturing",
            "pattern": "production_commitment_intervention",
            "evidence": [quality],
        }
    )
    candidate = _candidate()
    candidate["evidence_ids"] = [quality.id]
    candidate["contradictions_checked"][0]["evidence_ids"] = [quality.id]
    result = validate_model_output(json.dumps(candidate), context)
    assert isinstance(result, AnalysisRejected)


def test_manufacturing_planner_never_invents_order_or_material() -> None:
    quality = EvidenceRecord(
        id="quality:HOLD-1",
        source="quality",
        source_record_id="HOLD-1",
        title="Production hold",
        body="A quality hold remains open.",
        observed_at="2026-09-25T10:00:00Z",
    )
    analysis = AnalyzeResponse(
        case_id="manufacturing-test",
        account="Example",
        claim="Production commitment at risk",
        decision="VERIFY",
        reason="A hold is open.",
        recommended_action="Ask the planner to review the hold.",
        suggested_owner="Production planner",
        due_hint="Today",
        evidence=[quality],
        contradictions_checked=[
            ChallengeResult(hypothesis="The hold is resolved.", result="not_supported", evidence_ids=[quality.id])
        ],
        missing_evidence=[],
    )
    case = Case(
        id="manufacturing-test",
        domain="manufacturing",
        pattern="production_commitment_intervention",
        account="Example",
        claim=analysis.claim,
        urgency="Today",
        source_count=1,
        disposition="VERIFY",
    )
    with pytest.raises(AppError):
        build_action_plan(analysis, case, SyntheticState())


class RepairProvider:
    name = "repair-test"

    def __init__(self, repaired_output: str) -> None:
        self.repaired_output = repaired_output
        self.complete_calls = 0
        self.repair_calls = 0

    def complete(self, prompt: object) -> str:
        del prompt
        self.complete_calls += 1
        return "not json"

    def repair(self, prompt: object, previous_output: str, errors: list[str]) -> str:
        del prompt, previous_output
        assert errors
        self.repair_calls += 1
        return self.repaired_output


def test_malformed_json_gets_one_repair_attempt() -> None:
    provider = RepairProvider(json.dumps(_candidate()))
    result = DecisionAgent(provider).decide(_open_context())
    assert result.decision == "VERIFY"
    assert provider.complete_calls == 1
    assert provider.repair_calls == 1


def test_malformed_json_after_repair_abstains() -> None:
    provider = RepairProvider("still not json")
    result = DecisionAgent(provider).decide(_open_context())
    assert result.decision == "ABSTAIN"
    assert result.missing_evidence
    assert provider.complete_calls == 1
    assert provider.repair_calls == 1
