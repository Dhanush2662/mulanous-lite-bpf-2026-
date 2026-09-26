"""Which records are exact facts, and which are semantic text.

Vector search must not decide ticket state, quantities, dates, ids, or status.
Those sources stay on the structured path.
"""

from __future__ import annotations

from app.schemas.models import RetrievalClass

SEMANTIC_SOURCES = frozenset({"slack", "meetings", "quality"})


def retrieval_class_for(source: str) -> RetrievalClass:
    if source in SEMANTIC_SOURCES:
        return "semantic"
    return "structured"
