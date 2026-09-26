"""Turn source payloads into flat evidence records."""

from __future__ import annotations

from app.adapters.sources import LoadedWorkspace
from app.evidence.timestamps import is_utc_timestamp
from app.logging_config import get_logger
from app.schemas.models import CaseRecord, EvidenceRecord, StoredEvidence

logger = get_logger(__name__)

def normalize_evidence(loaded: LoadedWorkspace) -> list[StoredEvidence]:
    stored: list[StoredEvidence] = []
    seen: set[str] = set()
    for raw in loaded.records:
        evidence_id = f"{raw.source}:{raw.seed.id}"
        if evidence_id in seen:
            logger.error("evidence_normalize state=duplicate id=%s", evidence_id)
            continue
        observed_at = raw.seed.observed_at
        if not is_utc_timestamp(observed_at):
            logger.error(
                "evidence_normalize state=timestamp_dropped id=%s",
                evidence_id,
            )
            observed_at = None
        seen.add(evidence_id)
        stored.append(
            StoredEvidence(
                account_id=raw.seed.account_id,
                record=EvidenceRecord(
                    id=evidence_id,
                    source=raw.source,
                    source_record_id=raw.seed.id,
                    title=raw.seed.title.strip(),
                    body=raw.seed.body_text(),
                    observed_at=observed_at,
                ),
            )
        )
    return stored


def build_cases(loaded: LoadedWorkspace, evidence: list[StoredEvidence]) -> list[CaseRecord]:
    counts: dict[str, int] = {}
    for item in evidence:
        counts[item.account_id] = counts.get(item.account_id, 0) + 1
    cases: list[CaseRecord] = []
    for seed in loaded.cases:
        cases.append(
            CaseRecord(
                id=seed.id,
                domain=seed.domain,
                pattern=seed.pattern,
                account=seed.account,
                claim=seed.claim,
                urgency=seed.urgency,
                source_count=counts.get(seed.account_id, 0),
                disposition=None,
                account_id=seed.account_id,
            )
        )
    return cases
