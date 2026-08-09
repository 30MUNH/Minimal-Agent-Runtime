# Submission Guide & Reviewer Brief

**Project:** Minimal Agent Runtime  
**Author / Repository:** [30MUNH/Minimal-Agent-Runtime](https://github.com/30MUNH/Minimal-Agent-Runtime)  
**Portal Website:** [Live Documentation Site](https://minimal-agent-runtime.vercel.app)

---

## 1. What This Project Implements

This repository contains a complete, self-contained Python implementation of an autonomous AI agent runtime built from scratch without external agent frameworks.

Key implemented components:
- **Orchestration Loop (`AgentRuntime`)**: Bounded iterative control loop supporting function calls and step limits.
- **Generic Tool Registry (`Tool`)**: Schema-driven tool registration and execution without tool-specific logic in the loop.
- **Sandboxed Workspace Tools (`filesystem_tools`)**: `list_files`, `read_file`, `write_file`, `search_files` restricted to `workspace/`.
- **Dual Memory Architecture (`JsonMemory`)**: Ephemeral working memory transcript + persistent cross-session JSON key/value store (`remember`, `recall`).
- **Observability System (`observability`)**: Console trace renderer, millisecond execution metrics, and non-sensitive JSON log exporter (`logs/run-XXX.json`).

---

## 2. How to Verify (2-Minute Reviewer Path)

You can verify the entire project offline without installing third-party packages or setting API keys:

```bash
# 1. Run full unit test suite (19 tests, ~0.02s)
python3 -m unittest discover -s tests -v

# 2. Run multi-step task & memory demo
python3 examples/multi_step_task.py

# 3. Run workspace TODO scanner & report generator demo
python3 examples/offline_todo_report_demo.py

# 4. Run execution trace & JSON log generator demo
python3 examples/offline_trace_demo.py
```

---

## 3. How to Run Live (OpenAI API Path)

```bash
# 1. Install optional SDK
python3 -m pip install -e ".[openai]"

# 2. Create .env file with your key
echo "OPENAI_API_KEY=sk-proj-your-key" > .env

# 3. Seed workspace files and execute task with trace
python3 examples/seed_workspace.py
python3 -m agent_runtime.cli --trace --save-trace --verbose \
  "Inspect the files in the workspace, find all TODO items, create a concise report at todo-report.md, and remember where the report was saved."
```

---

## 4. Expected Outputs

- **Unit Tests**: `Ran 19 tests in 0.024s OK`
- **TODO Report Demo**: Creates `workspace/todo-report.md` and saves `todo_report_path` to `.agent-memory.json`.
- **Trace Demo**: Displays step-by-step model/tool interactions and writes `logs/run-002.json`.

---

## 5. Known Limitations

- **Bounded Execution**: Hard cap on iterations via `max_steps` to guarantee termination.
- **Sequential Execution**: Tool calls execute synchronously in single-threaded mode.
- **Sandbox Boundary**: File operations outside `workspace/` are strictly rejected.

---

## 6. Repository Structure

```text
.
├── agent_runtime/    # Core runtime package
├── docs/             # Technical design notes
├── docs-site/        # Static submission portal website
├── examples/         # Offline & online execution scripts
├── tests/            # 19 passing unit tests
├── .env              # Local API environment file
├── DELIVERABLES.md   # Requirement traceability matrix
├── PROJECT_SUMMARY.md# One-page executive summary
├── README.md         # Full project documentation
├── SUBMISSION.md     # This reviewer guide
└── vercel.json       # Vercel deployment config
```
