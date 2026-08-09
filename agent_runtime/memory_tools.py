from __future__ import annotations

from typing import Any

from .memory import JsonMemory
from .tools import Tool


def build_memory_tools(memory: JsonMemory) -> list[Tool]:
    return [
        Tool(
            name="remember",
            description="Persist a key/value fact in long-term JSON memory.",
            schema={
                "type": "object",
                "properties": {"key": {"type": "string"}, "value": {}},
                "required": ["key", "value"],
                "additionalProperties": False,
            },
            handler=lambda args: _remember(memory, args),
        ),
        Tool(
            name="recall",
            description="Recall a value from long-term JSON memory by key.",
            schema={
                "type": "object",
                "properties": {"key": {"type": "string"}},
                "required": ["key"],
                "additionalProperties": False,
            },
            handler=lambda args: memory.recall(str(args["key"])),
        ),
    ]


def _remember(memory: JsonMemory, args: dict[str, Any]) -> str:
    memory.remember(str(args["key"]), args["value"])
    return "stored"
