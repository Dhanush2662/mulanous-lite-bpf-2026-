"""Load case seeds and synthetic CRM, Jira, Slack, and meeting fixtures."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from app.logging_config import get_logger
from app.schemas.models import Domain

logger = get_logger(__name__)

EVIDENCE_SOURCES = ("crm", "jira", "slack", "meetings")


class CaseSeed(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str = Field(min_length=1)
    domain: Domain
    pattern: str = Field(min_length=1)
    account: str = Field(min_length=1)
    account_id: str = Field(min_length=1)
    claim: str = Field(min_length=1)
    urgency: str = Field(min_length=1)


class EvidenceSeed(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str = Field(min_length=1)
    account_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    text: str | None = None
    body: str | None = None
    observed_at: str | None = None

    def body_text(self) -> str:
        return (self.body if self.body is not None else self.text or "").strip()


@dataclass
class RawEvidence:
    source: str
    seed: EvidenceSeed


@dataclass
class LoadedWorkspace:
    cases: list[CaseSeed] = field(default_factory=list)
    records: list[RawEvidence] = field(default_factory=list)
    statuses: dict[str, str] = field(default_factory=dict)


def load_workspace(data_dir: Path) -> LoadedWorkspace:
    loaded = LoadedWorkspace()
    loaded.cases = _load_cases(data_dir / "cases.json", loaded.statuses)
    for source in EVIDENCE_SOURCES:
        loaded.records.extend(
            _load_evidence(data_dir / f"{source}.json", source, loaded.statuses)
        )
    logger.info("source_load state=%s", loaded.statuses)
    return loaded


def _read_json_array(path: Path, statuses: dict[str, str], label: str) -> list[object] | None:
    if not path.is_file():
        statuses[label] = "unavailable"
        logger.error("source_load source=%s state=unavailable", label)
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        statuses[label] = "unavailable"
        logger.error(
            "source_load source=%s state=unavailable error_type=%s",
            label,
            type(exc).__name__,
        )
        return None
    if not isinstance(payload, list):
        statuses[label] = "unavailable"
        logger.error("source_load source=%s state=unavailable error_type=not_a_list", label)
        return None
    return payload


def _load_cases(path: Path, statuses: dict[str, str]) -> list[CaseSeed]:
    payload = _read_json_array(path, statuses, "cases")
    if payload is None:
        return []
    cases: list[CaseSeed] = []
    for index, item in enumerate(payload):
        try:
            cases.append(CaseSeed.model_validate(item))
        except ValidationError:
            logger.error("source_load source=cases state=skipped index=%s", index)
    statuses["cases"] = f"loaded:{len(cases)}"
    return cases


def _load_evidence(path: Path, source: str, statuses: dict[str, str]) -> list[RawEvidence]:
    payload = _read_json_array(path, statuses, source)
    if payload is None:
        return []
    records: list[RawEvidence] = []
    for index, item in enumerate(payload):
        try:
            seed = EvidenceSeed.model_validate(item)
        except ValidationError:
            logger.error("source_load source=%s state=skipped index=%s", source, index)
            continue
        if not seed.body_text():
            logger.error("source_load source=%s state=skipped index=%s", source, index)
            continue
        records.append(RawEvidence(source=source, seed=seed))
    statuses[source] = f"loaded:{len(records)}"
    return records
