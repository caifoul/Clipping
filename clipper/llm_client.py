from __future__ import annotations

import json
from typing import Any

from .config import SETTINGS


def generate_structured(prompt: str, schema: dict[str, Any], schema_name: str) -> dict[str, Any]:
    """Run `prompt` through the configured LLM backend and return a dict matching `schema`."""
    if SETTINGS.llm_backend == "ollama":
        return _generate_ollama(prompt, schema)
    return _generate_anthropic(prompt, schema, schema_name)


def _generate_ollama(prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
    import ollama

    client = ollama.Client(host=SETTINGS.ollama_host)
    response = client.chat(
        model=SETTINGS.ollama_model,
        messages=[{"role": "user", "content": prompt}],
        format=schema,
        options={"temperature": 0.2},
    )
    return json.loads(response["message"]["content"])


def _generate_anthropic(prompt: str, schema: dict[str, Any], schema_name: str) -> dict[str, Any]:
    from anthropic import Anthropic

    client = Anthropic(api_key=SETTINGS.anthropic_api_key)
    tool = {
        "name": schema_name,
        "description": f"Return {schema_name}",
        "input_schema": schema,
    }
    response = client.messages.create(
        model=SETTINGS.claude_model,
        max_tokens=4096,
        tools=[tool],
        tool_choice={"type": "tool", "name": schema_name},
        messages=[{"role": "user", "content": prompt}],
    )
    tool_use = next(b for b in response.content if b.type == "tool_use")
    return tool_use.input
