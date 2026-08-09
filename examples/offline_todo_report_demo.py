from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent_runtime import AgentRuntime, FakeModel, JsonMemory, ModelReply
from agent_runtime.filesystem_tools import build_filesystem_tools
from agent_runtime.memory_tools import build_memory_tools
from examples.seed_workspace import seed_workspace


REPORT = """# TODO Report

- app.py:2 - TODO: validate command line arguments
- notes.md:3 - TODO: write reviewer setup instructions
- notes.md:4 - TODO: document the memory file location
- src/helpers.py:2 - TODO: handle empty strings
"""


def main() -> None:
    workspace = seed_workspace()
    memory_path = Path(".agent-memory.json")
    memory = JsonMemory(memory_path)
    tools = build_filesystem_tools(workspace) + build_memory_tools(memory)
    model = FakeModel(
        [
            ModelReply.tool_call("list_files", {}),
            ModelReply.tool_call("search_files", {"query": "TODO"}),
            ModelReply.tool_call("write_file", {"path": "todo-report.md", "content": REPORT}),
            ModelReply.tool_call("remember", {"key": "todo_report_path", "value": "workspace/todo-report.md"}),
            ModelReply.final("Created workspace/todo-report.md and remembered its location."),
        ]
    )
    result = AgentRuntime(model=model, tools=tools, memory=memory).run(
        "Inspect the files in the workspace, find all TODO items, create a concise report at todo-report.md, and remember where the report was saved."
    )

    fresh_memory = JsonMemory(memory_path)
    recall_model = FakeModel(
        [
            ModelReply.tool_call("recall", {"key": "todo_report_path"}),
            ModelReply.final(f"The TODO report was saved at {fresh_memory.recall('todo_report_path')}."),
        ]
    )
    recall_result = AgentRuntime(
        model=recall_model,
        tools=build_memory_tools(fresh_memory),
        memory=fresh_memory,
    ).run("Where did you save the TODO report?")

    report_path = workspace / "todo-report.md"
    print(result.answer)
    print(f"report_exists={report_path.exists()}")
    print(f"report_path={report_path}")
    print(f"memory.todo_report_path={fresh_memory.recall('todo_report_path')}")
    print(recall_result.answer)


if __name__ == "__main__":
    main()
