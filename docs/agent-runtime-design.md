# Minimal Agent Runtime Design

## Orchestration Loop

`AgentRuntime.run(task)` starts one run-level working memory transcript with the user task. Each loop iteration sends the current `messages` transcript plus generic tool definitions to the configured model provider. The provider returns a normalized `ModelReply`: either a final answer or one function/tool call.

For a tool call, the runtime records the model request, looks up the tool by name, executes it, appends a structured observation (`tool_result` or `tool_error`) to both the trace and the transcript, then calls the model again. Unknown tools, invalid arguments, and tool exceptions become observations when the model can still recover. The loop terminates on a final answer or `max_steps`.

```text
user task -> model(messages, tools)
          -> final answer -> stop
          -> tool call -> registry lookup -> run(args)
                       -> observation -> model(messages, tools) ...
```

## Tool Interface

Each `Tool` exposes `name`, `description`, a JSON input `schema`, and a `handler` executed by `run(args)`. The runtime only knows this interface; there are no tool-specific branches in the orchestration loop.

The registry is a dictionary keyed by tool name. Filesystem tools (`list_files`, `read_file`, `write_file`, `search_files`) are bounded to `workspace/`. Memory tools (`remember`, `recall`) expose persistent memory explicitly to the model.

## Memory

Run memory is the in-memory transcript for one execution: user task, model replies, tool calls, and tool observations. It is discarded after `run()` returns.

Persistent memory is `JsonMemory`, a JSON-backed key/value store that survives process restarts. The model accesses it through explicit `remember(key, value)` and `recall(key)` tools, so cross-run facts are deliberate rather than a hidden dump of the whole memory file into every prompt. A fresh runtime can reload the same JSON file and recall a saved fact.

## Observability

Execution tracing exists so reviewers can see the loop think-act-observe cycle without reading raw Python objects. The runtime records model invocations, tool requests, tool outcomes, termination, and per-tool durations in the same trace used by tests and CLI output.

Structured JSON logs make a run inspectable after the fact: task, provider, steps, tool calls, observations, timings, final answer, and stop reason are stored without secrets. Timing is intentionally lightweight, using simple millisecond measurements around tool execution and total runtime, which is enough to debug slow tools and confirm that the harness really iterated.
