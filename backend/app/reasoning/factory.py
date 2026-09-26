"""Choose the live model from the environment. Never log the API key."""

from __future__ import annotations

import os

from app.logging_config import get_logger
from app.reasoning.deterministic import DeterministicDecisionProvider
from app.reasoning.provider import DecisionProvider

logger = get_logger(__name__)

DEFAULT_MODEL = "gpt-4o-mini"


def build_provider() -> DecisionProvider:
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        logger.info("llm_provider name=deterministic reason=no_api_key")
        return DeterministicDecisionProvider()
    model = os.environ.get("OPENAI_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL
    try:
        from app.reasoning.openai_provider import OpenAIDecisionProvider

        provider = OpenAIDecisionProvider(api_key=api_key, model=model)
    except Exception as exc:
        logger.error(
            "llm_provider name=deterministic reason=openai_unavailable error_type=%s",
            type(exc).__name__,
        )
        return DeterministicDecisionProvider()
    logger.info("llm_provider name=openai model=%s", model)
    return provider
