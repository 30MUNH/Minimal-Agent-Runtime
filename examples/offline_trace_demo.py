from __future__ import annotations

import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent_runtime import AgentRuntime, FakeModel, JsonMemory, ModelReply, Tool
from agent_runtime.observability import format_execution_summary, format_human_trace, save_run_log


def main() -> None:
    with TemporaryDirectory() as directory:
        runtime = AgentRuntime(
            model=FakeModel(
                [
                    ModelReply.tool_call("echo", {"text": "trace me"}),
                    ModelReply.final("Trace complete."),
                ]
            ),
            tools=[Tool("echo", "Echo text.", {"type": "object"}, lambda args: args["text"])],
            memory=JsonMemory(Path(directory) / "memory.json"),
        )
        result = runtime.run("Show a trace.")
        log_path = save_run_log(result, Path("logs"))

        print(result.answer)
        print()
        print(format_human_trace(result, verbose=True))
        print()
        print(format_execution_summary(result))
        print(f"\nSaved trace: {log_path}")


if __name__ == "__main__":
    main()
