from __future__ import annotations

import json
from typing import Any, Protocol

from .runtime import ModelReply


class ModelProvider(Protocol):
    def complete(self, messages: list[dict[str, Any]], tools: list[dict[str, Any]]) -> ModelReply:
        ...


class FakeModel:
    def __init__(self, replies: list[ModelReply]):
        self.replies = list(replies)
        self.calls: list[dict[str, Any]] = []

    def complete(self, messages: list[dict[str, Any]], tools: list[dict[str, Any]]) -> ModelReply:
        self.calls.append({"messages": list(messages), "tools": list(tools)})
        if not self.replies:
            raise RuntimeError("FakeModel has no replies left")
        return self.replies.pop(0)


class OpenAIModelProvider:
    def __init__(self, model: str = "gpt-4.1-mini", client: Any | None = None):
        self.model = model
        self.client = client or self._build_client()

    def complete(self, messages: list[dict[str, Any]], tools: list[dict[str, Any]]) -> ModelReply:
        response = self.client.responses.create(
            model=self.model,
            input=messages,
            tools=[self._openai_tool(tool) for tool in tools],
        )
        return self._normalize(response)

    def _openai_tool(self, tool: dict[str, Any]) -> dict[str, Any]:
        return {
            "type": "function",
            "name": tool["name"],
            "description": tool["description"],
            "parameters": tool["schema"],
        }

    def _normalize(self, response: Any) -> ModelReply:
        for item in getattr(response, "output", []):
            item_type = self._get(item, "type")
            if item_type == "function_call":
                return ModelReply.tool_call(
                    self._get(item, "name"),
                    json.loads(self._get(item, "arguments") or "{}"),
                    call_id=self._get(item, "call_id"),
                )
            if item_type == "message":
                text = self._message_text(self._get(item, "content") or [])
                if text:
                    return ModelReply.final(text)
        text = getattr(response, "output_text", None)
        if text:
            return ModelReply.final(text)
        raise ValueError("OpenAI response did not contain a final answer or function call")

    def _message_text(self, content: Any) -> str:
        parts: list[str] = []
        for item in content:
            item_type = self._get(item, "type")
            if item_type in {"output_text", "text"}:
                parts.append(self._get(item, "text") or "")
        return "".join(parts)

    def _get(self, item: Any, key: str) -> Any:
        if isinstance(item, dict):
            return item.get(key)
        return getattr(item, key, None)

    def _build_client(self) -> Any:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("Install the optional OpenAI SDK with `python3 -m pip install openai`.") from exc
        return OpenAI()
