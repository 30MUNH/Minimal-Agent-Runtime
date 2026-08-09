import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from agent_runtime import JsonMemory
from agent_runtime.memory_tools import build_memory_tools


class MemoryToolTests(unittest.TestCase):
    def test_remember_and_recall_are_explicit_tools_across_instances(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "memory.json"
            tools = {tool.name: tool for tool in build_memory_tools(JsonMemory(path))}

            self.assertEqual(tools["remember"].run({"key": "report_path", "value": "todo-report.md"}), "stored")

            fresh_tools = {tool.name: tool for tool in build_memory_tools(JsonMemory(path))}
            self.assertEqual(fresh_tools["recall"].run({"key": "report_path"}), "todo-report.md")
