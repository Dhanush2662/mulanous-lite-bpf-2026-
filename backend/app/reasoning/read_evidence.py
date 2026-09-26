"""Read stance from evidence text. This module does not know case ids."""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.schemas.models import EvidenceRecord

_TOKEN = re.compile(r"[a-z0-9]+")
_STOPWORDS = frozenset(
    """
    a an the of to at is on for and or by with from was were be this that it as in
    not no are but if we they you our their has have had will can may
    """.split()
)

OPEN_PHRASES = (
    "remains open",
    "still blocked",
    "still open",
    "unresolved",
    "cannot complete",
    "blocker",
    "blocked by",
    "no resolution",
    "not shipped",
    "remains blocked",
    "material shortage",
    "quality hold",
    "throughput drop",
    "cannot meet",
)
RESOLVED_PHRASES = (
    "resolved",
    "verified",
    "signed off",
    "no further action",
    "do not reopen",
    "already resolved",
    "closed",
)
VAGUE_PHRASES = (
    "might",
    "possible",
    "possibility",
    "exploring",
    "no milestone",
    "no owner",
    "no signed",
    "no target date",
    "no details",
    "no acceptance",
    "unscheduled",
    "no decision",
    "no scope",
    "not scheduled",
    "insufficient",
)
_STRONG_OPEN = (
    "remains open",
    "unresolved",
    "still blocked",
    "still open",
    "no resolution",
    "blocker",
    "blocked by",
    "material shortage",
    "quality hold",
    "throughput drop",
)


@dataclass(frozen=True)
class EvidenceRead:
    relevant: list[EvidenceRecord]
    open_records: list[EvidenceRecord]
    resolved_records: list[EvidenceRecord]
    vague_records: list[EvidenceRecord]
    neutral_records: list[EvidenceRecord]


def read_evidence(claim: str, evidence: list[EvidenceRecord]) -> EvidenceRead:
    terms = _terms(claim)
    relevant = [record for record in evidence if _on_claim(record, terms)]
    grouped: dict[str, list[EvidenceRecord]] = {
        "open": [],
        "resolved": [],
        "vague": [],
        "neutral": [],
    }
    for record in relevant:
        grouped[record_stance(record)].append(record)
    return EvidenceRead(
        relevant=relevant,
        open_records=grouped["open"],
        resolved_records=grouped["resolved"],
        vague_records=grouped["vague"],
        neutral_records=grouped["neutral"],
    )


def record_stance(record: EvidenceRecord) -> str:
    text = f"{record.title} {record.body}".lower()
    open_hit = _any_phrase(text, OPEN_PHRASES)
    resolved_hit = _any_phrase(text, RESOLVED_PHRASES)
    if open_hit and resolved_hit:
        return (
            "open"
            if _last_phrase_end(text, _STRONG_OPEN) > _last_phrase_end(text, RESOLVED_PHRASES)
            else "resolved"
        )
    if open_hit:
        return "open"
    if resolved_hit:
        return "resolved"
    if _any_phrase(text, VAGUE_PHRASES):
        return "vague"
    return "neutral"


def combined_text(records: list[EvidenceRecord]) -> str:
    return " ".join(f"{record.title} {record.body}" for record in records).lower()


def _on_claim(record: EvidenceRecord, terms: set[str]) -> bool:
    if not terms:
        return True
    return bool(_terms(f"{record.title} {record.body}") & terms)


def _terms(text: str) -> set[str]:
    return {
        token
        for token in _TOKEN.findall(text.lower())
        if token not in _STOPWORDS and len(token) > 2
    }


def _any_phrase(text: str, phrases: tuple[str, ...]) -> bool:
    return any(_contains(text, phrase) for phrase in phrases)


def _last_phrase_end(text: str, phrases: tuple[str, ...]) -> int:
    return max(
        (match.end() for phrase in phrases for match in re.finditer(_pattern(phrase), text)),
        default=-1,
    )


def _contains(text: str, phrase: str) -> bool:
    return re.search(_pattern(phrase), text) is not None


def _pattern(phrase: str) -> str:
    return rf"(?<!\w){re.escape(phrase)}(?!\w)"
