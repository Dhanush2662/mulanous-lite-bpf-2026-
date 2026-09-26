"""Schema and grounding checks. Malformed output is rejected, not coerced."""

from __future__ import annotations

import json
from dataclasses import dataclass

from pydantic import ValidationError

from app.evidence.timestamps import is_utc_timestamp
from app.schemas.models import (
    AnalyzeResponse,
    AssembledContext,
    ChallengeResult,
    EvidenceRecord,
    ModelDecision,
)


@dataclass(frozen=True)
class AnalysisAccepted:
    response: AnalyzeResponse


@dataclass(frozen=True)
class AnalysisRejected:
    errors: list[str]


def validate_model_output(
    raw: str,
    context: AssembledContext,
) -> AnalysisAccepted | AnalysisRejected:
    parsed = _parse(raw)
    if isinstance(parsed, AnalysisRejected):
        return parsed
    errors = _grounding_errors(parsed, context)
    if errors:
        return AnalysisRejected(errors)
    return AnalysisAccepted(_response(parsed, context))


def safe_abstain(context: AssembledContext) -> AnalyzeResponse:
    """Controlled failure after the repair attempt. Not a coerced model payload."""
    return AnalyzeResponse(
        case_id=context.case_id,
        account=context.account,
        claim=context.claim,
        decision="ABSTAIN",
        reason=(
            "The analysis could not be grounded in the supplied evidence, "
            "so no intervention is recommended."
        ),
        recommended_action=(
            "Collect clearer evidence before intervening. "
            "Do not treat the commitment as verified."
        ),
        suggested_owner="Delivery owner",
        due_hint=None,
        evidence=[],
        contradictions_checked=[],
        missing_evidence=[
            "The model output could not be validated against the supplied evidence."
        ],
    )


def _parse(raw: str) -> ModelDecision | AnalysisRejected:
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return AnalysisRejected(["model output is not valid JSON"])
    if not isinstance(payload, dict):
        return AnalysisRejected(["model output is not an object"])
    try:
        return ModelDecision.model_validate(payload)
    except ValidationError:
        return AnalysisRejected(["model output does not match the decision schema"])


def _grounding_errors(decision: ModelDecision, context: AssembledContext) -> list[str]:
    by_id = {record.id: record for record in context.evidence}
    errors: list[str] = []
    selected = _selected_records(decision.evidence_ids, by_id, errors)
    _check_decision_shape(decision, selected, errors)
    _check_challenges(decision.contradictions_checked, set(decision.evidence_ids), errors)
    _check_missing(decision, errors)
    return errors


def _selected_records(
    evidence_ids: list[str],
    by_id: dict[str, EvidenceRecord],
    errors: list[str],
) -> list[EvidenceRecord]:
    if len(evidence_ids) != len(set(evidence_ids)):
        errors.append("evidence_ids contains duplicates")
    selected: list[EvidenceRecord] = []
    for evidence_id in evidence_ids:
        record = by_id.get(evidence_id)
        if record is None:
            errors.append(f"unknown evidence id: {evidence_id}")
            continue
        if record.id != f"{record.source}:{record.source_record_id}":
            errors.append(f"evidence id does not match source fields: {evidence_id}")
            continue
        if not is_utc_timestamp(record.observed_at):
            errors.append(f"observed_at is not UTC: {evidence_id}")
            continue
        selected.append(record)
    return selected


def _check_decision_shape(
    decision: ModelDecision,
    selected: list[EvidenceRecord],
    errors: list[str],
) -> None:
    if decision.decision in {"VERIFY", "SUPPRESS"} and not selected:
        errors.append(f"{decision.decision} requires at least one evidence record")
    if decision.decision == "ABSTAIN" and not decision.missing_evidence:
        errors.append("ABSTAIN requires missing_evidence")
    if decision.due_hint is not None and not decision.due_hint.strip():
        errors.append("due_hint must be null or non-empty")


def _check_challenges(
    challenges: list[ChallengeResult],
    selected_ids: set[str],
    errors: list[str],
) -> None:
    for challenge in challenges:
        for evidence_id in challenge.evidence_ids:
            if evidence_id not in selected_ids:
                errors.append(f"challenge evidence id is not selected: {evidence_id}")


def _check_missing(decision: ModelDecision, errors: list[str]) -> None:
    for item in decision.missing_evidence:
        if not item.strip():
            errors.append("missing_evidence contains a blank item")
        elif len(item) > 500:
            errors.append("missing_evidence item is too long")


def _response(decision: ModelDecision, context: AssembledContext) -> AnalyzeResponse:
    by_id = {record.id: record for record in context.evidence}
    evidence = [by_id[evidence_id] for evidence_id in decision.evidence_ids]
    return AnalyzeResponse(
        case_id=context.case_id,
        account=context.account,
        claim=context.claim,
        decision=decision.decision,
        reason=decision.reason,
        recommended_action=decision.recommended_action,
        suggested_owner=decision.suggested_owner,
        due_hint=decision.due_hint,
        evidence=evidence,
        contradictions_checked=decision.contradictions_checked,
        missing_evidence=decision.missing_evidence,
    )
