"""OpenAI structured-output provider. Used only when OPENAI_API_KEY is set."""

from __future__ import annotations

from app.reasoning.prompt import (
    MODEL_OUTPUT_SCHEMA,
    SYSTEM_PROMPT,
    DecisionPrompt,
    render_repair_prompt,
    render_user_prompt,
)


class OpenAIDecisionProvider:
    name = "openai"

    def __init__(self, api_key: str, model: str) -> None:
        from openai import OpenAI

        self._model = model
        self._client = OpenAI(api_key=api_key, timeout=20.0)

    def complete(self, prompt: DecisionPrompt) -> str:
        return self._complete(render_user_prompt(prompt))

    def repair(self, prompt: DecisionPrompt, previous_output: str, errors: list[str]) -> str:
        return self._complete(render_repair_prompt(prompt, previous_output, errors))

    def _complete(self, user_prompt: str) -> str:
        response = self._client.chat.completions.create(
            model=self._model,
            temperature=0,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "DecisionOutput",
                    "strict": True,
                    "schema": MODEL_OUTPUT_SCHEMA,
                },
            },
        )
        content = response.choices[0].message.content
        if not content:
            raise RuntimeError("empty model content")
        return content
