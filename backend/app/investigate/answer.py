"""Deterministic grounded answers. Replace this router in P1 with a tool-limited model."""

from __future__ import annotations

import re
from collections.abc import Callable

from app.investigate.tools import get_case, get_evidence, inspect_evidence, reanalyze_case
from app.schemas.models import (
    AnalyzeResponse,
    Case,
    EvidenceRecord,
    InvestigateResponse,
    InvestigationTool,
)

_EVIDENCE_ID = re.compile(r"\b(?:crm|jira|slack|meetings):[A-Za-z0-9-]+\b")
_REANALYZE = ("reanalyze", "analyze again", "analyse again", "decide again", "run the analysis")


def answer_question(
    case: Case,
    assembled: list[EvidenceRecord],
    catalog: dict[str, EvidenceRecord],
    message: str,
    stored_analysis: AnalyzeResponse | None,
    reanalyze: Callable[[], AnalyzeResponse],
    refresh_case: Callable[[], Case],
) -> InvestigateResponse:
    tools_used: list[InvestigationTool] = []
    analysis = stored_analysis
    if _wants_reanalyze(message):
        analysis = reanalyze_case(reanalyze)
        tools_used.append("reanalyze_case")
        case = refresh_case()
    case, analysis = get_case(case, analysis)
    tools_used.append("get_case")
    evidence = get_evidence(assembled)
    tools_used.append("get_evidence")
    inspected = _inspect_requested(message, catalog, tools_used)
    evidence_ids = _collect_ids(evidence, inspected, analysis)
    return InvestigateResponse(
        case_id=case.id,
        answer=_compose(case, evidence, inspected, analysis),
        tools_used=tools_used,
        evidence_ids=evidence_ids,
    )


def _wants_reanalyze(message: str) -> bool:
    text = message.lower()
    return any(phrase in text for phrase in _REANALYZE)


def _inspect_requested(
    message: str,
    catalog: dict[str, EvidenceRecord],
    tools_used: list[InvestigationTool],
) -> list[EvidenceRecord]:
    inspected: list[EvidenceRecord] = []
    for evidence_id in _EVIDENCE_ID.findall(message):
        record = inspect_evidence(catalog, evidence_id)
        if record is None:
            continue
        inspected.append(record)
        if "inspect_evidence" not in tools_used:
            tools_used.append("inspect_evidence")
    return inspected


def _collect_ids(
    evidence: list[EvidenceRecord],
    inspected: list[EvidenceRecord],
    analysis: AnalyzeResponse | None,
) -> list[str]:
    ordered: list[str] = []
    pools = [evidence, inspected]
    if analysis is not None:
        pools.append(analysis.evidence)
    for pool in pools:
        for record in pool:
            if record.id not in ordered:
                ordered.append(record.id)
    return ordered


def _compose(
    case: Case,
    evidence: list[EvidenceRecord],
    inspected: list[EvidenceRecord],
    analysis: AnalyzeResponse | None,
) -> str:
    parts = [f"{case.account}: {case.claim}.", f"Urgency: {case.urgency}."]
    if analysis is None:
        parts.append("This case has not been analyzed yet.")
    else:
        parts.append(f"Disposition is {analysis.decision}. {analysis.reason}")
        parts.append(f"Recommended action: {analysis.recommended_action}")
        if analysis.missing_evidence:
            parts.append("Missing evidence: " + "; ".join(analysis.missing_evidence))
    if inspected:
        for record in inspected:
            parts.append(f"{record.id}: {record.title}. {record.body}")
    elif evidence:
        titles = ", ".join(record.title for record in evidence[:6])
        parts.append(f"Assembled evidence: {titles}.")
    else:
        parts.append("No evidence was assembled for this case.")
    return " ".join(parts)
