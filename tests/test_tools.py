import unittest

from agent_runtime import Tool


class ToolTests(unittest.TestCase):
    def test_tool_runs_handler_with_arguments(self):
        tool = Tool(
            name="add",
            description="Add two numbers.",
            schema={"type": "object"},
            handler=lambda args: args["a"] + args["b"],
        )

        self.assertEqual(tool.run({"a": 2, "b": 5}), 7)

    def test_tool_requires_mapping_arguments(self):
        tool = Tool(
            name="echo",
            description="Return the input.",
            schema={"type": "object"},
            handler=lambda args: args,
        )

        with self.assertRaisesRegex(TypeError, "arguments"):
            tool.run(["not", "a", "mapping"])


if __name__ == "__main__":
    unittest.main()
