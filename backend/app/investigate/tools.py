"""Case-scoped read tools. A later agent may call these and nothing else."""

from __future__ import annotations

from collections.abc import Callable

from app.schemas.models import AnalyzeResponse, Case, EvidenceRecord


def get_case(
    case: Case,
    analysis: AnalyzeResponse | None,
) -> tuple[Case, AnalyzeResponse | None]:
    return case, analysis


def get_evidence(evidence: list[EvidenceRecord]) -> list[EvidenceRecord]:
    return list(evidence)


def inspect_evidence(
    catalog: dict[str, EvidenceRecord],
    evidence_id: str,
) -> EvidenceRecord | None:
    return catalog.get(evidence_id)


def reanalyze_case(reanalyze: Callable[[], AnalyzeResponse]) -> AnalyzeResponse:
    return reanalyze()
