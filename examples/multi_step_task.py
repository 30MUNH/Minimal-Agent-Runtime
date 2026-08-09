from __future__ import annotations

import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent_runtime import AgentRuntime, FakeModel, JsonMemory, ModelReply, Tool


def main() -> None:
    with TemporaryDirectory() as directory:
        memory = JsonMemory(Path(directory) / "memory.json")
        tools = [
            Tool("add", "Add two numbers.", {"type": "object"}, lambda args: args["a"] + args["b"]),
            Tool(
                "remember",
                "Persist a key/value pair in memory.",
                {"type": "object"},
                lambda args: memory.remember(args["key"], args["value"]) or "stored",
            ),
        ]
        model = FakeModel(
            [
                ModelReply.tool_call("add", {"a": 13, "b": 29}),
                ModelReply.tool_call("remember", {"key": "demo_sum", "value": 42}),
                ModelReply.final("I added the numbers and remembered 42."),
            ]
        )
        runtime = AgentRuntime(model=model, tools=tools, memory=memory)
        result = runtime.run("Add 13 and 29, remember the result, then report it.")

        print(result.answer)
        print(f"memory.demo_sum={memory.recall('demo_sum')}")
        print(f"trace_steps={len(result.trace)}")


if __name__ == "__main__":
    main()
