import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from agent_runtime import AgentRuntime, FakeModel, JsonMemory, ModelReply, Tool


class RuntimeTests(unittest.TestCase):
    def test_runtime_returns_final_answer_without_tool(self):
        with TemporaryDirectory() as directory:
            model = FakeModel([ModelReply.final("No tools needed.")])
            runtime = AgentRuntime(model=model, tools=[], memory=JsonMemory(Path(directory) / "memory.json"))

            result = runtime.run("Answer directly.")

            self.assertEqual(result.answer, "No tools needed.")
            self.assertEqual([step["type"] for step in result.trace], ["model_invocation", "final"])
            self.assertEqual(model.calls[0]["messages"][0], {"role": "user", "content": "Answer directly."})

    def test_runtime_runs_one_tool_then_final_answer(self):
        with TemporaryDirectory() as directory:
            model = FakeModel(
                [
                    ModelReply.tool_call("add", {"a": 2, "b": 5}),
                    ModelReply.final("7"),
                ]
            )
            runtime = AgentRuntime(
                model=model,
                tools=[Tool("add", "Add two numbers.", {}, lambda args: args["a"] + args["b"])],
                memory=JsonMemory(Path(directory) / "memory.json"),
            )

            result = runtime.run("Add 2 and 5.")

            self.assertEqual(result.answer, "7")
            self.assertEqual([step["type"] for step in result.trace], ["model_invocation", "tool_call", "tool_result", "model_invocation", "final"])

    def test_runtime_completes_multi_step_task_with_tool_and_memory(self):
        with TemporaryDirectory() as directory:
            memory = JsonMemory(Path(directory) / "memory.json")
            tools = [
                Tool("add", "Add two numbers.", {}, lambda args: args["a"] + args["b"]),
                Tool("remember", "Store a memory value.", {}, lambda args: memory.remember(args["key"], args["value"]) or "stored"),
            ]
            model = FakeModel(
                [
                    ModelReply.tool_call("add", {"a": 20, "b": 22}),
                    ModelReply.tool_call("remember", {"key": "answer", "value": 42}),
                    ModelReply.final("The answer is 42."),
                ]
            )
            runtime = AgentRuntime(model=model, tools=tools, memory=memory)

            result = runtime.run("Add the numbers, remember the answer, then report it.")

            self.assertEqual(result.answer, "The answer is 42.")
            self.assertEqual(memory.recall("answer"), 42)
            self.assertEqual(
                [step["type"] for step in result.trace],
                ["model_invocation", "tool_call", "tool_result", "model_invocation", "tool_call", "tool_result", "model_invocation", "final"],
            )
            self.assertEqual(model.calls[-1]["messages"][0]["role"], "user")
            self.assertEqual(model.calls[-1]["messages"][-1]["type"], "function_call_output")

    def test_runtime_records_unknown_tool_as_observation(self):
        with TemporaryDirectory() as directory:
            model = FakeModel(
                [
                    ModelReply.tool_call("missing", {}),
                    ModelReply.final("I could not use that tool."),
                ]
            )
            runtime = AgentRuntime(model=model, tools=[], memory=JsonMemory(Path(directory) / "memory.json"))

            result = runtime.run("Use a missing tool.")

            self.assertEqual(result.answer, "I could not use that tool.")
            self.assertEqual(
                result.trace[2],
                {
                    "type": "tool_error",
                    "tool": "missing",
                    "error": "Unknown tool: missing",
                    "duration_ms": result.trace[2]["duration_ms"],
                },
            )

    def test_runtime_stops_at_step_limit(self):
        with TemporaryDirectory() as directory:
            model = FakeModel([ModelReply.tool_call("noop", {}) for _ in range(3)])
            runtime = AgentRuntime(
                model=model,
                tools=[Tool("noop", "Do nothing.", {}, lambda args: "ok")],
                memory=JsonMemory(Path(directory) / "memory.json"),
                max_steps=2,
            )

            result = runtime.run("Loop forever.")

            self.assertIsNone(result.answer)
            self.assertEqual(result.stopped_reason, "max_steps")

    def test_runtime_records_tool_exception_as_observation(self):
        with TemporaryDirectory() as directory:
            model = FakeModel(
                [
                    ModelReply.tool_call("explode", {}),
                    ModelReply.final("Recovered."),
                ]
            )

            def fail(args):
                raise RuntimeError("boom")

            runtime = AgentRuntime(
                model=model,
                tools=[Tool("explode", "Raise an error.", {}, fail)],
                memory=JsonMemory(Path(directory) / "memory.json"),
            )

            result = runtime.run("Try an erroring tool.")

            self.assertEqual(result.answer, "Recovered.")
            self.assertEqual(result.trace[2]["type"], "tool_error")
            self.assertEqual(result.trace[2]["tool"], "explode")
            self.assertEqual(result.trace[2]["error"], "boom")
            self.assertIn("duration_ms", result.trace[2])


if __name__ == "__main__":
    unittest.main()
