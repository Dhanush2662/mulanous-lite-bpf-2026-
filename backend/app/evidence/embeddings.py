"""Query and document embeddings. Tests use the deterministic hasher."""

from __future__ import annotations

import hashlib
import math
import os
import re

from app.logging_config import get_logger
from app.schemas.models import StoredEvidence

logger = get_logger(__name__)

DEFAULT_DIMENSIONS = 64
_TOKEN = re.compile(r"[a-z0-9]+")
_STOPWORDS = frozenset(
    """
    a an the of to at is on for and or by with from was were be this that it as in
    not no are but if we they you our their has have had will can may
    """.split()
)


class FakeEmbedder:
    """Bag-of-tokens hash embedding. Same text always yields the same vector."""

    name = "fake"

    def __init__(self, dimensions: int = DEFAULT_DIMENSIONS) -> None:
        self.dimensions = dimensions
        self._cache: dict[str, list[float]] = {}

    def embed(self, text: str) -> list[float]:
        cached = self._cache.get(text)
        if cached is not None:
            return cached
        vector = [0.0] * self.dimensions
        for token in _tokens(text):
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % self.dimensions
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign
        normalized = _normalize(vector)
        self._cache[text] = normalized
        return normalized


class OpenAIEmbedder:
    name = "openai"

    def __init__(self, api_key: str, model: str, dimensions: int) -> None:
        from openai import OpenAI

        self.dimensions = dimensions
        self._model = model
        self._client = OpenAI(api_key=api_key, timeout=20.0)
        self._cache: dict[str, list[float]] = {}

    def embed(self, text: str) -> list[float]:
        cached = self._cache.get(text)
        if cached is not None:
            return cached
        response = self._client.embeddings.create(
            model=self._model,
            input=text,
            dimensions=self.dimensions,
        )
        vector = [float(value) for value in response.data[0].embedding]
        self._cache[text] = vector
        return vector


def build_embedder(force_fake: bool = False) -> FakeEmbedder | OpenAIEmbedder:
    dimensions = _dimensions()
    if force_fake or not os.environ.get("OPENAI_API_KEY", "").strip():
        logger.info("embedder name=fake dimensions=%s", dimensions)
        return FakeEmbedder(dimensions)
    model = os.environ.get("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small").strip()
    model = model or "text-embedding-3-small"
    try:
        embedder = OpenAIEmbedder(
            api_key=os.environ["OPENAI_API_KEY"].strip(),
            model=model,
            dimensions=dimensions,
        )
    except Exception as exc:
        logger.error("embedder name=fake reason=openai_unavailable error_type=%s", type(exc).__name__)
        return FakeEmbedder(dimensions)
    logger.info("embedder name=openai model=%s dimensions=%s", model, dimensions)
    return embedder


def attach_embeddings(records: list[StoredEvidence], embedder: FakeEmbedder | OpenAIEmbedder) -> None:
    for item in records:
        if item.retrieval_class != "semantic":
            item.embedding = None
            continue
        item.embedding = _embed_text(item, embedder)


def attach_missing_embeddings(
    records: list[StoredEvidence],
    embedder: FakeEmbedder | OpenAIEmbedder,
) -> list[StoredEvidence]:
    """Fill semantic rows that Go ingest stored without a vector."""

    filled: list[StoredEvidence] = []
    for item in records:
        if item.retrieval_class != "semantic" or item.embedding:
            continue
        item.embedding = _embed_text(item, embedder)
        filled.append(item)
    return filled


def _embed_text(item: StoredEvidence, embedder: FakeEmbedder | OpenAIEmbedder) -> list[float]:
    text = f"{item.record.title}\n{item.record.body}"
    try:
        return embedder.embed(text)
    except Exception as exc:
        logger.error(
            "embedder state=skipped id=%s error_type=%s",
            item.record.id,
            type(exc).__name__,
        )
        return FakeEmbedder(embedder.dimensions).embed(text)


def cosine(left: list[float], right: list[float]) -> float:
    if not left or len(left) != len(right):
        return 0.0
    dot = sum(a * b for a, b in zip(left, right, strict=True))
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / (left_norm * right_norm)


def rank_by_cosine(
    records: list[StoredEvidence],
    vector: list[float],
    limit: int,
) -> list[StoredEvidence]:
    scored = [
        (cosine(item.embedding, vector), item)
        for item in records
        if item.embedding
    ]
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [item for score, item in scored if score > 0][:limit]


def _tokens(text: str) -> list[str]:
    return [
        token
        for token in _TOKEN.findall(text.lower())
        if token not in _STOPWORDS and len(token) > 2
    ]


def _normalize(vector: list[float]) -> list[float]:
    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        return vector
    return [value / norm for value in vector]


def _dimensions() -> int:
    raw = os.environ.get("EMBEDDING_DIMENSIONS", str(DEFAULT_DIMENSIONS)).strip()
    try:
        parsed = int(raw)
    except ValueError:
        return DEFAULT_DIMENSIONS
    if parsed < 8:
        return DEFAULT_DIMENSIONS
    return parsed
