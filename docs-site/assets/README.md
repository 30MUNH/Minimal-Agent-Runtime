# Screenshot Capture & Verification Instructions

This directory contains visual assets and placeholder visual cards for the Minimal Agent Runtime submission portal.

## How to Capture Official Screenshots

For full submission submission packages, replace the placeholder SVGs with real PNG terminal captures:

### 1. `terminal-tests.png`
- **Command:** `python3 -m unittest discover -s tests -v`
- **Capture Area:** Terminal output showing all 19 unit tests passing (`Ran 19 tests in 0.024s OK`).

### 2. `offline-demo.png`
- **Command:** `python3 examples/multi_step_task.py`
- **Capture Area:** Terminal showing FakeModel multi-step loop completion and memory key storing `42`.

### 3. `execution-trace.png`
- **Command:** `python3 examples/offline_trace_demo.py`
- **Capture Area:** Terminal output showing step-by-step trace formatting and `Execution Summary` metrics.

### 4. `todo-report.png`
- **Command:** `python3 examples/offline_todo_report_demo.py && cat workspace/todo-report.md`
- **Capture Area:** Terminal showing the generated `todo-report.md` artifact and `.agent-memory.json` verification.
