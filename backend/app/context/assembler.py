"""Account filter, light lexical relevance, recency, dedupe, and a small cap."""

from __future__ import annotations

import re

from app.schemas.models import EvidenceRecord, StoredEvidence

EVIDENCE_CAP = 12

_STOPWORDS = frozenset(
    """
    a an the of to at is on for and or by with from was were be this that it as in
    not no are but if we they you our their has have had will can may
    """.split()
)
_TOKEN = re.compile(r"[a-z0-9]+")


def assemble_context(
    account_id: str,
    claim: str,
    account: str,
    evidence: list[StoredEvidence],
) -> list[EvidenceRecord]:
    account_records = [item for item in evidence if item.account_id == account_id]
    terms = _terms(f"{claim} {account}")
    scored = [(_score(item.record, terms), item.record) for item in account_records]
    positive = [pair for pair in scored if pair[0] > 0]
    chosen = positive or scored
    chosen.sort(key=lambda pair: (pair[0], pair[1].observed_at or ""), reverse=True)
    return _dedupe(chosen)[:EVIDENCE_CAP]


def filter_evidence(
    records: list[EvidenceRecord],
    source: str | None,
    query: str | None,
) -> list[EvidenceRecord]:
    selected = records
    if source and source.strip():
        selected = [record for record in selected if record.source == source.strip()]
    needle = (query or "").strip().lower()
    if needle:
        selected = [record for record in selected if _matches(record, needle)]
    return selected


def _terms(text: str) -> set[str]:
    return {token for token in _TOKEN.findall(text.lower()) if token not in _STOPWORDS and len(token) > 2}


def _score(record: EvidenceRecord, terms: set[str]) -> int:
    if not terms:
        return 0
    haystack = _terms(f"{record.title} {record.body}")
    return len(haystack & terms)


def _dedupe(scored: list[tuple[int, EvidenceRecord]]) -> list[EvidenceRecord]:
    selected: list[EvidenceRecord] = []
    seen: set[str] = set()
    for _score_value, record in scored:
        if record.id in seen:
            continue
        seen.add(record.id)
        selected.append(record)
    return selected


def _matches(record: EvidenceRecord, needle: str) -> bool:
    haystack = f"{record.title} {record.body} {record.source_record_id}".lower()
    return needle in haystack
