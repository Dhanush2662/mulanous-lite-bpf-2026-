"""Disposition follows evidence text, not case id or the claim string."""

from __future__ import annotations

from pathlib import Path

from app.reasoning.deterministic import classify_evidence
from app.schemas.models import EvidenceRecord


def test_application_code_does_not_embed_demo_case_ids() -> None:
    root = Path(__file__).resolve().parents[1] / "app"
    banned = ("acme-sso-rollout", "globex-export-timeout", "initech-europe-expansion")
    for path in root.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        for token in banned:
            assert token not in text, f"{path} contains {token}"


def test_same_claim_with_different_evidence_changes_the_decision() -> None:
    open_issue = _record(
        "jira:X-1",
        "jira",
        "X-1",
        "Export timeout still open",
        "The export timeout is still blocked and unresolved. The customer cannot complete the nightly run.",
    )
    resolved_issue = _record(
        "jira:X-2",
        "jira",
        "X-2",
        "SSO rollout closed",
        "The SSO rollout is resolved and verified with the customer. No further action.",
    )
    vague_issue = _record(
        "crm:X-3",
        "crm",
        "X-3",
        "SSO note",
        "The SSO rollout might happen someday. No milestone, no owner, and no target date. It is only a possibility.",
    )
    assert classify_evidence("Export timeout escalation", [open_issue]).decision == "VERIFY"
    assert classify_evidence("SSO rollout blocked", [resolved_issue]).decision == "SUPPRESS"
    assert classify_evidence("SSO rollout blocked", [vague_issue]).decision == "ABSTAIN"


def test_an_open_blocker_outweighs_a_closed_aside() -> None:
    mixed = _record(
        "meetings:X-4",
        "meetings",
        "X-4",
        "Weekly check-in",
        "A separate export question was closed. The SSO blocker remains open and unresolved.",
    )
    decision = classify_evidence("SSO rollout blocked", [mixed])
    assert decision.decision == "VERIFY"
    assert decision.evidence_ids == ["meetings:X-4"]


def _record(evidence_id: str, source: str, source_record_id: str, title: str, body: str) -> EvidenceRecord:
    return EvidenceRecord(
        id=evidence_id,
        source=source,
        source_record_id=source_record_id,
        title=title,
        body=body,
        observed_at="2026-09-25T10:00:00Z",
    )
