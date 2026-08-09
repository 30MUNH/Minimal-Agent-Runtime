# Agent Runtime Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a minimal Python agent runtime with an orchestration loop, tool-calling, JSON-backed memory, tests, a demo, and a short design note.

**Architecture:** The runtime is a deterministic harness: a model callable returns either a final answer or a tool call, the loop executes tools and records observations, and memory persists facts in a JSON file. The model interface is intentionally simple so tests and local demos can run without network access.

**Tech Stack:** Python 3.11+, standard library, pytest.

## Global Constraints

- Keep the implementation minimal but real.
- Avoid external runtime dependencies.
- Tool failures must become observations in the loop instead of crashing ordinary task execution.
- Memory must persist across runtime instances by reading and writing JSON.
- The design note must explain the orchestration loop, tool interface, and memory.

---

### Task 1: Package And Memory

**Files:**
- Create: `pyproject.toml`
- Create: `agent_runtime/__init__.py`
- Create: `agent_runtime/memory.py`
- Test: `tests/test_memory.py`

**Interfaces:**
- Produces: `JsonMemory(path: str | Path)`, `remember(key: str, value: Any) -> None`, `recall(key: str, default: Any = None) -> Any`, `context() -> dict[str, Any]`

- [x] **Step 1: Write the failing test**
- [ ] **Step 2: Run test to verify it fails**
- [ ] **Step 3: Write minimal implementation**
- [ ] **Step 4: Run test to verify it passes**

### Task 2: Tool Interface

**Files:**
- Create: `agent_runtime/tools.py`
- Test: `tests/test_tools.py`

**Interfaces:**
- Produces: `Tool(name: str, description: str, schema: dict[str, Any], handler: Callable[[dict[str, Any]], Any])`, `Tool.run(args: dict[str, Any]) -> Any`

- [x] **Step 1: Write the failing test**
- [ ] **Step 2: Run test to verify it fails**
- [ ] **Step 3: Write minimal implementation**
- [ ] **Step 4: Run test to verify it passes**

### Task 3: Orchestration Loop

**Files:**
- Create: `agent_runtime/runtime.py`
- Test: `tests/test_runtime.py`

**Interfaces:**
- Consumes: `JsonMemory`, `Tool`
- Produces: `AgentRuntime(model, tools, memory, max_steps=8)`, `run(task: str) -> AgentResult`

- [x] **Step 1: Write the failing test**
- [ ] **Step 2: Run test to verify it fails**
- [ ] **Step 3: Write minimal implementation**
- [ ] **Step 4: Run test to verify it passes**

### Task 4: Demo And Design Note

**Files:**
- Create: `examples/multi_step_task.py`
- Create: `docs/agent-runtime-design.md`

**Interfaces:**
- Consumes: public package API from `agent_runtime`

- [ ] **Step 1: Add a deterministic demo that completes a multi-step task**
- [ ] **Step 2: Add a short design note covering loop, tools, and memory**
- [ ] **Step 3: Run full test suite and demo**
