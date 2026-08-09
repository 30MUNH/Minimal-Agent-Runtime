from __future__ import annotations

import argparse
import os
from pathlib import Path

from .filesystem_tools import build_filesystem_tools
from .memory import JsonMemory
from .memory_tools import build_memory_tools
from .models import OpenAIModelProvider
from .observability import format_execution_summary, format_human_trace, save_run_log
from .runtime import AgentRuntime


def _load_dotenv(path: str = ".env") -> None:
    """Load key=value pairs from a .env file into os.environ (no dependencies)."""
    env_path = Path(path)
    if not env_path.is_file():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, _, value = line.partition("=")
        if key and _:
            os.environ.setdefault(key.strip(), value.strip())


def main() -> int:
    _load_dotenv()

    parser = argparse.ArgumentParser(description="Run a task through the minimal agent runtime.")
    parser.add_argument("task", help="User task for the agent")
    parser.add_argument("--workspace", default="workspace", help="Workspace directory for filesystem tools")
    parser.add_argument("--memory", default=".agent-memory.json", help="JSON file for persistent memory")
    parser.add_argument("--model", default=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"), help="OpenAI model name")
    parser.add_argument("--max-steps", type=int, default=12, help="Maximum tool/model iterations")
    parser.add_argument("--trace", action="store_true", help="Print a human-readable execution trace")
    parser.add_argument("--save-trace", action="store_true", help="Save a structured JSON trace under logs/")
    parser.add_argument("--verbose", action="store_true", help="Show detailed tool observations in trace output")
    args = parser.parse_args()

    if not os.getenv("OPENAI_API_KEY"):
        print("OPENAI_API_KEY is not set; live model execution is unavailable.")
        return 2

    memory = JsonMemory(args.memory)
    tools = build_filesystem_tools(Path(args.workspace)) + build_memory_tools(memory)
    runtime = AgentRuntime(
        model=OpenAIModelProvider(model=args.model),
        tools=tools,
        memory=memory,
        max_steps=args.max_steps,
    )
    result = runtime.run(args.task)

    print(result.answer or f"Stopped without final answer: {result.stopped_reason}")
    if args.trace:
        print()
        print(format_human_trace(result, verbose=args.verbose))
        print()
        print(format_execution_summary(result))
    if args.save_trace:
        path = save_run_log(result)
        print(f"\nSaved trace: {path}")
    return 0 if result.answer else 1


if __name__ == "__main__":
    raise SystemExit(main())
