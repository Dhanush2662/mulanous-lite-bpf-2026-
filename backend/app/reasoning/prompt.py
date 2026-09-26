"""Versioned decision prompt. Grounded in supplied evidence. Schema output only."""

from __future__ import annotations

from dataclasses import dataclass

from app.schemas.models import EvidenceRecord

PROMPT_VERSION = "decision-v2"

SYSTEM_PROMPT = f"""You are the Mulanous Lite decision agent ({PROMPT_VERSION}).
A delivery manager asked whether a customer commitment needs intervention.
The claim is the question. The evidence records are the only facts.

Decide from the evidence:
- VERIFY when the evidence is sufficient and consistent that a commitment is still blocked or otherwise needs intervention.
- SUPPRESS when the evidence shows the suspected issue is already resolved, contradicted, or does not need intervention. Do not recommend escalation.
- ABSTAIN when the evidence is missing, vague, or insufficient to support or dismiss intervention. Name the gaps in missing_evidence.

Rules:
- Use only evidence ids from the supplied list. Never invent an id, a source, or a fact.
- contradictions_checked.evidence_ids must be a subset of evidence_ids.
- decision is exactly VERIFY, SUPPRESS, or ABSTAIN.
- Do not output a confidence percentage, a risk score, or chain-of-thought.
- Return only the structured object. No prose outside the schema.
"""

MODEL_OUTPUT_SCHEMA: dict[str, object] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "decision": {"type": "string", "enum": ["VERIFY", "SUPPRESS", "ABSTAIN"]},
        "reason": {"type": "string"},
        "recommended_action": {"type": "string"},
        "suggested_owner": {"type": "string"},
        "due_hint": {"anyOf": [{"type": "string"}, {"type": "null"}]},
        "evidence_ids": {"type": "array", "items": {"type": "string"}},
        "contradictions_checked": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "hypothesis": {"type": "string"},
                    "result": {
                        "type": "string",
                        "enum": ["supported", "not_supported", "inconclusive"],
                    },
                    "evidence_ids": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["hypothesis", "result", "evidence_ids"],
            },
        },
        "missing_evidence": {"type": "array", "items": {"type": "string"}},
    },
    "required": [
        "decision",
        "reason",
        "recommended_action",
        "suggested_owner",
        "due_hint",
        "evidence_ids",
        "contradictions_checked",
        "missing_evidence",
    ],
}


@dataclass(frozen=True)
class DecisionPrompt:
    domain: str
    pattern: str
    account: str
    claim: str
    urgency: str
    evidence: tuple[EvidenceRecord, ...]

    @property
    def allowed_ids(self) -> list[str]:
        return [record.id for record in self.evidence]


def render_user_prompt(prompt: DecisionPrompt) -> str:
    return "\n".join(
        [
            f"Prompt-Version: {PROMPT_VERSION}",
            f"Domain: {prompt.domain}",
            f"Pattern: {prompt.pattern}",
            f"Account: {prompt.account}",
            f"Claim: {prompt.claim}",
            f"Urgency: {prompt.urgency}",
            "Allowed evidence ids:",
            "\n".join(f"- {evidence_id}" for evidence_id in prompt.allowed_ids) or "- (none)",
            "Evidence JSON:",
            _evidence_json(prompt.evidence),
        ]
    )


def render_repair_prompt(prompt: DecisionPrompt, previous_output: str, errors: list[str]) -> str:
    error_lines = "\n".join(f"- {error}" for error in errors) or "- invalid output"
    return "\n".join(
        [
            render_user_prompt(prompt),
            "The previous structured output failed validation.",
            "Errors:",
            error_lines,
            "Previous output:",
            previous_output[:4000],
            "Return one corrected object. Use only allowed evidence ids.",
        ]
    )


def _evidence_json(evidence: tuple[EvidenceRecord, ...]) -> str:
    lines = []
    for record in evidence:
        lines.append(
            "{"
            f'"id": {_quote(record.id)}, '
            f'"source": {_quote(record.source)}, '
            f'"source_record_id": {_quote(record.source_record_id)}, '
            f'"title": {_quote(record.title)}, '
            f'"body": {_quote(record.body)}, '
            f'"observed_at": {_quote(record.observed_at) if record.observed_at else "null"}'
            "}"
        )
    return "[\n" + ",\n".join(lines) + "\n]"


def _quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ")
    return f'"{escaped}"'
