"""UTC timestamp checks. Invalid source timestamps become null. Never invent one."""

from __future__ import annotations

from datetime import datetime, timedelta


def is_utc_timestamp(value: str | None) -> bool:
    if value is None:
        return True
    if not isinstance(value, str) or not value.strip():
        return False
    text = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return False
    if parsed.tzinfo is None:
        return False
    return parsed.utcoffset() == timedelta(0)
