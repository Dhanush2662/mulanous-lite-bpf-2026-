"""Scripted model providers. They do not read case ids."""

from __future__ import annotations

from app.reasoning.prompt import DecisionPrompt


class ScriptedDecisionProvider:
    name = "scripted"

    def __init__(self, outputs: list[str]) -> None:
        self._outputs = list(outputs)

    def complete(self, prompt: DecisionPrompt) -> str:
        del prompt
        if not self._outputs:
            raise RuntimeError("scripted provider has no output")
        return self._outputs.pop(0)

    def repair(self, prompt: DecisionPrompt, previous_output: str, errors: list[str]) -> str:
        del prompt, errors
        if not self._outputs:
            return previous_output
        return self._outputs.pop(0)


class FailingDecisionProvider:
    name = "failing"

    def complete(self, prompt: DecisionPrompt) -> str:
        del prompt
        raise TimeoutError("model timeout")

    def repair(self, prompt: DecisionPrompt, previous_output: str, errors: list[str]) -> str:
        del prompt, previous_output, errors
        raise TimeoutError("model timeout")
