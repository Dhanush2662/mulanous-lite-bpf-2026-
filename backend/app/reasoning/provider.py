"""Decision model boundary. Tests supply a fake. Live demo may use OpenAI."""

from __future__ import annotations

from typing import Protocol

from app.reasoning.prompt import DecisionPrompt


class DecisionProvider(Protocol):
    name: str

    def complete(self, prompt: DecisionPrompt) -> str:
        """Return schema JSON. Do not include chain-of-thought."""

    def repair(self, prompt: DecisionPrompt, previous_output: str, errors: list[str]) -> str:
        """One repair attempt after validation rejects the first output."""
