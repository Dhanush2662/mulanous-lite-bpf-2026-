"""Evidence-reading stand-in for the decision model.

The label comes from blocker, resolution, and vagueness language in the
supplied records. The claim is only the question used to keep records on
topic. Case id is not an input.
"""

from __future__ import annotations

from app.reasoning.prompt import DecisionPrompt
from app.reasoning.read_evidence import combined_text, read_evidence
from app.schemas.models import ChallengeResult, EvidenceRecord, ModelDecision


class DeterministicDecisionProvider:
    name = "deterministic"

    def complete(self, prompt: DecisionPrompt) -> str:
        decision = classify_evidence(prompt.claim, list(prompt.evidence))
        return decision.model_dump_json()

    def repair(self, prompt: DecisionPrompt, previous_output: str, errors: list[str]) -> str:
        del previous_output, errors
        return self.complete(prompt)


def classify_evidence(claim: str, evidence: list[EvidenceRecord]) -> ModelDecision:
    reading = read_evidence(claim, evidence)
    if reading.open_records:
        return _verify(reading.relevant, reading.open_records)
    if reading.resolved_records:
        return _suppress(reading.relevant, reading.resolved_records)
    return _abstain(reading.relevant)


def _verify(relevant: list[EvidenceRecord], open_records: list[EvidenceRecord]) -> ModelDecision:
    titles = _titles(open_records)
    blob = combined_text(relevant)
    if "checkpoint" in blob:
        due_hint = "Before today's customer checkpoint"
        action = (
            "Confirm the unresolved blocker with the delivery owner and track it "
            "before the customer checkpoint."
        )
    elif "monday" in blob and ("material shortage" in blob or "quality hold" in blob):
        due_hint = "Before Monday"
        action = (
            "Confirm the material shortage and quality hold with the production planner before Monday."
        )
    else:
        due_hint = "Before the next customer commitment review"
        action = (
            "Confirm the unresolved blocker with the delivery owner and track it "
            "before the next commitment review."
        )
    owner = "Production planner" if "production planner" in blob else "Delivery owner"
    open_ids = [record.id for record in open_records[:4]]
    return ModelDecision(
        decision="VERIFY",
        reason=(
            f"Open evidence still shows an unresolved blocker ({titles}). "
            "The hypothesis that this is already resolved is not supported."
        ),
        recommended_action=action,
        suggested_owner=owner,
        due_hint=due_hint,
        evidence_ids=[record.id for record in relevant],
        contradictions_checked=[
            ChallengeResult(
                hypothesis="The reported issue is already resolved.",
                result="not_supported",
                evidence_ids=open_ids,
            )
        ],
        missing_evidence=[],
    )


def _suppress(
    relevant: list[EvidenceRecord],
    resolved_records: list[EvidenceRecord],
) -> ModelDecision:
    titles = _titles(resolved_records)
    return ModelDecision(
        decision="SUPPRESS",
        reason=(
            f"Available evidence shows the issue is already resolved ({titles}). "
            "Intervention is not required."
        ),
        recommended_action=(
            "Do not escalate. Leave the resolved issue closed unless new evidence appears."
        ),
        suggested_owner="Delivery owner",
        due_hint=None,
        evidence_ids=[record.id for record in relevant],
        contradictions_checked=[
            ChallengeResult(
                hypothesis="The issue still requires intervention.",
                result="not_supported",
                evidence_ids=[record.id for record in resolved_records[:4]],
            )
        ],
        missing_evidence=[],
    )


def _abstain(relevant: list[EvidenceRecord]) -> ModelDecision:
    if not relevant:
        reason = "The supplied evidence does not address the claim, so the decision is abstain."
        gaps = ["No supplied evidence addresses this claim."]
        evidence_ids: list[str] = []
        challenges: list[ChallengeResult] = []
    else:
        reason = (
            "The supplied evidence is insufficient to support or dismiss intervention "
            f"({_titles(relevant)})."
        )
        gaps = _gaps(relevant)
        evidence_ids = [record.id for record in relevant]
        challenges = [
            ChallengeResult(
                hypothesis="A dated commitment, owner, and unresolved blocker support intervention.",
                result="inconclusive",
                evidence_ids=evidence_ids[:4],
            )
        ]
    return ModelDecision(
        decision="ABSTAIN",
        reason=reason,
        recommended_action=(
            "Gather a dated milestone, an accountable owner, and whether any delivery "
            "blocker exists before intervening."
        ),
        suggested_owner="Account owner",
        due_hint=None,
        evidence_ids=evidence_ids,
        contradictions_checked=challenges,
        missing_evidence=gaps,
    )


def _gaps(records: list[EvidenceRecord]) -> list[str]:
    blob = combined_text(records)
    gaps = ["No evidence describes an unresolved delivery blocker."]
    if "resolved" not in blob and "verified" not in blob:
        gaps.append("No evidence shows the issue was resolved and verified.")
    if "no milestone" in blob or "no target date" in blob or "milestone" not in blob:
        gaps.append("No dated milestone or target date is established.")
    if "no owner" in blob or "owner" not in blob:
        gaps.append("No accountable owner is named.")
    return gaps[:4]


def _titles(records: list[EvidenceRecord]) -> str:
    return "; ".join(record.title for record in records[:3])
