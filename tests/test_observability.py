import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from agent_runtime import AgentRuntime, FakeModel, JsonMemory, ModelReply, Tool
from agent_runtime.observability import format_execution_summary, format_human_trace, save_run_log


class ObservabilityTests(unittest.TestCase):
    def test_human_trace_shows_model_tool_execution_and_final_answer(self):
        with TemporaryDirectory() as directory:
            runtime = AgentRuntime(
                model=FakeModel([ModelReply.tool_call("echo", {"text": "hi"}), ModelReply.final("done")]),
                tools=[Tool("echo", "Echo text.", {}, lambda args: args["text"])],
                memory=JsonMemory(Path(directory) / "memory.json"),
            )

            result = runtime.run("Echo hi.")
            text = format_human_trace(result)

            self.assertIn("STEP 1", text)
            self.assertIn("Model requested tool:", text)
            self.assertIn("echo", text)
            self.assertIn("Arguments:", text)
            self.assertIn('"text": "hi"', text)
            self.assertIn("STEP 2", text)
            self.assertIn("Executed tool:", text)
            self.assertIn("Duration:", text)
            self.assertIn("Returned:", text)
            self.assertIn("STEP 3", text)
            self.assertIn("Final Answer", text)
            self.assertIn("Termination reason: final", text)

    def test_execution_summary_lists_tools_and_total_runtime(self):
        with TemporaryDirectory() as directory:
            runtime = AgentRuntime(
                model=FakeModel([ModelReply.tool_call("echo", {"text": "hi"}), ModelReply.final("done")]),
                tools=[Tool("echo", "Echo text.", {}, lambda args: args["text"])],
                memory=JsonMemory(Path(directory) / "memory.json"),
            )

            result = runtime.run("Echo hi.")
            text = format_execution_summary(result)

            self.assertIn("Execution Summary", text)
            self.assertIn("Steps: 5", text)
            self.assertIn("- echo", text)
            self.assertIn("Total runtime:", text)

    def test_save_run_log_writes_structured_json(self):
        with TemporaryDirectory() as directory:
            runtime = AgentRuntime(
                model=FakeModel([ModelReply.tool_call("echo", {"text": "hi"}), ModelReply.final("done")]),
                tools=[Tool("echo", "Echo text.", {}, lambda args: args["text"])],
                memory=JsonMemory(Path(directory) / "memory.json"),
            )
            result = runtime.run("Echo hi.")

            path = save_run_log(result, Path(directory) / "logs")
            data = json.loads(path.read_text(encoding="utf-8"))

            self.assertEqual(path.name, "run-001.json")
            self.assertEqual(data["task"], "Echo hi.")
            self.assertEqual(data["model_provider"], "FakeModel")
            self.assertEqual(data["termination_reason"], "final")
            self.assertEqual(data["final_answer"], "done")
            self.assertEqual(data["steps"][0]["type"], "model_invocation")
            self.assertEqual(data["steps"][1]["type"], "tool_call")
            self.assertEqual(data["steps"][2]["type"], "tool_result")
            self.assertIn("duration_ms", data["steps"][2])
