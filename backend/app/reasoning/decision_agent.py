"""Run one structured model call, then one repair, then a safe abstain."""

from __future__ import annotations

from app.logging_config import get_logger
from app.reasoning.prompt import PROMPT_VERSION, DecisionPrompt
from app.reasoning.provider import DecisionProvider
from app.schemas.models import AnalyzeResponse, AssembledContext
from app.validation.validator import AnalysisAccepted, safe_abstain, validate_model_output

logger = get_logger(__name__)


class DecisionAgent:
    def __init__(self, provider: DecisionProvider) -> None:
        self._provider = provider

    def decide(self, context: AssembledContext) -> AnalyzeResponse:
        prompt = self._prompt(context)
        logger.info(
            "analysis_start case_id=%s prompt=%s context_size=%s provider=%s",
            context.case_id,
            PROMPT_VERSION,
            len(context.evidence),
            self._provider.name,
        )
        raw = self._complete(prompt)
        first = validate_model_output(raw, context)
        if isinstance(first, AnalysisAccepted):
            return self._accepted(first, "initial")
        logger.info("validation result=rejected phase=initial errors=%s", first.errors)
        repaired = self._repair(prompt, raw, first.errors)
        second = validate_model_output(repaired, context)
        if isinstance(second, AnalysisAccepted):
            return self._accepted(second, "repair")
        logger.info("validation result=rejected phase=repair errors=%s", second.errors)
        logger.info("analysis_end decision=ABSTAIN case_id=%s", context.case_id)
        return safe_abstain(context)

    def _prompt(self, context: AssembledContext) -> DecisionPrompt:
        return DecisionPrompt(
            account=context.account,
            claim=context.claim,
            urgency=context.urgency,
            evidence=tuple(context.evidence),
        )

    def _complete(self, prompt: DecisionPrompt) -> str:
        try:
            raw = self._provider.complete(prompt)
        except Exception as exc:
            logger.error("model_call result=failure phase=initial error_type=%s", type(exc).__name__)
            return ""
        logger.info("model_call result=success phase=initial")
        return raw if isinstance(raw, str) else ""

    def _repair(self, prompt: DecisionPrompt, previous: str, errors: list[str]) -> str:
        try:
            raw = self._provider.repair(prompt, previous, errors)
        except Exception as exc:
            logger.error("model_call result=failure phase=repair error_type=%s", type(exc).__name__)
            return ""
        logger.info("model_call result=success phase=repair")
        return raw if isinstance(raw, str) else ""

    def _accepted(self, outcome: AnalysisAccepted, phase: str) -> AnalyzeResponse:
        decision = outcome.response.decision
        logger.info("validation result=accepted phase=%s decision=%s", phase, decision)
        logger.info(
            "analysis_end decision=%s case_id=%s",
            decision,
            outcome.response.case_id,
        )
        return outcome.response
