from __future__ import annotations

from dataclasses import dataclass, field
import json
from time import perf_counter
from typing import Any, Literal, Protocol, Sequence

from .memory import JsonMemory
from .tools import Tool


class ModelProvider(Protocol):
    def complete(self, messages: list[dict[str, Any]], tools: list[dict[str, Any]]) -> "ModelReply":
        ...


@dataclass(frozen=True)
class ModelReply:
    kind: Literal["final", "tool_call"]
    content: str | None = None
    tool: str | None = None
    args: dict[str, Any] = field(default_factory=dict)
    call_id: str | None = None

    @classmethod
    def final(cls, content: str) -> "ModelReply":
        return cls(kind="final", content=content)

    @classmethod
    def tool_call(cls, tool: str, args: dict[str, Any], call_id: str | None = None) -> "ModelReply":
        return cls(kind="tool_call", tool=tool, args=args, call_id=call_id)


@dataclass(frozen=True)
class AgentResult:
    answer: str | None
    trace: list[dict[str, Any]]
    stopped_reason: Literal["final", "max_steps"]
    task: str = ""
    model_provider: str = ""
    total_duration_ms: int = 0


class AgentRuntime:
    def __init__(
        self,
        model: ModelProvider,
        tools: Sequence[Tool],
        memory: JsonMemory,
        max_steps: int = 8,
    ):
        self.model = model
        self.tools = {tool.name: tool for tool in tools}
        self.memory = memory
        self.max_steps = max_steps

    def run(self, task: str) -> AgentResult:
        started = perf_counter()
        trace: list[dict[str, Any]] = []
        messages: list[dict[str, Any]] = [{"role": "user", "content": task}]

        for _ in range(self.max_steps):
            trace.append({"type": "model_invocation", "step": len(trace) + 1})
            reply = self.model.complete(list(messages), self._tool_descriptions())

            if reply.kind == "final":
                trace.append({"type": "final", "content": reply.content})
                messages.append({"role": "assistant", "content": reply.content or ""})
                return self._result(task, reply.content, trace, "final", started)

            if reply.kind != "tool_call":
                raise ValueError(f"Unsupported model reply kind: {reply.kind}")

            tool_name = reply.tool or ""
            call_id = reply.call_id or f"call_{len(trace)}"
            trace.append({"type": "tool_call", "tool": tool_name, "args": dict(reply.args), "call_id": call_id})
            messages.append(
                {
                    "type": "function_call",
                    "call_id": call_id,
                    "name": tool_name,
                    "arguments": json.dumps(reply.args),
                }
            )
            tool = self.tools.get(tool_name)
            if tool is None:
                error = f"Unknown tool: {tool_name}"
                trace.append({"type": "tool_error", "tool": tool_name, "error": error, "duration_ms": 0})
                messages.append(self._tool_message(call_id, {"error": error}))
                continue

            tool_started = perf_counter()
            try:
                value = tool.run(reply.args)
            except Exception as exc:
                duration_ms = self._elapsed_ms(tool_started)
                error = str(exc)
                trace.append({"type": "tool_error", "tool": tool_name, "error": error, "duration_ms": duration_ms})
                messages.append(self._tool_message(call_id, {"error": error}))
            else:
                duration_ms = self._elapsed_ms(tool_started)
                trace.append({"type": "tool_result", "tool": tool_name, "result": value, "duration_ms": duration_ms})
                messages.append(self._tool_message(call_id, {"result": value}))

        return self._result(task, None, trace, "max_steps", started)

    def _tool_descriptions(self) -> list[dict[str, Any]]:
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "schema": tool.schema,
            }
            for tool in self.tools.values()
        ]

    def _tool_message(self, call_id: str, payload: dict[str, Any]) -> dict[str, str]:
        return {
            "type": "function_call_output",
            "call_id": call_id,
            "content": json.dumps(payload, ensure_ascii=False),
        }

    def _result(
        self,
        task: str,
        answer: str | None,
        trace: list[dict[str, Any]],
        stopped_reason: Literal["final", "max_steps"],
        started: float,
    ) -> AgentResult:
        if trace:
            trace[-1]["termination_reason"] = stopped_reason
        return AgentResult(
            answer=answer,
            trace=trace,
            stopped_reason=stopped_reason,
            task=task,
            model_provider=type(self.model).__name__,
            total_duration_ms=self._elapsed_ms(started),
        )

    def _elapsed_ms(self, started: float) -> int:
        return max(0, round((perf_counter() - started) * 1000))
