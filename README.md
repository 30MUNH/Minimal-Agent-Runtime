# Minimal Agent Runtime

A small Python agent runtime with a real orchestration loop, generic tool-calling, JSON-backed persistent memory, deterministic tests, and an optional OpenAI provider for live runs.

## Install

No dependency is required for offline tests and demos:

```bash
python3 -m unittest discover -s tests -v
```

For live OpenAI runs, install the optional SDK:

```bash
python3 -m pip install -e ".[openai]"
export OPENAI_API_KEY="..."
```

## Deterministic / Offline Verification

Run all deterministic tests:

```bash
python3 -m unittest discover -s tests -v
```

Run the fake-model multi-step demo:

```bash
python3 examples/multi_step_task.py
```

Expected shape:

```text
I added the numbers and remembered 42.
memory.demo_sum=42
trace_steps=5
```

This proves the harness loop, tool dispatch, and persistent JSON memory without network access. It does not exercise a production LLM.

Run the stronger offline TODO-report demo, which uses real workspace filesystem tools and fresh-runtime memory recall:

```bash
python3 examples/offline_todo_report_demo.py
```

This creates `workspace/todo-report.md` and stores `todo_report_path` in `.agent-memory.json` using deterministic model replies.

## Production / Live Verification

Seed the reviewer workspace:

```bash
python3 examples/seed_workspace.py
```

Run the live TODO-report task:

```bash
python3 -m agent_runtime.cli \
  "Inspect the files in the workspace, find all TODO items, create a concise report at todo-report.md, and remember where the report was saved."
```

Verify the artifact:

```bash
test -f workspace/todo-report.md
cat workspace/todo-report.md
cat .agent-memory.json
```

Start a fresh invocation and recall the saved report path:

```bash
python3 -m agent_runtime.cli "Where did you save the TODO report?"
```

The CLI exits with code `2` and a clear message if `OPENAI_API_KEY` is not configured.

## Runtime Trace

The CLI keeps normal output minimal. Add `--trace` to print a human-readable execution trace and metrics summary:

```bash
python3 -m agent_runtime.cli --trace "Where did you save the TODO report?"
```

Add `--verbose` to include detailed tool observations in the trace:

```bash
python3 -m agent_runtime.cli --trace --verbose "Where did you save the TODO report?"
```

Add `--save-trace` to write structured JSON logs under `logs/`:

```bash
python3 -m agent_runtime.cli --trace --save-trace \
  "Inspect the files in the workspace, find all TODO items, create a concise report at todo-report.md, and remember where the report was saved."
```

Without OpenAI credentials, reviewers can exercise the same trace renderer and JSON log writer offline:

```bash
python3 examples/offline_trace_demo.py
```

JSON logs are named `logs/run-001.json`, `logs/run-002.json`, and so on. They include timestamp, task, model provider, step list, tool calls, tool results/errors, durations, final answer, and termination reason. They do not log secrets.

Example trace shape:

```text
STEP 1
Model invocation

STEP 2
Model requested tool:
  search_files
Arguments:
  {"query": "TODO"}

STEP 3
Executed tool:
  search_files
Status:
  success
Duration:
  1 ms
Returned:
  4 matches

STEP 4
Final Answer
Termination reason: final

Execution Summary

Steps: 4

Tools:
- search_files ..... 1 ms (ok)

Total runtime:
3 ms
```

## Built-In Tools

Filesystem tools are restricted to `workspace/` and reject traversal outside it:

- `list_files`
- `read_file`
- `write_file`
- `search_files`

Persistent memory tools:

- `remember`
- `recall`

## Design Note

See [docs/agent-runtime-design.md](docs/agent-runtime-design.md).
