from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .runtime import AgentResult


def format_human_trace(result: AgentResult, verbose: bool = False) -> str:
    lines: list[str] = []
    for index, step in enumerate(result.trace, start=1):
        lines.append(f"STEP {index}")
        step_type = step["type"]
        if step_type == "model_invocation":
            lines.append("Model invocation")
        elif step_type == "tool_call":
            lines.append("Model requested tool:")
            lines.append(f"  {step['tool']}")
            lines.append("Arguments:")
            lines.append(f"  {_json(step.get('args', {}))}")
        elif step_type in {"tool_result", "tool_error"}:
            lines.append("Executed tool:")
            lines.append(f"  {step['tool']}")
            lines.append("Status:")
            lines.append(f"  {'success' if step_type == 'tool_result' else 'failure'}")
            lines.append("Duration:")
            lines.append(f"  {step.get('duration_ms', 0)} ms")
            lines.append("Returned:" if step_type == "tool_result" else "Error:")
            lines.append(f"  {_summarize(step.get('result') if step_type == 'tool_result' else step.get('error'), verbose)}")
        elif step_type == "final":
            lines.append("Final Answer")
            if verbose and step.get("content"):
                lines.append(f"  {step['content']}")
        if "termination_reason" in step:
            lines.append(f"Termination reason: {step['termination_reason']}")
        lines.append("")
    return "\n".join(lines).rstrip()


def format_execution_summary(result: AgentResult) -> str:
    lines = ["Execution Summary", "", f"Steps: {len(result.trace)}", "", "Tools:"]
    tool_steps = [step for step in result.trace if step["type"] in {"tool_result", "tool_error"}]
    if not tool_steps:
        lines.append("- none")
    for step in tool_steps:
        status = "ok" if step["type"] == "tool_result" else "failed"
        lines.append(f"- {step['tool']} ..... {step.get('duration_ms', 0)} ms ({status})")
    lines.extend(["", "Total runtime:", f"{result.total_duration_ms} ms"])
    return "\n".join(lines)


def save_run_log(result: AgentResult, log_dir: str | Path = "logs") -> Path:
    directory = Path(log_dir)
    directory.mkdir(parents=True, exist_ok=True)
    path = _next_log_path(directory)
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "task": result.task,
        "model_provider": result.model_provider,
        "steps": result.trace,
        "tool_calls": [step for step in result.trace if step["type"] == "tool_call"],
        "tool_results": [step for step in result.trace if step["type"] in {"tool_result", "tool_error"}],
        "final_answer": result.answer,
        "termination_reason": result.stopped_reason,
        "total_duration_ms": result.total_duration_ms,
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


def _next_log_path(directory: Path) -> Path:
    existing = sorted(directory.glob("run-*.json"))
    if not existing:
        return directory / "run-001.json"
    highest = max(int(path.stem.split("-")[1]) for path in existing)
    return directory / f"run-{highest + 1:03d}.json"


def _json(value: Any) -> str:
    return json.dumps(value, sort_keys=True)


def _summarize(value: Any, verbose: bool) -> str:
    if verbose:
        return _json(value)
    if isinstance(value, list):
        if value and all(isinstance(item, dict) and "line" in item for item in value):
            return f"{len(value)} matches"
        return f"{len(value)} items"
    if isinstance(value, dict):
        return f"{len(value)} keys"
    text = str(value)
    if len(text) > 80:
        return text[:77] + "..."
    return text
